import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional
import json
from models.schemas import UserInfo

logger = logging.getLogger(__name__)

class LinkedInService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

    async def get_user_info(self) -> UserInfo:
        """Get LinkedIn user information using OpenID Connect"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use OpenID Connect userinfo endpoint instead of people endpoint
                userinfo_url = "https://api.linkedin.com/v2/userinfo"

                async with session.get(
                    userinfo_url,
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"LinkedIn API error: {response.status} - {error_text}")

                    data = await response.json()

                    # OpenID Connect userinfo response format
                    return UserInfo(
                        id=data.get('sub'),  # 'sub' is the user ID in OpenID Connect
                        first_name=data.get('given_name', ''),
                        last_name=data.get('family_name', ''),
                        headline=data.get('name', ''),  # Full name as headline
                        profile_picture=data.get('picture', None)
                    )

        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            raise

    async def create_post(self, content: str, person_id: str) -> Dict[str, Any]:
        """Create a LinkedIn post using UGC API with character limit validation"""
        try:
            # SAFETY CHECK: Ensure content is within LinkedIn's character limit
            if len(content) > 3000:
                logger.warning(f"⚠️ Content too long ({len(content)} chars). Truncating to 3000 chars.")
                # Smart truncation - try to end at a sentence
                truncated = content[:2950]  # Leave some margin
                last_period = truncated.rfind('.')
                last_question = truncated.rfind('?')
                last_exclamation = truncated.rfind('!')
                
                best_ending = max(last_period, last_question, last_exclamation)
                if best_ending > 2800:  # Good ending point found
                    content = content[:best_ending + 1]
                else:
                    content = truncated
                
                logger.info(f"✂️ Content truncated to {len(content)} characters")

            # For OpenID Connect person IDs, we need to format them properly
            # person_id from userinfo is just the ID, we need to format it as URN
            if not person_id.startswith('urn:li:person:'):
                author_urn = f"urn:li:person:{person_id}"
            else:
                author_urn = person_id

            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/ugcPosts",
                    headers=self.headers,
                    json=post_data
                ) as response:
                    if response.status not in [200, 201]:
                        error_text = await response.text()
                        
                        # Specific handling for character limit errors
                        if "text length" in error_text and "exceeded" in error_text:
                            logger.error(f"❌ Character limit exceeded. Content length: {len(content)}")
                            raise Exception(f"LinkedIn post creation failed: Content too long ({len(content)} characters). LinkedIn limit is 3000 characters.")
                        
                        raise Exception(f"LinkedIn post creation failed: {response.status} - {error_text}")

                    result = await response.json()
                    logger.info(f"✅ Post created successfully: {result.get('id')}")
                    logger.info(f"📊 Final content length: {len(content)} characters")
                    return result

        except Exception as e:
            logger.error(f"Error creating LinkedIn post: {e}")
            raise

    async def create_article_post(self, title: str, content: str, person_id: str) -> Dict[str, Any]:
        """Create a LinkedIn article post"""
        try:
            # Combine title and content for total length check
            combined_content = f"{title}\n\n{content}"
            if len(combined_content) > 3000:
                logger.warning(f"⚠️ Article content too long ({len(combined_content)} chars). Consider shortening.")

            post_data = {
                "author": f"urn:li:person:{person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": combined_content
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": content
                                },
                                "title": {
                                    "text": title
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/ugcPosts",
                    headers=self.headers,
                    json=post_data
                ) as response:
                    if response.status not in [200, 201]:
                        error_text = await response.text()
                        raise Exception(f"LinkedIn article creation failed: {response.status} - {error_text}")

                    return await response.json()

        except Exception as e:
            logger.error(f"Error creating LinkedIn article: {e}")
            raise

    async def get_posts(self, person_id: str, count: int = 10) -> list:
        """Get recent posts for a user"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": "authors",
                    "authors": f"urn:li:person:{person_id}",
                    "count": count,
                    "sortBy": "LAST_MODIFIED"
                }

                async with session.get(
                    f"{self.base_url}/ugcPosts",
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"LinkedIn get posts failed: {response.status} - {error_text}")

                    data = await response.json()
                    return data.get('elements', [])

        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            raise

    async def delete_post(self, post_id: str) -> bool:
        """Delete a LinkedIn post"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/ugcPosts/{post_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 204:
                        logger.info(f"Post {post_id} deleted successfully")
                        return True
                    else:
                        error_text = await response.text()
                        raise Exception(f"LinkedIn delete post failed: {response.status} - {error_text}")

        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            raise

    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post"""
        try:
            async with aiohttp.ClientSession() as session:
                # Note: This requires specific permissions and may not be available for all apps
                async with session.get(
                    f"{self.base_url}/socialActions/{post_id}",
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"LinkedIn analytics failed: {response.status} - {error_text}")

                    return await response.json()

        except Exception as e:
            logger.error(f"Error fetching post analytics: {e}")
            raise

    async def test_connection(self) -> bool:
        """Test if the LinkedIn connection is working"""
        try:
            await self.get_user_info()
            return True
        except Exception as e:
            logger.error(f"LinkedIn connection test failed: {e}")
            return False

    def _build_share_content(self, content: str, media_type: str = "NONE") -> Dict[str, Any]:
        """Helper method to build share content"""
        share_content = {
            "shareCommentary": {
                "text": content
            },
            "shareMediaCategory": media_type
        }

        return share_content

    async def upload_image(self, image_data: bytes, person_id: str) -> str:
        """Upload image to LinkedIn (for future use with image posts)"""
        try:
            # First, register the upload
            register_upload_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{person_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            async with aiohttp.ClientSession() as session:
                # Register upload
                async with session.post(
                    f"{self.base_url}/assets?action=registerUpload",
                    headers=self.headers,
                    json=register_upload_data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Image upload registration failed: {response.status} - {error_text}")

                    upload_info = await response.json()
                    upload_url = upload_info['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
                    asset_id = upload_info['value']['asset']

                    # Upload the actual image
                    upload_headers = {"Authorization": f"Bearer {self.access_token}"}

                    async with session.put(
                        upload_url,
                        headers=upload_headers,
                        data=image_data
                    ) as upload_response:
                        if upload_response.status != 201:
                            error_text = await upload_response.text()
                            raise Exception(f"Image upload failed: {upload_response.status} - {error_text}")

                        return asset_id

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise
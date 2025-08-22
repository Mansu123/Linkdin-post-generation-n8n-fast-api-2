import asyncio
import logging
import random
from typing import Optional
from groq import Groq
from models.schemas import PostTone, PostLength

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self, api_key: str, model_name: str = None):
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
        
        # Available current models (as of August 2025)
        self.available_models = {
            "fast": "llama-3.1-8b-instant",       # Fastest, cheapest
            "balanced": "gemma2-9b-it",           # Good balance of speed/quality  
            "quality": "llama-3.3-70b-versatile", # Best quality (replacement for deprecated model)
            "compound": "compound-beta"           # Latest compound AI system
        }
        
        # Use provided model or default to quality
        if model_name and model_name in self.available_models.values():
            self.model_name = model_name
        elif model_name and model_name in self.available_models:
            self.model_name = self.available_models[model_name]
        else:
            self.model_name = self.available_models["quality"]  # Default to best quality
            
        logger.info(f"✅ Initialized Groq with model: {self.model_name}")

    def switch_model(self, model_key: str):
        """Switch to a different model"""
        if model_key in self.available_models:
            self.model_name = self.available_models[model_key]
            logger.info(f"🔄 Switched to model: {self.model_name}")
        else:
            logger.warning(f"⚠️ Unknown model key: {model_key}. Available: {list(self.available_models.keys())}")

    async def generate_post_content(
        self,
        topic: str,
        tone: PostTone = PostTone.PROFESSIONAL,
        length: PostLength = PostLength.MEDIUM,
        hashtags: bool = True,
        target_audience: Optional[str] = None,
        call_to_action: Optional[str] = None
    ) -> str:
        """Generate LinkedIn post content using Groq AI"""
        try:
            logger.info(f"🤖 Generating content for topic: {topic}")
            logger.info(f"🔧 Using model: {self.model_name}")

            # Build a detailed, specific prompt
            prompt = self._build_prompt(topic, tone, length, hashtags, target_audience, call_to_action)

            # Generate with Groq
            content = await self._generate_with_groq(prompt)

            # CRITICAL: Ensure content fits LinkedIn's character limit
            content = self._enforce_character_limit(content)

            logger.info(f"✅ Generated {len(content)} characters successfully")
            return content

        except Exception as e:
            logger.error(f"❌ Error in generate_post_content: {e}")
            
            # Check if it's a model error and suggest fallback
            if "model" in str(e).lower() and ("decommissioned" in str(e).lower() or "deprecated" in str(e).lower()):
                logger.info("🔄 Model issue detected, trying fallback model...")
                try:
                    # Try with the fast model as fallback
                    original_model = self.model_name
                    self.model_name = self.available_models["fast"]
                    content = await self._generate_with_groq(prompt)
                    content = self._enforce_character_limit(content)
                    logger.info(f"✅ Fallback successful with {self.model_name}")
                    return content
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback also failed: {fallback_error}")
                    self.model_name = original_model  # Restore original
                    
            # Handle rate limits
            if "rate" in str(e).lower() or "quota" in str(e).lower() or "429" in str(e):
                return f"""⚠️ Rate limit reached for Groq API.
Please wait a moment before generating more content.

Topic requested: {topic}

Current model: {self.model_name}
Try switching to a faster model like 'fast' for higher rate limits.

Visit: https://console.groq.com/docs/rate-limits for more info."""
            else:
                raise e

    def _enforce_character_limit(self, content: str, max_chars: int = 2950) -> str:
        """Ensure content fits within LinkedIn's character limit with safety margin"""
        if len(content) <= max_chars:
            return content
        
        logger.warning(f"⚠️ Content too long ({len(content)} chars). Trimming to {max_chars} chars.")
        
        # Smart truncation - try to end at a sentence or paragraph
        truncated = content[:max_chars]
        
        # Find the last complete sentence
        last_period = truncated.rfind('.')
        last_question = truncated.rfind('?')
        last_exclamation = truncated.rfind('!')
        
        # Use the latest sentence ending
        best_ending = max(last_period, last_question, last_exclamation)
        
        if best_ending > max_chars - 200:  # If we found a good ending point
            truncated = content[:best_ending + 1]
        
        # Add continuation indicator if we had to truncate
        if len(content) > max_chars:
            # Remove any trailing incomplete hashtags or words
            lines = truncated.split('\n')
            cleaned_lines = []
            
            for line in lines:
                if line.startswith('#') and len(line) < 3:  # Incomplete hashtag
                    continue
                cleaned_lines.append(line)
            
            truncated = '\n'.join(cleaned_lines)
            
            # Add continuation note if space allows
            if len(truncated) < max_chars - 50:
                truncated += "\n\n[Content continued in comments...]"
        
        return truncated

    def _build_prompt(
        self,
        topic: str,
        tone: PostTone,
        length: PostLength,
        hashtags: bool,
        target_audience: Optional[str] = None,
        call_to_action: Optional[str] = None
    ) -> str:
        """Build a detailed prompt for any topic - ENHANCED VERSION with CHARACTER LIMITS"""
        
        # Enhanced topic-specific guidance
        topic_expertise = {
            "ai agent": "Discuss different types of AI agents (reactive, deliberative, learning, collaborative), specific platforms like OpenAI GPTs, Microsoft Copilot, real business applications, implementation strategies, and measurable ROI",
            "artificial intelligence": "Cover current AI trends, specific technologies (GPT, Claude, Midjourney), real company case studies, practical applications across industries, ethical considerations, and future predictions",
            "machine learning": "Explain ML types (supervised, unsupervised, reinforcement), specific tools (TensorFlow, PyTorch, scikit-learn), real-world applications, data requirements, career paths, and business impact",
            "programming": "Discuss modern frameworks, specific languages and their use cases, development best practices, emerging trends (AI-assisted coding), career advice, and productivity tools",
            "data science": "Cover the full data science pipeline, specific tools and platforms, real project examples, business impact measurement, career paths, and industry applications"
        }

        # Get topic-specific guidance
        topic_lower = topic.lower()
        specific_guidance = "Provide detailed, expert-level insights with specific examples, tools, companies, and actionable advice"
        
        for key, guidance in topic_expertise.items():
            if key in topic_lower:
                specific_guidance = guidance
                break

        # UPDATED: Character-aware length specifications
        length_specs = {
            PostLength.SHORT: "1-2 concise paragraphs (aim for 400-800 characters total)",
            PostLength.MEDIUM: "2-3 focused paragraphs (aim for 1500-2500 characters total)",
            PostLength.LONG: "3-4 detailed paragraphs (aim for 2500-2800 characters total)"
        }

        tone_specs = {
            PostTone.PROFESSIONAL: "authoritative and expert-level",
            PostTone.CASUAL: "conversational but knowledgeable",
            PostTone.INSPIRATIONAL: "motivating and forward-thinking",
            PostTone.EDUCATIONAL: "informative and teaching-focused",
            PostTone.PROMOTIONAL: "persuasive and benefit-focused"
        }

        # Build enhanced prompt with character limits
        prompt = f"""You are a recognized expert writing a LinkedIn post about "{topic}".

CRITICAL REQUIREMENTS:
- MAXIMUM 2900 characters total (LinkedIn limit is 3000, stay under for safety)
- Length: {length_specs[length]}
- Tone: {tone_specs[tone]}
- Focus: {specific_guidance}
- Include specific company names, tools, statistics, or real examples
- Provide actionable insights professionals can immediately use
- Use professional LinkedIn formatting with line breaks
- Sound like a subject matter expert who has deep hands-on experience

IMPORTANT: Keep the post concise and within LinkedIn's character limit. Quality over quantity."""

        if target_audience:
            prompt += f"\n- Target audience: {target_audience}"

        if call_to_action:
            prompt += f"\n- End with: {call_to_action}"
        else:
            cta_options = [
                f"What's your experience with {topic}?",
                f"How are you implementing {topic} in your work?",
                f"What challenges have you faced with {topic}?",
                f"Which {topic} tools have you found most effective?"
            ]
            prompt += f"\n- End with this question: {random.choice(cta_options)}"

        if hashtags:
            prompt += f"\n- Include 3-4 specific hashtags related to {topic} (keep hashtags short)"

        prompt += f"\n\nWrite a compelling LinkedIn post that stays under 2900 characters:"

        return prompt

    async def _generate_with_groq(self, prompt: str) -> str:
        """Generate content using Groq API with enhanced response processing"""
        try:
            logger.info(f"📡 Calling Groq API with model: {self.model_name}")

            # Adjust parameters based on model type
            if self.model_name == "compound-beta":
                # Compound AI system uses different parameters
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert LinkedIn content creator who writes engaging, professional posts that drive meaningful conversations and engagement. Always keep posts under 2900 characters for LinkedIn compatibility."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                # Async wrapper for Groq API call
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        messages=messages,
                        model=self.model_name,
                        max_tokens=800,  # Reduced to help stay within character limit
                        temperature=0.7
                    )
                )
            else:
                # Standard chat completion
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert LinkedIn content creator who writes engaging, professional posts that drive meaningful conversations and engagement. Always keep posts under 2900 characters for LinkedIn compatibility."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                # Async wrapper for Groq API call
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        messages=messages,
                        model=self.model_name,
                        max_tokens=800,  # Reduced to help stay within character limit
                        temperature=0.7,
                        top_p=0.9
                    )
                )

            if response and response.choices and len(response.choices) > 0:
                raw_content = response.choices[0].message.content.strip()
                
                # Clean the response to remove prompt leakage
                cleaned_content = self._clean_response(raw_content)
                
                logger.info(f"✅ Groq returned {len(cleaned_content)} characters")
                return cleaned_content
            else:
                logger.error("❌ Empty response from Groq")
                raise Exception("Empty response from Groq API")

        except Exception as e:
            logger.error(f"❌ Groq API call failed: {e}")
            raise Exception(f"Groq API error: {str(e)}")

    def _clean_response(self, content: str) -> str:
        """Clean Groq response to remove prompt instructions and improve quality"""
        
        # Remove common instruction phrases that leak through
        instruction_phrases = [
            "Here's a LinkedIn post about",
            "Here's a professional LinkedIn post",
            "LinkedIn post:",
            "Content Requirements:",
            "REQUIREMENTS:",
            "Instructions:",
            "Write the LinkedIn post:",
            "Generate the post content now:",
            "Post content:",
            "CRITICAL:",
            "Length:",
            "Tone:",
            "Focus:",
            "Target audience:",
            "End with:",
            "Include 3-4",
            "- Write",
            "- Use",
            "- Include",
            "- Provide",
            "- Sound like"
        ]

        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip lines containing instruction phrases
            should_skip = False
            for phrase in instruction_phrases:
                if phrase.lower() in line.lower():
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Skip empty lines at the beginning
            if not line and not cleaned_lines:
                continue
            
            # Skip lines that look like prompt formatting
            if line.startswith('-') and len(line.split()) < 8:
                continue
            
            cleaned_lines.append(line)

        # Join back together
        final_content = '\n'.join(cleaned_lines).strip()
        
        # If content is too short, it might be corrupted
        if len(final_content) < 50:
            logger.warning("Content seems too short after cleaning")
        
        return final_content

    async def enhance_content(self, content: str) -> str:
        """Enhance existing content"""
        prompt = f"""Improve this LinkedIn post while keeping it under 2900 characters:

{content}

Make it more engaging, professional, and add a compelling call to action.
IMPORTANT: Must stay under 2900 characters for LinkedIn.

Enhanced post:"""

        enhanced = await self._generate_with_groq(prompt)
        return self._enforce_character_limit(enhanced)

    async def generate_hashtags(self, content: str, count: int = 4) -> list:
        """Generate hashtags for content"""
        prompt = f"""Generate {count} relevant LinkedIn hashtags for this post:

{content}

Return only hashtags separated by spaces, starting with #:"""

        response = await self._generate_with_groq(prompt)
        hashtags = response.strip().split()
        return [tag for tag in hashtags if tag.startswith('#')][:count]  # Limit to requested count

    def get_available_models(self) -> dict:
        """Get list of available models"""
        return self.available_models.copy()
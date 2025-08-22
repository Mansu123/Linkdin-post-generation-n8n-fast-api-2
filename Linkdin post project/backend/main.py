from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Optional
from services.groq_service import GroqService  # Changed from gemini_service to groq_service
from services.linkedin_service import LinkedInService
from models.schemas import PostRequest, PostResponse, UserInfo
from config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for services
groq_service = None  # Changed from gemini_service to groq_service
linkedin_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting LinkedIn Post Automation API")
    global groq_service, linkedin_service  # Changed from gemini_service to groq_service
    
    settings = get_settings()
    groq_service = GroqService(settings.groq_api_key)  # Changed from gemini to groq
    linkedin_service = LinkedInService(settings.linkedin_access_token)
    
    yield
    # Shutdown
    logger.info("🛑 Shutting down LinkedIn Post Automation API")

app = FastAPI(title="LinkedIn Post Automation", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LinkedIn Post Automation API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/user/info", response_model=UserInfo)
async def get_user_info():
    """Get LinkedIn user information"""
    try:
        user_info = await linkedin_service.get_user_info()
        return user_info
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-content")
async def generate_content(request: PostRequest):
    """Generate content using Groq AI - SIMPLE VERSION"""  # Updated comment
    try:
        logger.info(f"📝 Content request for topic: '{request.topic}'")
        
        if not request.topic or request.topic.strip() == "":
            raise HTTPException(status_code=400, detail="Topic is required")

        # Call Groq service instead of Gemini
        content = await groq_service.generate_post_content(
            topic=request.topic.strip(),
            tone=request.tone,
            length=request.length,
            hashtags=request.include_hashtags,
            target_audience=request.target_audience,
            call_to_action=request.call_to_action
        )

        logger.info(f"✅ Generated content: {len(content)} characters")
        
        return {
            "generated_content": content,
            "topic": request.topic,
            "status": "success"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )

@app.post("/post/create", response_model=PostResponse)
async def create_post(request: PostRequest, background_tasks: BackgroundTasks):
    """Create and publish LinkedIn post"""
    try:
        settings = get_settings()
        
        # Generate content using Groq if not provided
        if not request.content:
            logger.info("Generating content using Groq AI")  # Updated comment
            content = await groq_service.generate_post_content(
                topic=request.topic,
                tone=request.tone,
                length=request.length,
                hashtags=request.include_hashtags
            )
        else:
            content = request.content

        # Post to LinkedIn
        logger.info("Publishing post to LinkedIn")
        post_result = await linkedin_service.create_post(
            content=content,
            person_id=settings.linkedin_person_id
        )

        return PostResponse(
            success=True,
            post_id=post_result.get("id"),
            content=content,
            message="Post published successfully"
        )

    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post/schedule")
async def schedule_post(request: PostRequest, background_tasks: BackgroundTasks):
    """Schedule a post for later publishing"""
    try:
        # Generate content if not provided
        content = await groq_service.generate_post_content(  # Changed from gemini_service to groq_service
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            hashtags=request.include_hashtags
        )

        # Add to background tasks for actual scheduling
        background_tasks.add_task(schedule_linkedin_post, content, request.schedule_time)

        return {"message": "Post scheduled successfully", "content": content}

    except Exception as e:
        logger.error(f"Error scheduling post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def schedule_linkedin_post(content: str, schedule_time: Optional[str]):
    """Background task for scheduled posting"""
    # Implement actual scheduling logic here
    logger.info(f"Post scheduled for {schedule_time}: {content[:50]}...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
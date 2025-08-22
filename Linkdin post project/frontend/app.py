import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configure page
st.set_page_config(
    page_title="LinkedIn Post Automation",
    page_icon="📱",
    layout="wide"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"

def check_backend_health() -> bool:
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_user_info() -> Dict[str, Any]:
    """Get LinkedIn user information"""
    try:
        response = requests.get(f"{BACKEND_URL}/user/info", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching user info: {response.text}")
            return {}
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return {}

def generate_content(topic: str, tone: str, length: str, include_hashtags: bool) -> str:
    """Generate content using Gemini AI - SIMPLE VERSION"""
    try:
        payload = {
            "topic": topic.strip(),
            "tone": tone,
            "length": length,
            "include_hashtags": include_hashtags
        }
        
        st.info(f"🤖 Generating content about: {topic}")
        
        response = requests.post(
            f"{BACKEND_URL}/generate-content", 
            json=payload, 
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("generated_content", "")
            
            if content and len(content.strip()) > 0:
                st.success(f"✅ Generated {len(content)} characters!")
                return content
            else:
                st.error("❌ Empty content generated")
                return ""
        else:
            error_msg = response.text
            st.error(f"❌ Backend error {response.status_code}: {error_msg}")
            return ""
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure it's running on port 8000")
        return ""
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. Try again.")
        return ""
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return ""

def create_post(content: str, topic: str = "") -> Dict[str, Any]:
    """Create and publish LinkedIn post"""
    try:
        payload = {
            "content": content,
            "topic": topic,
            "tone": "professional",
            "length": "medium",
            "include_hashtags": True
        }
        response = requests.post(f"{BACKEND_URL}/post/create", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error creating post: {response.text}")
            return {"success": False, "message": "Failed to create post"}
    except Exception as e:
        st.error(f"Error: {e}")
        return {"success": False, "message": str(e)}

def main():
    st.title("🚀 LinkedIn Post Automation")
    st.markdown("Generate and publish professional LinkedIn posts using AI")

    # Check backend health
    if not check_backend_health():
        st.error("❌ Backend service is not running. Please start the FastAPI backend first.")
        st.code("cd backend && python main.py")
        return

    # Sidebar for user info and settings
    with st.sidebar:
        st.header("👤 Profile")
        
        # Get and display user info
        with st.spinner("Loading profile..."):
            user_info = get_user_info()
        
        if user_info:
            st.success("✅ LinkedIn Connected")
            st.write(f"**Name:** {user_info.get('first_name', '')} {user_info.get('last_name', '')}")
            if user_info.get('headline'):
                st.write(f"**Headline:** {user_info['headline']}")
        else:
            st.warning("⚠️ LinkedIn not connected")

        st.divider()
        
        # Settings
        st.header("⚙️ Settings")
        tone = st.selectbox(
            "Post Tone",
            ["professional", "casual", "inspirational", "educational", "promotional"]
        )
        
        length = st.selectbox(
            "Post Length",
            ["short", "medium", "long"],
            index=1
        )
        
        include_hashtags = st.checkbox("Include Hashtags", value=True)

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 Content Generation")
        
        # Topic input
        topic = st.text_input(
            "Post Topic",
            placeholder="e.g., AI in business, remote work tips, leadership strategies..."
        )
        
        # Generate content button
        if st.button("🎯 Generate Content", type="primary"):
            if topic.strip():
                with st.spinner(f"🤖 Generating content about '{topic}'..."):
                    generated_content = generate_content(topic.strip(), tone, length, include_hashtags)
                    if generated_content:
                        st.session_state.generated_content = generated_content
                        st.experimental_rerun()
            else:
                st.warning("⚠️ Please enter a topic first")

    with col2:
        st.header("📱 Post Preview & Publishing")
        
        # Content editor
        if 'generated_content' in st.session_state:
            content = st.text_area(
                "✏️ Edit Your Generated Content",
                value=st.session_state.generated_content,
                height=300
            )
        else:
            content = st.text_area(
                "📝 Write Your Post",
                placeholder="Enter your LinkedIn post content here or generate content using AI...",
                height=300
            )
        
        # Character count
        if content:
            char_count = len(content)
            st.caption(f"Characters: {char_count}/3000")
            if char_count > 3000:
                st.warning("⚠️ LinkedIn posts should be under 3000 characters")
        
        # Publishing buttons
        col_pub1, col_pub2 = st.columns(2)
        
        with col_pub1:
            if st.button("📤 Publish Now", type="primary"):
                if content.strip():
                    with st.spinner("Publishing to LinkedIn..."):
                        result = create_post(content, topic)
                        
                        if result.get("success"):
                            st.success("🎉 Post published successfully!")
                            st.balloons()
                        else:
                            st.error(f"❌ {result.get('message', 'Failed to publish')}")
                else:
                    st.warning("Please write some content first")
        
        with col_pub2:
            if st.button("💾 Save Draft"):
                if content.strip():
                    if 'drafts' not in st.session_state:
                        st.session_state.drafts = []
                    
                    draft = {
                        "content": content,
                        "topic": topic,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.drafts.append(draft)
                    st.success("💾 Draft saved!")

    # Show content preview if generated
    if 'generated_content' in st.session_state:
        st.divider()
        st.header("📖 Generated Content Preview")
        with st.expander("View Generated Content", expanded=True):
            st.write(st.session_state.generated_content)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🤖 Powered by Gemini AI • 📱 LinkedIn API Integration • ⚡ Real-time Content Generation
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
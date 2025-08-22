#!/usr/bin/env python3
"""
Test script to find the correct Gemini model name
Google has updated their API and model names
"""

import google.generativeai as genai

# Your API key
API_KEY = "AIzaSyAui30vn9YL5kuOzr3XGBVnoyyj0kt8fJg"

def test_available_models():
    """Find all available Gemini models"""
    print("🔍 Checking available Gemini models...")
    print("=" * 60)
    
    try:
        # Configure Gemini
        genai.configure(api_key=API_KEY)
        
        # List all available models
        print("📋 Available Models:")
        models = genai.list_models()
        
        working_models = []
        
        for model in models:
            model_name = model.name
            print(f"📦 Model: {model_name}")
            
            # Check if it supports generateContent
            if 'generateContent' in model.supported_generation_methods:
                working_models.append(model_name)
                print(f"   ✅ Supports generateContent")
            else:
                print(f"   ❌ Does not support generateContent")
        
        print("\n" + "=" * 60)
        print("🎯 WORKING MODELS FOR CONTENT GENERATION:")
        for model in working_models:
            print(f"✅ {model}")
        
        return working_models
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def test_model_generation(model_name):
    """Test content generation with a specific model"""
    try:
        print(f"\n🧪 Testing model: {model_name}")
        
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content("Write 2 sentences about artificial intelligence.")
        
        if response and response.text:
            print(f"✅ SUCCESS with {model_name}!")
            print(f"📝 Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ Empty response from {model_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error with {model_name}: {e}")
        return False

def find_working_model():
    """Find the working model name"""
    print("🚀 FINDING WORKING GEMINI MODEL")
    print("=" * 60)
    
    # Common model names to try
    model_names_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-pro",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-pro",
        "gemini-1.0-pro",
        "models/gemini-1.0-pro"
    ]
    
    # First, get available models
    available_models = test_available_models()
    
    # Test the available models
    working_model = None
    
    print(f"\n🔬 TESTING MODELS FOR CONTENT GENERATION:")
    print("-" * 40)
    
    # Test models from the available list first
    for model in available_models:
        if test_model_generation(model):
            working_model = model
            break
    
    # If none from available list work, try common names
    if not working_model:
        print("\n🔄 Trying common model names...")
        for model_name in model_names_to_try:
            if test_model_generation(model_name):
                working_model = model_name
                break
    
    print("\n" + "=" * 60)
    if working_model:
        print(f"🎉 FOUND WORKING MODEL: {working_model}")
        print("=" * 60)
        print("📋 TO FIX YOUR CODE:")
        print(f"Replace 'gemini-pro' with '{working_model}' in your gemini_service.py")
        print("=" * 60)
        return working_model
    else:
        print("❌ NO WORKING MODEL FOUND")
        print("🔧 Possible solutions:")
        print("1. Check your API key permissions")
        print("2. Enable Generative AI API in Google Cloud Console")
        print("3. Check if you have quota/billing enabled")
        return None

if __name__ == "__main__":
    working_model = find_working_model()
    
    if working_model:
        print(f"\n✅ Use this model name: {working_model}")
    else:
        print("\n❌ Need to fix API access first")
"""
Gemini API Diagnostic Tool
Checks what models are available with your API key
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_gemini_access():
    """Check Gemini API access and available models"""
    
    print("=" * 70)
    print("GEMINI API DIAGNOSTIC TOOL")
    print("=" * 70)
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("\nPlease:")
        print("1. Create a .env file in the mtp_v2 directory")
        print("2. Add: GEMINI_API_KEY=your_actual_key_here")
        print("3. Get key from: https://makersuite.google.com/app/apikey")
        return
    
    print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
    print(f"   Length: {len(api_key)} characters")
    
    # Configure API
    try:
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure API: {e}")
        return
    
    # List available models
    print("\n" + "-" * 70)
    print("CHECKING AVAILABLE MODELS...")
    print("-" * 70)
    
    try:
        models = list(genai.list_models())
        
        if not models:
            print("\n❌ No models found!")
            print("\nPossible reasons:")
            print("1. API key is invalid")
            print("2. Gemini API not enabled in Google Cloud project")
            print("3. Account doesn't have access to Gemini")
            print("\nTo fix:")
            print("- Visit: https://makersuite.google.com/app/apikey")
            print("- Create a new API key")
            print("- Ensure Gemini API is enabled")
            return
        
        print(f"\n✅ Found {len(models)} total models\n")
        
        # Filter models that support generateContent
        content_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                content_models.append(m)
        
        if not content_models:
            print("❌ No models support generateContent!")
            print("\nAll models found:")
            for m in models:
                print(f"   - {m.name}: {m.supported_generation_methods}")
            return
        
        print(f"✅ Found {len(content_models)} models with generateContent support:\n")
        
        for i, model in enumerate(content_models, 1):
            print(f"{i}. {model.name}")
            print(f"   Display name: {model.display_name}")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")
            print()
        
        # Test the most common models
        print("-" * 70)
        print("TESTING MODEL ACCESS...")
        print("-" * 70)
        
        test_models = [
            "gemini-pro",
            "models/gemini-pro",
            "gemini-2.5-pro",
            "models/gemini-2.5-pro",
            "gemini-2.5-flash",
            "models/gemini-2.5-flash"
        ]
        
        working_models = []
        
        for model_name in test_models:
            try:
                print(f"\nTesting: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'hello'")
                print(f"   ✅ WORKS! Response: {response.text[:50]}")
                working_models.append(model_name)
            except Exception as e:
                error_str = str(e)
                if "404" in error_str:
                    print(f"   ❌ Not found (404)")
                elif "403" in error_str:
                    print(f"   ❌ Access denied (403)")
                else:
                    print(f"   ❌ Error: {error_str[:100]}")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        
        if working_models:
            print(f"\n✅ {len(working_models)} working model(s) found:")
            for model in working_models:
                print(f"   - {model}")
            
            print(f"\n💡 RECOMMENDATION:")
            print(f"   Use this model: {working_models[0]}")
            print(f"\n   In the Streamlit UI, select: {working_models[0]}")
            
        else:
            print("\n❌ NO WORKING MODELS FOUND!")
            print("\nPlease check:")
            print("1. API key is correct and valid")
            print("2. Gemini API is enabled in your Google Cloud Console")
            print("3. Your account has access to Gemini models")
            print("4. You're not in a region where Gemini is restricted")
            print("\nGet a new API key:")
            print("https://makersuite.google.com/app/apikey")
        
    except Exception as e:
        print(f"\n❌ Error listing models: {e}")
        print("\nThis usually means:")
        print("1. Invalid API key")
        print("2. Gemini API not enabled")
        print("3. Network connectivity issues")
        print("\nPlease verify your API key at:")
        print("https://makersuite.google.com/app/apikey")


if __name__ == "__main__":
    check_gemini_access()
    
    print("\n" + "=" * 70)
    print("\nFor more help, see TROUBLESHOOTING.md")
    print("=" * 70)
import google.generativeai as genai
import os

# ==========================================
GEMINI_API_KEY = "AIzaSyBuiM0z6SlJpA_L1B_tdf9-8cFYJOYklS4".strip()
# ==========================================

genai.configure(api_key=GEMINI_API_KEY)

print("🔍 Checking available models for your API Key...")

try:
    available_models = []
    for m in genai.list_models():
        # فقط مدل‌هایی که قابلیت تولید متن دارند رو نشون بده
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
            available_models.append(m.name)

    if not available_models:
        print("❌ No text generation models found. Check your API Key permissions.")
    else:
        print("\n💡 Copy one of the names above (e.g., 'models/gemini-1.5-flash') and give it to me.")

except Exception as e:
    print(f"❌ Error: {e}")
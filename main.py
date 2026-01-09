import google.generativeai as genai
import feedparser
import json
import os
import requests
import re # برای تمیز کردن خروجی جیسون

# ==========================================
# 🔑 کلید API خودت رو اینجا بزار
GEMINI_API_KEY = "AIzaSyBuiM0z6SlJpA_L1B_tdf9-8cFYJOYklS4".strip()
# ==========================================

HISTORY_FILE = "history.txt"
genai.configure(api_key=GEMINI_API_KEY)

# ✅ استفاده از مدل قدرتمند و سریع 2.0 Flash که در لیست شما بود
model = genai.GenerativeModel('models/gemini-2.0-flash')

# --- توابع حافظه ---
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def save_to_history(link):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

# --- ۱. پیدا کردن خبر ---
def get_news():
    print("🌍 Acting like a browser to fetch news...")
    
    # لینک اخبار
    rss_url = "https://news.google.com/rss/search?q=Europe+immigration+visa+rules&hl=en-US&gl=US&ceid=US:en"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        
        if feed.entries:
            news_item = feed.entries[0]
            print(f"✅ News Found: {news_item.title}")
            return {
                "title": news_item.title,
                "link": news_item.link,
                "summary": news_item.summary if 'summary' in news_item else news_item.title
            }
        else:
            print("⚠️ Google returned empty feed.")
            return None
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

# --- ۲. تولید محتوا ---
def generate_content(news_item):
    print("🤖 Gemini 2.0 is thinking...")
    
    prompt = f"""
    You are a social media expert.
    News Title: "{news_item['title']}"
    
    Task:
    1. Identify the country. If none, use "Europe 🇪🇺".
    2. Write a short Twitter post (under 280 chars).
    3. Write a LinkedIn post (professional).
    
    IMPORTANT: Output ONLY valid JSON.
    Format:
    {{
        "twitter_draft": "Your tweet here",
        "linkedin_draft": "Your linkedin post here"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # 🧹 تمیزکاری حرفه‌ای برای اینکه ارور نده
        # گاهی مدل‌ها ```json اولش میزارن، این کد پاکش میکنه
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()
        
        return json.loads(text)
    except Exception as e:
        print(f"❌ AI Parsing Error: {e}")
        print(f"Raw Output: {response.text if 'response' in locals() else 'No response'}")
        return None

# --- اجرا ---
if __name__ == "__main__":
    sent_links = load_history()
    news = get_news()
    
    if news:
        if news['link'] in sent_links:
            print("⛔ Duplicate! We sent this already.")
        else:
            content = generate_content(news)
            if content:
                print("\n" + "="*30)
                # از .get استفاده میکنیم که اگر کلید نبود ارور نده
                print("🐦 TWITTER:\n" + content.get('twitter_draft', 'No Tweet Generated'))
                print(f"\n🔗 {news['link']}")
                print("-" * 30)
                print("💼 LINKEDIN:\n" + content.get('linkedin_draft', 'No LinkedIn Post Generated'))
                print("="*30 + "\n")
                
                save_to_history(news['link'])
                print("💾 Saved to history.")
    else:
        print("😴 No news found.")
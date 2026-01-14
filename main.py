import os
import feedparser
import json
import requests
import random
import time
from google import genai
from dotenv import load_dotenv

# ۱. تنظیمات و بارگذاری
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
HISTORY_FILE = "history.txt"

if not all([GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
    print("❌ ERROR: Missing config! Check .env file.")
    exit()

client = genai.Client(api_key=GEMINI_API_KEY)
print("✅ System initialized. Using Stable Model Alias.")

# --- مدیریت تاریخچه ---
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def save_to_history(link):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

# --- ۱. تابع دریافت خبر ---
def get_news():
    print("🌍 Scanning European updates...")
    queries = [
        "Europe immigration visa updates",
        "real estate investment Europe 2026",
        "registering a company in Europe non-EU",
        "best startup hubs in Europe 2026",
        "Schengen visa rules 2026"
    ]
    
    selected_query = random.choice(queries)
    print(f"🔍 Topic: {selected_query}")
    
    rss_url = f"https://news.google.com/rss/search?q={selected_query}+when:1d&hl=en-US&gl=US&ceid=US:en"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        if feed.entries:
            sent_links = load_history()
            for entry in feed.entries[:10]:
                if entry.link not in sent_links:
                    return {"title": entry.title, "link": entry.link, "topic": selected_query}
        return None
    except Exception as e:
        print(f"❌ RSS Error: {e}")
        return None

# --- ۲. تابع تولید محتوا (با اصلاح نام مدل و Retry) ---
def generate_content(news_item):
    print(f"🤖 AI is analyzing with Gemini...")
    
    prompt = f"""
    You are a professional social media manager.
    News: "{news_item['title']}"
    Topic: {news_item['topic']}
    
    Task: Write a Twitter post and a LinkedIn post.
    Output ONLY valid JSON:
    {{
        "twitter": "text",
        "linkedin": "text"
    }}
    """
    
    for attempt in range(3):
        try:
            # استفاده از نام مستعار پایدار که در لیست شما هم بود
            response = client.models.generate_content(
                model="gemini-flash-latest", 
                contents=prompt
            )
            
            clean_text = response.text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0]
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0]
                
            return json.loads(clean_text)
            
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                print(f"⚠️ Server busy or limit hit, retrying in 15s... ({attempt+1}/3)")
                time.sleep(15)
            else:
                print(f"❌ AI Error: {e}")
                break
    return None

# --- ۳. ارسال به تلگرام ---
def send_telegram(content, news_item):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    topic_header = news_item['topic'].title()
    
    message_text = (
        f"<b>📢 Topic: {topic_header}</b>\n\n"
        f"<b>🐦 Twitter:</b>\n{content.get('twitter')}\n\n"
        f"<b>💼 LinkedIn:</b>\n{content.get('linkedin')}\n\n"
        f'<a href="{news_item["link"]}">🔗 Source</a>'
    )
    
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text, "parse_mode": "HTML"}
    
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("🚀 Success! Sent to Telegram.")
        else:
            print(f"⚠️ Telegram Error: {res.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

# --- اجرا ---
if __name__ == "__main__":
    news = get_news()
    if news:
        ai_result = generate_content(news)
        if ai_result:
            send_telegram(ai_result, news)
            save_to_history(news['link'])
            print("💾 Done.")
        else:
            print("❌ AI failed.")
    else:
        print("😴 No news.")
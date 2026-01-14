import os
import feedparser
import json
import requests
from google import genai
from dotenv import load_dotenv

# ۱. تنظیمات و بارگذاری متغیرهای محیطی
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
HISTORY_FILE = "history.txt"

# بررسی امنیت تنظیمات
if not all([GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
    print("❌ ERROR: Missing configuration in .env file!")
    exit()

# تعریف کلاینت مدرن گوگل (نسخه ۲۰۲۶)
client = genai.Client(api_key=GEMINI_API_KEY)
print("✅ System initialized: Gemini AI & Telegram ready.")

# --- توابع مدیریت تاریخچه ---
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def save_to_history(link):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

# --- ۱. تابع دریافت خبر (Google News RSS) ---
def get_news():
    print("🌍 Monitoring news sources...")
    rss_url = "https://news.google.com/rss/search?q=Europe+immigration+visa+rules&hl=en-US&gl=US&ceid=US:en"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        if feed.entries:
            news_item = feed.entries[0]
            print(f"✅ Latest News Found: {news_item.title}")
            return {"title": news_item.title, "link": news_item.link}
        return None
    except Exception as e:
        print(f"❌ RSS Error: {e}")
        return None

# --- ۲. تابع تولید محتوا با هوش مصنوعی (Gemini) ---
def generate_content(news_item):
    print("🤖 AI is drafting social media posts...")
    
    prompt = f"""
    You are a professional immigration news analyst.
    News: "{news_item['title']}"
    
    Task:
    1. Summarize for Twitter (max 250 chars, with hashtags).
    2. Write a professional LinkedIn post.
    
    Output ONLY valid JSON:
    {{
        "twitter": "tweet text",
        "linkedin": "linkedin text"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=prompt
        )
        
        # پاکسازی و استخراج JSON
        clean_text = response.text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0]
            
        return json.loads(clean_text)
    except Exception as e:
        print(f"❌ AI Generation Error: {e}")
        return None

# --- ۳. تابع ارسال به تلگرام (نسخه اصلاح شده با HTML) ---
def send_telegram_notification(content, link):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # استفاده از تگ‌های HTML برای پایداری بیشتر در برابر کاراکترهای خاص
    message_text = (
        f"<b>📢 New Immigration Update</b>\n\n"
        f"<b>🐦 Twitter Draft:</b>\n{content.get('twitter')}\n\n"
        f"<b>💼 LinkedIn Draft:</b>\n{content.get('linkedin')}\n\n"
        f'<a href="{link}">🔗 Original Source</a>'
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML"
    }
    
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("🚀 Notification successfully sent to Telegram!")
        else:
            print(f"⚠️ Telegram API Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Telegram Network Error: {e}")

# --- بدنه اصلی اجرا ---
if __name__ == "__main__":
    sent_links = load_history()
    news = get_news()
    
    if news:
        if news['link'] in sent_links:
            print("⛔ Duplicate news. Skipping...")
        else:
            ai_result = generate_content(news)
            if ai_result:
                # ارسال به تلگرام
                send_telegram_notification(ai_result, news['link'])
                
                # ذخیره در تاریخچه
                save_to_history(news['link'])
                print("💾 History updated.")
            else:
                print("❌ AI failed to generate content.")
    else:
        print("😴 No new news found.")
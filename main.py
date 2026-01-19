import os
import feedparser
import requests
import tweepy
from google import genai
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی (برای اجرای لوکال)
load_dotenv()

# --- تنظیمات کلیدها (این‌ها از فایل .env یا GitHub Secrets خوانده می‌شوند) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# کلیدهای توییتر (X)
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

# --- ۱. دریافت اخبار از RSS ---
def get_news():
    print("🌍 Scanning for updates...")
    rss_url = "https://news.google.com/rss/search?q=schengen+visa+rules+2026+OR+european+residency+investment&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    # خواندن تاریخچه برای جلوگیری از تکرار
    if os.path.exists("history.txt"):
        with open("history.txt", "r") as f:
            history = f.read().splitlines()
    else:
        history = []

    for entry in feed.entries:
        if entry.link not in history:
            return entry # اولین خبر جدید را برمی‌گرداند
    return None

# --- ۲. پردازش خبر با هوش مصنوعی Gemini ---
def generate_content(news_entry):
    print("🤖 AI is analyzing with Gemini...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Analyze this news: {news_entry.title}
    Link: {news_entry.link}
    
    Task: Create a professional summary for immigration and investment interests.
    Output MUST be in this exact format:
    TELEGRAM: (A catchy title and 3 bullet points in Persian)
    X_POST: (A short, engaging English tweet with hashtags, max 240 chars)
    """
    
    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        text = response.text
        
        # جدا کردن محتوای تلگرام و توییتر
        parts = text.split("X_POST:")
        telegram_part = parts[0].replace("TELEGRAM:", "").strip()
        x_part = parts[1].strip() if len(parts) > 1 else ""
        
        return {"telegram": telegram_part, "x": x_part}
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

# --- ۳. ارسال به توییتر (X) ---
def post_to_x(tweet_text):
    print("🐦 Posting to X (Twitter)...")
    try:
        # استفاده از Tweepy برای ارسال پست
        client_x = tweepy.Client(
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_SECRET
        )
        client_x.create_tweet(text=tweet_text)
        print("✅ Posted to X successfully!")
    except Exception as e:
        print(f"❌ X API Error: {e}")

# --- ۴. ارسال به تلگرام ---
def send_telegram(text, link):
    print("📢 Sending to Telegram...")
    message = f"{text}\n\n🔗 Source: {link}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"})

# --- ۵. ذخیره در تاریخچه ---
def save_history(link):
    with open("history.txt", "a") as f:
        f.write(link + "\n")

# --- اجرای اصلی ---
if __name__ == "__main__":
    news = get_news()
    if news:
        ai_content = generate_content(news)
        if ai_content:
            # ارسال به تلگرام
            send_telegram(ai_content['telegram'], news.link)
            
            # ارسال به توییتر
            if ai_content['x']:
                post_to_x(ai_content['x'])
            
            # ذخیره لینک
            save_history(news.link)
            print("💾 Done! Everything synchronized.")
    else:
        print("☕ No new news found.")
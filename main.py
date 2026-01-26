import os
import feedparser
import requests
import tweepy
from google import genai
from dotenv import load_dotenv

load_dotenv()

# کلیدها
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

def get_news():
    print("🌍 Scanning Google News...")
    rss_url = "https://news.google.com/rss/search?q=schengen+visa+rules+2026+OR+european+residency+investment&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    if os.path.exists("history.txt"):
        with open("history.txt", "r") as f:
            history = f.read().splitlines()
    else:
        history = []

    for entry in feed.entries:
        if entry.link not in history:
            return entry
    return None

def generate_content(news_entry):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"Summarize this news for Telegram (Persian) and X (English): {news_entry.title}. Link: {news_entry.link}. Format: TELEGRAM: ... X_POST: ..."
    
    # تست مدل‌های مختلف به ترتیب اولویت برای فرار از ارور 404 و 429
    for model_name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        try:
            print(f"🤖 Trying model: {model_name}...")
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = response.text
            
            if "X_POST:" in text:
                parts = text.split("X_POST:")
                return {"telegram": parts[0].replace("TELEGRAM:", "").strip(), "x": parts[1].strip()}
            return {"telegram": text, "x": ""}
        except Exception as e:
            print(f"⚠️ {model_name} failed: {e}")
            continue # رفتن به مدل بعدی
            
    print("❌ All models failed.")
    return None

def post_to_x(tweet_text):
    try:
        client_x = tweepy.Client(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
        client_x.create_tweet(text=tweet_text)
        print("✅ Posted to X!")
    except Exception as e:
        print(f"❌ X Error: {e}")

def send_telegram(text, link):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": f"{text}\n\n🔗 {link}"})
    print("✅ Sent to Telegram!")

if __name__ == "__main__":
    news = get_news()
    if news:
        ai_content = generate_content(news)
        if ai_content:
            send_telegram(ai_content['telegram'], news.link)
            if ai_content['x']:
                post_to_x(ai_content['x'])
            with open("history.txt", "a") as f: f.write(news.link + "\n")
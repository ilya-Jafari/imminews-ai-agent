import os
import feedparser
import requests
import tweepy
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# کلیدها
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

def get_news():
    print("🌍 Scanning News...")
    rss_url = "https://news.google.com/rss/search?q=schengen+visa+rules+2026&hl=en-US&gl=US&ceid=US:en"
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
    print("🦙 AI is analyzing with Llama 3.3 (Groq)...")
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"Summarize this news: {news_entry.title}. Link: {news_entry.link}. Format your response EXACTLY like this:\nTELEGRAM: (Persian summary with emojis)\nX_POST: (Short English tweet with hashtags)"
    
    try:
        # استفاده از مدل فوق‌سریع Llama 3.3
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        text = completion.choices[0].message.content
        
        parts = text.split("X_POST:")
        return {
            "telegram": parts[0].replace("TELEGRAM:", "").strip(),
            "x": parts[1].strip() if len(parts) > 1 else ""
        }
    except Exception as e:
        print(f"❌ Groq Error: {e}")
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
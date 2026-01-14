# 🤖 ImmiNews AI Agent
### Automated Immigration News Monitor & Social Media Content Creator

**ImmiNews AI Agent** is a specialized automation tool designed to monitor the latest immigration news and visa policy changes. It leverages the power of **Google Gemini 2.0 Flash** to transform complex news articles into engaging content for X and LinkedIn.

---

## 🌟 Key Features
* **Real-time News Monitoring:** Fetches the latest updates from Google News RSS.
* **Gemini 2.0 Flash Integration:** Uses state-of-the-art AI for content generation.
* **Smart History Management:** Prevents duplicate posts using `history.txt`.
* **Platform-Specific Optimization:** Drafts tailored posts for X and LinkedIn.

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **AI Model:** Google Gemini 2.0 Flash
* **Libraries:** `google-generativeai`, `feedparser`, `requests`.

## 🚀 Getting Started
1. Install dependencies: `pip install -U google-generativeai feedparser requests`
2. Add your **Gemini API Key** in the script.
3. Run the agent: `python main.py`

## ⚠️ Setup Environment Variables
Before running the script, create a `.env` file in the root directory and add your Gemini API Key:
`GEMINI_API_KEY=your_api_key_here`

---
Developed with ❤️ by Ilya Jafari
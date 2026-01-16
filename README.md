# 🚀 European Immigration & Investment AI Agent

An intelligent, automated agent leveraging **Google's Gemini AI** to track the latest trends in European immigration, investment, startups, and visa regulations. It autonomously analyzes news and generates professional content drafts for social media platforms.

---

## ✨ Key Features

- **🕵️‍♂️ Smart Monitoring:** Automated Google News search using rotating keywords (e.g., Real Estate, Company Registration, Schengen Visa, Startup Hubs).
- **🧠 Gemini 1.5 Flash Analysis:** AI-powered analysis of news articles to generate optimized Twitter & LinkedIn drafts (via structured JSON output).
- **📲 Telegram Notifications:** Instant delivery of generated content directly to Telegram, formatted neatly in HTML.
- **☁️ Fully Cloud-Native (24/7):** Runs autonomously on **GitHub Actions**, eliminating the need for a local machine to be online.
- **💾 Deduplication System:** Manages a `history.txt` database to prevent sending duplicate news articles.

---

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **AI Model:** Google Gemini 1.5 Flash (via `google-genai` SDK)
* **Automation:** GitHub Actions (CI/CD - Scheduled Cron Jobs)
* **Data Source:** Google News RSS Feed
* **Communication:** Telegram Bot API

---

## ⚙️ Project Structure


-   `main.py`: The core script containing the logic for fetching news, AI processing, and sending notifications.
-   `.github/workflows/main.yml`: Configuration for GitHub Actions to run the bot automatically every 6 hours.
-   `history.txt`: A simple, flat-file database to store links of already processed news.
-   `.env`: (Local use only) Stores sensitive API keys and tokens.
---
## ⚙️ Project Preview

<p align="center">
  <img src="assets/screenshot.png" width="70%" alt="Bot Screenshot">
</p>
---

## 🚀 Setup & Usage

If you want to fork and run this project for yourself:

1.  **Fork** this repository.
2.  Go to repository **Settings > Secrets and variables > Actions**.
3.  Add the following repository secrets:
    * `GEMINI_API_KEY`: Your Google AI Studio API Key.
    * `TELEGRAM_BOT_TOKEN`: Your Telegram Bot token.
    * `TELEGRAM_CHAT_ID`: Your target Telegram Chat ID.
4.  Go to **Settings > Actions > General**, scroll down to "Workflow permissions", and select **Read and write permissions** (Crucial for updating `history.txt`).
5.  The bot will run automatically on schedule. You can also trigger it manually via the "Actions" tab.

---

### 👤 About

Developed with ❤️ by Ilya Jafarias an automated AI-driven news analysis project.
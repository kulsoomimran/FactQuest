# FactQuest 📚🧠

**FactQuest** is a Chainlit-based chatbot powered by Gemini via the OpenAI Agents SDK.  
It intelligently uses a `news_search` tool to fetch and display recent news (from NewsAPI) and also handles historical or factual queries directly.

---

## 🚀 Features

- **📢 News Fetching** – Uses a tool to call NewsAPI and returns up-to-date headlines with links.
- **🗓️ Historical Facts** – Provides factual answers (e.g., “When did Pakistan gain independence?”).
- **💬 Streaming Replies** – Smooth, token-by-token streaming like ChatGPT via Chainlit.
- **🛠️ Built with**:
  - Gemini API (OpenAI-compatible chat)
  - Chainlit for the UI
  - Pydantic for structured tool inputs
  - NewsAPI backend

---
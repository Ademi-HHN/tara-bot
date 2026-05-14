# TARA BOT 🤖✈️🛒

**AI agent cá nhân trên Telegram — săn vé máy bay, so sánh giá, cào deal.**

[![Deploy on Fly.io](https://img.shields.io/badge/deploy-fly.io-6a0dad?style=flat-square)](https://fly.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-4ade80?style=flat-square)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-60a5fa?style=flat-square)](https://python.org)

> Build bởi [Tara Le](https://github.com/thaolst) — AI × Growth Marketing

---

## ✨ Tính năng

| Tính năng | Mô tả | Trạng thái |
|-----------|-------|------------|
| 💬 **Chat tự nhiên** | Hỏi "tìm vé SG Đà Nẵng cuối tuần" — LLM hiểu, SerpAPI search | ✅ |
| ✈️ **Tra cứu chuyến bay** | Giá, hãng, giờ bay real-time từ Google Flights | ✅ |
| 🛒 **So sánh giá đồ** | Search sản phẩm, so sánh từ nhiều nguồn | ✅ |
| 🔔 **Daily monitor** | Mỗi sáng check giá các tuyến quen thuộc, gửi alert | ✅ |
| 🧠 **Context-aware** | LLM nhớ lịch sử chat trong session | ✅ |
| 🔗 **Affiliate inject** | Tự động thêm affiliate link vào kết quả | ✅ |
| 🆕 **Shopee cào giá** | *(coming soon)* |

## 🎬 Demo

*Screenshot / GIF sẽ update sau khi deploy*

```
👤: tìm vé SG ra Hà Nội thứ 7 tuần này
🤖: ✈️ SGN → HAN
    📅 2026-05-16 → 2026-05-21

    1. Vietjet Air — 1,450,000 VND (2h05m)
       SGN 06:00 → HAN 08:05

    2. Vietnam Airlines — 2,100,000 VND (2h)
       SGN 08:30 → HAN 10:30
```

## 🧱 Tech stack

```
┌──────────┐     ┌───────────┐     ┌──────────┐
│ Telegram │ ←→ │   LLM     │ ←→ │ SerpAPI  │
│   Bot    │     │ Anthropic │     │(Flights+ │
│          │     │ / OpenAI  │     │ Shopping)│
└──────────┘     └───────────┘     └──────────┘
                       ↕
                 ┌──────────┐
                 │ GitHub   │
                 │ Actions  │
                 │(scheduler)│
                 └──────────┘
```

- **Telegram Bot** — python-telegram-bot v20+
- **Anthropic or OpenAI-compatible LLM** — NLU + tool-calling
- **SerpAPI** — Google Flights + Google Shopping (250 free/tháng)
- **Fly.io** — host 24/7 (free tier)
- **GitHub Actions** — daily cron monitor (free)

## 🚀 Deploy 5 phút

1. **Fork repo** → `git clone https://github.com/thaolst/tara-bot`
2. **Get API keys**:
   - [@BotFather](https://t.me/botfather) → tạo bot → copy token
   - [SerpAPI](https://serpapi.com) → sign up → copy key (500 free/tháng)
   - [Anthropic API](https://console.anthropic.com/settings/keys) → copy key
   - [Google AI Studio](https://aistudio.google.com/app/apikey) → copy OpenAI-compatible key
3. **Deploy lên Fly.io**:
   ```bash
   fly launch --from Dockerfile
   fly secrets set TELEGRAM_TOKEN=xxx LLM_MODE=anthropic ANTHROPIC_API_KEY=xxx SERPAPI_KEY=xxx ALLOWED_USER_ID=xxx
   fly deploy
   ```
4. **Bật monitor**:
   - Settings → Secrets → thêm vào GitHub repo
   - Actions → enable workflow

### Chạy local bằng `.env`
Tạo file `.env` ở root repo, rồi chạy:
```bash
python -m src.bot
```
`dotenv` sẽ tự load biến môi trường từ file này.

*Chi tiết: [DEPLOY.md](./DEPLOY.md)*

## 📁 Cấu trúc

```
src/
├── bot.py              # Telegram bot entry point
├── agents.py           # LLM agent + tool-calling
├── config.py           # Env config loader
└── tools/
    └── serpapi.py      # Flight + shopping search
.github/workflows/
└── monitor.yml         # Daily price check
```

## 🗺️ Roadmap

- [x] Flight search (SerpAPI)
- [x] Shopping price compare
- [x] Daily price monitor (GitHub Actions)
- [x] 24/7 Telegram bot (Fly.io)
- [x] Anthropic / OpenAI-compatible LLM mode switch
- [ ] Shopee price scraper
- [ ] Affiliate link injection vào kết quả
- [ ] Auto-deal: notify khi deal tốt xuất hiện
- [ ] Multi-user support

## 📝 License

MIT — free to use, fork, modify.

---

*Tara Bot — AI agent cá nhân, build public để chia sẻ, không phải product thương mại.*

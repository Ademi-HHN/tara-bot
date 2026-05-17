# DEPLOY.md — Hướng dẫn setup Tara Bot

---

## 1. Chuẩn bị API keys

### Telegram Bot Token
1. Mở Telegram → tìm `@BotFather`
2. Gửi `/newbot` → đặt tên → nhận token dạng `123456:ABC-DEF1234`

### Telegram User ID
1. Tìm `@userinfobot` → gửi `/start`
2. Copy số ID (VD: `123456789`) — dùng cho cả `ALLOWED_USER_ID` và `TELEGRAM_CHAT_ID`

### SerpAPI Key
- Vào [serpapi.com](https://serpapi.com) → sign up → copy key
- Free: **250 searches/tháng** (đủ cho bot + daily monitor)

### LLM Mode
- Chọn `LLM_MODE=anthropic` (Claude) hoặc `LLM_MODE=openai` (OpenAI-compatible)
- `openai` dùng với Google AI Studio hoặc local LLM endpoint

### Anthropic API Key
- Vào [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
- Create key — model dùng: `claude-sonnet-4-6`
- Free $5 credit khi đăng ký mới

### Google AI Studio Key (cho OpenAI mode)
- Vào https://aistudio.google.com/app/apikey
- Create key
- Dùng với `OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`

---

## 2. Deploy lên Fly.io

### Cài Fly CLI
```bash
# macOS
brew install flyctl

# Linux / WSL
curl -L https://fly.io/install.sh | sh
```

### Launch và deploy
```bash
git clone https://github.com/thaolst/tara-bot
cd tara-bot

fly auth login
fly launch --from Dockerfile --name tara-bot-yourname

fly secrets set \
  TELEGRAM_TOKEN=your_bot_token \
  ANTHROPIC_API_KEY=your_anthropic_key \
  SERPAPI_KEY=your_serpapi_key \
  ALLOWED_USER_ID=your_telegram_id \
  TELEGRAM_CHAT_ID=your_telegram_id

fly deploy
```

### Check logs
```bash
fly logs
```

Bot chạy 24/7 sau khi deploy. Mở Telegram → tìm tên bot → `/start`.

---

## 3. Bật Daily Monitor (GitHub Actions)

Monitor chạy độc lập trên GitHub Actions — **không** dùng Fly.io.

### Thêm secrets vào GitHub repo
- Vào repo → **Settings → Secrets and variables → Actions**
- Thêm 3 secrets:
  - `SERPAPI_KEY`
  - `TELEGRAM_TOKEN`
  - `TELEGRAM_CHAT_ID`

### Enable workflow
- **Actions tab** → **Flight Monitor** → **Enable workflow**
- Tự chạy mỗi ngày lúc **9:00 AM Vietnam** (UTC+7)
- Hoặc chạy tay: Actions → Flight Monitor → **Run workflow**

Monitor check 4 tuyến mặc định: SGN↔HAN, SGN↔DAD, SGN↔PQC, HAN→SGN.
Muốn thay đổi tuyến → sửa `scripts/monitor.py`.

---

## 4. Test sau deploy

```
/start          — xem hướng dẫn
/uptime         — kiểm tra bot đang chạy

tìm vé SG Hà Nội thứ 7
iPhone 16 giá bao nhiêu
so sánh giá máy lọc không khí

/reset          — xóa lịch sử chat
```

---

## 5. Update

```bash
git pull
fly deploy
```

---

## 6. Chi phí ước tính

| Service | Cost | Ghi chú |
|---|---|---|
| Fly.io | $0 | Free tier: shared CPU 1GB RAM |
| SerpAPI | $0 | 250 req/tháng free |
| Anthropic | ~$0.50/tháng | Prompt caching giảm ~90% cost |
| GitHub Actions | $0 | Public repo miễn phí |
| **Tổng** | **~$0.50/tháng** | |

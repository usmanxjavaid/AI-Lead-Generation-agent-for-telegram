# 🤖 AI Lead Generation Agent for Telegram

An intelligent lead generation agent for Telegram that collects and qualifies potential customer information through natural conversation, powered by a robust admin panel.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-supported-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🗣️ **Conversational Lead Collection** — Collects name, email, phone, service interest and requirement through natural conversation
- ✅ **Input Validation** — Validates email format and international phone numbers
- 🗄️ **Database Storage** — Saves all leads permanently in SQLite
- 🔔 **Instant Admin Notifications** — Admin gets Telegram notification for every new lead
- 📊 **Admin Panel** — Full lead management via Telegram commands
- 📤 **CSV Export** — Export all leads directly as Excel-ready file
- 🔄 **Lead Status Tracking** — Track leads as new/contacted/converted
- 📢 **Broadcast Messages** — Send messages to all leads at once
- 📝 **Proper Logging** — All events logged with timestamps
- 🐳 **Docker Support** — Fully containerized for easy deployment
- ✅ **CI/CD** — GitHub Actions automatically tests Docker build on every push

---

## 📁 Project Structure

```
├── handlers/
│   ├── user.py         → conversation flow and lead collection
│   └── admin.py        → admin commands and panel
├── core/
│   ├── database.py     → SQLite operations
│   ├── validator.py    → email and phone validation
│   └── logger.py       → logging setup
├── config.py           → all settings in one place
├── bot.py              → entry point
├── Dockerfile          → Docker configuration
├── .github/workflows/  → GitHub Actions CI
└── requirements.txt    → Python dependencies
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/usmanxjavaid/lead-gen-agent
cd lead-gen-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
ADMIN_ID=your_telegram_user_id
```

### 5. Customize for your client in `config.py`
```python
COMPANY_NAME = "Your Client Business Name"
BOT_NAME = "Sara"
SERVICES = ["Service 1", "Service 2", "Service 3", "Other"]
FOLLOWUP_HOURS = 24
```

### 6. Run the bot
```bash
python bot.py
```

---

## 📊 Admin Commands

| Command | Usage | What it does |
|---|---|---|
| `/admin` | `/admin` | Shows stats + action buttons |
| `/leads` | `/leads` | View last 10 leads with details |
| `/export` | `/export` | Get CSV file of all leads |
| `/status` | `/status 123456 contacted` | Update lead status |
| `/broadcast` | `/broadcast message here` | Message all leads |

### Lead Status Options
```
new        → fresh lead, not contacted yet
contacted  → you reached out to them
converted  → they became a paying client
```

---

## 🐳 Docker

```bash
docker build -t lead-gen-agent .
docker run --env-file .env lead-gen-agent
```

---

## 🔑 API Keys (All Free)

| Service | Purpose | Get it |
|---|---|---|
| Telegram BotFather | Bot token | [@BotFather](https://t.me/botfather) |
| Groq | AI responses | [console.groq.com](https://console.groq.com) |

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Telegram Framework | python-telegram-bot 21.5 |
| AI | Groq API (LLaMA 3.1) |
| Database | SQLite |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

## 📦 Per Client Customization

Only 4 lines to change in `config.py`:

```python
COMPANY_NAME = "Client Business Name"
BOT_NAME = "Assistant Name"
SERVICES = ["Their", "Service", "Options"]
FOLLOWUP_HOURS = 24
```

Delivery time per client: under 30 minutes ⚡

---

## 🔄 Conversation Flow

```
/start
↓ Bot asks name
↓ Bot asks email (validated)
↓ Bot asks phone (international format supported)
↓ Bot shows service buttons
↓ Bot asks requirement
↓ Lead saved + Admin notified instantly
```

---

## 📄 License

MIT License — free to use for commercial purposes.

---

## 👨‍💻 Author

**Usman Javaid**
- GitHub: [@usmanxjavaid](https://github.com/usmanxjavaid)
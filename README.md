# JooTRH GBV & Mental Health Support Chatbot

An AI-powered triage assistant designed to provide immediate support for Gender-Based Violence (GBV) and Mental Health crises, with seamless escalation to human counselors.

## Tech Stack
- **Backend:** FastAPI (Python 3.9+)
- **AI:** Groq (Llama 3.3 70B)
- **Messaging:** Twilio WhatsApp API
- **Database:** SQLite with SQLAlchemy ORM
- **Security:** JWT Authentication
- **Frontend:** Tailwind CSS & Vanilla JavaScript

---

## 🚀 How to Run the Project

Follow these steps every time you want to start the application:

### Step 1: Activate the Environment
Open your terminal in the project folder and run:
```bash
source venv/bin/activate
```

### Step 2: Start the Backend Server
Run the FastAPI application using uvicorn:
```bash
uvicorn app.main:app --port 8000 --reload
```
*The app is now running locally at `http://localhost:8000`.*

### Step 3: Start the WhatsApp Tunnel (ngrok)
In a **new terminal window**, start ngrok to connect to Twilio:
```bash
ngrok http 8000
```
*Copy the `https://...` Forwarding URL provided by ngrok.*

### Step 4: Configure Twilio
1. Go to your **Twilio Console > Messaging > Try it Out > WhatsApp Sandbox Settings**.
2. Paste your ngrok URL into the **"When a message comes in"** box.
3. Add `/api/v1/whatsapp/webhook` to the end of the URL.
   - *Example:* `https://xxxx.ngrok-free.app/api/v1/whatsapp/webhook`
4. Click **Save**.

---

## 📱 Connecting to the Bot (WhatsApp)
1. In WhatsApp, send the code **spite-apple** to **+14155238886**.
2. Start chatting! (Try: "Hi, I need someone to talk to").

---

## 🖥️ Accessing Dashboards
Once the server is running, you can access these in your browser:

- **Landing Page:** [http://localhost:8000/](http://localhost:8000/)
- **Mentor Dashboard:** [http://localhost:8000/mentor](http://localhost:8000/mentor)
- **Admin Dashboard:** [http://localhost:8000/admin](http://localhost:8000/admin)

### Default Admin Credentials
- **Email:** `admin@jootrh.org`
- **Password:** `password123`

---

## 🛠️ Initial Installation (First Time Only)
If you haven't installed dependencies yet:
1. Ensure Python 3.9+ is installed.
2. `pip install -r requirements.txt`
3. Create a `.env` file based on `.env.example` with your Twilio and Groq keys.

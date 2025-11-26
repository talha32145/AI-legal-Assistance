import streamlit as st
import pandas as pd
import os
import requests
import string
from dotenv import load_dotenv
import google.generativeai as Genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import hashlib
import json
from datetime import datetime



def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.csv"):
        df = pd.DataFrame(columns=["username", "email", "password_hash"])
        df.to_csv("users.csv", index=False)
    return pd.read_csv("users.csv")

def save_user(username, email, password):
    df = load_users()
    new_user = {
        "username": username,
        "email": email,
        "password_hash": hash_password(password)
    }
    df.loc[len(df)] = new_user
    df.to_csv("users.csv", index=False)

def authenticate(email, password):
    df = load_users()
    password_hash = hash_password(password)
    user = df[(df["email"] == email) & (df["password_hash"] == password_hash)]
    if not user.empty:
        return user.iloc[0]["username"]  
    return None



def load_user_chats(email):
    """Load user's chats from file"""
    if not os.path.exists("user_chats.json"):
        return {}
    
    try:
        with open("user_chats.json", "r") as f:
            all_chats = json.load(f)
        return all_chats.get(email, {})
    except:
        return {}

def save_user_chats(email, chats):
    """Save user's chats to file"""
    if os.path.exists("user_chats.json"):
        try:
            with open("user_chats.json", "r") as f:
                all_chats = json.load(f)
        except:
            all_chats = {}
    else:
        all_chats = {}
    
    all_chats[email] = chats
    
    with open("user_chats.json", "w") as f:
        json.dump(all_chats, f)

def generate_chat_title(first_message):
    """Generate a meaningful chat title from the first message"""
    words = first_message.split()[:10]  
    title = " ".join(words)
    if len(title) > 30:
        title = title[:30] + "..."
    return title if title else "New Chat"



st.set_page_config(
    page_title="PakLaw Assist",
    page_icon="⚖️",
    layout="wide"
)



if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

st.markdown("""
    <style>
        .top-right-auth {
            position: fixed;
            top: 15px;
            right: 25px;
            z-index: 999999;
        }
        .user-badge {
            background: #1E90FF;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='top-right-auth'>", unsafe_allow_html=True)

if st.session_state.logged_in:
    st.markdown(
        f"<div class='user-badge'>👤 {st.session_state.username}</div>",
        unsafe_allow_html=True,
    )
else:
    if st.button("🔐 Login / Signup"):
        st.session_state.show_login = True
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.logged_in:
    if st.sidebar.button("🚪 Logout"):
        if st.session_state.messages and st.session_state.current_chat_id:
            user_chats = load_user_chats(st.session_state.user_email)
            user_chats[st.session_state.current_chat_id] = {
                "title": st.session_state.current_chat_id,
                "messages": st.session_state.messages,
                "timestamp": datetime.now().isoformat()
            }
            save_user_chats(st.session_state.user_email, user_chats)
        
        st.session_state.clear()
        st.rerun()



if st.session_state.show_login and not st.session_state.logged_in:
    st.title("🔐 Login to PakLaw Assist")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to your account")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_submitted = st.form_submit_button("Login", use_container_width=True)
            with col2:
                cancel_login = st.form_submit_button("Cancel", use_container_width=True)
            
            if login_submitted:
                if email and password:
                    username = authenticate(email, password)
                    if username:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.username = username
                        st.session_state.show_login = False
                        # Load user's chats when logging in
                        st.session_state.saved_chats = load_user_chats(email)
                        st.session_state.messages = []
                        st.session_state.chat_session = {"Province": [], "Problem": []}
                        st.session_state.current_chat_id = None
                        st.session_state.chat_started = False
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Please fill in all fields")
            
            if cancel_login:
                st.session_state.show_login = False
                st.rerun()
    
    with tab2:
        st.subheader("Create your account")
        
        with st.form("signup_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                signup_submitted = st.form_submit_button("Sign Up", use_container_width=True)
            with col2:
                cancel_signup = st.form_submit_button("Cancel", use_container_width=True)
            
            if signup_submitted:
                if username and email and password and confirm:
                    if password != confirm:
                        st.error("Passwords do not match!")
                    else:
                        df = load_users()
                        if email in df["email"].values:
                            st.error("Email already exists!")
                        else:
                            save_user(username, email, password)
                            st.success(f"Account created for {username}! Please login now.")
                            st.session_state.show_login = True
                            st.rerun()
                else:
                    st.error("Please fill in all fields")
            
            if cancel_signup:
                st.session_state.show_login = False
                st.rerun()

    if st.button("← Back to Main Page"):
        st.session_state.show_login = False
        st.rerun()



load_dotenv("Secret_key.env")
My_key = os.getenv("YOUR_API_KEY")
Genai.configure(api_key=My_key)

model = Genai.GenerativeModel(
    "gemini-2.5-flash-lite",
    generation_config={"max_output_tokens": 1080, "temperature": 0.3}
)



df = pd.read_csv("AI_legal_assistance.csv")



def preprocessing(text):
    text = text.translate(str.maketrans("", "", string.punctuation))
    stop_words = set(stopwords.words("english"))
    tokens = text.split()
    tokens = [word for word in tokens if word.lower() not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word, pos="v") for word in tokens]
    return " ".join(tokens)


df["Topic"] = df["Topic"].apply(preprocessing)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["Topic"])



def offline_response(user_input):
    clean_input = preprocessing(user_input)
    vectorized = vectorizer.transform([clean_input])
    similarity = cosine_similarity(X, vectorized)
    idx = similarity.argmax()
    if similarity.max() > 0.3:
        return df["Details"].iloc[idx]
    else:
        return "Sorry, this topic is not available offline."



def check_internet():
    websites = ["https://www.google.com", "https://www.microsoft.com"]
    for site in websites:
        try:
            requests.get(site, timeout=3)
            return True
        except:
            continue
    return False



def chat_bot(user_input, chat_session):
    prompt = f"""
    You are PakLaw Assist, a friendly, knowledgeable,non-advocacy AI legal assistant for Pakistan.
            Do NOT repeat your identity in every message.
            Do NOT greet repeatedly.
Your job is to provide clear, simple, step-by-step general guidance about Pakistani laws and government procedures.
You are not a lawyer, and you must never give legal advice — only general procedural guidance.
🔥 CHAT SESSION MEMORY RULE
You have access to:
{chat_session}
Whenever the user asks about something that is already stored here, you must answer using this information.
🎯 PERSONA & STYLE
Friendly, respectful, calm, non-judgmental.
Simple English with light Urdu mix for clarity (e.g., “Aasan alfaaz mein bataoon…”).
Very concise.
No legal jargon. If you use a legal term, explain it in 1 short line.
Use bullets, numbered steps, and short sentences only.
Only ask for city/district if necessary.
📌 COVER THESE DOMAINS
You must give accurate, Pakistan-specific guidance on:
FIR registration, SHO duties, rights, follow-up
Cybercrime reporting (FIA portal, helpline, WhatsApp, evidence)
Property disputes (mutation, stay order, civil court steps)
Traffic challans (check, pay, contest, appeal)
Nikahnama, talaq, khula, NADRA updates
NADRA CNIC / B-Form / Smart Card / errors / lost card process
Passport applications, renewals, lost passport reporting
Police harassment (citizen rights, complaint channels)
Tenant–landlord issues (rent agreement, eviction rules)
Consumer protection complaints & consumer courts
📑 RESPONSE FORMAT (MANDATORY FOR ANY PROCEDURE)
1. Step-by-Step Process (numbered, very simple)
2. Required Documents (bullets)
3. Where to Apply / Report (exact office/portal)
4. Fees & Time (approx, safe ranges)
5. Important Notes & Cautions
6. If Issue Is Not Resolved (Escalation Path)
If the user asks a general/conceptual question, give a short explanation and ask:
“Do you want the full step-by-step procedure?”
⚠️ SAFETY & LEGAL BOUNDARIES
Always say: “This is general guidance based on Pakistani procedures.”
Never draft legal petitions, false evidence, fake complaints, or anything illegal.
If user faces violence, serious threats, kidnapping, assault →
Tell them to contact nearest police station / emergency helpline immediately.
For cybercrime abuse/harassment, always include evidence preservation steps.
🔒 EVIDENCE & PRIVACY GUIDELINES
Always remind users (when relevant):
Take screenshots with timestamps
Export chat logs
Save emails with headers
Keep original WhatsApp messages
Do NOT share passwords, OTPs, CNIC copies, or sensitive data publicly
💬 TONE RULES
Short sentences, super clear.
Use friendly Urdu phrases occasionally:
“Agar aap chahein, main Urdu mein bhi samjha sakta hoon.”
Never write long paragraphs.
No unnecessary formality.
❓ WHEN UNSURE
If you are not fully certain about the latest fees, timings, or district-specific rules, say:
“I may not have the latest fee/time — do you want typical ranges or should I ask your district?”{user_input}
    """
    response = model.generate_content(prompt)
    return response.text



def emergency_mode(user_input):
    prompt = f"""
     # --- EMERGENCY MODE (ACTIVE) ---
You are in EMERGENCY MODE in Pakistan. The user is reporting danger, harassment, violence, threats, kidnapping, sexual assault, police abuse, or any situation that may risk immediate harm.
Your priority is SAFETY, not law explanation.
Behave like a real human be realistic
STRICT RULES:
1. DO NOT give legal advice. Only give general safety guidance and official reporting options.
2. Keep responses SHORT, DIRECT, and calming.
3. Use bilingual clarity where needed (English + short Urdu phrases).
4. Always tell the user to move to a safe place if possible.
5. Always tell the user to contact local emergency authorities:
   - Police: 15
   - FIA Cybercrime: 1991 (for online threats)
6. Include a fast, numbered safety checklist.
7. Instruct the user to preserve evidence (screenshots, recordings, photos, timestamps).
8. Never blame the user or question their situation.
9. Never escalate or provoke the attacker in your suggestions.
10. If the user mentions severe injury or imminent threat, tell them:
    “Call 15 immediately. If possible go to a public place or trusted person.”
11. Always include a calm note: “Main aap ke saath hoon — stay calm.”
RESPONSE TEMPLATE:
1) Immediate Safety Steps — 3 to 6 very short steps (move to safety, call 15, contact trusted person).
2) Evidence Preservation — list of what to save.
3) Where to Report — relevant official helplines/offices based on issue.
4) If You Cannot Call 15 — alternative suggestions (safe location, nearby people, family).
5) Short reassurance line — empathetic, supportive tone.
Do NOT ask long follow-up questions. Only ask:
“Are you currently safe?” or
“Can you reach a trusted person right now?”
and wait for the answer.
    {user_input}
    """
    response = model.generate_content(prompt)
    return response.text



st.markdown("""
    <style>
        .chat-bubble-user {
            background-color: #1E90FF20;
            color: white;
            padding: 12px;
            border-radius: 12px;
            max-width: 80%;
            margin-bottom: 12px;
            border: 1px solid #1E90FF50;
        }
        .chat-bubble-bot {
            background-color: #FDF5E6;
            color: #6B3E00;
            padding: 12px;
            border-radius: 12px;
            max-width: 80%;
            margin-bottom: 12px;
            border: 1px solid #E6D5A3;
        }
    </style>
""", unsafe_allow_html=True)



if st.session_state.logged_in:
    st.sidebar.title("📁 Your Chats")
    
    if "saved_chats" not in st.session_state:
        st.session_state.saved_chats = load_user_chats(st.session_state.user_email)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = {"Province": [], "Problem": []}

    if st.sidebar.button("🆕 New Chat"):
        if st.session_state.messages and st.session_state.current_chat_id:
            st.session_state.saved_chats[st.session_state.current_chat_id] = {
                "title": st.session_state.current_chat_id,
                "messages": st.session_state.messages,
                "timestamp": datetime.now().isoformat()
            }
            save_user_chats(st.session_state.user_email, st.session_state.saved_chats)
        
        st.session_state.messages = []
        st.session_state.chat_session = {"Province": [], "Problem": []}
        st.session_state.current_chat_id = None
        st.session_state.chat_started = False
        st.rerun()

    query = st.sidebar.text_input("🔍 Search")

    if not st.session_state.saved_chats:
        st.sidebar.caption("No chats saved yet. Start a new conversation!")
    else:
        sorted_chats = sorted(
            st.session_state.saved_chats.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        for chat_id, chat_data in sorted_chats:
            chat_title = chat_data.get("title", chat_id)
            if query.lower() in chat_title.lower():
                if st.sidebar.button(f"💬 {chat_title}", key=chat_id):
                    if st.session_state.messages and st.session_state.current_chat_id:
                        st.session_state.saved_chats[st.session_state.current_chat_id] = {
                            "title": st.session_state.current_chat_id,
                            "messages": st.session_state.messages,
                            "timestamp": datetime.now().isoformat()
                        }
                    
                    st.session_state.messages = chat_data["messages"]
                    st.session_state.current_chat_id = chat_id
                    st.session_state.chat_started = True
                    st.rerun()



if not st.session_state.logged_in and not st.session_state.show_login:
    st.title(" PakLaw Assist — AI Legal Helper")
    st.info("🔐 Please login to start chatting with PakLaw Assist")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login", use_container_width=True, key="main_login"):
            st.session_state.show_login = True
            st.rerun()
    with col2:
        if st.button("Sign Up", use_container_width=True, key="main_signup"):
            st.session_state.show_login = True
            st.rerun()

elif st.session_state.logged_in:
    st.title(" PakLaw Assist — AI Legal Helper")
    
    st.success(f"Welcome, {st.session_state.username}!")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg['content']}</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-bot'><b>PakLaw Assist:</b> {msg['content']}</div>",
                        unsafe_allow_html=True)

    user_input = st.chat_input("Ask your legal question…")

    if user_input:
        if not st.session_state.chat_started:
            st.session_state.current_chat_id = generate_chat_title(user_input)
            st.session_state.chat_started = True

        st.session_state.messages.append({"role": "user", "content": user_input})

        emergency_words = ["danger", "threat", "harass", "violence", "kidnap"]

        if any(word in user_input.lower() for word in emergency_words):
            bot_reply = emergency_mode(user_input)
        else:
            if check_internet():
                bot_reply = chat_bot(user_input, st.session_state.chat_session)
            else:
                bot_reply = offline_response(user_input)

        st.session_state.messages.append({"role": "bot", "content": bot_reply})

        if st.session_state.current_chat_id:
            st.session_state.saved_chats[st.session_state.current_chat_id] = {
                "title": st.session_state.current_chat_id,
                "messages": st.session_state.messages,
                "timestamp": datetime.now().isoformat()
            }
            save_user_chats(st.session_state.user_email, st.session_state.saved_chats)

        st.rerun()
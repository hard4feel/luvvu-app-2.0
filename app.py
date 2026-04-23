import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os

# --- 1. CONNECTIVITY ---
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Check your Secrets.")

# --- 2. THE BLACKOUT UI (MINIMALISM) ---
st.set_page_config(page_title="Luvvu Terminal", page_icon="⚫", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=JetBrains+Mono&display=swap');
    
    /* Глобальные стили */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    header, footer { visibility: hidden; }

    /* Эффект пульса на фоне */
    .pulse-bg {
        position: fixed;
        top: 50%;
        left: 0;
        width: 100%;
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        animation: pulse 4s infinite ease-in-out;
        z-index: -1;
    }

    @keyframes pulse {
        0% { opacity: 0.1; transform: scaleX(0.8); }
        50% { opacity: 0.5; transform: scaleX(1); }
        100% { opacity: 0.1; transform: scaleX(0.8); }
    }

    /* Стиль сообщений */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 0px !important;
        color: #FFFFFF !important;
        margin-bottom: 10px !important;
    }

    /* Желтая лента ремонта */
    .caution-tape {
        background: #ffd700;
        color: #000;
        padding: 5px;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
        border: 2px dashed #000;
        margin: 10px 0;
    }

    /* Поля ввода */
    .stChatInputContainer textarea {
        background-color: #000 !important;
        color: #fff !important;
        border: 1px solid #fff !important;
        border-radius: 0px !important;
    }

    .stButton>button {
        background-color: #fff !important;
        color: #000 !important;
        border-radius: 0px !important;
        font-weight: bold;
        border: none !important;
    }
    </style>
    <div class="pulse-bg"></div>
""", unsafe_allow_html=True)

# --- 3. DATABASE ---
def sync_user(uid):
    res = supabase.table("users").select("*").eq("id", uid).execute()
    return res.data[0] if res.data else None

def save_user(uid, data):
    supabase.table("users").upsert({
        "id": uid,
        "traits": data.get("traits", []),
        "chat_history": data.get("chat_history", []),
        "auth": True
    }).execute()

# --- 4. SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None

# ЭКРАН ВХОДА
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='height: 20vh'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; letter-spacing: 15px; font-weight: 300;'>LUVVU</h1>", unsafe_allow_html=True)
        
        uid = st.text_input("ID").strip().lower()
        pwd = st.text_input("KEY", type="password")
        
        if st.button("ENTER"):
            if uid == st.secrets["LOGIN_USER"].lower() and pwd == st.secrets["LOGIN_PASSWORD"]:
                data = sync_user(uid)
                if not data:
                    data = {"id": uid, "traits": [], "chat_history": []}
                    save_user(uid, data)
                st.session_state.user = data
                st.rerun()
    st.stop()

# --- 5. MAIN SYSTEM ---
user = st.session_state.user

# Сайдбар с модулями в разработке
with st.sidebar:
    st.markdown("<h2 style='letter-spacing: 5px;'>LUVVU</h2>", unsafe_allow_html=True)
    st.write(f"Active: `{user['id']}`")
    st.markdown("---")
    
    # Модули с лентой
    st.write("📁 MOD_BUSINESS")
    st.markdown('<div class="caution-tape">🚧 UNDER CONSTRUCTION 🚧</div>', unsafe_allow_html=True)
    
    st.write("🤝 MOD_FRIENDSHIP")
    st.markdown('<div class="caution-tape">🚧 UNDER CONSTRUCTION 🚧</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.write("🎯 TRAITS:")
    for t in user["traits"]:
        st.markdown(f"• `{t.upper()}`")
    
    if st.button("EXIT"):
        st.session_state.user = None
        st.rerun()

# Чат
st.markdown("<h4 style='letter-spacing: 2px; color: rgba(255,255,255,0.5);'>CORE_COMPANION_V.1</h4>", unsafe_allow_html=True)

for msg in user["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Input command..."):
    user["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Networking analysis
    try:
        tag_resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"One word trait for: {prompt}"}]
        )
        tag = tag_resp.choices[0].message.content.strip().lower()
        if len(tag.split()) == 1 and tag not in user["traits"]:
            user["traits"].append(tag)
    except: pass

    # AI Response
    sys = "Ты — Luvvu, минималистичный ИИ. Твоя речь строгая, умная, без эмодзи. Только черный и белый смысл."
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": sys}] + user["chat_history"]
    )
    
    ans = res.choices[0].message.content
    user["chat_history"].append({"role": "assistant", "content": ans})
    with st.chat_message("assistant"): st.markdown(ans)
    
    save_user(user["id"], user)
import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os

# --- 1. ТЕХНИЧЕСКАЯ ЧАСТЬ ---
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Ошибка подключения. Проверь Secrets.")

# --- 2. ДИЗАЙН "WARM MINIMALISM" ---
st.set_page_config(page_title="Luvvu Space", page_icon="🤍", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Основной фон - мягкий и теплый */
    .stApp {
        background-color: #FDFDFB !important;
        color: #2D2D2D !important;
        font-family: 'Inter', sans-serif;
    }

    header, footer { visibility: hidden; }

    /* Контейнер чата */
    .stChatMessage {
        background-color: #FFFFFF !important;
        border: 1px solid #F0F0EE !important;
        border-radius: 24px !important;
        padding: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
        margin-bottom: 12px !important;
    }

    /* Кнопки - мягкий акцент */
    .stButton>button {
        width: 100%;
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 12px !important;
        font-weight: 500 !important;
        border: none !important;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Инпут */
    .stChatInputContainer textarea {
        border-radius: 20px !important;
        border: 1px solid #EBEBEB !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. ЛОГИКА БАЗЫ ---
def get_data(uid):
    res = supabase.table("users").select("*").eq("id", uid).execute()
    return res.data[0] if res.data else None

def save_data(uid, data):
    supabase.table("users").upsert({
        "id": uid,
        "traits": data.get("traits", []),
        "chat_history": data.get("chat_history", [])
    }).execute()

# --- 4. СЕССИЯ ---
if "user" not in st.session_state:
    st.session_state.user = None

# Экран входа
if st.session_state.user is None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div style='height: 15vh'></div>", unsafe_allow_html=True)
        # Логотип (если есть файл logo.jpg или png)
        if os.path.exists("logo.jpg"): st.image("logo.jpg")
        elif os.path.exists("logo.png"): st.image("logo.png")
        else: st.markdown("<h2 style='text-align: center; font-weight: 300; letter-spacing: 2px;'>LUVVU</h2>", unsafe_allow_html=True)
        
        uid = st.text_input("Ваш ID").strip().lower()
        pwd = st.text_input("Пароль", type="password")
        
        if st.button("Войти"):
            if uid == st.secrets["LOGIN_USER"].lower() and pwd == st.secrets["LOGIN_PASSWORD"]:
                data = get_data(uid)
                if not data:
                    data = {"id": uid, "traits": [], "chat_history": []}
                    save_data(uid, data)
                st.session_state.user = data
                st.rerun()
    st.stop()

# --- 5. ТЕРМИНАЛ ЧАТА ---
user = st.session_state.user

# Сайдбар (минималистичный)
with st.sidebar:
    st.markdown("### Luvvu Profile")
    st.write(f"ID: `{user['id']}`")
    st.markdown("---")
    st.write("✨ Интересы:")
    for t in user["traits"]:
        st.caption(f"• {t.capitalize()}")
    
    if st.button("Выйти"):
        st.session_state.user = None
        st.rerun()

# Основной контент
st.markdown("<h4 style='font-weight: 400; color: #8E8E8E;'>Личный ассистент</h4>", unsafe_allow_html=True)

for msg in user["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Напишите что-нибудь..."):
    user["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    # Анализ интересов
    try:
        tag_resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Extract 1 keyword from: {prompt}. One word only."}]
        )
        tag = tag_resp.choices[0].message.content.strip().lower()
        if len(tag.split()) == 1 and tag not in user["traits"]:
            user["traits"].append(tag)
    except: pass

    # Ответ Luvvu
    sys = "Ты — Luvvu, теплый, эмпатичный и мудрый друг. Твоя речь безупречна. Никаких эмодзи."
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": sys}] + user["chat_history"]
    )
    
    answer = res.choices[0].message.content
    user["chat_history"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"): st.write(answer)
    
    # Сохранение
    save_data(user["id"], user)
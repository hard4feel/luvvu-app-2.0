import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os

# --- 1. CONNECTIVITY (SUPABASE & GROQ) ---
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Критическая ошибка подключения. Проверь Secrets в настройках Streamlit.")

# --- 2. LUXURY UI (BLACK & WHITE HIGH CONTRAST) ---
st.set_page_config(page_title="Luvvu Space", page_icon="⚫", layout="wide")

# Умный поиск логотипа
def get_logo():
    for ext in ["jpg", "png", "jpeg"]:
        if os.path.exists(f"logo.{ext}"):
            return f"logo.{ext}"
    return "https://cdn-icons-png.flaticon.com/512/2583/2583158.png" # Элегантная иконка-заглушка

LOGO_PATH = get_logo()

# Боковое меню для настроек
with st.sidebar:
    st.markdown("### НАСТРОЙКИ СТИЛЯ")
    ui_mode = st.radio("Цветовая схема", ["LUXURY WHITE", "TOTAL BLACK"])
    st.markdown("---")

# CSS для радикального контраста
if ui_mode == "LUXURY WHITE":
    bg, text, card = "#FFFFFF", "#000000", "#F2F2F2"
else:
    bg, text, card = "#000000", "#FFFFFF", "#1A1A1A"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Cinzel:wght@400;700&display=swap');
    
    .stApp {{
        background-color: {bg} !important;
        color: {text} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    header, footer {{ visibility: hidden; }}
    
    /* Сообщения чата */
    [data-testid="stChatMessage"] {{
        background-color: {card} !important;
        border: 1px solid rgba(128,128,128,0.2) !important;
        border-radius: 0px !important;
        padding: 25px !important;
        color: {text} !important;
        margin-bottom: 15px !important;
    }}

    /* Поля ввода */
    .stTextInput>div>div>input, .stChatInputContainer textarea {{
        background-color: {bg} !important;
        color: {text} !important;
        border: 1px solid {text} !important;
        border-radius: 0px !important;
    }}

    /* Кнопки */
    .stButton>button {{
        background-color: {text} !important;
        color: {bg} !important;
        border: none !important;
        border-radius: 0px !important;
        font-family: 'Cinzel', serif;
        font-weight: 700;
        letter-spacing: 2px;
        padding: 15px !important;
        width: 100%;
    }}
    
    /* Сайдбар */
    [data-testid="stSidebar"] {{
        background-color: {bg} !important;
        border-right: 1px solid rgba(128,128,128,0.2);
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATABASE LOGIC ---
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

# --- 4. SESSION MANAGEMENT ---
if "session_user" not in st.session_state:
    st.session_state.session_user = None

# ЭКРАН ВХОДА (Если сессия пуста)
if st.session_state.session_user is None:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<div style='height: 15vh'></div>", unsafe_allow_html=True)
        st.image(LOGO_PATH, use_container_width=True)
        st.markdown(f"<h1 style='text-align: center; font-family: Cinzel; color: {text};'>LUVVU</h1>", unsafe_allow_html=True)
        
        entry_id = st.text_input("ID FOUNDER").strip().lower()
        entry_key = st.text_input("SECURITY KEY", type="password")
        
        if st.button("AUTHORIZE"):
            if entry_id == st.secrets["LOGIN_USER"].lower() and entry_key == st.secrets["LOGIN_PASSWORD"]:
                data = sync_user(entry_id)
                if not data:
                    data = {"id": entry_id, "traits": [], "chat_history": []}
                    save_user(entry_id, data)
                st.session_state.session_user = data
                st.rerun()
            else:
                st.error("Доступ отклонен.")
    st.stop()

# --- 5. MAIN TERMINAL (AUTHENTICATED) ---
user = st.session_state.session_user

# Панель управления (Сайдбар)
with st.sidebar:
    st.image(LOGO_PATH, width=100)
    st.markdown(f"<h2 style='font-family: Cinzel;'>{user['id'].upper()}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("🎯 **NETWORKING TRAITS:**")
    if user["traits"]:
        for t in user["traits"]:
            st.markdown(f"• `{t.upper()}`")
    else:
        st.caption("Анализирую твой путь...")
    
    st.markdown("---")
    if st.button("TERMINATE"):
        st.session_state.session_user = None
        st.rerun()

# Чат-интерфейс
st.markdown(f"<h3 style='font-family: Cinzel; border-bottom: 1px solid {text}; padding-bottom: 10px;'>Luvvu / Ecosystem</h3>", unsafe_allow_html=True)

# Вывод истории из Supabase
for msg in user["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div style='font-family: Inter; font-weight: 300;'>{msg['content']}</div>", unsafe_allow_html=True)

# Новый ввод
if prompt := st.chat_input("Введи сообщение..."):
    user["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # 1. Анализ для нетворкинга (Легкая модель)
    try:
        tag_resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Extract 1 trait or interest from: '{prompt}'. One word only, no punctuation."}]
        )
        tag = tag_resp.choices[0].message.content.strip().lower()
        if len(tag.split()) == 1 and tag not in [t.lower() for t in user["traits"]]:
            user["traits"].append(tag)
    except: pass

    # 2. Основной ответ Luvvu (Мощная модель)
    sys_instruction = f"""
    Ты — Luvvu, интеллект высшего уровня. Твоя речь — это эталон русского языка. 
    Никаких опечаток, никаких эмодзи. Стиль: строгий, глубокий, мудрый минимализм.
    Твои знания о пользователе: {', '.join(user['traits'])}.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            messages=[{"role": "system", "content": sys_instruction}] + user["chat_history"]
        )
        ai_reply = response.choices[0].message.content
        user["chat_history"].append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"): st.markdown(ai_reply)
    except Exception:
        st.warning("Лимит модели достигнут. Попробуй позже.")

    # Сохраняем в Supabase
    save_user(user["id"], user)
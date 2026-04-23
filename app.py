import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os

# --- 1. ТЕХНИЧЕСКАЯ УСТАНОВКА (SUPABASE & GROQ) ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Ошибка подключения к базе данных. Проверь Secrets.")

# --- 2. LUXURY UI (OLD MONEY STYLE) ---
st.set_page_config(page_title="Luvvu Hub", page_icon="⚪", layout="wide")

# Файл логотипа
LOGO_FILE = "logo.jpg"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');
    
    /* Основной фон и шрифт */
    .stApp {{
        background-color: #F9F9F7; /* Мягкий кремовый */
        color: #1C1C1C;
        font-family: 'Montserrat', sans-serif;
    }}
    
    /* Убираем стандартные элементы Streamlit */
    header, footer {{ visibility: hidden; }}
    
    /* Стилизация контейнера логотипа */
    .logo-container {{
        text-align: center;
        padding: 40px 0;
    }}
    
    /* Чат (Чистый минимализм) */
    [data-testid="stChatMessage"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #EAEAEA !important;
        border-radius: 0px !important; /* Квадратные формы для серьезности */
        box-shadow: 5px 5px 15px rgba(0,0,0,0.02);
        padding: 20px !important;
        margin-bottom: 15px !important;
    }}
    
    /* Поля ввода */
    .stTextInput>div>div>input {{
        border-radius: 0px !important;
        border: 1px solid #D1D1D1 !important;
        background-color: transparent !important;
    }}
    
    /* Кнопки (Акцент на премиальность) */
    .stButton>button {{
        width: 100%;
        background-color: #1C1C1C !important;
        color: #F9F9F7 !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 15px !important;
        font-family: 'Cinzel', serif;
        letter-spacing: 2px;
        transition: 0.4s ease;
    }}
    .stButton>button:hover {{
        background-color: #4A4A4A !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }}

    /* Боковая панель */
    [data-testid="stSidebar"] {{
        background-color: #FFFFFF !important;
        border-right: 1px solid #EAEAEA;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. ФУНКЦИИ БАЗЫ ---
def fetch_user(uid):
    try:
        res = supabase.table("users").select("*").eq("id", uid).execute()
        return res.data[0] if res.data else None
    except: return None

def update_user(uid, data):
    supabase.table("users").upsert({
        "id": uid,
        "traits": data.get("traits", []),
        "chat_history": data.get("chat_history", []),
        "auth": True
    }).execute()

# --- 4. СЕССИЯ И АВТОРИЗАЦИЯ ---
if "user" not in st.session_state:
    st.session_state.user = None

# Экран входа
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_column_width=True)
        else:
            st.markdown("<h1 style='font-family: Cinzel; letter-spacing: 5px;'>LUVVU</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        uid = st.text_input("FOUNDER ID").strip().lower()
        pwd = st.text_input("ACCESS KEY", type="password")
        
        if st.button("AUTHENTICATE"):
            if uid == st.secrets["LOGIN_USER"].lower() and pwd == st.secrets["LOGIN_PASSWORD"]:
                data = fetch_user(uid)
                if not data:
                    data = {"id": uid, "traits": [], "chat_history": []}
                    update_user(uid, data)
                st.session_state.user = data
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

# --- 5. ОСНОВНОЙ ТЕРМИНАЛ ---
user = st.session_state.user

# Сайдбар (Networking & Profile)
with st.sidebar:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE)
    st.markdown(f"<h2 style='font-family: Cinzel;'>{user['id'].upper()}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("🎯 **Luvvu Insights (Networking):**")
    if user["traits"]:
        for t in user["traits"]:
            st.markdown(f"• `{t.upper()}`")
    else:
        st.caption("Ожидание данных...")
    
    st.markdown("---")
    if st.button("TERMINATE SESSION"):
        st.session_state.user = None
        st.rerun()

# Чат-модуль
st.markdown("<h3 style='font-family: Cinzel; letter-spacing: 3px;'>Luvvu / Companion</h3>", unsafe_allow_html=True)

# Отображение истории
for m in user["chat_history"]:
    with st.chat_message(m["role"]):
        st.markdown(f"<div style='font-weight: 300;'>{m['content']}</div>", unsafe_allow_html=True)

# Ввод сообщения
if prompt := st.chat_input("Напишите сообщение..."):
    user["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Интеллект и анализ (Groq)
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # 1. Анализ качеств (Networking)
    try:
        tag_resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Выдели одно качество человека из фразы: '{prompt}'. Ответь 1 словом без знаков препинания."}]
        )
        tag = tag_resp.choices[0].message.content.strip()
        if len(tag.split()) == 1 and tag.lower() not in [t.lower() for t in user["traits"]]:
            user["traits"].append(tag)
    except: pass

    # 2. Основной ответ (Luvvu Soul)
    sys_msg = f"""
    Ты — Luvvu, душа проекта. Ты — зеркало собеседника. 
    Твоя речь безупречна, грамотна и лишена эмодзи. 
    Ты используешь чистый, красивый русский язык. 
    Твои знания о пользователе: {', '.join(user['traits'])}.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        messages=[{"role": "system", "content": sys_msg}] + user["chat_history"]
    )
    
    ai_msg = response.choices[0].message.content
    user["chat_history"].append({"role": "assistant", "content": ai_msg})
    with st.chat_message("assistant"): st.markdown(ai_msg)
    
    # Синхронизация с Supabase
    update_user(user["id"], user)
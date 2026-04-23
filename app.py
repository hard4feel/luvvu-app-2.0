import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import time

# --- 1. ТЕХНИЧЕСКАЯ УСТАНОВКА ---
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except: st.error("Ошибка Supabase. Проверь Secrets.")

# --- 2. LUXURY UI & THEMING (OLD MONEY STYLE) ---
st.set_page_config(page_title="Luvvu OS", page_icon="⚪", layout="wide")

# Файл логотипа
LOGO_FILE = "logo.jpg"

# Ссылки на фоновые изображения из сети (Атмосферные, спокойные)
BG_AUTH = "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=2670&auto=format&fit=crop" # Йога/Туман
BG_CHAT = "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=2574&auto=format&fit=crop" # Глубокий космос

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600;700&display=swap');
    
    /* Убираем стандартные элементы Streamlit */
    header, footer {{ visibility: hidden; }}
    
    /* Стилизация баблов чата для читаемости на темном фоне */
    .stChatMessage {{
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 20px !important;
        color: #FFFFFF !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
    }}
    
    /* Ввод сообщения (Мобильный стайл) */
    .stChatInputContainer {{
        background: rgba(26,26,26,0.9) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 20px !important;
    }}
    
    /* Кнопки - акцент на премиальность */
    .stButton>button {{
        width: 100%;
        background-color: #1C1C1C !important;
        color: #F9F9F7 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-family: 'Cinzel', serif;
        letter-spacing: 2px;
        transition: 0.4s ease;
    }}
    .stButton>button:hover {{
        background-color: #4A4A4A !important;
        box-shadow: 0 5px 15px rgba(255,0,0,0.1);
    }}

    /* Боковая панель */
    [data-testid="stSidebar"] {{
        background-color: #FFFFFF !important;
        border-right: 1px solid #EAEAEA;
    }}
    
    /* Адаптация под телефон */
    @media (max-width: 600px) {{
        h1 {{ font-size: 2rem !important; }}
        .stChatMessage {{ padding: 10px !important; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. ФУНКЦИИ БАЗЫ ДАННЫХ ---
def fetch_user_state(uid):
    try:
        res = supabase.table("users").select("*").eq("id", uid).execute()
        return res.data[0] if res.data else None
    except: return None

def save_user_state(uid, data):
    supabase.table("users").upsert({
        "id": uid,
        "auth": True,
        "traits": data.get("traits", []),
        "chat_history": data.get("chat_history", [])
    }).execute()

# --- 4. УПРАВЛЕНИЕ СЕССИЕЙ ---
if "user_state" not in st.session_state:
    st.session_state.user_state = None

# --- ЭКРАН 1: АВТОРИЗАЦИЯ (С ФОНОМ ИЗ СЕТИ) ---
if st.session_state.user_state is None:
    # Применяем фон для экрана входа
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("{BG_AUTH}");
            background-size: cover;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height: 15vh'></div>", unsafe_allow_html=True)
        # Умная проверка логотипа
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_column_width=True)
        else:
            # Стилизованный заголовок, если лого пока нет
            st.markdown("<h1 style='font-family: Cinzel; text-align: center; letter-spacing: 10px; color: #FFFFFF;'>LUVVU</h1>", unsafe_allow_html=True)
        
        st.markdown("<center style='color: #EEEEEE; margin-bottom: 20px;'>Ecosystem for Growth</center>", unsafe_allow_html=True)
        
        u = st.text_input("ID Основателя").strip().lower()
        p = st.text_input("Secure Pass", type="password")
        
        if st.button("AUTHENTICATE", use_container_width=True):
            if u == st.secrets["LOGIN_USER"].lower() and p == st.secrets["LOGIN_PASSWORD"]:
                data = fetch_user_state(u)
                if not data:
                    data = {"id": u, "traits": [], "chat_history": []}
                    save_user_state(u, data)
                st.session_state.user_state = data
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

# --- ЭКРАН 2: ЧАТ (С ФОНОМ ИЗ СЕТИ + ПАМЯТЬ) ---
user = st.session_state.user_state

# Применяем фон для чата (Темный, для читаемости баблов)
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("{BG_CHAT}");
        background-size: cover;
        background-position: center;
    }}
    h1, h2, h3 {{ color: #FFFFFF !important; }}
    </style>
""", unsafe_allow_html=True)

# Сайдбар (Профиль & Networking)
with st.sidebar:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE)
    st.markdown(f"<h2 style='font-family: Cinzel; text-align: center; color: #1a1a1a !important;'>{user['id'].upper()}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("🎯 **Твои теги (Networking):**")
    if user["traits"]:
        traits_list = ", ".join(user["traits"])
        st.info(f"`{traits_list.upper()}`")
    else:
        st.caption("Ожидание данных...")
    
    st.markdown("---")
    if st.button("TERMINATE SESSION"):
        st.session_state.user_state = None
        st.rerun()

# Чат-интерфейс
st.markdown("<h3 style='font-family: Cinzel; letter-spacing: 3px;'>Luvvu / Companion</h3>", unsafe_allow_html=True)

# Отображение истории чата (из Supabase)
for m in user["chat_history"]:
    with st.chat_message(m["role"]):
        st.markdown(f"<div style='font-family: Montserrat; font-weight: 300;'>{m['content']}</div>", unsafe_allow_html=True)

# Обработка ввода
if prompt := st.chat_input("Напишите сообщение..."):
    # Добавляем в историю
    user["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Запускаем фоновый анализ нетворкинга (Groq 8B)
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    try:
        tag_resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Выдели одно качество человека из фразы: '{prompt}'. Ответь 1 словом без знаков препинания."}]
        )
        tag = tag_resp.choices[0].message.content.strip()
        if len(tag.split()) == 1 and tag.lower() not in [t.lower() for t in user["traits"]]:
            user["traits"].append(tag)
    except: pass

    # Основной ответ Luvvu (Groq 70B Versatile)
    traits_str = ", ".join(user['traits'])
    sys_prompt = f"""
    Ты — Luvvu, душа проекта. Ты — мудрый соратник Ансара.
    Твоя речь эталонная, грамотная, лишена эмодзи. Стиль: 'Тихая уверенность'.
    Твои знания о пользователе: {traits_str}.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7, # Снижаем для точности слов
        messages=[{"role": "system", "content": sys_prompt}] + user["chat_history"]
    )
    
    ai_msg = response.choices[0].message.content
    user["chat_history"].append({"role": "assistant", "content": ai_msg})
    with st.chat_message("assistant"): st.markdown(ai_msg)
    
    # Синхронизация с Supabase (Сохраняем всё!)
    save_user_state(user["id"], user)
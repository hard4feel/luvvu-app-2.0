import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os

# --- 1. ИНИЦИАЛИЗАЦИЯ SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. КОНФИГУРАЦИЯ И ТЕМЫ ---
st.set_page_config(page_title="Luvvu Space", page_icon="❤️", layout="wide")

LOGO_FILE = "logo.png"

# Боковое меню для выбора стиля (без агрессии)
with st.sidebar:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
    st.markdown("### Визуальный стиль")
    theme_choice = st.selectbox("Тема", ["Soft White", "Deep Dark", "Minimalist Grey"])

themes = {
    "Soft White": {"bg": "#FFFFFF", "text": "#1A1A1A", "card": "#F8F9FA"},
    "Deep Dark": {"bg": "#0D0D0D", "text": "#E0E0E0", "card": "#1A1A1A"},
    "Minimalist Grey": {"bg": "#F5F5F0", "text": "#2C3E50", "card": "#EAEAEA"}
}
style = themes[theme_choice]

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&display=swap');
    
    .stApp {{
        background-color: {style['bg']};
        color: {style['text']};
        font-family: 'Montserrat', sans-serif;
    }}
    
    /* Сообщения чата */
    .stChatMessage {{
        background-color: {style['card']} !important;
        border-radius: 20px !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
        margin-bottom: 10px;
    }}
    
    /* Кнопки - аккуратный акцент */
    .stButton>button {{
        background: #B71C1C !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        opacity: 0.8;
        transform: translateY(-2px);
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. ФУНКЦИИ БАЗЫ ДАННЫХ ---
def get_user_data(username):
    response = supabase.table("users").select("*").eq("id", username).execute()
    return response.data[0] if response.data else None

def save_user_data(username, data):
    supabase.table("users").upsert({
        "id": username,
        "auth": data.get("auth", True),
        "traits": data.get("traits", []),
        "chat_history": data.get("chat_history", []),
        "theme": data.get("theme", "Light")
    }).execute()

# --- 4. ЛОГИКА СЕССИИ ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# --- ЭКРАН ВХОДА ---
if not st.session_state.user_id:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height: 10vh'></div>", unsafe_allow_html=True)
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE)
        
        uid = st.text_input("ID Основателя").strip().lower()
        pwd = st.text_input("Security Key", type="password")
        
        if st.button("ДОСТУП", use_container_width=True):
            if uid == st.secrets["LOGIN_USER"].lower() and pwd == st.secrets["LOGIN_PASSWORD"]:
                # Загружаем данные или создаем новые
                data = get_user_data(uid)
                if not data:
                    data = {"id": uid, "auth": True, "traits": [], "chat_history": [], "theme": theme_choice}
                    save_user_data(uid, data)
                
                st.session_state.user_id = uid
                st.session_state.user_data = data
                st.rerun()
            else:
                st.error("Данные неверны.")
    st.stop()

# --- 5. ОСНОВНОЙ МОДУЛЬ (PERSONAL & NETWORKING) ---
user_data = st.session_state.user_data

with st.sidebar:
    st.write(f"Привет, **{st.session_state.user_id}**")
    st.markdown("---")
    st.write("🎯 **Твои теги (Networking):**")
    st.info(", ".join(user_data["traits"]) if user_data["traits"] else "Изучаю твои интересы...")
    
    if st.button("Выйти из системы"):
        st.session_state.user_id = None
        st.rerun()

st.title("Luvvu Companion")

# Отображение чата из Supabase
for msg in user_data["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Расскажи, что нового..."):
    # Добавляем сообщение пользователя
    user_data["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    # 1. Анализ для нетворкинга (в фоне через легкую модель)
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    try:
        tag_resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Выдели 1 ключевой интерес из фразы: '{prompt}'. Ответь одним словом."}]
        )
        tag = tag_resp.choices[0].message.content.strip().lower()
        if len(tag) < 15 and tag not in user_data["traits"]:
            user_data["traits"].append(tag)
    except: pass

    # 2. Основной ответ Luvvu
    sys_prompt = f"""
    Ты — Luvvu, теплый и мудрый соратник. Твоя речь безупречна.
    Твои текущие знания о пользователе (теги): {', '.join(user_data['traits'])}.
    Будь эмпатичным, не используй агрессивные цвета в речи, будь мягким зеркалом души.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[{"role": "system", "content": sys_prompt}] + user_data["chat_history"]
    )
    
    full_response = response.choices[0].message.content
    user_data["chat_history"].append({"role": "assistant", "content": full_response})
    
    with st.chat_message("assistant"): st.markdown(full_response)
    
    # Сохраняем всё в Supabase
    save_user_data(st.session_state.user_id, user_data)
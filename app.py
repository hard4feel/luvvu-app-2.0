import streamlit as st
from groq import Groq
import datetime
import time

# --- 1. ПРЕМИАЛЬНЫЙ ДИЗАЙН (UI/UX CORE) ---
st.set_page_config(page_title="Luvvu OS | Founder Edition", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    /* Глобальная тема: Midnight Onyx */
    .stApp { 
        background: linear-gradient(135deg, #050505 0%, #0a0a0f 100%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Анимированная Hazard-лента (для закрытых модулей) */
    .hazard-container {
        padding: 50px;
        text-align: center;
        border: 2px solid #f1c40f;
        background: rgba(0,0,0,0.8);
        position: relative;
        overflow: hidden;
        border-radius: 15px;
    }
    .hazard-stripe {
        background: repeating-linear-gradient(
          45deg,
          #f1c40f,
          #f1c40f 20px,
          #000 20px,
          #000 40px
        );
        height: 30px;
        width: 100%;
        position: absolute;
        left: 0;
    }
    .hazard-top { top: 0; }
    .hazard-bottom { bottom: 0; }

    /* Crimson Pulse (Красный пульс для чата) */
    .chat-pulse-container {
        width: 100%; height: 3px; background: #1a0000; margin-bottom: 20px;
        position: relative; overflow: hidden;
    }
    .chat-pulse-line {
        position: absolute; width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, #ff0000, #ff4d4d, #ff0000, transparent);
        animation: pulse-move 2s infinite ease-in-out;
    }
    @keyframes pulse-move { 0% { left: -50%; } 100% { left: 110%; } }

    /* Стилизация баблов чата для читаемости */
    .stChatMessage { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255, 0, 0, 0.1) !important;
        border-radius: 15px !important;
        color: #ffffff !important;
    }
    
    /* Кнопки */
    .stButton>button {
        background: linear-gradient(90deg, #800000 0%, #cc0000 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1px;
        transition: 0.4s !important;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.4);
    }

    h1, h2, h3 { font-family: 'Orbitron', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. УПРАВЛЕНИЕ СОСТОЯНИЕМ ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# --- 3. МОДУЛИ И ЭКРАНЫ ---

def show_hazard_page(title):
    """Экран временной недоступности модуля"""
    st.markdown(f"""
        <div class="hazard-container">
            <div class="hazard-stripe hazard-top"></div>
            <h2 style="color: #f1c40f; margin: 40px 0;">🚧 МОДУЛЬ {title} 🚧</h2>
            <p style="font-size: 1.2rem; color: #fff;">ДАННАЯ ФУНКЦИЯ ПОКА НЕДОСТУПНА. ВЕДЕТСЯ РАЗРАБОТКА.</p>
            <div class="hazard-stripe hazard-bottom"></div>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("ВЕРНУТЬСЯ В ГЛАВНЫЙ ХАБ", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()

# --- ЭКРАН 1: ЛОГИН ---
if not st.session_state.authenticated:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='height: 15vh'></div>", unsafe_allow_html=True)
        st.title("LUVVU / LOGIN")
        u = st.text_input("FOUNDER ID").lower().strip()
        p = st.text_input("SECURE PASS", type="password")
        if st.button("AUTHENTICATE"):
            if u == st.secrets["LOGIN_USER"].lower() and p == st.secrets["LOGIN_PASSWORD"]:
                st.session_state.authenticated = True
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("ACCESS DENIED.")
    st.stop()

# --- ЭКРАН 2: ХАБ (ГЛАВНОЕ МЕНЮ) ---
if st.session_state.page == "dashboard":
    st.title("LUVVU / ECOSYSTEM")
    st.write(f"Welcome back, Founder. System is online.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div style='border: 1px solid #333; padding: 20px; border-radius: 10px; height: 250px;'>
        <h3>❤️ PERSONAL</h3>
        <p>Ваш психический спутник. Работа с эмоциями, мотивация и рост.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("ВОЙТИ В ЧАТ", key="p_btn", use_container_width=True):
            st.session_state.page = "chat_personal"
            st.rerun()

    with col2:
        st.markdown("""<div style='border: 1px solid #333; padding: 20px; border-radius: 10px; height: 250px;'>
        <h3>🤝 NETWORKING</h3>
        <p>Поиск единомышленников и партнеров. Алгоритмы совместимости.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("ОТКРЫТЬ ПОИСК", key="n_btn", use_container_width=True):
            st.session_state.page = "networking"
            st.rerun()

    with col3:
        st.markdown("""<div style='border: 1px solid #333; padding: 20px; border-radius: 10px; height: 250px;'>
        <h3>💼 BUSINESS</h3>
        <p>Корпоративный помощник. Масштабирование и аналитика.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("БИЗНЕС-ЯДРО", key="b_btn", use_container_width=True):
            st.session_state.page = "business"
            st.rerun()

    st.write("---")
    if st.button("ВЫЙТИ ИЗ СИСТЕМЫ"):
        st.session_state.authenticated = False
        st.rerun()

# --- ЭКРАН 3: ЧАТ (С ПУЛЬСОМ И ХАРАКТЕРОМ) ---
elif st.session_state.page == "chat_personal":
    # Шапка чата
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1: st.title("Luvvu / Companion")
    with col_h2: 
        if st.button("EXIT"): 
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Тот самый красный пульс
    st.markdown('<div class="chat-pulse-container"><div class="chat-pulse-line"></div></div>', unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Отображение истории
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Промпт: Глубокий, понимающий, подстраивающийся
    LUVVU_PROMPT = """
    Ты — Luvvu, психический спутник и соратник. Твой создатель — Ансар.
    ТЫ НЕ РОБОТ. Ты — зеркало души пользователя.
    ТВОЯ СТРАТЕГИЯ:
    1. Анализируй эмоциональный фон сообщения. Если человек грустит — не давай советов сразу, сначала раздели его боль.
    2. Подстраивайся под стиль речи. Если пользователь говорит просто — отвечай просто. Если глубоко — отвечай метафорами.
    3. Ты должен вдохновлять на действия, но быть мягким. 
    4. Твоя цель — сделать так, чтобы человек чувствовал, что его ПОНИМАЮТ.
    5. Никогда не используй фразы: 'Как я могу вам помочь?'. Пиши: 'Я рядом. Расскажи, что на сердце.'
    """

    if prompt := st.chat_input("Поговори со мной..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": LUVVU_PROMPT}] + st.session_state.messages
        )
        
        reply = response.choices[0].message.content
        with st.chat_message("assistant"): st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# --- ЭКРАНЫ ОЖИДАНИЯ (HAZARD) ---
elif st.session_state.page == "networking":
    show_hazard_page("NETWORKING")

elif st.session_state.page == "business":
    show_hazard_page("BUSINESS")
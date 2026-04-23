import streamlit as st
from groq import Groq
import datetime
import time

# --- 1. КОНФИГУРАЦИЯ И ДИЗАЙН (PREMIUM LOOK) ---
st.set_page_config(page_title="Luvvu Ecosystem", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=Playfair+Display:ital@1&display=swap');
    
    .stApp { background-color: #fdfdfd; color: #2c3e50; font-family: 'Montserrat', sans-serif; }
    
    /* Стиль карточек модулей */
    .module-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #eee;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        transition: 0.3s;
        margin-bottom: 20px;
    }
    .module-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    
    /* Статусы подписок */
    .status-vip { color: #d4af37; font-weight: bold; }
    .status-corp { color: #4A90E2; font-weight: bold; }
    
    /* Чат мессенджер */
    .stChatMessage { border-radius: 25px !important; padding: 15px !important; margin-bottom: 15px !important; }
    
    h1 { font-family: 'Playfair Display', serif; font-size: 3rem !important; color: #1a1a1a !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЙ ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "Free" # Free, VIP, Corporate, Admin

# --- 3. ФУНКЦИИ БЕЗОПАСНОСТИ ---
def login():
    u = st.session_state.u_input.lower().strip()
    p = st.session_state.p_input
    
    # Твои секреты из Streamlit Cloud
    if u == st.secrets["LOGIN_USER"].lower() and p == st.secrets["LOGIN_PASSWORD"]:
        st.session_state.authenticated = True
        st.session_state.page = "dashboard"
        st.session_state.user_tier = "Admin" # Ты как создатель всегда Admin
    elif u == "guest" and p == "luvvu2026":
        st.session_state.authenticated = True
        st.session_state.page = "dashboard"
        st.session_state.user_tier = "Free"
    else:
        st.error("Доступ запрещен. Проверьте ID.")

# --- ЭКРАН 1: ВХОД (CLEAN ENTRANCE) ---
if not st.session_state.authenticated:
    st.markdown("<div style='height: 15vh'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.title("luvvu.")
        st.caption("Ecosystem for human & business growth")
        st.text_input("System ID", key="u_input")
        st.text_input("Security Key", type="password", key="p_input")
        st.button("AUTHENTICATE", on_click=login, use_container_width=True)
        st.markdown("<center style='color: #888; font-size: 0.8em;'>Version 3.0 Build 2026</center>", unsafe_allow_html=True)
    st.stop()

# --- ЭКРАН 2: ЦЕНТРАЛЬНЫЙ ХАБ (DASHBOARD) ---
if st.session_state.page == "dashboard":
    st.title(f"Luvvu Hub")
    st.write(f"Уровень доступа: **{st.session_state.user_tier}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="module-card">
            <h3>❤️ Luvvu Personal</h3>
            <p>Моральная поддержка и психологический спутник. Анализ эмоций и мотивация.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Запустить Спутника", use_container_width=True):
            st.session_state.page = "chat_personal"
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="module-card">
            <h3>🤝 Luvvu Networking</h3>
            <p>Поиск идеальных друзей и партнеров на основе ваших ценностей.</p>
            <small class="status-vip">Требуется VIP подписка</small>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.user_tier in ["VIP", "Admin"]:
            if st.button("Найти людей", use_container_width=True):
                st.session_state.page = "networking"
                st.rerun()
        else:
            st.button("Активировать VIP", disabled=True, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="module-card">
            <h3>💼 Luvvu Business</h3>
            <p>Ваш цифровой подчиненный. Аналитика, идеи, рутина. Строго на "Вы".</p>
            <small class="status-corp">Корпоративный доступ</small>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.user_tier in ["Corporate", "Admin"]:
            if st.button("Открыть Бизнес-модуль", use_container_width=True):
                st.session_state.page = "chat_business"
                st.rerun()
        else:
            st.button("Связаться по подписке ($100k+)", disabled=True, use_container_width=True)

    st.write("---")
    if st.button("Выход из системы"):
        st.session_state.authenticated = False
        st.rerun()

# --- ЭКРАН 3: ЧАТ PERSONAL (Спутник) ---
elif st.session_state.page == "chat_personal":
    if st.button("← Вернуться в Хаб"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    st.title("Luvvu / Companion")
    
    if "messages_p" not in st.session_state:
        st.session_state.messages_p = []

    for m in st.session_state.messages_p:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("О чем ты думаешь?")
    if prompt:
        st.session_state.messages_p.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # ЛОГИКА СПУТНИКА
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        L_PROMPT = "Ты — Luvvu, эмпатичный спутник. Ты анализируешь боли и радости. Твоя цель — помочь человеку расти. Ты не бот, ты — поддержка."
        
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": L_PROMPT}] + st.session_state.messages_p
        )
        reply = resp.choices[0].message.content
        with st.chat_message("assistant"): st.markdown(reply)
        st.session_state.messages_p.append({"role": "assistant", "content": reply})

# --- ЭКРАН 4: ЧАТ BUSINESS (Подчиненный) ---
elif st.session_state.page == "chat_business":
    if st.button("← Вернуться в Хаб"):
        st.session_state.page = "dashboard"
        st.rerun()
        
    st.title("Luvvu / Business Consultant")
    st.info("Режим: Корпоративный помощник. Тон: Профессиональный.")

    if "messages_b" not in st.session_state:
        st.session_state.messages_b = []

    for m in st.session_state.messages_b:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Поставьте задачу...")
    if prompt:
        st.session_state.messages_b.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # Тот самый промпт: на ВЫ, подчиненный, не дает готовых идей, но улучшает
        B_PROMPT = """
        Вы — бизнес-ассистент Luvvu. Обращайтесь к пользователю строго на 'Вы'. 
        Вы эксперт в экономике, бухгалтерии и стратегии. 
        ЗАПРЕТ: Вам нельзя предлагать готовые идеи 'под ключ'. 
        ВАША РОЛЬ: Критиковать, улучшать идеи пользователя, делать расчеты и помогать с рутиной.
        """
        
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": B_PROMPT}] + st.session_state.messages_b
        )
        reply = resp.choices[0].message.content
        with st.chat_message("assistant"): st.markdown(reply)
        st.session_state.messages_b.append({"role": "assistant", "content": reply})
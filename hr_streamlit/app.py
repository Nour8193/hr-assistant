import streamlit as st
import requests
import uuid
import time

# ─── Конфигурация страницы ───────────────────────────────────────────────────
st.set_page_config(
    page_title="HR-ассистент | Технологии ООО",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Стили ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Скрыть стандартный header Streamlit */
  header[data-testid="stHeader"] { display: none; }
  .block-container { padding-top: 1.5rem; max-width: 720px; }

  /* Шапка ассистента */
  .bot-header {
    display: flex; align-items: center; gap: 14px;
    padding: 16px 20px; background: #1a1d27;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; margin-bottom: 1.2rem;
  }
  .bot-avatar {
    width: 48px; height: 48px; border-radius: 50%;
    background: linear-gradient(135deg, #21a038, #2ecc5a);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
    box-shadow: 0 0 0 3px rgba(33,160,56,0.2);
  }
  .bot-name { font-size: 16px; font-weight: 700; color: #e8eaf6; margin: 0; }
  .bot-sub  { font-size: 12px; color: #7b80a0; margin: 3px 0 0; }
  .bot-badge {
    margin-left: auto; display: flex; align-items: center; gap: 6px;
    font-size: 12px; color: #34d399;
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.2);
    padding: 5px 12px; border-radius: 20px;
  }
  .dot { width: 7px; height: 7px; border-radius: 50%;
         background: #21a038; display: inline-block; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

  /* Быстрые вопросы */
  .chip-label { font-size: 12px; color: #7b80a0; margin-bottom: 8px; }

  /* Промпт */
  .sys-box {
    background: #1a1d27; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 12px 16px;
    font-size: 12px; color: #7b80a0; line-height: 1.7;
    font-family: monospace; white-space: pre-wrap; margin-top: 8px;
  }
</style>
""", unsafe_allow_html=True)

# ─── Системный промпт ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Ты — HR-ассистент компании «Технологии ООО».

БАЗА ЗНАНИЙ:

=== НАЙМ И ОНБОРДИНГ ===
Процесс найма: публикация вакансии → скрининг резюме (3 дня) → телефонное интервью с HR (20-30 мин) → техническое интервью (1-1.5ч) → финальное интервью с директором → проверка рекомендаций → оффер.
Онбординг 90 дней: 1-30 день — адаптация (документы, знакомство, регламенты); 31-60 день — погружение (задачи, обучение, 1:1); 61-90 день — интеграция (самостоятельная работа, годовые цели).
Документы при приёме: паспорт, ИНН, СНИЛС, трудовая книжка, образование, военный билет.

=== ОПЛАТА И ЛЬГОТЫ ===
Оклад: 2 раза в месяц (15-го и последнего числа). KPI-бонус: квартальный до 20%. Индексация: не менее 5%/год.
Льготы: ДМС с первого дня; питание 500 руб/день; обучение до 50 000 руб/год (после 6 мес); фитнес 50%; удалёнка 3 дня из 5.
Отпуск: 28 дней + 3 дня (после 3 лет) + 5 дней (после 5 лет). Больничный: первые 3 дня за счёт работодателя.

=== ОБУЧЕНИЕ ===
Форматы: вебинары еженедельно, внешние курсы по согласованию, менторинг первые 3 мес, библиотека @tech_library.
Оценка дважды в год (март/сентябрь): self-review + 360° + 1:1 + ИПР.
Карьерный трек: Специалист → Старший → Ведущий → Руководитель группы → Руководитель отдела.

=== КУЛЬТУРА И ГРАФИК ===
График: 9:00-18:00 МСК ±2 часа. Пятница без совещаний. Переработки компенсируются.
Инструменты: Telegram, Jira/Notion, Яндекс Телемост.

=== УВОЛЬНЕНИЕ ===
Заявление за 2 недели → передача задач → exit-interview → сдача оборудования → расчёт в последний день.

=== КОНТАКТЫ HR ===
Анна Соколова — найм: @anna_hr | Дмитрий Лебедев — льготы: @dmitry_hr | Мария Иванова — обучение: @maria_hr | Helpdesk: @hr_help

Правило: отвечай только по базе знаний. Если не знаешь — направь в HR. Отвечай на русском языке."""

# ─── GigaChat API ─────────────────────────────────────────────────────────────
def get_access_token(auth_key: str) -> str | None:
    try:
        resp = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4()),
                "Authorization": f"Basic {auth_key}",
            },
            data={"scope": "GIGACHAT_API_PERS"},
            verify=False,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except Exception:
        return None


def chat_gigachat(token: str, messages: list) -> str:
    try:
        payload = {
            "model": "GigaChat-2",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "max_tokens": 1000,
            "temperature": 0.7,
        }
        resp = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json=payload,
            verify=False,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка запроса к GigaChat: {e}"


# ─── Состояние сессии ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "token_time" not in st.session_state:
    st.session_state.token_time = 0
if "connected" not in st.session_state:
    st.session_state.connected = False

# ─── Шапка ───────────────────────────────────────────────────────────────────
status_label = "GigaChat подключён" if st.session_state.connected else "Не подключён"
st.markdown(f"""
<div class="bot-header">
  <div class="bot-avatar">🤖</div>
  <div>
    <p class="bot-name">HR-ассистент</p>
    <p class="bot-sub">Технологии ООО · На базе GigaChat от Сбера</p>
  </div>
  <div class="bot-badge"><span class="dot"></span>{status_label}</div>
</div>
""", unsafe_allow_html=True)

# ─── Боковая панель: ключ + инструкция ───────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Подключение GigaChat")
    st.markdown("""
**Как получить бесплатный ключ:**
1. Зайдите на [giga.chat](https://giga.chat) → войдите через Сбер ID (номер телефона)
2. Профиль → **GigaChat API**
3. [developers.sber.ru/studio](https://developers.sber.ru/studio) → **Создать проект**
4. Скопируйте **«Ключ авторизации»** (длинная строка base64)
5. Вставьте ниже ↓
""")

    auth_key = st.text_input(
        "Ключ авторизации (Base64)",
        type="password",
        placeholder="Вставьте ключ...",
        key="auth_key_input"
    )

    if st.button("🔌 Подключить", use_container_width=True):
        with st.spinner("Проверяем ключ..."):
            token = get_access_token(auth_key)
            if token:
                st.session_state.access_token = token
                st.session_state.token_time = time.time()
                st.session_state.connected = True
                st.success("✅ Подключено успешно!")
                st.rerun()
            else:
                st.error("❌ Неверный ключ или ошибка соединения")

    st.divider()
    st.markdown("### 📋 Системный промпт")
    with st.expander("Показать промпт"):
        st.markdown(f'<div class="sys-box">{SYSTEM_PROMPT}</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("🗑 Очистить чат", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─── Быстрые вопросы ──────────────────────────────────────────────────────────
quick = [
    ("📅 Отпуск", "Какой у нас размер отпуска?"),
    ("👋 Онбординг", "Расскажи про онбординг новых сотрудников"),
    ("🎁 Льготы", "Какие льготы есть в компании?"),
    ("📊 Оценка", "Как проходит оценка сотрудников?"),
    ("🚪 Увольнение", "Как уволиться из компании?"),
    ("📚 Обучение", "Кто отвечает за обучение в HR?"),
    ("🕘 График", "Какой у нас рабочий график?"),
]

st.markdown('<div class="chip-label">Быстрые вопросы:</div>', unsafe_allow_html=True)
cols = st.columns(4)
for i, (label, question) in enumerate(quick):
    if cols[i % 4].button(label, key=f"chip_{i}", use_container_width=True):
        if not st.session_state.connected:
            st.warning("Сначала введите ключ авторизации в боковой панели →")
        else:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("GigaChat думает..."):
                reply = chat_gigachat(st.session_state.access_token, st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

st.divider()

# ─── История чата ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.info("👋 Привет! Я HR-ассистент компании Технологии ООО.\n\nВведите ключ GigaChat в боковой панели (→) и задайте вопрос.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

# ─── Поле ввода ───────────────────────────────────────────────────────────────
if prompt := st.chat_input("Задайте вопрос об HR..."):
    if not st.session_state.connected:
        st.warning("⚠️ Сначала введите ключ авторизации GigaChat в боковой панели →")
    else:
        # Обновляем токен если истёк (30 мин)
        if time.time() - st.session_state.token_time > 1700:
            token = get_access_token(st.session_state.get("auth_key_input", ""))
            if token:
                st.session_state.access_token = token
                st.session_state.token_time = time.time()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("GigaChat думает..."):
                reply = chat_gigachat(st.session_state.access_token, st.session_state.messages)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

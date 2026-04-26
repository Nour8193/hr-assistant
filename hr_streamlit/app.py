import streamlit as st
import requests
import uuid
import time

st.set_page_config(
    page_title="HR-ассистент | Технологии ООО",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  [data-testid="stSidebar"] { display: none; }
  [data-testid="collapsedControl"] { display: none; }
  header[data-testid="stHeader"] { display: none; }
  .block-container { padding-top: 1.5rem; max-width: 720px; }
  .sys-box {
    background: #f8f9fa; border: 1px solid #dee2e6;
    border-radius: 10px; padding: 12px 16px;
    font-size: 12px; color: #6c757d; line-height: 1.7;
    font-family: monospace; white-space: pre-wrap;
  }
</style>
""", unsafe_allow_html=True)

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

# ─── GigaChat ────────────────────────────────────────────────────────────────
def get_access_token(auth_key: str):
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
        resp = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={
                "model": "GigaChat-2",
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                "max_tokens": 1000,
                "temperature": 0.7,
            },
            verify=False,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка запроса к GigaChat: {e}"

# ─── Получаем ключ из Secrets (один раз при запуске) ─────────────────────────
AUTH_KEY = st.secrets.get("GIGACHAT_KEY", "")

# ─── Состояние сессии ────────────────────────────────────────────────────────
for k, v in [("messages", []), ("access_token", None), ("token_time", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# Получаем токен если его нет или истёк
def ensure_token():
    if not st.session_state.access_token or time.time() - st.session_state.token_time > 1700:
        token = get_access_token(AUTH_KEY)
        if token:
            st.session_state.access_token = token
            st.session_state.token_time = time.time()
    return st.session_state.access_token

# ─── Шапка ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;padding:16px 20px;
  background:#1a1d27;border-radius:14px;margin-bottom:1.2rem">
  <div style="width:48px;height:48px;border-radius:50%;
    background:linear-gradient(135deg,#21a038,#2ecc5a);
    display:flex;align-items:center;justify-content:center;font-size:22px">🤖</div>
  <div>
    <div style="font-size:16px;font-weight:700;color:#e8eaf6">HR-ассистент</div>
    <div style="font-size:12px;color:#7b80a0;margin-top:2px">Технологии ООО · GigaChat от Сбера</div>
  </div>
  <div style="margin-left:auto;padding:5px 14px;border-radius:20px;font-size:12px;
    color:#21a038;border:1px solid #21a03833">
    ● Онлайн
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Быстрые вопросы ─────────────────────────────────────────────────────────
quick = [
    ("📅 Отпуск",     "Какой у нас размер отпуска?"),
    ("👋 Онбординг",  "Расскажи про онбординг новых сотрудников"),
    ("🎁 Льготы",     "Какие льготы есть в компании?"),
    ("📊 Оценка",     "Как проходит оценка сотрудников?"),
    ("🚪 Увольнение", "Как уволиться из компании?"),
    ("📚 Обучение",   "Кто отвечает за обучение в HR?"),
    ("🕘 График",     "Какой у нас рабочий график?"),
    ("📞 Контакты",   "Как связаться с HR-отделом?"),
]

st.markdown('<p style="font-size:12px;color:#888;margin-bottom:4px">Быстрые вопросы:</p>', unsafe_allow_html=True)
row1 = st.columns(4)
row2 = st.columns(4)
for i, (label, question) in enumerate(quick):
    col = row1[i] if i < 4 else row2[i - 4]
    if col.button(label, key=f"q{i}", use_container_width=True):
        token = ensure_token()
        if token:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("GigaChat думает..."):
                reply = chat_gigachat(token, st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.error("Ошибка подключения к GigaChat. Проверьте ключ в Secrets.")

st.divider()

# ─── История чата ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.info("👋 Привет! Я HR-ассистент компании Технологии ООО.\n\nЗадайте вопрос — или нажмите одну из кнопок выше.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
    if st.button("🗑 Очистить чат", key="clear"):
        st.session_state.messages = []
        st.rerun()

# ─── Поле ввода ──────────────────────────────────────────────────────────────
if prompt := st.chat_input("Задайте вопрос об HR..."):
    token = ensure_token()
    if not token:
        st.error("Ошибка подключения к GigaChat. Проверьте ключ в Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("GigaChat думает..."):
                reply = chat_gigachat(token, st.session_state.messages)
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ─── Системный промпт (скрыт) ────────────────────────────────────────────────
with st.expander("⚙️ Системный промпт"):
    st.markdown(f'<div class="sys-box">{SYSTEM_PROMPT}</div>', unsafe_allow_html=True)

import streamlit as st
import requests

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


def chat_gemini(messages: list) -> str:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return "❌ Ключ GEMINI_API_KEY не найден в Secrets."

    # Форматируем историю для Gemini
    gemini_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_messages.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                },
                "contents": gemini_messages,
                "generationConfig": {
                    "maxOutputTokens": 1000,
                    "temperature": 0.7,
                }
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 429:
            return "⚠️ Превышен лимит запросов Gemini (бесплатный тариф). Подождите минуту и попробуйте снова."
        return f"Ошибка HTTP {resp.status_code}: {e}"
    except Exception as e:
        return f"Ошибка: {e}"


# ─── Состояние ───────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Шапка ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;padding:16px 20px;
  background:#1a1d27;border-radius:14px;margin-bottom:1.2rem">
  <div style="width:48px;height:48px;border-radius:50%;
    background:linear-gradient(135deg,#4285F4,#34A853);
    display:flex;align-items:center;justify-content:center;font-size:22px">🤖</div>
  <div>
    <div style="font-size:16px;font-weight:700;color:#e8eaf6">HR-ассистент</div>
    <div style="font-size:12px;color:#7b80a0;margin-top:2px">Технологии ООО · на базе Google Gemini</div>
  </div>
  <div style="margin-left:auto;padding:5px 14px;border-radius:20px;font-size:12px;
    color:#34d399;border:1px solid #34d39933">
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
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Gemini думает..."):
            reply = chat_gemini(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

st.divider()

# ─── История чата ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.info("👋 Привет! Я HR-ассистент компании Технологии ООО.\n\nЗадайте вопрос или нажмите одну из кнопок выше.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
    if st.button("🗑 Очистить чат", key="clear"):
        st.session_state.messages = []
        st.rerun()

# ─── Поле ввода ──────────────────────────────────────────────────────────────
if prompt := st.chat_input("Задайте вопрос об HR..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Gemini думает..."):
            reply = chat_gemini(st.session_state.messages)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ─── Системный промпт ────────────────────────────────────────────────────────
with st.expander("⚙️ Системный промпт"):
    st.markdown(f'<div class="sys-box">{SYSTEM_PROMPT}</div>', unsafe_allow_html=True)

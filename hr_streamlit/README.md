# HR-ассистент на GigaChat + Streamlit

ИИ-ассистент по управлению персоналом компании «Технологии ООО».  
Работает на GigaChat от Сбера — бесплатно, без VPN, на русском языке.

---

## 🚀 Деплой на Streamlit Cloud (бесплатно)

### Шаг 1 — Загрузить на GitHub
1. Зайдите на [github.com](https://github.com) → **New repository**
2. Название: `hr-assistant`
3. Нажмите **Create repository**
4. Загрузите оба файла: `app.py` и `requirements.txt`

### Шаг 2 — Деплой на Streamlit
1. Зайдите на [share.streamlit.io](https://share.streamlit.io)
2. Войдите через GitHub
3. Нажмите **New app**
4. Выберите репозиторий `hr-assistant`, файл `app.py`
5. Нажмите **Deploy** → через 1-2 минуты получите ссылку вида:  
   `https://ваш-логин-hr-assistant.streamlit.app`

### Шаг 3 — Добавить ключ GigaChat как секрет (опционально)
Чтобы не вводить ключ каждый раз:
1. В Streamlit Cloud → настройки приложения → **Secrets**
2. Добавьте:
```
GIGACHAT_KEY = "ваш_ключ_base64"
```

---

## 🔑 Как получить бесплатный ключ GigaChat

1. Зайдите на [giga.chat](https://giga.chat) → войдите по номеру телефона
2. Профиль → **GigaChat API** → [developers.sber.ru/studio](https://developers.sber.ru/studio)
3. **Создать проект** → скопируйте **«Ключ авторизации»**
4. Вставьте в боковую панель приложения

---

## 📁 Структура проекта

```
hr-assistant/
├── app.py            # Основной файл приложения
├── requirements.txt  # Зависимости Python
└── README.md         # Инструкция
```

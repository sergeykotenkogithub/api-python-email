# 🚀 Developer Portfolio Landing Page Backend

Полноценный backend-сервис для лендинг-презентации разработчика с REST API и интеграцией AI-инструментов.

## 📋 Содержание
- [Как запустить проект](#как-запустить-проект)
- [Стек технологий](#стек-технологий)
- [Архитектура](#архитектура)
- [Реализация API](#реализация-api)
- [AI-интеграция](#ai-интеграция)
- [Хранение данных](#хранение-данных)
- [Что сделано с помощью AI](#что-сделано-с-помощью-ai)

---

## 🚀 Как запустить проект

### Предварительные требования
- Python 3.9+
- pip или poetry
- OpenAI API ключ (или другой AI-провайдер)

### Установка и запуск

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd developer-portfolio-backend
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив свои значения
```

5. **Запустите сервер:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Проверьте работу:**
- API будет доступен по адресу: http://localhost:8000
- Swagger документация: http://localhost:8000/docs
- ReDoc документация: http://localhost:8000/redoc

### Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```env
# Приложение
APP_NAME=Developer Portfolio API
APP_VERSION=1.0.0
DEBUG=True

# Сервер
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Email настройки
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=owner@example.com

# AI настройки
AI_PROVIDER=openai  # openai, anthropic, local
OPENAI_API_KEY=your-openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Rate Limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=3600  # в секундах (1 час)

# Хранение данных
DATA_DIR=./data
LOGS_DIR=./logs
```

---

## 🛠 Стек технологий

### Backend
- **Python 3.9+** - основной язык программирования
- **FastAPI** - современный веб-фреймворк для создания API
- **Pydantic** - валидация и сериализация данных
- **Uvicorn** - ASGI сервер
- **Python-JOSE** - работа с JWT токенами
- **Passlib** - хеширование паролей

### AI интеграция
- **OpenAI API** - анализ тональности, генерация ответов
- **LangChain** - работа с LLM моделями
- **Fallback механизмы** - при недоступности AI

### Дополнительно
- **Aiosmtplib** - асинхронная отправка email
- **Aiofiles** - асинхронная работа с файлами
- **Python-dotenv** - работа с переменными окружения
- **Loguru** - логирование

---

## 🏗 Архитектура

### Структура проекта

```
app/
├── main.py                 # Точка входа, создание приложения
├── config.py               # Конфигурация приложения
├── models/                 # Pydantic модели
│   ├── contact.py          # Модели контактной формы
│   └── responses.py        # Модели ответов API
├── api/                    # API роуты
│   ├── routes/
│   │   ├── contact.py      # Эндпоинты контактов
│   │   └── health.py       # Health check и метрики
│   └── deps.py             # Зависимости
├── services/               # Бизнес-логика
│   ├── contact_service.py  # Логика обработки контактов
│   ├── email_service.py    # Отправка email
│   └── ai_service.py       # AI интеграция
├── repositories/           # Работа с данными
│   ├── file_repository.py  # Файловое хранилище
│   └── rate_limiter.py     # Rate limiting
├── utils/                  # Утилиты
│   ├── logger.py           # Настройка логирования
│   └── validators.py       # Валидаторы
├── middleware/              # Middleware
│   ├── error_handler.py    # Обработка ошибок
│   └── rate_limit.py       # Rate limiting middleware
└── data/                   # Данные (создается автоматически)
    ├── logs/               # Логи запросов
    ├── stats/              # Статистика
    └── rate_limits/        # Данные rate limiting
```

### Паттерны проектирования

1. **Layered Architecture** (Слоистая архитектура):
   - **API Layer** (Routes) → Обработка HTTP запросов
   - **Service Layer** → Бизнес-логика
   - **Repository Layer** → Работа с данными

2. **Dependency Injection**:
   - Использование FastAPI Depends для внедрения зависимостей
   - Легкое тестирование и замена компонентов

3. **Repository Pattern**:
   - Абстракция работы с данными
   - Возможность легко переключиться на БД

4. **Service Layer Pattern**:
   - Инкапсуляция бизнес-логики
   - Переиспользование кода

### Обоснование выбора технологий

- **FastAPI**: Высокая производительность, автоматическая документация, типизация
- **Pydantic**: Надежная валидация данных, интеграция с FastAPI
- **OpenAI API**: Надежный AI-провайдер с хорошей документацией
- **Асинхронность**: Высокая производительность при I/O операциях

---

## 🔌 Реализация API

### Эндпоинты

#### POST /api/contact
Обработка контактной формы.

**Запрос:**
```json
{
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "phone": "+7 (999) 123-45-67",
  "comment": "Хочу обсудить проект"
}
```

**Ответ (200 OK):**
```json
{
  "success": true,
  "message": "Ваше сообщение успешно отправлено",
  "data": {
    "id": "uuid-string",
    "timestamp": "2024-01-15T10:30:00Z",
    "ai_analysis": {
      "sentiment": "positive",
      "category": "project_inquiry",
      "priority": "medium",
      "suggested_response": "Спасибо за ваш интерес! Я свяжусь с вами в ближайшее время."
    }
  }
}
```

**Ошибка валидации (422 Unprocessable Entity):**
```json
{
  "success": false,
  "error": "Validation Error",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

#### GET /api/health
Проверка статуса сервиса.

**Ответ:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "api": "up",
    "ai": "up",
    "email": "up"
  }
}
```

#### GET /api/metrics
Статистика обращений.

**Ответ:**
```json
{
  "total_requests": 150,
  "successful_requests": 142,
  "failed_requests": 8,
  "requests_today": 12,
  "average_response_time_ms": 245,
  "top_categories": [
    {"category": "project_inquiry", "count": 45},
    {"category": "collaboration", "count": 32}
  ],
  "sentiment_distribution": {
    "positive": 89,
    "neutral": 45,
    "negative": 16
  }
}
```

### Валидация и обработка ошибок

- **Pydantic валидация**: Автоматическая валидация входных данных
- **Кастомные валидаторы**: Проверка формата телефона, email
- **Глобальный error handler**: Единый формат ошибок
- **HTTP статус-коды**: Корректные коды ответов

---

## 🤖 AI-интеграция

### Реализованные AI-функции

1. **Анализ тональности комментария**
   - Определение позитивной/негативной/нейтральной тональности
   - Оценка эмоциональной окраски сообщения

2. **Классификация типов запросов**
   - Автоматическое определение категории обращения
   - Приоритизация запросов

3. **Генерация ответов**
   - Автоматическая генерация персонализированных ответов
   - Учет контекста и тональности

### Используемые промпты

#### Анализ тональности
```
Analyze the sentiment of the following message. 
Respond with only one word: positive, negative, or neutral.

Message: {user_message}
```

#### Классификация запроса
```
Classify this message into one of the following categories:
- project_inquiry (вопрос о проекте)
- collaboration (предложение о сотрудничестве)
- job_offer (предложение работы)
- general_question (общий вопрос)
- feedback (отзыв)
- other (другое)

Message: {user_message}

Respond with only the category name.
```

#### Генерация ответа
```
Generate a professional response to this message from a potential client.
The response should be:
- Polite and professional
- Personalized based on the message content
- Brief (2-3 sentences)
- Include a call to action

Original message: {user_message}
Sender name: {sender_name}
```

### Fallback механизмы

При недоступности AI-сервиса:
1. Используются предопределенные шаблоны ответов
2. Базовая классификация на основе ключевых слов
3. Нейтральная тональность по умолчанию
4. Логирование ошибок AI для мониторинга

---

## 💾 Хранение данных

### Логирование
- **Формат**: JSON файлы
- **Ротация**: Ежедневная
- **Структура**: `logs/YYYY-MM-DD.log`
- **Содержание**: Все запросы, ответы, ошибки

### Rate Limiting
- **Хранение**: JSON файлы
- **Алгоритм**: Sliding window
- **Структура**: `rate_limits/{ip_address}.json`
- **Очистка**: Автоматическая по истечении окна

### Статистика
- **Хранение**: JSON файлы
- **Обновление**: При каждом запросе
- **Структура**: `stats/metrics.json`
- **Бэкапы**: Еженедельные

---

## 🎯 Что сделано с помощью AI

### Сгенерированный код

1. **Базовая структура FastAPI приложения**
   - Промпт: "Create a FastAPI application structure with proper error handling and logging"
   - Результат: Основной каркас приложения

2. **AI сервис с OpenAI интеграцией**
   - Промпт: "Implement an AI service with OpenAI API for sentiment analysis and response generation"
   - Результат: Полноценный AI сервис с fallback

3. **Rate limiting middleware**
   - Промпт: "Create a rate limiting middleware using file-based storage"
   - Результат: Рабочий rate limiter

### Использованные промпты

- "Design a layered architecture for a contact form API"
- "Implement proper error handling for email sending"
- "Create comprehensive API documentation with examples"
- "Generate test cases for the contact form endpoint"

### Что исправлялось вручную

1. **Оптимизация промптов**: Уточнение для более точных результатов
2. **Обработка ошибок**: Добавление специфичных для домена ошибок
3. **Валидация**: Настройка правил под конкретные требования
4. **Тестирование**: Исправление edge cases

---

## 📝 Примеры запросов

### cURL

```bash
# Отправка контактной формы
curl -X POST "http://localhost:8000/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "phone": "+7 (999) 123-45-67",
    "comment": "Хочу обсудить разработку веб-приложения"
  }'

# Проверка здоровья
curl "http://localhost:8000/api/health"

# Получение метрик
curl "http://localhost:8000/api/metrics"
```

### Python (requests)

```python
import requests

# Отправка формы
response = requests.post(
    "http://localhost:8000/api/contact",
    json={
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "phone": "+7 (999) 123-45-67",
        "comment": "Интересует ваш опыт в бэкенд разработке"
    }
)
print(response.json())
```

---

## 🔧 Команды для разработки

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск в режиме разработки
uvicorn app.main:app --reload

# Запуск тестов
pytest tests/ -v

# Проверка качества кода
black app/
flake8 app/
mypy app/

# Генерация документации
python generate_docs.py
```

---

## 📊 Мониторинг и метрики

- **Health Check**: `/api/health`
- **Метрики**: `/api/metrics`
- **Логи**: `./logs/` директория
- **Статистика**: Обновляется в реальном времени

---

## 🔒 Безопасность

- **Валидация входных данных**: Pydantic модели
- **Rate Limiting**: Защита от спама
- **CORS**: Настроенные политики
- **Санитизация**: Очистка пользовательского ввода
- **Environment Variables**: Безопасное хранение секретов

---

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:
1. Проверьте документацию API: `/docs`
2. Изучите логи: `./logs/`
3. Создайте issue в репозитории

---
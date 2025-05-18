# Telegram Bot для общежития

Telegram бот для помощи студентам с информацией о заселении, переселении и расписании автобусов.

## Функциональность

- **Заселение**: Проверка статуса заселения пользователя
- **Переселение**: Проверка статуса заявки на переселение
- **Расписание автобусов**: Получение актуального расписания автобусов
- **Нейровопрос**: Возможность задать вопросы по заселению и получить ответы от нейросети
- **API для уведомлений**: Возможность отправки уведомлений пользователям через API

## Технологии

- Python 3.9
- FastAPI
- pyTelegramBotAPI
- Docker

## Структура проекта

```
.
├── app/
│   ├── api/              # API эндпоинты
│   ├── bot/              # Функциональность Telegram бота
│   ├── services/         # Сервисы для работы с внешними API
│   └── utils/            # Вспомогательные функции
├── .env                  # Файл с переменными окружения
├── Dockerfile            # Файл для сборки Docker образа
├── main.py               # Точка входа в приложение
└── requirements.txt      # Зависимости проекта
```

## Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Directus Configuration
DIRECTUS_URL=your_directus_url_here
DIRECTUS_TOKEN=your_directus_token_here

# Web Application Configuration
WEB_APP_URL=your_web_app_url_here

# LLM RAG API Configuration
LLM_RAG_API_URL=your_llm_rag_api_url_here
LLM_RAG_API_TOKEN=your_llm_rag_api_token_here
```

## Запуск локально

1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

2. Запустите приложение:
   ```
   python main.py
   ```

## Запуск с Docker

1. Соберите Docker образ:
   ```
   docker build -t telegram-bot .
   ```

2. Запустите контейнер:
   ```
   docker run -p 8000:8000 --env-file .env telegram-bot
   ```

## Нейровопрос

Функциональность "Нейровопрос" позволяет пользователям задавать вопросы по заселению в общежитие и получать ответы от нейросети:

1. Пользователь нажимает кнопку "Нейровопрос"
2. Бот показывает описание функциональности и кнопку "Начать"
3. После нажатия на кнопку "Начать", пользователь может задавать вопросы
4. Бот отправляет вопросы в LLM RAG API и показывает ответы пользователю
5. Пользователь может завершить разговор, нажав на кнопку "Завершить разговор"

Для работы этой функциональности необходимо настроить переменные окружения `LLM_RAG_API_URL` и `LLM_RAG_API_TOKEN`.

## API для уведомлений

Бот предоставляет API для отправки уведомлений пользователям:

### Отправка уведомления

**Endpoint**: `POST /api/notify`

**Тело запроса**:
```json
{
  "user_id": 123456789,
  "notification_type": "checkin",
  "message": "Ваша заявка на заселение одобрена",
  "status": "Одобрено"
}
```

**Параметры**:
- `user_id`: ID пользователя в Telegram
- `notification_type`: Тип уведомления (checkin, relocation, general)
- `message`: Текст уведомления
- `status`: Статус (опционально)

**Ответ**:
```json
{
  "status": "success",
  "message": "Notification sent successfully"
}
```

# Media Processing Service

Асинхронный backend-сервис для загрузки и обработки изображений и видео.
Проект реализует полный пайплайн обработки медиафайлов с использованием очередей,
object storage и транзакционной базы данных.

Проект является учебным (pet project).

---

## Возможности

- Загрузка изображений и видео
- Асинхронная обработка файлов
- Presets для изображений (несколько размеров)
- Извлечение poster и metadata из видео
- Idempotency (один и тот же файл + preset → один job)
- Retry с лимитами и backoff
- Webhooks по завершению обработки
- Presigned URLs для доступа к результатам
- Object storage (S3-compatible, MinIO)
- Docker-based окружение

---

## Архитектура

### Основные компоненты

- **Django + DRF** — REST API
- **Celery** — асинхронные фоновые задачи
- **RabbitMQ** — брокер сообщений
- **PostgreSQL** — основная база данных
- **MinIO** — S3-compatible object storage
- **Docker / docker-compose** — локальная инфраструктура

### Общий поток обработки

1. Клиент загружает файл через API
2. Django:
   - валидирует запрос
   - вычисляет hash файла
   - проверяет idempotency
   - создаёт `MediaJob`
3. Задача отправляется в очередь Celery
4. Worker:
   - определяет тип медиа (image / video)
   - обрабатывает файл согласно preset
   - сохраняет результаты в MinIO
   - обновляет статус job
   - отправляет webhook (если задан)
5. Клиент опрашивает статус или получает webhook

---

## Модель данных

### MediaJob

- `id` — UUID
- `original_file` — путь к исходному файлу в storage
- `file_name`
- `content_type`
- `size`
- `preset`
- `file_hash` — используется для idempotency
- `status` — queued / processing / done / failed
- `attempts`
- `result` — JSON с результатами обработки
- `error`
- `callback_url`
- `created_at`, `updated_at`

---

## Idempotency

Сервис реализует идемпотентность на уровне базы данных:

- Вычисляется hash загружаемого файла
- Уникальная комбинация: `(file_hash, preset)`
- Повторная загрузка того же файла с тем же preset
  вернёт уже существующий job

---

## Обработка изображений

- Используется Pillow
- Presets задаются конфигурацией
- Для каждого preset создаются несколько вариантов (thumb, medium, large)
- Результаты сохраняются в object storage

---

## Обработка видео

- Используется ffmpeg
- Извлекается poster (кадр на заданной секунде)
- Извлекаются метаданные:
  - ширина
  - высота
  - длительность
  - кодек
- Результаты сохраняются в object storage

---

## Webhooks

Если в запросе передан `callback_url`, сервис отправляет POST-запрос
после завершения обработки.

Пример payload:

```json
{
  "job_id": "uuid",
  "status": "done",
  "result": {
    "poster": "thumbnails/...",
    "width": 848,
    "height": 480,
    "codec": "h264",
    "duration": 9.26
  },
  "error": null
}
```

---

## API

### Загрузка файла

### POST /api/media/
Загружает файл и инициирует асинхронную обработку.

#### Form-data

| Поле          | Тип     | Обязательное | Описание |
|---------------|---------|--------------|----------|
| `file`        | file    | да           | Файл изображения или видео |
| `preset`      | string  | да           | Имя preset для обработки |
| `callback_url`| string  | нет          | URL для webhook-уведомления |

#### Пример запроса

```bash
curl -X POST http://localhost:8000/api/media/ \
  -F "file=@image.jpg" \
  -F "preset=default" \
  -F "callback_url=https://example.com/webhook"
```

Ответ
```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

Получение статуса обработки
```
GET /api/media/{job_id}/
```
##### Возвращает текущий статус задачи и результаты обработки (если они готовы).

Пример ответа
```json
{
  "id": "uuid",
  "status": "done",
  "result_urls": {
    "thumb": "https://..."
  },
  "result": {
    "width": 848,
    "height": 480,
    "codec": "h264",
    "duration": 9.26
  },
  "error": null
}
```

Повторная обработка
```
POST /api/media/{job_id}/retry/
```
##### Сбрасывает статус задачи и повторно отправляет её в очередь обработки (с учётом лимита попыток).

Ответ
```json
{
  "job_id": "uuid",
  "status": "queued",
  "attempts": 2
}
```

---

## Запуск проекта
### Требования

- Docker
- Docker Compose

### Запуск
```
docker compose up -d
```

### Применение миграций
```
docker compose exec web python manage.py migrate
```

---

## Ограничения

- Отсутствует авторизация пользователей
- Нет пользовательского интерфейса (UI)
- Нет транскодинга видео (только poster + metadata)
- Нет мониторинга и алертинга
- Не реализована проверка подписи webhook

---

## Назначение проекта

### Проект создан для практического изучения и отработки следующих тем:

- асинхронная обработка задач
- работа с object storage (S3-совместимые хранилища)
- проектирование REST API
- обеспечение идемпотентности
- построение backend-сервисов для обработки медиа

# That Sound API

**English** | [Русский](#русский)

---

## English

### Overview

That Sound API is a RESTful microservice designed to aggregate and manage music listening data from multiple streaming platforms. The service integrates with Spotify and Yandex Music to track user listening history, handle scrobbling (tracking what users listen to), and facilitate audio file caching through an external ripper service.

The API serves as a backend for music-related applications, providing unified access to user listening data across different music streaming services while maintaining user privacy through hashed identifiers.

### Privacy & Anonymity

**The API does not know its users' real identities.** This is a fundamental design principle that ensures user privacy.

#### How hgramid Works

Users are identified by `hgramid` (hashed Telegram ID), not by their actual Telegram user IDs. The hashing process:

1. **Client-side hashing**: The Telegram bot (or client application) hashes the user's Telegram ID using HMAC-SHA256 (or SHA3-256) with a shared secret key (`TELEGRAM_HASH_KEY`)
2. **One-way transformation**: The hash is irreversible - you cannot derive the original Telegram ID from hgramid
3. **Consistent identification**: The same Telegram ID always produces the same hgramid (deterministic hashing)
4. **Shared secret**: The `TELEGRAM_HASH_KEY` must be identical in both the API and the client application

**Example:**
```
telegram_id: 123456789
TELEGRAM_HASH_KEY: "secret_key"
hgramid: "a1b2c3d4e5f6..." (64-character hex string)
```

#### Privacy Benefits

- **No personal data**: The API never receives or stores real Telegram user IDs
- **Pseudonymous operations**: All user operations use hgramid, which cannot be linked back to real identities
- **Data isolation**: Even if the database is compromised, attackers cannot identify users
- **Compliance-friendly**: Reduces privacy concerns as no personally identifiable information (PII) is stored

#### Important Notes

- The `TELEGRAM_HASH_KEY` must be kept secret and synchronized between the API and client applications
- Changing the hash key will invalidate all existing hgramids
- The API has no way to "know" who a user is - it only knows their hgramid

### Architecture

The service is built using:
- **FastAPI** - Modern, high-performance web framework for building APIs
- **PostgreSQL** - Primary database for persistent data storage
- **Redis** - Caching layer for OAuth tokens and session management
- **Async/Await** - Fully asynchronous architecture for optimal performance

#### Core Components

1. **API Layer** (`thatsoundapi/api/v1/`)
   - REST endpoints for user operations
   - Integration management endpoints
   - OAuth callback handlers

2. **Core Services** (`thatsoundapi/core/`)
   - `integrations.py` - Integration status management
   - `sounds.py` - Recent tracks aggregation from multiple providers
   - `scrobbles.py` - Scrobbling logic and track caching
   - `ripper.py` - External ripper service communication
   - `spotify/` - Spotify API integration
   - `yandex/` - Yandex Music API integration

3. **Data Layer** (`thatsoundapi/db/`)
   - SQLAlchemy models for PostgreSQL
   - Redis client for token caching
   - Transaction management

4. **Repositories** (`thatsoundapi/repositories/`)
   - Data access layer abstraction
   - User and track repositories

### Key Algorithms & Workflows

#### 1. OAuth Integration Flow

**Spotify Integration:**
```
1. User initiates login → GET /api/v1/{hgramid}/integrations/spotify/login
2. API generates OAuth state token and stores it in Redis (TTL: 600s)
3. User redirected to Spotify authorization page
4. User authorizes → Spotify redirects to callback URL
5. Callback handler validates state token
6. Exchange authorization code for access/refresh tokens
7. Store tokens in Redis with user's hgramid
8. Return success page
```

**Yandex Music Integration:**
```
1. User provides authorized Yandex URL
2. Callback handler extracts token from URL fragment
3. Validate and store token in Redis
4. Return success page
```

#### 2. Recent Tracks Aggregation

The service fetches recent tracks from all integrated providers in parallel:

```python
# Pseudo-code workflow
async def get_recent_tracks(hgramid):
    # Fetch tokens from Redis in parallel
    spotify_tokens, yandex_token = await gather(
        redis.get_spotify_tokens(hgramid),
        redis.get_yandex_token(hgramid)
    )

    # Check token expiry and refresh if needed (Spotify only)
    if spotify_tokens.expires_soon:
        spotify_tokens = await refresh_access_token(...)

    # Fetch tracks from all providers in parallel
    spotify_tracks = await get_spotify_recent_tracks(...)
    yandex_tracks = await get_yandex_recent_tracks(...)

    # Merge and return unified response
    return RecentTracksResponse(
        spotify=spotify_tracks,
        yandex_music=yandex_tracks
    )
```

**Track Processing:**
- Spotify: Fetches 7 recent tracks + current playing track (if any)
- Yandex Music: Fetches 15 tracks from history + current playing track
- Tracks are deduplicated and sorted by play time
- Current playing track is prioritized and inserted at position 0

#### 3. Scrobbling Algorithm

Scrobbling is the process of recording what a user listens to:

```
1. Client requests scrobble → GET /api/v1/{hgramid}/scrobble?track_id=...&track_provider=...
2. Check if track exists in database by external_id
   - If exists: retrieve track
   - If not: create new track record
3. Check if scrobble exists (user + track combination)
   - If exists: return existing scrobble
   - If not: create new scrobble record
4. Check if track has cached audio file (tfile_url)
   - If cached: return tfile_url immediately
   - If not cached: trigger ripper service to cache the track
     - Send async request to ripper service with exponential backoff retry
     - Return scrobble object (client will receive tfile_url later via callback)
```

**Ripper Service Integration:**
- When a track needs caching, the API sends a PUT request to the ripper service
- Retry mechanism: up to 5 attempts with exponential backoff (1s, 2s, 4s, 8s...)
- Ripper service processes the track and calls back with `tfile_url`
- The `tfile_url` is saved to the track record for future use

#### 4. Token Management

**Spotify Token Refresh:**
- Tokens are stored in Redis as hash maps
- Access tokens expire after 1 hour
- Refresh tokens are used to obtain new access tokens
- Automatic refresh when token expires within 5 minutes (300s)
- Manual refresh endpoint available: `/api/v1/{hgramid}/integrations/spotify/refresh`

**Yandex Token:**
- Tokens stored in Redis with expiration time
- No automatic refresh mechanism (handled by client)

### Data Models

#### Database Schema

**Users Table:**
- `hgramid` (PK) - Hashed Telegram user ID (primary identifier)
- `created_at` - User creation timestamp
- `updated_at` - Last update timestamp

**Tracks Table:**
- `id` (PK) - UUID primary key
- `provider_id` (FK) - Reference to track_providers (1=Spotify, 2=YandexMusic)
- `external_id` - Track ID from the provider's API
- `tfile_url` - Cached Telegram file URL (nullable, populated by ripper service)

**Scrobbles Table:**
- `id` (PK) - UUID primary key
- `track_id` (FK) - Reference to tracks.id
- `listener_id` (FK) - Reference to users.hgramid

#### Redis Keys Structure

```
spotify:tokens:{hgramid}          # Hash: Spotify tokens (access_token, refresh_token, expires_at)
spotify:oauth:state:{state}       # String: OAuth state -> hgramid mapping (TTL: 600s)
yandex:token:{hgramid}            # Hash: Yandex token data
```

### API Endpoints

#### User Endpoints

- `GET /api/v1/{hgramid}/integrations` - Get user's integration status
- `GET /api/v1/{hgramid}/recent` - Get recently played tracks from all providers
- `GET /api/v1/{hgramid}/scrobble` - Scrobble a track (create/retrieve scrobble record)
- `PATCH /api/v1/{hgramid}/scrobble/` - Save cached audio file URL

#### Spotify Integration

- `GET /api/v1/{hgramid}/integrations/spotify/login` - Initiate Spotify OAuth flow
- `GET /api/v1/{hgramid}/integrations/spotify/refresh` - Manually refresh Spotify tokens

#### Callback Endpoints

- `GET /api/v1/callback/spotify` - Spotify OAuth callback handler
- `GET /api/v1/callback/yandex` - Yandex Music OAuth callback handler

#### System Endpoints

- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API info

### Configuration

The service uses environment variables with `BACKEND_` prefix. Key settings:

- **Database**: PostgreSQL connection settings
- **Redis**: Redis connection and configuration
- **Spotify**: OAuth credentials, API endpoints, scopes
- **Yandex**: API base URL
- **Ripper**: External ripper service URL and retry attempts
- **Security**: Authentication keys, Telegram hash key
- **TSDirect**: Integration with That Sound Direct API

See `.env.example` for complete configuration reference.

### Error Handling

The API implements a unified error response format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

Custom exceptions are defined in `thatsoundapi/utils/exceptions/`:
- `BaseAPIException` - Base exception class
- `NoSpotifyIntegrationError` - Spotify integration not found
- `InvalidSpotifyOAuthStateError` - Invalid OAuth state
- `TrackNotFoundError` - Track not found in database
- `UserNotFoundError` - User not found
- Provider-specific API errors

### Security

- **Basic Authentication** - Required for most endpoints (except OAuth callbacks)
- **Hashed User IDs (hgramid)** - Users identified by hashed Telegram IDs using HMAC-SHA256. The API **never sees or stores real Telegram user IDs**, ensuring complete user anonymity
- **OAuth State Validation** - Prevents CSRF attacks in OAuth flows
- **Token Encryption** - Sensitive tokens stored securely in Redis
- **Secret Management** - All secrets loaded from environment variables
- **Privacy by Design** - No personally identifiable information (PII) is stored in the database

### Performance Optimizations

1. **Parallel API Calls** - Fetches from multiple providers concurrently using `asyncio.gather()`
2. **Token Caching** - OAuth tokens cached in Redis to minimize API calls
3. **Database Connection Pooling** - SQLAlchemy connection pool for efficient DB access
4. **Async Architecture** - Fully asynchronous I/O operations
5. **Exponential Backoff** - Retry mechanism for external service calls

### Development

**Requirements:**
- Python 3.13+
- Poetry for dependency management
- PostgreSQL 12+
- Redis 6+

**Setup:**
```bash
poetry install
cp .env.example .env
# Configure .env file
poetry run uvicorn main:app --reload
```

**Linting:**
```bash
./scripts/linters.sh
```

---

## Русский

### Обзор

That Sound API — это RESTful микросервис, предназначенный для агрегации и управления данными о прослушивании музыки из различных стриминговых платформ. Сервис интегрируется со Spotify и Яндекс.Музыкой для отслеживания истории прослушиваний пользователей, обработки скробблинга (записи того, что слушают пользователи) и обеспечения кэширования аудиофайлов через внешний сервис ripper.

API служит бэкендом для музыкальных приложений, предоставляя унифицированный доступ к данным о прослушивании пользователей из разных музыкальных стриминговых сервисов, сохраняя при этом приватность пользователей через хэшированные идентификаторы.

### Приватность и анонимность

**API не знает реальных идентичностей своих пользователей.** Это фундаментальный принцип проектирования, обеспечивающий приватность пользователей.

#### Как работает hgramid

Пользователи идентифицируются по `hgramid` (хэшированный Telegram ID), а не по их реальным Telegram ID пользователей. Процесс хэширования:

1. **Хэширование на стороне клиента**: Telegram бот (или клиентское приложение) хэширует Telegram ID пользователя с помощью HMAC-SHA256 (или SHA3-256) с использованием общего секретного ключа (`TELEGRAM_HASH_KEY`)
2. **Одностороннее преобразование**: Хэш необратим - невозможно получить исходный Telegram ID из hgramid
3. **Последовательная идентификация**: Один и тот же Telegram ID всегда производит один и тот же hgramid (детерминированное хэширование)
4. **Общий секрет**: `TELEGRAM_HASH_KEY` должен быть идентичным в API и клиентском приложении

**Пример:**
```
telegram_id: 123456789
TELEGRAM_HASH_KEY: "secret_key"
hgramid: "a1b2c3d4e5f6..." (64-символьная hex строка)
```

#### Преимущества приватности

- **Нет персональных данных**: API никогда не получает и не хранит реальные Telegram ID пользователей
- **Псевдонимные операции**: Все операции пользователей используют hgramid, который нельзя связать с реальными идентичностями
- **Изоляция данных**: Даже если база данных скомпрометирована, злоумышленники не могут идентифицировать пользователей
- **Соответствие требованиям**: Снижает проблемы приватности, так как никакая личная информация (PII) не хранится

#### Важные замечания

- `TELEGRAM_HASH_KEY` должен храниться в секрете и быть синхронизирован между API и клиентскими приложениями
- Изменение ключа хэширования сделает недействительными все существующие hgramid
- API не имеет способа "узнать", кто пользователь - он знает только его hgramid

### Архитектура

Сервис построен с использованием:
- **FastAPI** - Современный высокопроизводительный веб-фреймворк для построения API
- **PostgreSQL** - Основная база данных для постоянного хранения данных
- **Redis** - Кэш-слой для OAuth токенов и управления сессиями
- **Async/Await** - Полностью асинхронная архитектура для оптимальной производительности

#### Основные компоненты

1. **API Слой** (`thatsoundapi/api/v1/`)
   - REST эндпоинты для операций с пользователями
   - Эндпоинты управления интеграциями
   - Обработчики OAuth коллбэков

2. **Основные сервисы** (`thatsoundapi/core/`)
   - `integrations.py` - Управление статусом интеграций
   - `sounds.py` - Агрегация недавних треков из нескольких провайдеров
   - `scrobbles.py` - Логика скробблинга и кэширования треков
   - `ripper.py` - Коммуникация с внешним ripper сервисом
   - `spotify/` - Интеграция с Spotify API
   - `yandex/` - Интеграция с Яндекс.Музыка API

3. **Слой данных** (`thatsoundapi/db/`)
   - SQLAlchemy модели для PostgreSQL
   - Redis клиент для кэширования токенов
   - Управление транзакциями

4. **Репозитории** (`thatsoundapi/repositories/`)
   - Абстракция слоя доступа к данным
   - Репозитории пользователей и треков

### Ключевые алгоритмы и процессы

#### 1. Процесс OAuth интеграции

**Интеграция Spotify:**
```
1. Пользователь инициирует вход → GET /api/v1/{hgramid}/integrations/spotify/login
2. API генерирует OAuth state токен и сохраняет его в Redis (TTL: 600s)
3. Пользователь перенаправляется на страницу авторизации Spotify
4. Пользователь авторизуется → Spotify перенаправляет на callback URL
5. Обработчик callback валидирует state токен
6. Обмен authorization code на access/refresh токены
7. Сохранение токенов в Redis с hgramid пользователя
8. Возврат страницы успеха
```

**Интеграция Яндекс.Музыка:**
```
1. Пользователь предоставляет авторизованный URL Яндекс
2. Обработчик callback извлекает токен из фрагмента URL
3. Валидация и сохранение токена в Redis
4. Возврат страницы успеха
```

#### 2. Агрегация недавних треков

Сервис получает недавние треки из всех интегрированных провайдеров параллельно:

```python
# Псевдокод процесса
async def get_recent_tracks(hgramid):
    # Получение токенов из Redis параллельно
    spotify_tokens, yandex_token = await gather(
        redis.get_spotify_tokens(hgramid),
        redis.get_yandex_token(hgramid)
    )

    # Проверка истечения токена и обновление при необходимости (только Spotify)
    if spotify_tokens.expires_soon:
        spotify_tokens = await refresh_access_token(...)

    # Получение треков из всех провайдеров параллельно
    spotify_tracks = await get_spotify_recent_tracks(...)
    yandex_tracks = await get_yandex_recent_tracks(...)

    # Объединение и возврат унифицированного ответа
    return RecentTracksResponse(
        spotify=spotify_tracks,
        yandex_music=yandex_tracks
    )
```

**Обработка треков:**
- Spotify: Получает 7 недавних треков + текущий воспроизводимый трек (если есть)
- Яндекс.Музыка: Получает 15 треков из истории + текущий воспроизводимый трек
- Треки дедуплицируются и сортируются по времени воспроизведения
- Текущий воспроизводимый трек приоритизируется и вставляется на позицию 0

#### 3. Алгоритм скробблинга

Скробблинг — это процесс записи того, что слушает пользователь:

```
1. Клиент запрашивает скроббл → GET /api/v1/{hgramid}/scrobble?track_id=...&track_provider=...
2. Проверка существования трека в БД по external_id
   - Если существует: получение трека
   - Если нет: создание новой записи трека
3. Проверка существования скроббла (комбинация пользователь + трек)
   - Если существует: возврат существующего скроббла
   - Если нет: создание новой записи скроббла
4. Проверка наличия кэшированного аудиофайла (tfile_url)
   - Если кэширован: немедленный возврат tfile_url
   - Если не кэширован: запуск ripper сервиса для кэширования трека
     - Отправка асинхронного запроса к ripper сервису с экспоненциальной задержкой повторов
     - Возврат объекта скроббла (клиент получит tfile_url позже через callback)
```

**Интеграция с Ripper сервисом:**
- Когда трек требует кэширования, API отправляет PUT запрос к ripper сервису
- Механизм повторов: до 5 попыток с экспоненциальной задержкой (1s, 2s, 4s, 8s...)
- Ripper сервис обрабатывает трек и вызывает callback с `tfile_url`
- `tfile_url` сохраняется в запись трека для будущего использования

#### 4. Управление токенами

**Обновление токенов Spotify:**
- Токены хранятся в Redis как hash maps
- Access токены истекают через 1 час
- Refresh токены используются для получения новых access токенов
- Автоматическое обновление, когда токен истекает в течение 5 минут (300s)
- Доступен эндпоинт ручного обновления: `/api/v1/{hgramid}/integrations/spotify/refresh`

**Токен Яндекс:**
- Токены хранятся в Redis с временем истечения
- Механизм автоматического обновления отсутствует (обрабатывается клиентом)

### Модели данных

#### Схема базы данных

**Таблица Users:**
- `hgramid` (PK) - Хэшированный Telegram ID пользователя (основной идентификатор)
- `created_at` - Временная метка создания пользователя
- `updated_at` - Временная метка последнего обновления

**Таблица Tracks:**
- `id` (PK) - UUID первичный ключ
- `provider_id` (FK) - Ссылка на track_providers (1=Spotify, 2=YandexMusic)
- `external_id` - ID трека из API провайдера
- `tfile_url` - Кэшированный URL файла Telegram (nullable, заполняется ripper сервисом)

**Таблица Scrobbles:**
- `id` (PK) - UUID первичный ключ
- `track_id` (FK) - Ссылка на tracks.id
- `listener_id` (FK) - Ссылка на users.hgramid

#### Структура ключей Redis

```
spotify:tokens:{hgramid}          # Hash: Токены Spotify (access_token, refresh_token, expires_at)
spotify:oauth:state:{state}       # String: OAuth state -> hgramid маппинг (TTL: 600s)
yandex:token:{hgramid}            # Hash: Данные токена Яндекс
```

### API Эндпоинты

#### Эндпоинты пользователей

- `GET /api/v1/{hgramid}/integrations` - Получить статус интеграций пользователя
- `GET /api/v1/{hgramid}/recent` - Получить недавно проигранные треки из всех провайдеров
- `GET /api/v1/{hgramid}/scrobble` - Скробблить трек (создать/получить запись скроббла)
- `PATCH /api/v1/{hgramid}/scrobble/` - Сохранить URL кэшированного аудиофайла

#### Интеграция Spotify

- `GET /api/v1/{hgramid}/integrations/spotify/login` - Инициировать OAuth поток Spotify
- `GET /api/v1/{hgramid}/integrations/spotify/refresh` - Вручную обновить токены Spotify

#### Эндпоинты Callback

- `GET /api/v1/callback/spotify` - Обработчик OAuth callback Spotify
- `GET /api/v1/callback/yandex` - Обработчик OAuth callback Яндекс.Музыка

#### Системные эндпоинты

- `GET /health` - Эндпоинт проверки здоровья
- `GET /` - Корневой эндпоинт с информацией об API

### Конфигурация

Сервис использует переменные окружения с префиксом `BACKEND_`. Ключевые настройки:

- **База данных**: Настройки подключения PostgreSQL
- **Redis**: Настройки подключения и конфигурация Redis
- **Spotify**: OAuth учетные данные, API эндпоинты, области доступа
- **Яндекс**: Базовый URL API
- **Ripper**: URL внешнего ripper сервиса и количество попыток повтора
- **Безопасность**: Ключи аутентификации, ключ хэширования Telegram
- **TSDirect**: Интеграция с That Sound Direct API

См. `.env.example` для полной справки по конфигурации.

### Обработка ошибок

API реализует унифицированный формат ответа об ошибке:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Человекочитаемое сообщение об ошибке"
  }
}
```

Пользовательские исключения определены в `thatsoundapi/utils/exceptions/`:
- `BaseAPIException` - Базовый класс исключений
- `NoSpotifyIntegrationError` - Интеграция Spotify не найдена
- `InvalidSpotifyOAuthStateError` - Неверный OAuth state
- `TrackNotFoundError` - Трек не найден в базе данных
- `UserNotFoundError` - Пользователь не найден
- Ошибки API провайдеров

### Безопасность

- **Базовая аутентификация** - Требуется для большинства эндпоинтов (кроме OAuth callbacks)
- **Хэшированные ID пользователей (hgramid)** - Пользователи идентифицируются по хэшированным Telegram ID с использованием HMAC-SHA256. API **никогда не видит и не хранит реальные Telegram ID пользователей**, обеспечивая полную анонимность пользователей
- **Валидация OAuth State** - Предотвращает CSRF атаки в OAuth потоках
- **Шифрование токенов** - Чувствительные токены хранятся безопасно в Redis
- **Управление секретами** - Все секреты загружаются из переменных окружения
- **Приватность по дизайну** - Никакая личная информация (PII) не хранится в базе данных

### Оптимизации производительности

1. **Параллельные API вызовы** - Получение данных из нескольких провайдеров одновременно с использованием `asyncio.gather()`
2. **Кэширование токенов** - OAuth токены кэшируются в Redis для минимизации API вызовов
3. **Пул соединений БД** - Пул соединений SQLAlchemy для эффективного доступа к БД
4. **Асинхронная архитектура** - Полностью асинхронные I/O операции
5. **Экспоненциальная задержка** - Механизм повторов для вызовов внешних сервисов

### Разработка

**Требования:**
- Python 3.13+
- Poetry для управления зависимостями
- PostgreSQL 12+
- Redis 6+

**Установка:**
```bash
poetry install
cp .env.example .env
# Настроить файл .env
poetry run uvicorn main:app --reload
```

**Линтинг:**
```bash
./scripts/linters.sh
```

---

## License

GPLv3

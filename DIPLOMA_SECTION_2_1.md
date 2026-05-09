# 2 Разработка программной системы

## 2.1 Разработка серверной части

### 2.1.1 Анализ структуры серверного кода

Серверная часть системы SwipeIt разработана на основе принципов чистой архитектуры (Clean Architecture), которая обеспечивает четкое разделение ответственности между слоями приложения и упрощает процессы тестирования, масштабирования и поддержки кода. Архитектурная модель состоит из пяти основных слоев, организованных согласно принципу инверсии зависимостей. Эта архитектурная схема была выбрана намеренно, так как позволяет команде разработчиков работать над отдельными компонентами независимо, обеспечивает гибкость при замене реализации различных компонентов (например, переход с одной БД на другую или смена ML-сервиса), и способствует повышению тестируемости кода благодаря четкому разделению интерфейсов и реализаций.

Архитектурная схема представлена следующим образом:

```
presentation ──> application ──> domain
                     ▲              ▲
                     │              │
                infrastructure ────┘
                     ▲
                     │
                    core (shared utilities)
```

Это разделение обеспечивает несколько ключевых преимуществ. Во-первых, **независимость слоев** позволяет каждому слою быть разработанным и протестированным отдельно без зависимости от других компонентов системы. Во-вторых, **легкое расширение** функционала достигается за счет того, что добавление новых возможностей не требует изменения существующих слоев - новый функционал может быть добавлен в соответствующий слой без влияния на остальную систему. В-третьих, **гибкость при замене реализации** означает, что если потребуется заменить БД, ML-сервис или любой другой компонент, это может быть сделано без необходимости переписывания бизнес-логики приложения. Наконец, **переиспользование кода** достигается благодаря отделению бизнес-логики от технических деталей реализации, что позволяет легко переносить логику между различными компонентами и даже различными проектами.

**Слой представления (Presentation Layer)**

Слой представления отвечает за взаимодействие с клиентами через REST API и формирование HTTP ответов. Этот слой является единственной точкой соприкосновения приложения с внешним миром и должен обрабатывать все аспекты HTTP протокола, включая валидацию входных данных, управление HTTP методами и кодами состояния, а также форматирование ответов в необходимый формат данных. Слой представления использует FastAPI в качестве web-фреймворка, что обеспечивает высокую производительность благодаря асинхронной обработке запросов и встроенной поддержке автоматического создания документации API через Swagger и ReDoc.

Структура слоя представления организована следующим образом:

```
presentation/
├── api/
│   ├── routes.py              # Главный маршрутизатор API
│   ├── schemas/               # Pydantic-схемы для валидации данных
│   │   ├── garment.py        # Схемы для одежды
│   │   ├── media.py          # Схемы для медиа-файлов
│   │   ├── feed.py           # Схемы для ленты
│   │   ├── user.py           # Схемы для пользователя
│   │   ├── likes.py          # Схемы для лайков
│   │   └── tryon.py          # Схемы для виртуальной примерки
│   └── v1/
│       ├── __init__.py
│       ├── auth.py            # Endpoints аутентификации
│       ├── garments.py        # Endpoints для управления гардеробом
│       ├── media.py           # Endpoints для загрузки и получения медиа
│       ├── feed.py            # Endpoints для ленты новостей
│       ├── health.py          # Endpoints для проверки здоровья сервиса
│       └── tryon.py           # Endpoints для виртуальной примерки
```

Система использует FastAPI версии 0.104.1 для создания асинхронного REST API высокой производительности. FastAPI был выбран для этого проекта по нескольким причинам: во-первых, он обеспечивает встроенную поддержку асинхронного программирования через asyncio, что позволяет эффективно обрабатывать большое количество одновременных запросов; во-вторых, имеет встроенную систему валидации данных через Pydantic, что обеспечивает безопасность и снижает объем boilerplate кода; в-третьих, автоматически генерирует полную интерактивную документацию API, что упрощает работу фронтенд-разработчикам и облегчает тестирование.

Каждый модуль в папке `v1/` содержит роутер (APIRouter), который определяет эндпоинты для конкретной функциональности. Для примера, модуль гарнитур (garments.py) содержит все эндпоинты, связанные с управлением одеждой в гардеробе пользователя. Роутеры регистрируются в главном файле приложения (main.py) и образуют полный API приложения. Это позволяет легко масштабировать приложение и добавлять новые функции без изменения существующего кода.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/", response_model=GarmentResponse)
async def create_garment(
    garment_data: GarmentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую одежду"""
    garment_repo = GarmentRepository()
    garment = await garment_repo.create(db, obj_in=garment_data)
    return garment
```

Валидация данных в слое представления обеспечивается Pydantic-схемами, которые определяют структуру и типы данных для всех входных и выходных параметров API. Когда клиент отправляет запрос с данными, FastAPI автоматически проверяет эти данные против схемы - если данные не соответствуют ожидаемому формату или типам, запрос отклоняется с ошибкой 422 Unprocessable Entity и подробным описанием причины ошибки. Это обеспечивает несколько важных функций: во-первых, **безопасность** - система не принимает неверные данные, что предотвращает инъекции и другие атаки; во-вторых, **автоматическая типизация** - данные автоматически конвертируются в правильные типы Python; в-третьих, **автоматическая документация** - схемы используются для генерации документации API в Swagger UI; в-четвертых, **улучшенная разработка** - разработчики видят точно, какой формат данных ожидает каждый эндпоинт, что упрощает интеграцию с фронтенд-частью.

**Слой приложения (Application Layer)**

Слой приложения содержит бизнес-логику и use cases приложения, отделяя их от технических деталей реализации и деталей HTTP протокола. Этот слой является сердцем приложения - именно здесь находится логика, которая определяет, как система должна работать и какие действия она должна выполнять при получении того или иного запроса. Слой приложения не знает ничего о том, как данные хранятся в БД или как они отправляются клиенту - он знает только о бизнес-правилах и логике системы.

Структура слоя приложения включает три основных компонента: Data Transfer Objects (DTO), которые используются для передачи данных между слоями; Ports (абстрактные интерфейсы), которые определяют контракты между приложением и инфраструктурой; и Use Cases, которые содержат бизнес-логику.

```
application/
├── dto/                       # Data Transfer Objects
│   └── tryon_dto.py          # DTO для виртуальной примерки
├── ports/                     # Абстрактные интерфейсы
│   └── tryon_gateway.py      # Портал для ML-сервиса
└── use_cases/                 # Use cases (бизнес-сценарии)
    └── tryon_use_case.py     # Use case для примерки
```

Use case представляет собой реализацию одного бизнес-сценария, инкапсулирующего все этапы его выполнения. Например, use case для виртуальной примерки одежды содержит логику валидации входных данных, проверку кэша, вызов ML-сервиса и сохранение результатов. Преимущество use cases заключается в том, что они представляют бизнес-правила в чистом и понятном виде, независимо от технических деталей. Если фронтенд изменится с веб-приложения на мобильное приложение, use cases останутся прежними - изменится только слой представления.

```python
class TryOnUseCase:
    """Use Case для виртуальной примерки одежды."""
    
    def __init__(self, ml_service: TryOnGateway):
        self._ml_service = ml_service
    
    def validate(self, request: TryOnRequest) -> None:
        """Валидация входных данных"""
        valid_model_types = ("hd", "dc")
        if request.model_type not in valid_model_types:
            raise ValueError(f"model_type должен быть одним из {valid_model_types}")
        
        valid_categories = (0, 1, 2)
        if request.category not in valid_categories:
            raise ValueError(f"category должен быть одним из {valid_categories}")
```

Data Transfer Objects (DTO) используются для передачи данных между слоями приложения, обеспечивая четкий контракт о структуре данных на каждой границе слоев. DTO отделяет схему данных API от внутреннего представления данных в системе, что позволяет менять один без влияния на другой. Например, DTO запроса на примерку определяет структуру данных, которые клиент должен отправить, в то время как внутри приложения эти данные могут быть обработаны и преобразованы в другой формат.

```python
class TryOnRequest(BaseModel):
    model_id: str
    model_type: str  # "hd" или "dc"
    category: int    # 0, 1 или 2
    garment_image: str  # base64 encoded
    person_image: str   # base64 encoded
```

Ports (абстрактные интерфейсы) определяют контракты между слоем приложения и слоем инфраструктуры. Это позволяет приложению не зависеть от конкретной реализации сервисов (например, не зависеть от конкретного ML-фреймворка). Если потребуется заменить ML-сервис, достаточно создать новую реализацию Port-а, не меняя код use case-ов. Это следует принципу инверсии зависимостей - высокоуровневые модули (use cases) зависят от абстракций (ports), а не от низкоуровневых деталей (конкретных реализаций).

```python
class TryOnGateway:
    """Портал для взаимодействия с ML-сервисом"""
    
    async def process_tryon(self, request: TryOnRequest) -> TryOnResponse:
        """Обработить запрос на виртуальную примерку"""
        pass
```

**Слой домена (Domain Layer)**

Слой домена содержит основные бизнес-сущности и правила, которые являются независимыми от технических деталей реализации и могут быть переиспользованы в разных проектах. Этот слой представляет собой чистый код, который не зависит ни от какой конкретной библиотеки или фреймворка, что делает его максимально переиспользуемым и тестируемым.

```
domain/
├── __init__.py
└── enums/                    # Перечисления бизнес-сущностей
    ├── garment_category.py
    ├── model_type.py
    └── ...
```

Слой домена предоставляет перечисления (enums) для бизнес-концепций, таких как категории одежды, типы моделей ML и статусы транзакций. Это обеспечивает типобезопасность и предотвращает ошибки при использовании некорректных значений по всей системе. Вместо использования строк или чисел (которые может быть сложно отследить и которые подвержены ошибкам), система использует типизированные перечисления, что делает код более безопасным и самодокументирующимся.

**Слой инфраструктуры (Infrastructure Layer)**

Слой инфраструктуры содержит все технические реализации и адаптеры, которые взаимодействуют с внешними системами и ресурсами. Этот слой изолирует сложности работы с базами данных, хранилищами файлов, кэшами, сервисами аутентификации и ML-моделями от остальной части приложения. Слой инфраструктуры должен быть максимально изолирован от остальной части кода, так что при необходимости замены реализации (например, переход с PostgreSQL на MongoDB или с локального хранилища на облачное) изменения будут минимальны и не повлияют на другие части системы.

Структура слоя инфраструктуры:

Слой инфраструктуры содержит все технические реализации и адаптеры:

```
infrastructure/
├── auth/
│   ├── security.py           # JWT, хеширование паролей
│   └── oauth.py              # OAuth провайдеры (если есть)
├── cache/
│   └── redis_client.py       # Клиент для кэширования
├── db/
│   ├── db.py                 # Конфигурация БД
│   └── schema_compat.py      # Миграции схемы
├── ml/
│   ├── hd_tryon_service.py   # HD модель для примерки
│   ├── dc_tryon_service.py   # DC модель для примерки
│   └── tryon_gateway.py      # Реализация портала ML
├── persistence/
│   ├── models/               # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── garment.py
│   │   ├── media.py
│   │   ├── feed.py
│   │   ├── likes.py
│   │   ├── tryon.py
│   │   ├── tryon_event.py
│   │   └── mixins.py
│   └── repositories/         # Data access objects
│       ├── base_repo.py
│       ├── user_repo.py
│       ├── garment_repo.py
│       ├── media_repo.py
│       ├── feed_repo.py
│       ├── like_repo.py
│       └── tryon_repo.py
├── queue/
│   ├── redis_client.py       # Redis очередь
│   └── task_manager.py       # Менеджер задач
├── storage/
│   ├── s3.py                 # S3 клиент для хранилища
│   ├── local_media.py        # Локальное хранилище медиа
│   └── storage_interface.py  # Абстрактный интерфейс
└── workers/
    └── tryon_worker.py       # Worker для обработки задач примерки
```

Слой базы данных является одним из ключевых компонентов инфраструктуры. Система использует PostgreSQL в качестве основной реляционной БД, асинхронный драйвер asyncpg для неблокирующих операций с БД, и SQLAlchemy ORM для объектно-реляционного отображения. Выбор этих технологий был сделан для обеспечения высокой производительности и надежности - асинхронные операции позволяют серверу обрабатывать много одновременных запросов без блокировок, а ORM упрощает работу с БД и делает код более читаемым и поддерживаемым.

```python
# db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = settings.async_database_url
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

SQLAlchemy модели определяют структуру таблиц в БД и отношения между ними. Каждая модель представляет собой Python класс, который отображается на таблицу в БД. Модели содержат информацию о типах данных, ограничениях (constraints), индексах и отношениях между таблицами. Например, модель пользователя определяет таблицу с полями для электронной почты, имени пользователя, хешированного пароля и временных меток создания/обновления. Отношения между моделями определяются через `relationship()`, что позволяет легко получать связанные данные (например, все вещи пользователя).

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    garments = relationship("Garment", back_populates="user")
    feed_items = relationship("FeedItem", back_populates="user")
    likes = relationship("Like", back_populates="user")
```

Репозитории реализуют паттерн Data Access Object (DAO) и обеспечивают абстракцию доступа к данным. Вместо того, чтобы писать SQL запросы прямо в use cases или API эндпоинтах, все операции с БД делегируются репозиториям. Это дает несколько преимуществ: во-первых, код более понятен - репозиторий явно показывает, какие операции возможны с данными; во-вторых, легче тестировать - можно создать mock репозиторий для тестирования; в-третьих, легче менять реализацию - если потребуется изменить способ получения данных, нужно изменить только репозиторий.

```python
class GarmentRepository(BaseRepository):
    def __init__(self):
        self.model = Garment
    
    async def create(self, db: AsyncSession, obj_in: GarmentCreate) -> Garment:
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: int) -> Garment | None:
        return await db.get(self.model, id)
    
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()
```

Аутентификация и безопасность являются критически важными компонентами любого веб-приложения. Система использует JWT (JSON Web Tokens) токены для аутентификации пользователей и BCrypt хеширование для защиты паролей. JWT позволяет избежать хранения сессий на сервере - каждый токен содержит информацию о пользователе и подписан секретным ключом, так что сервер может проверить подлинность токена без обращения к БД. BCrypt - это криптографическое хеширование, специально разработанное для паролей, и оно содержит встроенную защиту от атак перебором (brute-force attacks).

```python
# security.py
from passlib.context import CryptContext
from python_jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

Хранилище медиа-файлов реализовано с использованием S3-совместимого хранилища (в разработке используется MinIO). S3 API стал стандартом де-факто для облачного хранилища объектов, и его использование обеспечивает совместимость с различными облачными провайдерами (AWS S3, DigitalOcean Spaces, и т.д.). S3 позволяет хранить большие объемы медиа-файлов без загромождения основного сервера, обеспечивает масштабируемость и надежность через репликацию данных.

```python
class S3Client:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
    
    async def upload_file(self, file_path: str, file_content: bytes):
        self._client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_path,
            Body=file_content
        )
```

Очередь задач и система кэширования реализованы с помощью Redis, in-memory хранилища данных с очень высокой производительностью. Redis используется для двух целей: во-первых, для кэширования результатов вычислений (например, результатов примерки), что позволяет избежать повторных вычислений для одинаковых входных данных; во-вторых, для управления очередью асинхронных задач (например, длительных процессов примерки), которые выполняются worker-процессами параллельно с основным приложением.

```python
REDIS_URL = settings.REDIS_URL
redis_client = redis.from_url(REDIS_URL)

# Кэширование результатов примерки
TRYON_CACHE_TTL = settings.TRYON_CACHE_TTL_SECONDS  # 86400 секунд (24 часа)

# Очередь для длительных задач
TRYON_QUEUE_NAME = "tryon:queue"
TRYON_DEAD_LETTER_QUEUE = "tryon:dead-letter"
```

**Слой конфигурации и утилит (Core Layer)**

Слой core содержит конфигурацию приложения, утилиты и общие функции, используемые несколькими слоями приложения. Этот слой включает в себя модули для управления переменными окружения, обработки ошибок, логирования, валидации и других утилит, которые необходимы для функционирования приложения.

```
core/
├── config.py                 # Конфигурация приложения
├── errors.py                 # Обработчики ошибок
├── hashing.py               # Функции хеширования
├── logging.py               # Настройка логирования
└── validators.py            # Валидаторы
```

Система использует Pydantic для валидации переменных окружения, что обеспечивает типобезопасность и автоматическую проверку корректности конфигурации при запуске приложения. Если требуемая переменная окружения не установлена или имеет неправильный тип, приложение не запустится и выведет понятное сообщение об ошибке. Это предотвращает ошибки конфигурации, которые могут быть обнаружены только при выполнении приложения.

```python
class BackendSettings(BaseSettings):
    API_V1: str = "/api/v1"
    SECRET_KEY: str
    DB_URL: AnyUrl
    
    # S3 Configuration
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str = "swipeit-media"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Try-On Configuration
    TRYON_CACHE_TTL_SECONDS: int = 86400
    TRYON_QUEUE_NAME: str = "tryon:queue"
    TRYON_RATE_LIMIT_REQUESTS: int = 5
    TRYON_RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    class Config:
        env_file = ".env"
```

Обработка ошибок является неотъемлемой частью надежного приложения. Система определяет custom исключения для различных типов ошибок и устанавливает обработчики исключений на уровне приложения. Когда возникает исключение, оно перехватывается обработчиком, который преобразует его в appropriate HTTP ответ с правильным кодом состояния и описанием ошибки. Это обеспечивает консистентные и информативные ошибки для клиентов приложения.

```python
class ValidationError(Exception):
    """Ошибка валидации"""
    pass

class NotFoundError(Exception):
    """Ресурс не найден"""
    pass

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
```

**Главная точка входа и инициализация приложения**

Главный файл приложения (main.py) инициализирует FastAPI приложение, подключает middleware, роутеры и устанавливает хуки жизненного цикла. Жизненный цикл приложения состоит из трех фаз: инициализация (startup) при запуске приложения, работа приложения (lifespan), и завершение (shutdown) при остановке приложения. На фазе инициализации система устанавливает соединения с БД, инициализирует Redis клиент, проверяет наличие S3 bucket-а и выполняет другие необходимые операции. На фазе завершения система корректно закрывает все открытые соединения и освобождает ресурсы.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: инициализация БД, redis, S3
    await init_database()
    await init_redis()
    ensure_demo_user_exists()
    seed_demo_feed()
    
    yield  # Приложение работает
    
    # Shutdown: закрытие соединений
    await close_database()
    await close_redis()

app = FastAPI(title="SwipeIt", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация исключений
setup_exception_handlers(app)

# Подключение роутеров
app.include_router(api_router, prefix=settings.API_V1)
```

Middleware (промежуточное ПО) обрабатывает каждый запрос и ответ, проходящий через приложение. CORS (Cross-Origin Resource Sharing) middleware позволяет фронтенд-приложению, работающему на другом хосте или порту, отправлять запросы к API. Это необходимо для разработки, когда фронтенд может работать на `localhost:5173`, а бэкенд на `localhost:8000`. В production среде обычно используется один домен для обоих, поэтому CORS может быть более ограничивающим.

**Стек технологий серверной части**

| Компонент | Технология | Версия | Назначение |
|-----------|-----------|--------|-----------|
| Framework | FastAPI | 0.104.1 | Асинхронный web framework |
| ASGI Server | Uvicorn | 0.24.0 | ASGI сервер приложения |
| ORM | SQLAlchemy | 2.0.23 | Object-relational mapping |
| Database Driver | asyncpg | 0.29.0 | Асинхронный драйвер PostgreSQL |
| Database | PostgreSQL | 13+ | Реляционная БД |
| Validation | Pydantic | 1.10.13 | Валидация данных |
| Authentication | python-jose | 3.3.0 | JWT токены |
| Password Hashing | passlib[bcrypt] | 1.7.4 | Безопасное хеширование |
| Cache | Redis | 5.0.1+ | In-memory кэш |
| File Storage | MinIO (S3) | - | Object storage |
| Image Processing | Pillow | 10.4.0 | Обработка изображений |
| Migrations | Alembic | 1.12.1 | Управление миграциями БД |

Архитектура серверной части обеспечивает надежность, масштабируемость и поддерживаемость кода. Четкое разделение на слои позволяет команде разработчиков работать параллельно над разными компонентами, легко тестировать код и вносить изменения без опасения сломать другие части системы. Использование современных инструментов и best practices (асинхронная обработка, типизация, валидация, логирование) делает систему готовой к использованию в production среде и способной масштабироваться с ростом требований к приложению.

---

### 2.1.2 Интеграция алгоритмов обработки и анализа данных

Система использует портальный паттерн для абстрагирования ML-сервиса:

```python
# application/ports/tryon_gateway.py
from abc import ABC, abstractmethod
from app.application.dto.tryon_dto import TryOnRequest, TryOnResponse

class TryOnGateway(ABC):
    """Абстрактный портал для ML-сервиса примерки"""
    
    @abstractmethod
    async def process_tryon(self, request: TryOnRequest) -> TryOnResponse:
        """
        Обработать запрос на виртуальную примерку
        
        Args:
            request: DTO запроса с данными изображений
            
        Returns:
            DTO ответа с результатом примерки
        """
        pass
```

**Реализация ML-сервиса**

Конкретная реализация ML-сервиса находится в инфраструктуре:

```python
# infrastructure/ml/tryon_gateway.py
from app.application.ports.tryon_gateway import TryOnGateway
from app.application.dto.tryon_dto import TryOnRequest, TryOnResponse
from app.infrastructure.ml.hd_tryon_service import HDTryOnService
from app.infrastructure.ml.dc_tryon_service import DCTryOnService

class TryOnGatewayImpl(TryOnGateway):
    def __init__(self):
        self.hd_service = HDTryOnService()
        self.dc_service = DCTryOnService()
    
    async def process_tryon(self, request: TryOnRequest) -> TryOnResponse:
        """Обработить запрос в зависимости от типа модели"""
        
        # Декодирование base64 изображений
        garment_image = self._decode_base64_image(request.garment_image)
        person_image = self._decode_base64_image(request.person_image)
        
        # Выбор модели в зависимости от типа
        if request.model_type == "hd":
            result = await self.hd_service.process(
                person_image, 
                garment_image, 
                request.category
            )
        elif request.model_type == "dc":
            result = await self.dc_service.process(
                person_image, 
                garment_image, 
                request.category
            )
        else:
            raise ValueError(f"Unknown model type: {request.model_type}")
        
        # Кодирование результата в base64
        result_base64 = self._encode_image_to_base64(result)
        
        return TryOnResponse(
            result_image=result_base64,
            model_id=request.model_id,
            processing_time_ms=result.get('processing_time_ms'),
            success=True
        )
```

#### 2.1.2.3 Система управления задачами

**Очередь задач с Redis**

Для обработки длительных ML-операций используется Redis очередь:

```python
# infrastructure/queue/redis_client.py
import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

class TryOnTaskQueue:
    def __init__(self):
        self.queue_name = settings.TRYON_QUEUE_NAME
        self.dead_letter_queue = settings.TRYON_DEAD_LETTER_QUEUE_NAME
        self.max_retries = settings.TRYON_QUEUE_MAX_RETRIES
    
    async def enqueue_tryon_task(self, task_data: dict) -> str:
        """Поместить задачу в очередь"""
        task_id = generate_task_id()
        task_data['task_id'] = task_id
        task_data['retries'] = 0
        
        redis_client.rpush(
            self.queue_name,
            json.dumps(task_data)
        )
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> dict:
        """Получить статус задачи"""
        status_key = f"tryon:task:{task_id}:status"
        status_data = redis_client.get(status_key)
        
        if status_data:
            return json.loads(status_data)
        return {"status": "pending"}
```

**Worker для обработки задач**

Worker-процесс обрабатывает задачи из очереди:

```python
# infrastructure/workers/tryon_worker.py
import asyncio
import json
from app.infrastructure.queue.redis_client import redis_client, TryOnTaskQueue
from app.infrastructure.ml.tryon_gateway import TryOnGatewayImpl

class TryOnWorker:
    def __init__(self):
        self.queue = TryOnTaskQueue()
        self.ml_gateway = TryOnGatewayImpl()
        self.processing = True
    
    async def run(self):
        """Главный цикл worker-а"""
        while self.processing:
            try:
                # Получить задачу из очереди
                task_data = redis_client.blpop(
                    self.queue.queue_name,
                    timeout=settings.TRYON_QUEUE_BLOCK_TIMEOUT_SECONDS
                )
                
                if not task_data:
                    continue
                
                task_json = json.loads(task_data[1])
                task_id = task_json['task_id']
                
                # Обновить статус на "processing"
                self._update_task_status(task_id, "processing")
                
                # Обработить задачу
                result = await self.ml_gateway.process_tryon(task_json)
                
                # Сохранить результат
                self._save_result(task_id, result)
                self._update_task_status(task_id, "completed")
                
            except Exception as e:
                self._handle_task_error(task_json, e)
    
    def _handle_task_error(self, task_data: dict, error: Exception):
        """Обработить ошибку задачи с повторами"""
        retries = task_data.get('retries', 0)
        
        if retries < self.queue.max_retries:
            # Поместить задачу обратно в очередь
            task_data['retries'] = retries + 1
            redis_client.rpush(self.queue.queue_name, json.dumps(task_data))
        else:
            # Переместить в dead-letter очередь
            redis_client.rpush(
                self.queue.dead_letter_queue,
                json.dumps({**task_data, 'error': str(error)})
            )
```

#### 2.1.2.4 Кэширование результатов

Система кэширует результаты примерки для одинаковых входных данных:

```python
# infrastructure/cache/tryon_cache.py
import hashlib
import json
from app.infrastructure.queue.redis_client import redis_client
from app.core.config import settings

class TryOnCache:
    def __init__(self):
        self.ttl = settings.TRYON_CACHE_TTL_SECONDS
        self.prefix = "tryon:cache"
    
    def _generate_cache_key(self, garment_id: int, person_id: int, 
                           category: int, model_type: str) -> str:
        """Сгенерировать ключ кэша на основе входных данных"""
        key_data = f"{garment_id}:{person_id}:{category}:{model_type}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{self.prefix}:{key_hash}"
    
    async def get(self, garment_id: int, person_id: int, 
                 category: int, model_type: str) -> dict | None:
        """Получить результат из кэша"""
        cache_key = self._generate_cache_key(
            garment_id, person_id, category, model_type
        )
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set(self, garment_id: int, person_id: int, 
                 category: int, model_type: str, result: dict):
        """Сохранить результат в кэш"""
        cache_key = self._generate_cache_key(
            garment_id, person_id, category, model_type
        )
        redis_client.setex(
            cache_key,
            self.ttl,
            json.dumps(result)
        )
```

#### 2.1.2.5 Обработка изображений

Система использует Pillow для предварительной обработки изображений:

```python
# infrastructure/ml/image_processor.py
from PIL import Image
import io
import base64

class ImageProcessor:
    @staticmethod
    def decode_base64_image(image_base64: str) -> Image.Image:
        """Декодировать base64 строку в PIL Image"""
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        return image
    
    @staticmethod
    def encode_image_to_base64(image: Image.Image) -> str:
        """Кодировать PIL Image в base64 строку"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    @staticmethod
    def resize_image(image: Image.Image, max_width: int = 1024, 
                    max_height: int = 1024) -> Image.Image:
        """Ресайзировать изображение"""
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def validate_image(image: Image.Image) -> bool:
        """Проверить валидность изображения"""
        if image.mode not in ('RGB', 'RGBA', 'L'):
            image = image.convert('RGB')
        return True
```

#### 2.1.2.6 Обработка ошибок при ML-обработке

```python
# infrastructure/ml/exceptions.py
class MLProcessingError(Exception):
    """Общая ошибка ML-обработки"""
    pass

class ModelNotFoundError(MLProcessingError):
    """ML-модель не найдена"""
    pass

class ImageProcessingError(MLProcessingError):
    """Ошибка при обработке изображения"""
    pass

class TimeoutError(MLProcessingError):
    """Превышено время обработки"""
    pass

# Обработчик в use case
class TryOnUseCase:
    async def execute(self, request: TryOnRequest) -> TryOnResponse:
        try:
            # Валидация
            self.validate(request)
            
            # Проверка кэша
            cached = await self.cache.get(...)
            if cached:
                return cached
            
            # Обработка
            result = await self.ml_service.process_tryon(request)
            
            # Кэширование
            await self.cache.set(...)
            
            return result
            
        except ImageProcessingError as e:
            logger.error(f"Image processing failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid image")
        except TimeoutError as e:
            logger.error(f"ML processing timeout: {e}")
            raise HTTPException(status_code=504, detail="Processing timeout")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
```

---

### 2.1.3 Оптимизация производительности серверной части

#### 2.1.3.1 Асинхронная обработка запросов

**AsyncIO и Uvicorn**

Система полностью асинхронна, используя asyncio и Uvicorn для обработки большого количества одновременных запросов:

```python
# app/main.py
from uvicorn import run
from fastapi import FastAPI

app = FastAPI(title="SwipeIt")

# Запуск с оптимальными настройками
if __name__ == "__main__":
    run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Число worker-процессов (4 × CPU cores)
        loop="uvloop",  # Быстрый event loop
        http="httptools",  # Быстрый HTTP парсер
    )
```

**Асинхронные роутеры**

Все эндпоинты определены как async функции:

```python
@router.post("/tryon", response_model=TryOnResponse)
async def create_tryon(
    request: TryOnRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Асинхронный эндпоинт для примерки"""
    
    # Параллельная загрузка данных
    garment_task = fetch_garment_async(request.garment_id, db)
    user_profile_task = fetch_user_profile_async(current_user.id, db)
    
    garment, user_profile = await asyncio.gather(
        garment_task,
        user_profile_task
    )
    
    # Асинхронный вызов ML-сервиса
    result = await ml_gateway.process_tryon(request)
    
    return result
```

#### 2.1.3.2 Оптимизация базы данных

**Пулинг соединений**

SQLAlchemy автоматически управляет пулом соединений:

```python
# infrastructure/db/db.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=AsyncPool,
    pool_size=20,           # Размер пула
    max_overflow=40,        # Максимальное переполнение
    pool_recycle=3600,      # Переиспользовать соединения через час
    pool_pre_ping=True,     # Проверить соединение перед использованием
)
```

**Индексирование**

Частые операции поиска оптимизированы индексами:

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)  # Индекс на email
    username = Column(String(100), unique=True, index=True)  # Индекс на username
    
    __table_args__ = (
        Index('ix_users_created_at', 'created_at'),  # Для сортировки по дате
    )

class Garment(Base):
    __tablename__ = "garments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    category = Column(String(50), index=True)  # Индекс для фильтрации
    
    __table_args__ = (
        Index('ix_garments_user_category', 'user_id', 'category'),  # Составной индекс
    )
```

**Ленивая загрузка с relationship.joinedload()**

```python
from sqlalchemy.orm import joinedload

async def get_user_with_garments(user_id: int, db: AsyncSession):
    """Загрузить пользователя с его гардеробом одним запросом"""
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(joinedload(User.garments))
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()
```

**Пакетные операции**

```python
# Эффективная вставка множества записей
async def bulk_insert_garments(garments_data: list[dict], user_id: int, db: AsyncSession):
    garments = [
        Garment(user_id=user_id, **data)
        for data in garments_data
    ]
    db.add_all(garments)
    await db.commit()
```

#### 2.1.3.3 Кэширование с Redis

**Кэширование результатов запросов**

```python
# Кэширование профиля пользователя
@router.get("/profile/{user_id}")
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    # Проверить кэш
    cache_key = f"user:profile:{user_id}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Загрузить из БД
    user = await db.get(User, user_id)
    
    # Сохранить в кэш на 1 час
    redis_client.setex(cache_key, 3600, json.dumps(user_dict))
    
    return user
```

**Кэширование сессий**

```python
# Кэширование сессий для быстрой аутентификации
class SessionCache:
    def __init__(self):
        self.prefix = "session"
        self.ttl = 3600  # 1 час
    
    async def get_session(self, token: str) -> dict | None:
        session_key = f"{self.prefix}:{token}"
        session_data = redis_client.get(session_key)
        
        if session_data:
            return json.loads(session_data)
        return None
    
    async def set_session(self, token: str, session_data: dict):
        session_key = f"{self.prefix}:{token}"
        redis_client.setex(
            session_key,
            self.ttl,
            json.dumps(session_data)
        )
```

#### 2.1.3.4 Оптимизация загрузки медиа

**Lazy loading изображений**

```python
class MediaRepository:
    async def get_user_media_paginated(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20,
        db: AsyncSession = None
    ):
        """Получить медиа с пагинацией"""
        stmt = (
            select(Media)
            .where(Media.user_id == user_id)
            .order_by(Media.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
```

**Генерация URL с CDN**

```python
class MediaService:
    def get_media_url(self, media_id: int, size: str = "original") -> str:
        """Получить URL медиа из CDN"""
        if settings.S3_PUBLIC_URL:
            return f"{settings.S3_PUBLIC_URL}/media/{media_id}/{size}.jpg"
        return f"{settings.S3_ENDPOINT}/swipeit-media/media/{media_id}/{size}.jpg"
```

#### 2.1.3.5 Сжатие ответов

```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)  # Сжимать ответы > 1KB
```

#### 2.1.3.6 Мониторинг производительности

```python
# core/monitoring.py
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def track_performance(func):
    """Декоратор для отслеживания производительности"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start
            logger.info(f"{func.__name__} took {duration:.2f}s")
    
    return wrapper

# Использование
@router.get("/profile/{user_id}")
@track_performance
async def get_user_profile(user_id: int):
    ...
```

#### 2.1.3.7 Метрики производительности

| Метрика | Целевое значение | Описание |
|---------|-----------------|---------|
| Response Time (p95) | < 200ms | 95-й процентиль времени ответа |
| Throughput | > 1000 req/s | Количество запросов в секунду |
| Database Query Time | < 50ms | Время выполнения запроса к БД |
| Cache Hit Rate | > 80% | Процент успешных попаданий в кэш |
| Memory Usage | < 500MB | Использование памяти на процесс |
| CPU Usage | < 80% | Использование CPU при нормальной нагрузке |

---

### 2.1.4 Реализация Rest-сервиса программной системы

#### 2.1.4.1 Архитектура REST API

REST (Representational State Transfer) API разработана с соблюдением принципов HATEOAS и правильного использования HTTP методов и кодов состояния.

#### 2.1.4.2 Структура API версий

```
/api/v1/
├── /auth              # Аутентификация и авторизация
├── /users             # Управление пользователями
├── /garments          # Управление гардеробом
├── /media             # Загрузка и получение медиа
├── /feed              # Лента новостей
├── /likes             # Система лайков
├── /tryon             # Виртуальная примерка
└── /health            # Проверка здоровья сервиса
```

#### 2.1.4.3 API эндпоинты аутентификации

**POST /api/v1/auth/signup - Регистрация пользователя**

```python
@router.post("/signup", response_model=TokenResponse)
async def signup(
    credentials: SignUpRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя
    
    Args:
        credentials: {email, username, password}
    
    Returns:
        {access_token, token_type, user}
    """
    # Проверить, что пользователь не существует
    user_repo = UserRepository()
    existing = await user_repo.get_by_email(db, credentials.email)
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )
    
    # Создать новго пользователя
    hashed_password = hash_password(credentials.password)
    user = await user_repo.create(
        db,
        obj_in={
            "email": credentials.email,
            "username": credentials.username,
            "hashed_password": hashed_password
        }
    )
    
    # Сгенерировать токен
    access_token = create_access_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
```

**POST /api/v1/auth/login - Вход в систему**

```python
@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Вход в систему"""
    # Найти пользователя
    user_repo = UserRepository()
    user = await user_repo.get_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Сгенерировать токен
    access_token = create_access_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
```

#### 2.1.4.4 API эндпоинты гардероба

**POST /api/v1/garments - Добавить вещь в гардероб**

```python
@router.post("/", response_model=GarmentResponse)
async def create_garment(
    garment_data: GarmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новую вещь в гардеробе
    
    Request:
        {
            "name": "Синий свитер",
            "description": "Уютный свитер",
            "category": "tops",
            "color": "blue",
            "size": "M",
            "image_url": "..."
        }
    """
    garment_repo = GarmentRepository()
    garment = await garment_repo.create(
        db,
        obj_in={
            **garment_data.dict(),
            "user_id": current_user.id
        }
    )
    return garment
```

**GET /api/v1/garments/{id} - Получить информацию о вещи**

```python
@router.get("/{garment_id}", response_model=GarmentResponse)
async def get_garment(
    garment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить информацию о конкретной вещи"""
    garment_repo = GarmentRepository()
    garment = await garment_repo.get(db, garment_id)
    
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")
    
    return garment
```

**GET /api/v1/garments - Получить список вещей**

```python
@router.get("/", response_model=list[GarmentResponse])
async def list_garments(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получить список вещей текущего пользователя"""
    garment_repo = GarmentRepository()
    
    # Построить фильтр
    filters = {"user_id": current_user.id}
    if category:
        filters["category"] = category
    
    garments = await garment_repo.get_multi(
        db,
        skip=skip,
        limit=limit,
        **filters
    )
    
    return garments
```

**PUT /api/v1/garments/{id} - Обновить информацию о вещи**

```python
@router.put("/{garment_id}", response_model=GarmentResponse)
async def update_garment(
    garment_id: int,
    garment_update: GarmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить информацию о вещи"""
    garment_repo = GarmentRepository()
    garment = await garment_repo.get(db, garment_id)
    
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")
    
    if garment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated = await garment_repo.update(db, garment, garment_update)
    return updated
```

**DELETE /api/v1/garments/{id} - Удалить вещь**

```python
@router.delete("/{garment_id}", status_code=204)
async def delete_garment(
    garment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить вещь из гардероба"""
    garment_repo = GarmentRepository()
    garment = await garment_repo.get(db, garment_id)
    
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")
    
    if garment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await garment_repo.delete(db, garment)
```

#### 2.1.4.5 API эндпоинты виртуальной примерки

**POST /api/v1/tryon - Создать задачу примерки**

```python
@router.post("/", response_model=TryOnResponse)
async def create_tryon(
    request: TryOnRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать задачу виртуальной примерки
    
    Request:
        {
            "garment_id": 123,
            "person_image": "base64_encoded_image",
            "garment_image": "base64_encoded_image",
            "model_type": "hd",  # "hd" или "dc"
            "category": 0         # 0, 1 или 2
        }
    
    Response:
        {
            "id": "task_id",
            "status": "processing",
            "created_at": "2024-01-01T00:00:00",
            "result_image": null,  # Будет заполнен при завершении
            "error": null
        }
    """
    # Использовать use case
    use_case = TryOnUseCase(ml_gateway)
    
    # Валидация
    use_case.validate(request)
    
    # Проверить кэш
    cached = await cache.get(...)
    if cached:
        return cached
    
    # Создать задачу
    task_id = await queue.enqueue_tryon_task({
        "garment_id": request.garment_id,
        "user_id": current_user.id,
        "model_type": request.model_type,
        "category": request.category,
        "images": {
            "garment": request.garment_image,
            "person": request.person_image
        }
    })
    
    # Сохранить в БД
    tryon_repo = TryOnRepository()
    tryon = await tryon_repo.create(
        db,
        obj_in={
            "task_id": task_id,
            "garment_id": request.garment_id,
            "user_id": current_user.id,
            "model_type": request.model_type,
            "category": request.category,
            "status": "processing"
        }
    )
    
    return TryOnResponse(
        id=tryon.id,
        task_id=task_id,
        status="processing",
        created_at=tryon.created_at
    )
```

**GET /api/v1/tryon/{id} - Получить статус примерки**

```python
@router.get("/{tryon_id}", response_model=TryOnResponse)
async def get_tryon(
    tryon_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить статус и результат примерки"""
    tryon_repo = TryOnRepository()
    tryon = await tryon_repo.get(db, tryon_id)
    
    if not tryon:
        raise HTTPException(status_code=404, detail="Try-on not found")
    
    if tryon.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Если статус завершен, вернуть результат
    if tryon.status == "completed":
        result = await cache.get_result(tryon.task_id)
        tryon.result_image = result.get("result_image")
    
    return tryon
```

#### 2.1.4.6 API эндпоинты загрузки медиа

**POST /api/v1/media - Загрузить изображение**

```python
@router.post("/upload", response_model=MediaResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузить медиа файл
    
    Поддерживаемые форматы: jpg, jpeg, png, gif
    Максимальный размер: 10MB
    """
    # Валидация файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=413, detail="File too large")
    
    # Прочитать и обработать файл
    content = await file.read()
    
    # Проверить целостность изображения
    try:
        image = Image.open(io.BytesIO(content))
        image.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Сгенерировать имя файла
    file_id = uuid.uuid4()
    file_path = f"media/{current_user.id}/{file_id}.jpg"
    
    # Загрузить в S3
    s3_client.upload_file(file_path, content)
    
    # Сохранить метаданные в БД
    media_repo = MediaRepository()
    media = await media_repo.create(
        db,
        obj_in={
            "user_id": current_user.id,
            "file_path": file_path,
            "file_name": file.filename,
            "file_size": file.size,
            "content_type": file.content_type
        }
    )
    
    return MediaResponse(
        id=media.id,
        url=s3_client.get_public_url(file_path),
        created_at=media.created_at
    )
```

**GET /api/v1/media/{id} - Получить медиа файл**

```python
@router.get("/{media_id}")
async def get_media(
    media_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить и вернуть медиа файл"""
    media_repo = MediaRepository()
    media = await media_repo.get(db, media_id)
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Получить файл из S3
    file_content = s3_client.download_file(media.file_path)
    
    return Response(
        content=file_content,
        media_type=media.content_type,
        headers={"Content-Disposition": f"inline; filename={media.file_name}"}
    )
```

#### 2.1.4.7 Обработка ошибок и коды состояния

```python
# core/errors.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

def setup_exception_handlers(app: FastAPI):
    """Настроить обработчики ошибок"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "status": exc.status_code,
                    "detail": exc.detail,
                    "path": str(request.url)
                }
            },
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "status": 422,
                    "detail": "Validation error",
                    "errors": exc.errors()
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "status": 500,
                    "detail": "Internal server error"
                }
            },
        )
```

**Таблица кодов состояния HTTP**

| Код | Название | Использование |
|-----|----------|---------------|
| 200 | OK | Успешный GET, PUT, DELETE запрос |
| 201 | Created | Успешный POST запрос создания ресурса |
| 204 | No Content | Успешный DELETE запрос |
| 400 | Bad Request | Ошибка валидации входных данных |
| 401 | Unauthorized | Отсутствует авторизация |
| 403 | Forbidden | Недостаточно прав доступа |
| 404 | Not Found | Ресурс не найден |
| 409 | Conflict | Конфликт (например, дубликат) |
| 413 | Payload Too Large | Файл слишком большой |
| 422 | Unprocessable Entity | Ошибка валидации схемы |
| 500 | Internal Server Error | Ошибка сервера |
| 503 | Service Unavailable | Сервис недоступен |

#### 2.1.4.8 CORS и безопасность

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:3000", "http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # 1 час кэширования preflight
)
```

#### 2.1.4.9 Документация API (Swagger UI)

FastAPI автоматически генерирует интерактивную документацию API:

```
GET /docs          # Swagger UI документация
GET /redoc         # ReDoc документация
GET /openapi.json  # OpenAPI спецификация
```

---

### 2.1.5 Организация структуры репозитория и конфигурации проекта

#### 2.1.5.1 Структура репозитория

```
Diplom/
├── README.md                  # Описание проекта
├── Config.py                  # Конфигурация проекта
├── requirements.txt           # Зависимости Python (общие)
├── environment.yml            # Conda окружение
├── docker-compose.yml         # Основной docker-compose
├── docker-compose.gpu.yml     # Docker-compose с GPU поддержкой
│
├── backend/                   # Серверная часть
│   ├── Dockerfile            # Docker для сервера
│   ├── pyproject.toml        # Конфигурация зависимостей
│   ├── requirements-test.txt # Тестовые зависимости
│   ├── pytest.ini            # Конфигурация pytest
│   ├── coverage.xml          # Отчет тестового покрытия
│   ├── alembic.ini           # Конфигурация Alembic
│   ├── run_server.py         # Запуск FastAPI сервера
│   ├── run_migrations.py     # Запуск миграций БД
│   ├── run_tryon_job.py      # Запуск периодической задачи примерки
│   ├── run_tryon_worker.py   # Запуск worker-а для примерки
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # Главная точка входа
│   │   ├── api/               # API层
│   │   ├── application/       # Бизнес-логика
│   │   ├── core/              # Ядро (конфиг, ошибки)
│   │   ├── domain/            # Бизнес-сущности
│   │   ├── infrastructure/    # Инфраструктура
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── presentation/      # Слой представления
│   │   ├── repositories/      # Data access
│   │   └── schemas/           # Pydantic схемы
│   │
│   ├── alembic/               # Миграции БД
│   │   ├── env.py
│   │   ├── versions/
│   │   └── script.py.mako
│   │
│   ├── tests/                 # Unit тесты
│   │   ├── test_api.py
│   │   ├── test_use_cases.py
│   │   └── test_repositories.py
│   │
│   └── htmlcov/               # Отчет покрытия кода
│
├── frontend/                  # Фронтенд часть
│   ├── Dockerfile
│   ├── package.json
│   ├── jsconfig.json
│   ├── public/
│   ├── src/
│   ├── build/
│   ├── coverage/
│   └── nginx/
│
├── ml/                        # ML модули
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── requirements-test.txt
│   ├── swipeit_ml/            # ML код
│   │   ├── models/
│   │   ├── preprocessing/
│   │   ├── training/
│   │   └── inference/
│   ├── checkpoints/           # Обученные модели
│   ├── scripts/               # Скрипты обучения
│   ├── tests/
│   └── examples/
│
├── batch/                     # Batch обработка
│   ├── Dockerfile
│   ├── airflow/               # Airflow DAG-и
│   └── swipeit_daily_metrics_job.py
│
├── docs/                      # Документация
│   └── secret-store.md
│
├── image/                     # Изображения и ассеты
│   ├── logo/
│   └── screenshots/
│
└── scripts/                   # Утилиты и скрипты
    └── data/
```

#### 2.1.5.2 Конфигурация проекта (Config.py)

Главный файл конфигурации централизует все настройки для разных частей проекта:

```python
# Config.py
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from pydantic import AnyUrl, BaseSettings

ROOT_DIR = Path(__file__).resolve().parent
ENV_FILE = ROOT_DIR / ".env"

class BackendSettings(BaseSettings):
    """Конфигурация серверной части"""
    
    # API
    API_V1: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    
    # Database
    DB_URL: AnyUrl = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/swipeit")
    DB_ASYNC_URL: AnyUrl | None = None
    
    @property
    def async_database_url(self) -> str:
        if self.DB_ASYNC_URL:
            return str(self.DB_ASYNC_URL)
        return str(self.DB_URL).replace("postgresql://", "postgresql+asyncpg://")
    
    # S3 Storage
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "swipeit-media")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_SECURE: bool = os.getenv("S3_SECURE", "false").lower() == "true"
    S3_PUBLIC_URL: Optional[str] = os.getenv("S3_PUBLIC_URL")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Try-On Configuration
    TRYON_CACHE_TTL_SECONDS: int = int(os.getenv("TRYON_CACHE_TTL_SECONDS", 86400))
    TRYON_QUEUE_NAME: str = os.getenv("TRYON_QUEUE_NAME", "tryon:queue")
    TRYON_DEAD_LETTER_QUEUE_NAME: str = os.getenv("TRYON_DEAD_LETTER_QUEUE_NAME", "tryon:dead-letter")
    TRYON_QUEUE_BLOCK_TIMEOUT_SECONDS: int = int(os.getenv("TRYON_QUEUE_BLOCK_TIMEOUT_SECONDS", 5))
    TRYON_QUEUE_MAX_RETRIES: int = int(os.getenv("TRYON_QUEUE_MAX_RETRIES", 2))
    TRYON_RATE_LIMIT_REQUESTS: int = int(os.getenv("TRYON_RATE_LIMIT_REQUESTS", 5))
    TRYON_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("TRYON_RATE_LIMIT_WINDOW_SECONDS", 60))
    TRYON_RETENTION_DAYS: int = int(os.getenv("TRYON_RETENTION_DAYS", 7))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"

@dataclass(frozen=True)
class FrontendSettings:
    """Конфигурация фронтенд части"""
    app_name: str = "SwipeIt"
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    use_mock_data: bool = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    mock_delay_ms: int = int(os.getenv("MOCK_DELAY_MS", 300))

@dataclass(frozen=True)
class MLSettings:
    """Конфигурация ML части"""
    model_checkpoint_path: str = os.getenv(
        "MODEL_CHECKPOINT_PATH",
        "checkpoints/tryon_model.pth"
    )
    device: str = os.getenv("ML_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
    batch_size: int = int(os.getenv("ML_BATCH_SIZE", 8))
    num_workers: int = int(os.getenv("ML_NUM_WORKERS", 4))

class ProjectConfig:
    def __init__(self):
        self.backend = BackendSettings()
        self.frontend = FrontendSettings()
        self.ml = MLSettings()

def load_project_config() -> ProjectConfig:
    """Загрузить конфигурацию проекта"""
    return ProjectConfig()
```

#### 2.1.5.3 Docker компоновка

**docker-compose.yml** - основной docker-compose для разработки:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: swipeit-postgres
    environment:
      POSTGRES_DB: swipeit
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: swipeit-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # MinIO S3 Storage
  minio:
    image: minio/minio:latest
    container_name: swipeit-minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: swipeit-backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/swipeit
      REDIS_URL: redis://redis:6379/0
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_BUCKET_NAME: swipeit-media
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: python run_server.py

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: swipeit-frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
  minio_data:
```

**docker-compose.gpu.yml** - для обучения ML моделей с GPU:

```yaml
version: '3.8'

services:
  ml-training:
    build:
      context: ./ml
      dockerfile: Dockerfile
    container_name: swipeit-ml-training
    environment:
      CUDA_VISIBLE_DEVICES: "0"
      ML_DEVICE: cuda
    ports:
      - "6006:6006"  # TensorBoard
    volumes:
      - ./ml:/workspace
      - ml_cache:/root/.cache
    stdin_open: true
    tty: true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  ml_cache:
```

#### 2.1.5.4 Миграции БД (Alembic)

Система использует Alembic для версионирования схемы БД:

```bash
# alembic/versions/001_initial.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_users_email', 'email'),
        sa.Index('ix_users_username', 'username'),
    )

def downgrade():
    op.drop_table('users')
```

**Команды для работы с миграциями**:

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "Add users table"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1

# Просмотреть текущую версию
alembic current
```

#### 2.1.5.5 Переменные окружения (.env)

```bash
# .env (не добавляется в git)

# Backend
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/swipeit
REDIS_URL=redis://localhost:6379/0

# S3 Storage
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=swipeit-media

# Try-On Settings
TRYON_CACHE_TTL_SECONDS=86400
TRYON_RATE_LIMIT_REQUESTS=5
TRYON_RATE_LIMIT_WINDOW_SECONDS=60

# Frontend
VITE_API_BASE_URL=http://localhost:8000

# ML Settings
ML_DEVICE=cuda
MODEL_CHECKPOINT_PATH=checkpoints/tryon_model.pth
```

#### 2.1.5.6 Скрипты запуска

**run_server.py** - запуск FastAPI сервера:

```python
#!/usr/bin/env python3
"""Запуск FastAPI сервера"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Перезагрузка при изменении кода (только для разработки)
        log_level="info",
    )
```

**run_migrations.py** - применить миграции:

```python
#!/usr/bin/env python3
"""Применить миграции БД"""

from alembic.config import Config
from alembic.command import upgrade
import sys

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    run_migrations()
```

**run_tryon_worker.py** - запуск worker-а для обработки примерок:

```python
#!/usr/bin/env python3
"""Запуск worker-а для обработки задач примерки"""

import asyncio
from app.infrastructure.workers.tryon_worker import TryOnWorker

async def main():
    worker = TryOnWorker()
    print("Starting Try-On Worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 2.1.5.7 Тестирование (pytest)

**pytest.ini** - конфигурация pytest:

```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=app
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

**Пример unit теста**:

```python
# tests/test_repositories.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.repositories.garment_repo import GarmentRepository
from app.presentation.api.schemas.garment import GarmentCreate

@pytest.mark.asyncio
async def test_create_garment(db: AsyncSession):
    """Тест создания вещи"""
    repo = GarmentRepository()
    garment_data = GarmentCreate(
        name="Blue Shirt",
        category="tops",
        user_id=1
    )
    
    garment = await repo.create(db, obj_in=garment_data)
    
    assert garment.id is not None
    assert garment.name == "Blue Shirt"
    assert garment.category == "tops"
```

#### 2.1.5.8 Лучшие практики организации кода

1. **Разделение ответственности**: каждый модуль отвечает за одну задачу
2. **DRY (Don't Repeat Yourself)**: переиспользование кода через базовые классы
3. **SOLID принципы**: особенно инверсия зависимостей через ports
4. **Асинхронность**: все операции I/O выполняются асинхронно
5. **Типизация**: использование type hints для всех функций
6. **Тестируемость**: слабая связанность компонентов для легкого тестирования
7. **Документирование**: docstrings для всех public функций и классов

---

## Выводы по разделу 2.1

В этом разделе был проведен анализ архитектуры и организации серверной части системы SwipeIt:

1. **Архитектура на основе Clean Architecture** обеспечивает четкое разделение ответственности и упрощает масштабирование
2. **Использование современного стека технологий** (FastAPI, SQLAlchemy, Redis, S3) позволяет построить высокопроизводительное приложение
3. **Интеграция ML-алгоритмов** через портальный паттерн позволяет асинхронно обрабатывать сложные вычисления
4. **REST API** соответствует лучшим практикам и обеспечивает удобный интерфейс для клиентов
5. **Организация репозитория** позволяет команде эффективно работать над разными компонентами системы

Все компоненты системы тесно интегрированы и работают вместе для обеспечения функциональности виртуальной примерки одежды.

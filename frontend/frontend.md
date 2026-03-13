Frontend-подпроект (frontend)
Этот каталог содержит React-клиент, UI-страницы, слой Clean Architecture (domain/application/infrastructure), mock-API и unit-тесты.

Корень frontend

.gitignore — исключения для node_modules, build, coverage, локальных .env и кэшей.
.env.example — пример env-переменных фронта (REACT_APP_*).
Config.py — Python-обертка для env-переменных фронта (формальное требование по отдельному config-файлу).
jsconfig.json — настройки путей/резолвинга для JS и IDE.
package.json — npm-скрипты, зависимости React, Jest coverage-пороги (>=70%).
package-lock.json — lock-файл npm с зафиксированным деревом зависимостей.
README.md — документация фронта: запуск, mock-режим, тесты, покрытие.
Папка public/

public/index.html — HTML-шаблон, куда монтируется React-приложение.
public/manifest.json — PWA-манифест (имя/иконки/метаданные).
public/service-worker.js — service worker для оффлайн/кэш-логики.
Папка src/ (entrypoint и базовые файлы)

src/index.js — входная точка React, рендер приложения и подключение AuthProvider.
src/serviceWorker.js — регистрация/анрегистрация service worker.
src/App.js — роутинг, сплеш-экраны, protected-роуты.
src/App.css — пустой/резервный css-файл для App.
Папка src/config/

src/config/appConfig.js — централизованный конфиг фронта (env, ключи хранилища, mock/delay, demo/guest аккаунты).
src/config/index.js — реэкспорт config-модулей.
src/config/appConfig.test.js — тесты иммутабельности и обязательных ключей конфига.
src/config/index.test.js — тест корректного реэкспорта из config/index.js.
Папка src/context/

src/context/AuthContext.js — auth-состояние приложения: init/login/register/logout через use-case слой и mock-репозиторий.
Папка src/hooks/

src/hooks/useAuth.js — hook-доступ к AuthContext с проверкой использования внутри провайдера.
src/hooks/useAuth.css — пустая заготовка стилей для hook-related UI.
Папка src/core/ (Clean Architecture)

src/core/domain/entities/

userEntity.js — создание/санитизация user-сущности.
userEntity.test.js — тесты создания, fallback-avatar, sanitize-логики.
src/core/domain/services/

authPolicy.js — доменные правила валидации (email/password/username, guest email, avatar url).
authPolicy.test.js — тесты всех правил/ветвлений authPolicy.
src/core/application/usecases/

initializeAuthSession.js — use-case инициализации auth-сессии.
initializeAuthSession.test.js — тест делегирования репозиторию.
loginUser.js — use-case логина с доменной валидацией.
loginUser.test.js — тесты ошибок валидации и вызова репозитория.
registerUser.js — use-case регистрации с доменной валидацией.
registerUser.test.js — тесты валидации и успешной регистрации через репозиторий.
logoutUser.js — use-case логаута.
logoutUser.test.js — тест, что вызывается repository.logout.
getFeedPosts.js — use-case получения ленты постов.
getFeedPosts.test.js — тест делегирования getFeedPosts в репозиторий.
src/core/infrastructure/mocks/

posts.js — mock-массив постов для ленты.
src/core/infrastructure/repositories/

mockAuthRepository.js — mock-репозиторий авторизации (session init, login/register/logout, localStorage).
mockAuthRepository.test.js — тесты сценариев demo/guest/user, дубликатов, invalid credentials, очистки сессии.
mockPostRepository.js — mock-репозиторий постов (возврат mock-постов с задержкой).
mockPostRepository.test.js — тест возврата mock-ленты и работы с дефолтным конфигом.
src/core/infrastructure/storage/

browserStorage.js — обертка над localStorage (get/set/remove).
browserStorage.test.js — тест делегирования операций переданному storage.
Папка src/services/

src/services/swipeService.js — утилиты навигации по индексам (next/prev с циклическим переходом).
src/services/swipeService.test.js — тесты расчета next/prev индексов.
src/services/api/auth.js — API-адаптер auth через use-cases и mockAuthRepository.
src/services/api/posts.js — API-адаптер ленты через use-case getFeedPosts.
src/services/api/comments.js — mock API комментариев (чтение/создание).
src/services/api/likes.js — mock API лайков (toggle).
src/services/api/tryon.js — mock API виртуальной примерки.
src/services/api/users.js — mock API пользователя.
src/services/api/wardrobe.js — mock API гардероба.
Папка src/utils/

src/utils/constants.js — константы маршрутов и валидации.
src/utils/formatDate.js — форматирование даты/даты-времени.
src/utils/formatDate.test.js — тесты корректного форматирования и обработки некорректных значений.
src/utils/validateForm.js — валидация login/register форм.
src/utils/validateForm.test.js — тесты ошибок и успешной валидации форм.
Папка src/pages/

src/pages/FeedPage/FeedPage.js — основная лента (навигация, свайпы, действия с постами, вкладки).
src/pages/FeedPage/FeedPage.css — стили ленты.
src/pages/LoginPage/LoginPage.js — страница входа (обычный и гостевой вход через AuthContext).
src/pages/LoginPage/LoginPage.css — стили страницы логина.
src/pages/RegisterPage/RegisterPage.js — страница регистрации через AuthContext/use-case.
src/pages/RegisterPage/RegisterPage.css — стили регистрации.
src/pages/ProfilePage/ProfilePage.js — профиль, фото для try-on, гостевой режим, выход.
src/pages/ProfilePage/ProfilePage.css — стили профиля.
src/pages/SearchPage/SearchPage.js — UI-страница поиска.
src/pages/SearchPage/SearchPage.css — стили поиска.
src/pages/TryOnPage/TryOnPage.js — экран виртуальной примерки.
src/pages/TryOnPage/TryOnPage.css — стили экрана примерки.
src/pages/WardrobePage/WardrobePage.js — экран гардероба.
src/pages/WardrobePage/WardrobePage.css — стили гардероба.
src/pages/ChatPage/ChatPage.js — UI-страница чатов.
src/pages/ChatPage/ChatPage.css — стили чатов.
src/pages/ForgotPasswordPage/ForgotPasswordPage.js — страница восстановления пароля.
src/pages/ForgotPasswordPage/ForgotPasswordPage.css — пустая/резервная таблица стилей.
Папка src/components/

src/components/SplashScreen/SplashScreen.js — splash-компонент при старте/загрузке.
src/components/SplashScreen/SplashScreen.css — стили splash.
src/components/Post/post.js — карточка поста с лайком/комментами/инфо.
src/components/Post/post.css — пустая/резервная таблица стилей поста.
src/components/Post/PostActions.js — пустая заготовка action-компонента.
src/components/Post/PostAction.css — пустая заготовка стилей action-компонента.
src/components/CommentsModal/CommentsModal.js — пустая заготовка модального окна комментариев.
src/components/CommentsModal/CommentsModal.css — пустая заготовка стилей comments modal.
src/components/NotificationItem/NotificationItem.js — пустая заготовка элемента уведомления.
src/components/NotificationItem/NotificationItem.css — пустая заготовка стилей уведомления.
src/components/OutfitCollection/OutfitCollection.js — пустая заготовка коллекции образов.
src/components/OutfitCollection/OutfitCollection.css — пустая заготовка стилей коллекции.
src/components/SearchBar/SearchBar.js — пустая заготовка поисковой строки.
src/components/SearchBar/SearchBar.css — пустая заготовка стилей поисковой строки.
src/components/Tabs/Tabs.js — пустая заготовка вкладок.
src/components/Tabs/Tabs.css — пустая заготовка стилей вкладок.
src/components/TryOnInterface/TryOnInterface.js — пустая заготовка интерфейса примерки.
src/components/TryOnInterface/TryOnInterface.css — пустая заготовка стилей интерфейса примерки.
src/components/UserCard/UserCard.js — пустая заготовка карточки пользователя.
src/components/UserCard/UserCard.css — пустая заготовка стилей карточки пользователя.
src/components/WardrobeUpload/WardrobeUpload.js — пустая заготовка загрузки вещей.
src/components/WardrobeUpload/WardrobeUpload.css — пустая заготовка стилей загрузки вещей.
Папка src/styles/

src/styles/global.css — глобальные стили приложения.
src/styles/App.css — стили контейнера/базового layout.
src/styles/SplashScreen.css — стили общего сплеш-экрана.
src/styles/animations.css — пустая заготовка под общие анимации.
src/styles/variables.css — пустая заготовка CSS-переменных.
Папка src/assets/icons/

comments.png — иконка комментариев.
download.png — иконка загрузки.
feed.png — иконка ленты.
like.png — иконка лайка.
profile.png — иконка профиля.
search.png — иконка поиска.
wardrobe.png — иконка гардероба.
Папка coverage/ (генерируется тестами)

coverage/lcov.info — coverage-данные в формате LCOV.
coverage/coverage-final.json — финальные coverage-метрики в JSON.
coverage/clover.xml — coverage-отчет в формате Clover XML.
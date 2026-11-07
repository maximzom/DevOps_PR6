# Практична робота №6. Автоматизоване тестування та розгортання Python-сервісу

Навчальний проєкт мікросервісу на Python (Flask) із налаштованим CI/CD процесом у GitHub Actions, модульним тестуванням (`pytest`), інфраструктурним тестуванням контейнера (`Testinfra`), діагностикою та механізмом автоматичного відкату (`rollback`).

---

## 1. Структура проєкту та опис середовища

- `app/main.py` — вебсервіс із маршрутами `GET /health` (стан сервісу) та `GET /version` (поточна версія).
- `Dockerfile` — опис образу на базі `python:3.11-slim`, запуск WSGI-сервера `gunicorn` від непривілейованого користувача `appuser` (UID `10001`).
- `compose.yaml` — конфігурація Docker Compose з підтримкою тегування образів через змінну `IMAGE_TAG`.
- `.env.example` — шаблон змінних середовища (`APP_PORT`, `APP_VERSION`, `APP_STATUS`, `IMAGE_TAG`).
- `tests/test_unit.py` — модульні тести `pytest` (фікстура клієнта, параметризація, `monkeypatch`).
- `tests/test_infra.py` — інфраструктурні тести `Testinfra` для перевірки запущеного контейнера.
- `.github/workflows/ci-cd.yml` — конфігурація CI/CD конвеєра з діагностикою та автоматичним відкатом.

---

## 2. Команди запуску застосунку

1. Створіть локальний файл конфігурації `.env` із шаблону:
   ```bash
   cp .env.example .env
   ```

2. Зберіть образ та запустіть контейнер у фоновому режимі через Docker Compose:
   ```bash
   docker compose up -d --build
   ```

3. Перевірте стан запущеного контейнера:
   ```bash
   docker compose ps
   ```

---

## 3. Команди перевірки та тестування

1. **HTTP-перевірка маршрутів сервісу (із тайм-аутом 3 секунди):**
   ```bash
   curl --fail --max-time 3 http://localhost:5000/health
   curl --fail --max-time 3 http://localhost:5000/version
   ```

2. **Запуск модульних тестів `pytest` (з генерацією XML-звіту):**
   ```bash
   pytest tests/test_unit.py -v --junitxml=reports/pytest-unit.xml
   ```

3. **Запуск інфраструктурних тестів `Testinfra` для запущеного контейнера:**
   *(Перевіряє наявність файлів, роботу процесу `gunicorn`, прослуховування порту `5000` та роботу не від `root`)*
   ```bash
   pytest --hosts=docker://devops_service_app tests/test_infra.py -v --junitxml=reports/testinfra.xml
   ```

4. **Перегляд логів контейнера для діагностики:**
   ```bash
   docker compose logs --no-color
   ```

---

## 4. Команди версіонування образу та відкату (Rollback)

1. **Збірка образу з позначенням коротким хешем поточного коміту та розгортання:**
   ```bash
   export CURR_SHA=$(git rev-parse --short HEAD)
   docker build -t devops-service:$CURR_SHA .
   IMAGE_TAG=$CURR_SHA docker compose up -d --force-recreate
   ```

2. **Повернення попередньої стабільної версії образу (відкат до `HEAD~1`):**
   ```bash
   export PREV_SHA=$(git rev-parse --short HEAD~1)
   git archive HEAD~1 | docker build -t devops-service:$PREV_SHA -
   IMAGE_TAG=$PREV_SHA docker compose up -d --force-recreate
   ```

3. **Повторна перевірка працездатності сервісу після відкату:**
   ```bash
   curl --fail --max-time 3 http://localhost:5000/health
   pytest --hosts=docker://devops_service_app tests/test_infra.py -v
   ```

4. **Зупинка та видалення контейнерів:**
   ```bash
   docker compose down
   ```

---

## 5. Обґрунтування розміщення (IaaS та PaaS)

Для перенесення цього рішення в хмару за моделлю **IaaS** (наприклад, AWS EC2 або Google Compute Engine) достатньо орендувати віртуальну Linux-машину з встановленим Docker Compose, куди CI/CD пайплайн доставлятиме образи через SSH, тоді як при переході на **PaaS** (AWS App Runner, Google Cloud Run або Azure Container Apps) достатньо передавати зібраний Docker-образ із реєстру без необхідності адмініструвати сервер. У моделі **IaaS** за оновлення операційної системи, патчі безпеки ядра, налаштування фаєрволу та Docker-рантайму повністю відповідає команда розробників (DevOps-інженер), а у моделі **PaaS** відповідальність за базову ОС, середовище виконання та оркестрацію бере на себе хмарний провайдер, залишаючи розробнику лише код застосунку та залежності всередині `Dockerfile`. Основні витрати в IaaS формують постійно увімкнені обчислювальні інстанси (vCPU/RAM), дискове сховище, публічна IPv4-адреса та вихідний трафік, тоді як у PaaS оплата стягується за фактично спожитий час CPU/пам'яті під час обробки запитів, зберігання образів у Container Registry та мережевий трафік.
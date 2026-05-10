Веб-приложение для учёта финансовых операций.
- **finance_app** (порт `5000`) — основное приложение: регистрация, авторизация, операции, управление аккаунтом.
- **rate_service** (порт `5001`) — внешний сервис курсов валют.

## Запуск проекта
### Создание виртуального окружения
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux
python3 -m venv venv
source venv/bin/activate
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка конфигурации
Создать файл `.env` в корне `finance_app/` на основе `.env.example`:
```bash
cp .env.example .env
```

### Инициализация базы данных
**Один раз** перед первым запуском:
```bash
cd finance_app
python init_db.py
```

###  Запуск приложений

#### Терминал 1: Сервис курсов валют
```bash
cd rate_service
python app.py
```
- Запустится на `http://127.0.0.1:5001`

### Терминал 2: Основное приложение
```bash
cd finance_app
python app.py
```
- Запустится на `http://127.0.0.1:5000`
---

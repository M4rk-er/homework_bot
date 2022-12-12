# Telegram-homework Python bot
### Telegram бот на Python, который обращается к API Яндекс.Практикум и проверяет статус проверки работы. При изменении статуса проверки присылает сообщение с статусом работы: взята ли на ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

### Технологии
- Python Telegram Bot
- API
- Requests

# Для развертывания проекта:
- Клонировать репрозиторий
```
git@github.com:M4rk-er/homework_bot.git
```
```
cd homework
```
- Установаите виртуальное окружение
``` 
python -m venv venv ``` / ``` python3 -m venv venv 
```
>
- Активируйте виртуальное окружение
``` 
source venv/Scripts/activate ``` /  ``` . venv bin activate 
```
>
- Установите requirements
``` 
pip install -r requirements.txt
```
- В файле homework.py вести свои данные в переменных ``` PRACTICUM_TOKEN  ```, ``` TELEGRAM_TOKEN ```, ``` TELEGRAM_CHAT_ID ```
- В переменной ``` RETRY_TIME ``` установить частоту повторения запросов к серверу в секундах
- Запустить проект
```
python homework.py
```

# Vepay Notifier - Telegram-нотификации об инцидентах

Параметры окружения **.env**:
 - **TOKEN** api-токен нужного бота (брать из @BotFather)
 - **WEBHOOK_IS_ACTIVE** True, если используем webhook | False, если хотим постоянно опрашивать сервера Telegram на наличие новых событий
 - **WEBHOOK_HOST** хост, к которому будет цепляться webhook серверов Telegram
 - **WEBHOOK_PATH** путь до нужного ресурса хоста в формате /hook. Telegram советует использовать в наименовании пути api-token для идентификации источника запроса
 - **WEBAPP_HOST** хост webserverа
 - **WEBAPP_PORT** порт webservera
 - **ACCEPTED_USER_ID** список пользователей, которым разрешено пользоваться ботом
 - **PROVIDER_{NAME}** чаты, по которым уйдёт рассылка по указанному провайдеру NAME

<hr>

**Как добавить нового провайдера**
1. В *const.py* создать константу с именем провайдера
2. В *settings.py* добавить новую константу в список *providers*
3. Добавить новую переменную окружения в *.env*
4. В *settings.py* добавить новую переменную окружения в качестве ключа словаря *chat_id*, значением указать *os.getenv('Название новой переменной окружения').split(',')*

<hr>

Сценарии:

1. /start <br>
 1.1. Выбор ситуации: #технический_сбой или #технические_работы <br>
 1.2. Выбор провайдера <br>
 1.3. Указание даты и времени события <br>
 1.4. Описание ситуации <br>
 1.5. Рассылка по чатам, указанным в settings.py, на основе выбранного провайдера <br>
   

2. /start <br>
 2.1. Выбор ситуации: #технический_сбой_устранён или #технические_работы_завершены <br>
 2.2. Выбор провайдера <br>
 2.3. Рассылка по чатам, указанным в settings.py, на основе выбранного провайдера


3. /cancel <br>
 3.1 Завершение работы на любом этапе до рассылки

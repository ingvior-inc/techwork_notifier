# Vepay Notifier - Telegram-нотификации об инцидентах

Параметры окружения **.env**:
 - **TOKEN** - api-токен нужного бота (брать из @BotFather)
 - **WEBHOOK_IS_ACTIVE** - True, если используем webhook | False, если хотим постоянно опрашивать сервера Telegram на наличие новых событий
 - **WEBHOOK_HOST** хост, к которому будет цепляться webhook серверов Telegram
 - **WEBHOOK_PATH** путь до нужного ресурса хоста в формате /hook. Telegram советует использовать в наименовании пути api-token для идентификации источника запроса
 - **WEBAPP_HOST** хост webserverа
 - **WEBAPP_PORT** порт webservera

<hr>

В **settings.py** необходимо добавить id пользователей, которые смогут использовать бота (переменная **accepted_user_id**), а также id чатов, по которым будет идти рассылка (**chat_id**)

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

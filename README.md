# Vepay Notifier - Telegram-нотификации об инцидентах

Параметры окружения **.env**:
 - **TOKEN** api-токен нужного бота (брать из @BotFather)
 - **WEBHOOK_IS_ACTIVE** True, если используем webhook | False, если хотим постоянно опрашивать сервера Telegram на наличие новых событий
 - **WEBHOOK_HOST** хост, к которому будет цепляться webhook серверов Telegram
 - **WEBHOOK_PATH** путь до нужного ресурса хоста в формате /hook. Telegram советует использовать в наименовании пути api-token для идентификации источника запроса
 - **WEBAPP_HOST** хост webserverа
 - **WEBAPP_PORT** порт webservera
 - **DB_NAME** название БД PostgreSQL
 - **DB_USER** имя администратора БД PostgreSQL
 - **DB_PASSWORD** пароль администратора БД PostgreSQL

<hr>

**Как добавить нового провайдера**
1. В таблице *providers* создать строку с именем провайдера
2. В таблице *chats* добавить строки с id нужных чатов и id созданного в п.1 провайдера

<hr>

Сценарии:

1. /start <br>
 1.1. Выбор ситуации: #технический_сбой или #технические_работы <br>
 1.2. Выбор провайдера <br>
 1.3. Указание даты и времени события <br>
 1.4. Описание ситуации <br>
 1.5. Рассылка по чатам, указанным в таблице chats, на основе выбранного провайдера <br>
   

2. /start <br>
 2.1. Выбор ситуации: #технический_сбой_устранён или #технические_работы_завершены <br>
 2.2. Выбор провайдера <br>
 2.3. Рассылка по чатам, указанным в таблице chats, на основе выбранного провайдера

3. /edit <br>
 4.1. Выбор ситуации: Добавить чаты или Удалить чаты
 4.2. Ввод списка чатов через запятую
 4.3. Добавление/удаление чатов в таблице chats
   
4. /edit <br>
 5.1. Выбор ситуации: Добавить провайдера или Удалить провайдера
 5.2. Ввод названия провайдера
 5.3. Добавление/удаление провайдера в таблице providers
   
5. /check_list <br>
 6.1. Вывод списка провайдеров и относящихся к ним чатов

6. /cancel <br>
 3.1 Завершение работы на любом промежуточном этапе

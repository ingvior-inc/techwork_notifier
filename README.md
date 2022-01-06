# Telegram notifications about incidents

## Environment variables
 - **TOKEN** bot API token 
 <br><br>
 - **WEBHOOK_IS_ACTIVE** True, if you want to use webhook (getting callbacks) | False, if you want to use polling Telegram servers
 - **WEBHOOK_HOST** host for sending callbacks from Telegram
 - **WEBHOOK_PATH** host's endpoint path (example - /hook). Telegram advises using api-token in the path name to identify the source of the request
 - **WEBAPP_HOST** internal webserver host
 - **WEBAPP_PORT** internal webserver port 
 <br><br>
 - **POSTGRES_HOST** host with PostgreSQL
 - **POSTGRES_DB** name of PostgreSQL DB
 - **POSTGRES_USER** admin username of PostgreSQL DB
 - **POSTGRES_PASSWORD** admin password of PostgreSQL DB

<hr>

## How to start

1. Create and fill .env file in root directory. Minimum required vars:
```bash
TOKEN
```

2. Build and run docker containers!
```bash
docker-compose up --build -d
```

<hr>

## Bot's Commands / Scenarios

1. /start : creating an incident start notification <br>
 1.1. Choice of situation from the const class *Situations* <br>
 1.2. Choice of provider from the table *providers* <br>
 1.3. Writing date and time of the incident <br>
 1.4. Writing description <br>
 1.5. Sending to the chats specified in the chats table, based on the selected provider <br>
   
2. /end : creating an incident end notification <br>
 2.1. Choice of situation from the const class *Situations* <br>
 2.2. Choice of provider from the table *providers* <br>
 2.3. Sending to the chats specified in the chats table, based on the selected provider <br>
   
3. /del : deleting last sended messages <br>
 3.1. Deleting last messages that was sended

4. /edit_recipients : editing chats list <br>
 4.1. Choice of situation: Add chats or Delete chats <br>
 4.2. Choice of chat from the table *chats_for_allocate* <br>
 4.3. Adding / Removing chat in *chats* table <br>
   
5. /edit_providers : editing providers list <br>
 5.1. Choice of situation: Add provider or Remove provider <br>
 5.2. Provider name input <br>
 5.3. Adding / Removing a provider in *providers* table <br>
   
6. /check_recipients : outputting providers and their chats list <br>
 6.1. Show providers and related chats <br>

7. /cancel <br>
 3.1. Stop scenario at any stage <br>

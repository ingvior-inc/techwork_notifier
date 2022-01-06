CREATE TABLE IF NOT EXISTS providers
(
    provider_desc TEXT   NOT NULL,
    id            SERIAL NOT NULL
        CONSTRAINT providers_pk
            PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS white_list
(
    chat_id BIGINT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS accepted_user_id_chat_id_uindex
    ON white_list (chat_id);

CREATE TABLE IF NOT EXISTS active_incidents
(
    id          SERIAL                                                          NOT NULL
        CONSTRAINT active_incidents_pk
            PRIMARY KEY,
    provider_id INTEGER                                                         NOT NULL
        CONSTRAINT active_incidents_providers__fk
            REFERENCES providers
            ON UPDATE CASCADE ON DELETE CASCADE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + '03:00:00'::INTERVAL) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS active_incidents_id_uindex
    ON active_incidents (id);

CREATE TABLE IF NOT EXISTS incidents_chats_messages
(
    message_id  BIGINT  NOT NULL,
    chat_id     BIGINT  NOT NULL,
    incident_id INTEGER NOT NULL
        CONSTRAINT incidents_messages_active_incidents__fk
            REFERENCES active_incidents
            ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chats_for_allocate
(
    chat_id    BIGINT NOT NULL,
    chat_title TEXT   NOT NULL
);

CREATE TABLE IF NOT EXISTS chats
(
    chat_id     BIGINT  NOT NULL
        CONSTRAINT chats_chats_for_allocate__fk
            REFERENCES chats_for_allocate (chat_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
    provider_id INTEGER NOT NULL
        CONSTRAINT chats_providers__fk
            REFERENCES providers
            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chats_chat_id_provider_id_key
        UNIQUE (chat_id, provider_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS chats_for_allocate_chat_id_uindex
    ON chats_for_allocate (chat_id);

INSERT INTO white_list (chat_id) VALUES (512309881);

INSERT INTO providers (id, provider_desc) VALUES (1, 'All');

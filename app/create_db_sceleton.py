def create_tables(connect, cur):
    cur.execute('create table if not exists providers(provider_desc text not null, id serial not null constraint providers_pk primary key);')
    cur.execute('create table if not exists chats(chat_id integer, provider_id integer constraint chats_providers__fk references providers (id));')
    cur.execute('create table if not exists accepted_user_id(chat_id integer);')
    connect.commit()

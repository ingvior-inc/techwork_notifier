class Situations:
    TECHNICAL_FAILURE = 'технический сбой'
    TECHNICAL_WORK = 'технические работы'
    LIST = [TECHNICAL_FAILURE, TECHNICAL_WORK]


class Buttons:
    ADD_CHAT = 'Добавить чат'
    DELETE_CHAT = 'Удалить чат'
    ADD_PROVIDER = 'Добавить провайдера'
    DELETE_PROVIDER = 'Удалить провайдера'
    ADD_ADMIN = 'Добавить админа'
    DELETE_ADMIN = 'Удалить админа'
    NOW = 'Сейчас'
    CANCEL = 'Отмена'


class MessageParts:
    PROVIDER = 'Ответственный'
    WHEN = 'Когда'
    USE_KEYBOARD_PLEASE = 'Пожалуйста, сделайте выбор с помощью клавиатуры'
    DONE = 'Выполнено:\n'
    INCIDENT_ENDED = 'Инцидент завершён'
    ACCESS_DENIED = 'Доступ запрещён'
    NO_ACTIVE_INCIDENTS = 'Нет активных инцидентов'
    WHICH_INCIDENT_NEED_END = 'Какой инцидент завершить?'
    WAITING_FOR_SITUATION = 'Выберите нужный сценарий'
    WAITING_FOR_PROVIDER = 'Выберите провайдера'
    WAITING_FOR_WRITING_PROVIDER = 'Укажите имя провайдера'
    WAITING_FOR_WRITING_DATE_AND_TIME = 'Когда?'
    WAITING_FOR_WRITING_DESCRIPTION = 'Опишите ситуацию'
    WAITING_FOR_CHAT_ID = 'Выберите чат'
    AFTER_CANCEL_CURRENT_OPERATION = ('Операция отменена.\n'
                                      '/start - запустить рассылку\n'
                                      '/end - завершить инцидент\n'
                                      '/edit_recipients - '
                                      'отредактировать список получателей\n'
                                      '/check_recipients - '
                                      'проверить список получателей')
    SENDING_FAILED = ('Рассылка не произведена.\n'
                      'Проверьте корректность заполнения списка '
                      'командой /check_recipients')
    NO_LAST_MESSAGES = 'Нет информации о последней рассылке'
    LAST_MESSAGES_DELETED = 'Сообщения из последней рассылки удалены'
    CHAT_WAS_ADDED = ('Чат добавлен.\n'
                      'Хотим добавить ещё?')
    CHAT_WAS_DELETED = ('Чат удалён.\n'
                        'Хотим удалить ещё?')
    INCORRECT_DATA = 'Некорректные данные'
    PROVIDERS_LIST = 'Список провайдеров'
    NEW_CHAT_DETECTED = 'Новый чат доступен для распределения'
    BOT_WAS_DELETED = 'Бот удалён из чата'

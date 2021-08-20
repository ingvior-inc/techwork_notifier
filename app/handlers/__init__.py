from . import sending_notif, edit_recipients_list, check_recipients_list


def setup_all(dp):
    sending_notif.setup(dp)
    edit_recipients_list.setup(dp)
    check_recipients_list.setup(dp)


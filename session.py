current_user = None


def login(user):
    global current_user
    current_user = user


def logout():
    global current_user
    current_user = None


def is_logged_in():
    return current_user is not None


def is_admin():
    return current_user is not None and current_user[3] == "admin"

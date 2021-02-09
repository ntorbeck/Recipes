from flask import redirect, session
from functools import wraps

def get_dict(id_name, sql_list):
    """Returns dict of dicts for id/name mapping"""
    
    # https://stackoverflow.com/questions/5236296/how-to-convert-list-of-dict-to-dict
    column_id = id_name
    sql_dict = dict()
    for item in sql_list:
        index = item.pop(column_id)
        sql_dict[index] = item
    return sql_dict


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
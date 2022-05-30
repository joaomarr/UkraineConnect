from flask import redirect, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_oblasts():
    """ All the regions of Ukraine """
    oblasts = [
    "Donets'ka oblast",
    "Dnipropetrovs'ka oblast",
    "Kyiv",
    "Kharkivs'ka oblast",
    "L'vivs'ka oblast",
    "Odessa",
    "Luhans'ka oblast",
    "Crimea",
    "Zaporizhzhia",
    "Vinnytsia",
    "Ivano-Frankivsk",
    "Khmel'nyts'kyy oblast",
    "Zakarpattia",
    "Zhytomyr",
    "Cherkasy",
    "Rivne",
    "Mykolaiv",
    "Sumy",
    "Ternopil",
    "Kherson",
    "Chernihiv",
    "Volyn",
    "Kirovohrad",
    "Chernivtsi",
    "Sevastopol"
    ]

    return oblasts
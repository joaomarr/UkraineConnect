from flask import redirect, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy("postgresql://jcbbzhfcombkdo:394fb3d023eba39a9ad5727189c8bc1f07c6af10cc257e6b4ac0960820363401@ec2-3-234-131-8.compute-1.amazonaws.com:5432/d38ao6p1p1btdb")

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
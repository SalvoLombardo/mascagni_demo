from app.extension import bcrypt
from app.models import Operator


def is_username_taken(username):
    return Operator.query.filter_by(operator_username=username).first() is not None

def login_operator_func(username,password):
    operator=Operator.query.filter_by(operator_username=username.strip()).first()

    if operator and bcrypt.check_password_hash(operator.operator_password,password):
        return operator
    else: return None
        


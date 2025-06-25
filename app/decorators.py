from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Effettua il login per continuare.", "warning")
            return redirect(url_for('admin.login_admin'))
        if not current_user.operator_is_admin:
            flash("Non hai i permessi necessari.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
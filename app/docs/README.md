


# FlaskApp – My First Complete Monolithic Flask Web Application

Welcome! This is my first **monolithic web application built with Flask**, developed after about **five months of self-taught learning**.  
It’s my first time here on GitHub,hope i'v donw everything right. 
Some technical choices are explained in a separate file (`design-decision.md`).

The whole app is written in Python/Flask, templates in HTML, styles in CSS (plus a little Bootstrap, but right now it's not my thing).

---

## Main Features

- User authentication (register / login / logout)  
- Admin panel with full CRUD  
- Modular structure via Blueprints (`auth`, `admin`, `main`)  
- Custom forms with Flask-WTF  
- Extensions in use: `Flask-SQLAlchemy`, `Flask-Login`, `Flask-WTF`, `CSRFProtect`  
- Clean, (hopefully) scalable architecture

---

## Project Structure

app/
│
├─ auth/          # blueprint for auth routes
├─ admin/         # admin routes & templates
├─ main/          # public pages
├─ models.py
├─ forms.py
├─ services/      # business-logic functions (easier to test)
└─ …

I've tried to keep simple as possibile the routes, using srvice section

---

## Tech Stack

- **Python 3.10+**  
- **Flask**  
- **Flask-Login / Flask-WTF / Flask-SQLAlchemy**  
- A pinch of **Bootstrap 5** on the front-end

---

## Installation (local)

```bash
# 1. create & activate venv
python -m venv venv
source venv/bin/activate     # or .\venv\Scripts\activate on Windows

# 2. install deps
pip install -r requirements.txt

# 3. set env vars (example)
export FLASK_APP=app
export FLASK_ENV=development
export SECRET_KEY=change-me

# 4. run
flask run

Demo credentials (admin):

user: admin_demo
pass: demo


⸻

Future Improvements
	•	Better error handling & logging
	•	Custom 404 / 500 pages
	•	Audit-log of operator actions
	•	More tests (PyTest) & CI

---

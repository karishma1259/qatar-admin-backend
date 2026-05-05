from flask import Flask, send_from_directory
from models import db
from flask_login import LoginManager
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

from models import Admin

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/')
def index():
    return send_from_directory('sky', 'admin.html')

@app.route('/admin.css')
def css():
    return send_from_directory('sky', 'admin.css')

@app.route('/admin.js')
def js():
    return send_from_directory('sky', 'admin.js')

@app.route('/sky/<path:filename>')
def sky_files(filename):
    return send_from_directory('sky', filename)

from routes import *

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from config import Config
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

# Initialize MongoDB
mongo = PyMongo(app)


# Import blueprints (auth, courses, payments)
from app.routes.home import home_blueprint
from app.routes.auth import auth_blueprint
from app.routes.courses import courses_blueprint
from app.routes.payments import payments_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(courses_blueprint)
app.register_blueprint(payments_blueprint, url_prefix='/payments')


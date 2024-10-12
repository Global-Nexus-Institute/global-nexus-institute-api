from flask import Blueprint, request, jsonify

home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/', methods=['GET'])
def home():
    return jsonify("Welcome "), 200

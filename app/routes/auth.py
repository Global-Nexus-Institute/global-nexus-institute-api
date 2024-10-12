import firebase_admin
from firebase_admin import auth, credentials
from flask import Blueprint, request, jsonify

auth_blueprint = Blueprint('auth', __name__)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    token = request.json.get('token')
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        return jsonify({"uid": uid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_blueprint.route('/signup', methods=['POST'])
def signup():

    data = request.json
    email = data.get('email')

    try:
        # Check if user already exists
        user = auth.get_user_by_email(email)
        return jsonify({"error": "User with this email already exists"}), 400
    except firebase_admin.auth.UserNotFoundError:
        # Create new user
        user = auth.create_user(
            email=email,
            password=data.get('password')
        )
        return jsonify({"message": "User created successfully", "user": user.uid}), 201

@auth_blueprint.route('/upload-file', methods=['POST'])
def upload_file():
    # Firebase storage logic here (using Firebase SDK)
    return jsonify({"message": "File uploaded successfully"})

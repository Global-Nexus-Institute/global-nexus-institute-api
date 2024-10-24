import firebase_admin
from firebase_admin import auth, credentials
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify
from app import mongo  # Import mongo instance from __init__.py
from datetime import datetime

auth_blueprint = Blueprint('auth', __name__)


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Password validation function
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None

@auth_blueprint.route('/login', methods=['POST'])
def login():
    token = request.json.get('token')
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        user = mongo.db.users.find_one({'uid': uid})
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_blueprint.route('/signup', methods=['POST'])
def signup(): 
    data = request.json.get('user', {})
    email = data.get('email')
    address = data.get('address', {})
    city = address.get('city')
    names = data.get('names')
    password = data.get('password')

    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    # Validate password
    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    password_error = validate_password(password)
    if password_error:
        return jsonify({"error": password_error}), 400

    try:
        # Check if user already exists
        user = auth.get_user_by_email(email)
        return jsonify({"error": "User with this email already exists"}), 400
    except firebase_admin.auth.UserNotFoundError:
        # Create new user
        user = auth.create_user(
            email=email,
            password=password
        )

        # Hash the password if needed
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        current_time = datetime.utcnow()
        # Add additional user data if needed
        new_user = {
            'uid': user.uid,
            'names': names,
            'email': email,
            'password': hashed_password,
            'role': 'admin',
            'address': {'city': city},
            'createdAt': current_time,
        }

        mongo.db.users.insert_one(new_user) # insert the new user into the database

        return jsonify({"message": "User created successfully", "user": user.uid}), 201

@auth_blueprint.route('/upload-file', methods=['POST'])
def upload_file():
    # Firebase storage logic here (using Firebase SDK)
    return jsonify({"message": "File uploaded successfully"})

@auth_blueprint.route('/logout', methods=['GET'])
def logout():
    # Handle logout if needed (e.g., remove session)
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_blueprint.route('/test-db', methods=['GET'])
def test_db():
    try:
        # Try to insert a test document into a collection
        mongo.db.test.insert_one({"test": "success"})
        return jsonify({"message": "MongoDB connection successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

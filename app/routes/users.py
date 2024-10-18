from flask import Blueprint, jsonify, request
from app import mongo  # Assuming mongo is initialized in your __init__.py
from bson.objectid import ObjectId
from config import Config

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/<_id>', methods=['PATCH'])
def update_user(_id):
    data = request.json
    
    try:
        # 1. Fin user with _id
        user = mongo.db.users.find_one({"_id": ObjectId(_id)})

        # Validate the data here (e.g., use a schema with marshmallow or manual validation)
        update_fields = {}  # Prepare the fields to update

        # Update the fields with the new data
        if 'email' in data:
            update_fields['email'] = data['email']
        if 'name' in data:
            update_fields['names'] = data['names']
        if 'address' in data:
            update_fields['address'] = data['address']
        if 'role' in data:
            update_fields['role'] = data['role']

        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Update the user in MongoDB
        mongo.db.users.update_one(
            {"_id": ObjectId(_id)},
            {"$set": update_fields}
        )
        updatedUser = mongo.db.users.find_one({"_id": ObjectId(_id)})

        updatedUser['_id'] = str(user['_id'])
        return jsonify({"message": "User updated successfully", "user": updatedUser}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_blueprint.route('/', methods=['GET'])
def get_users():
    try:
        # 4. Fetch courses from MongoDB
        users = list(mongo.db.users.find({"role":"admin"}))
        # Convert MongoDB ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

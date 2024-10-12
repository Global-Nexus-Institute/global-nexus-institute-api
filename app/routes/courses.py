import requests
from flask import Blueprint, jsonify
from app import mongo  # Assuming mongo is initialized in your __init__.py

courses_blueprint = Blueprint('courses', __name__)

ILLUMIDESK_API_URL = 'https://illumidesk-api-url.com'

@courses_blueprint.route('/update-courses', methods=['POST'])
def update_courses():
    try:
        # 1. Fetch courses from Illumidesk
        response = requests.get(f'{ILLUMIDESK_API_URL}/courses')
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch courses from Illumidesk"}), 500

        illumidesk_courses = response.json()

        # 2. Delete existing courses in MongoDB
        mongo.db.courses.delete_many({})

        # 3. Insert new courses into MongoDB
        mongo.db.courses.insert_many(illumidesk_courses)

        return jsonify({"message": "Courses updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_blueprint.route('/courses', methods=['GET'])
def get_courses():
    try:
        # 4. Fetch courses from MongoDB
        courses = list(mongo.db.courses.find())
        # Convert MongoDB ObjectId to string
        for course in courses:
            course['_id'] = str(course['_id'])
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

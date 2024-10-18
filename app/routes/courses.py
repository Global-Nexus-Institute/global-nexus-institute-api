import requests
from flask import Blueprint, jsonify
from app import mongo  # Assuming mongo is initialized in your __init__.py

from config import Config

courses_blueprint = Blueprint('courses', __name__)

ILLUMIDESK_API_URL = Config.ILLUMIDESK_API_URL
apiKey = Config.API_KEY

@courses_blueprint.route('/update-courses', methods=['POST'])
def update_courses():
    # url = f'{ILLUMIDESK_API_URL}/courses/'
    url = "https://api.illumidesk.com/api/v1/campuses/public/campuses/globalnexusinstitute/courses/"

    headers = {"accept": "application/json", "Authorization": f'{apiKey}'}
    try:
        # 1. Fetch courses from Illumidesk
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch courses from Illumidesk"}), 500

        illumidesk_courses = response.json().get('results')

        # 2. Loop through each course and insert/update in MongoDB
        for course in illumidesk_courses:
            # Assuming `course_id` is the unique identifier
            course_id = course.get('uuid')  # Replace with the actual unique identifier

            if course_id:
                # Use `replace_one` to either update or insert the course
                mongo.db.courses.replace_one(
                    {"uuid": course_id},  # Find course by unique ID
                    course,                    # Replace the document with new data
                    upsert=True                 # Insert if it doesn't exist
                )
            else:
                return jsonify({"error": "Missing uuid in course data"}), 400

        return jsonify({"message": "Courses updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_blueprint.route('/', methods=['GET'])
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

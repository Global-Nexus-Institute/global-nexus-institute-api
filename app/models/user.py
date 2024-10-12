from app import mongo

class User:
    @staticmethod
    def create_user(data):
        return mongo.db.users.insert_one(data)

    @staticmethod
    def get_user_by_id(user_id):
        return mongo.db.users.find_one({"_id": user_id})

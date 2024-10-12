from app import app as application

if __name__ == '__main__':
    application.run(debug=True, port=5003, host="0.0.0.0")

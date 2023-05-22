# This is the app file which will be run to start the web app. It is responsible for creating the Flask app and registering the routes. 
# It also contains the main function which will be run when the app is started. The main function will load the documents and models and then start the app. 
# The app will be run in debug mode so that it will automatically reload when changes are made to the code. This is useful for development, but should not be used in production.

from flask import Flask, request, render_template, jsonify
import google.generativeai as palm
from routes import main_routes

app = Flask(__name__)
app.secret_key = 'c6beb68cf8cda747fc0e6b13812b1c65'

main_routes.register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
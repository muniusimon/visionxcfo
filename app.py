from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, Simon!'

@pp.route('/about')
def about ():
    return "<h1>This is our about us</h1>"

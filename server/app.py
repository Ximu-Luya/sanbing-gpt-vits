from flask import Flask, send_from_directory
from flask_cors import CORS

from server.route import chat, memory

app = Flask(__name__)
CORS(app)

app.register_blueprint(chat)
app.register_blueprint(memory)

@app.route('/')
def send_static():
    return send_from_directory('dist', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('dist', path)
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return 'Enterprise Dashboard'

@app.route('/health')
def health():
    return jsonify(status='ok')

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(host='0.0.0.0', port=port)

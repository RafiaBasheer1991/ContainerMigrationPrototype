from flask import Flask, request, jsonify
import time

app = Flask(__name__)
request_timestamps = []

@app.route('/compute', methods=['POST'])
def compute():
    number = request.json.get("number")
    result = number * number
    request_timestamps.append(time.time())
    return jsonify({"result": result})

@app.route('/metrics')
def metrics():
    now = time.time()
    one_minute_hits = len([t for t in request_timestamps if now - t < 60])
    return jsonify({"rpm": one_minute_hits})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

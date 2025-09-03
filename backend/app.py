from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # simple dev-friendly CORS (restrict in prod)

@app.route("/")
def home():
    return "Hello, Flask is working!"


@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/patients")
def list_patients():
    return jsonify(patients=[{"id":1,"name":"Asha","age":33},{"id":2,"name":"Ravi","age":40}])

@app.post("/patients")
def create_patient():
    data = request.get_json(force=True)
    return jsonify(message="created", patient=data), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

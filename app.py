from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from optimizer import optimize_code

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not file.filename.endswith(".py"):
        return jsonify({"error": "Only .py files allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    with open(filepath, "r") as f:
        original_code = f.read()

    optimized_code, energy_saved = optimize_code(original_code)

    return jsonify({
        "original": original_code,
        "optimized": optimized_code,
        "energy_saved": energy_saved
    })

if __name__ == "__main__":
    app.run(debug=True)
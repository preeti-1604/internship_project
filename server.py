from flask import Flask, send_file, send_from_directory
import subprocess
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "ev_charging_site_selection")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")

# Run pipeline once on startup to generate dashboard
def run_pipeline():
    print("Running EV site selection pipeline...")
    result = subprocess.run(
        ["python", "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("Pipeline error:", result.stderr)

run_pipeline()

@app.route("/")
def index():
    return send_file(os.path.join(OUTPUT_DIR, "dashboard.html"))

@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

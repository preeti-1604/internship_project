from flask import Flask, send_file, send_from_directory
import subprocess
import os

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ev_charging_site_selection", "outputs")

@app.route("/")
def index():
    return send_file(os.path.join(OUTPUT_DIR, "dashboard.html"))

@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    # Run pipeline first to generate dashboard
    print("Running EV site selection pipeline...")
    os.chdir("ev_charging_site_selection")
    subprocess.run(["python", "main.py"], check=True)
    os.chdir("..")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

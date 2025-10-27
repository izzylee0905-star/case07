from flask import Flask, request, jsonify, render_template
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os

# ==========================
# Configuration
# ==========================
CONTAINER_NAME = "images-demo"

# Use environment variable for your Azure Storage connection string
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable")

# ==========================
# Azure Blob Setup
# ==========================
bsc = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
cc = bsc.get_container_client(CONTAINER_NAME)

try:
    cc.create_container()
except ResourceExistsError:
    pass  # container already exists

# ==========================
# Flask App
# ==========================
app = Flask(__name__)

@app.post("/api/v1/upload")
def upload():
    if "file" not in request.files:
        return jsonify(ok=False, error="No file part"), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify(ok=False, error="No selected file"), 400

    blob_client = cc.get_blob_client(file.filename)
    blob_client.upload_blob(file, overwrite=True)

    return jsonify(ok=True, url=f"{cc.url}/{file.filename}")

@app.get("/api/v1/gallery")
def gallery():
    blobs = cc.list_blobs()
    urls = [f"{cc.url}/{blob.name}" for blob in blobs]
    return jsonify(ok=True, gallery=urls)

@app.get("/api/v1/health")
def health():
    return jsonify(ok=True, status="healthy")

@app.get("/")
def index():
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

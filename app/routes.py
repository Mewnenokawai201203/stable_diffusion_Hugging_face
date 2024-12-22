from flask import Blueprint, request, jsonify, render_template, send_from_directory
import requests
import os
from datetime import datetime
from threading import Thread
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

routes_bp = Blueprint("routes_bp", __name__)

API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
API_KEY = "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"
SAVE_FOLDER = "app/static/images"
MAX_FILE_AGE = 24 * 60 * 60  


if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

@routes_bp.route("/")
def index():
    return render_template("index.html")

@routes_bp.route("/generate-image", methods=["POST"])
def generate_image():
    try:

        data = request.json
        prompt = data.get("prompt", "A cat sleeping in the street")

        headers = {"Authorization": f"Bearer {API_KEY}"}
        payload = {"inputs": prompt}
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"output_{timestamp}.png"
            filepath = os.path.join(SAVE_FOLDER, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            image_url = f"/static/images/{filename}"
            return jsonify({
                "status": "success",
                "image_url": image_url,
                "download_url": image_url
            })
        else:
            return jsonify({"status": "error", "message": response.text})
    except Exception as e:
        logger.error(f"Error in generate_image: {e}")
        return jsonify({"status": "error", "message": str(e)})

@routes_bp.route("/download/<filename>")
def download_file(filename):
    try:
        return send_from_directory(SAVE_FOLDER, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error in download_file: {e}")
        return jsonify({"status": "error", "message": str(e)})

def cleanup_old_files():
    """Xóa file cũ được lưu trong thư mục."""
    now = datetime.now().timestamp()
    for filename in os.listdir(SAVE_FOLDER):
        filepath = os.path.join(SAVE_FOLDER, filename)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > MAX_FILE_AGE:
                try:
                    os.remove(filepath)
                    logger.info(f"Deleted old file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to delete file {filename}: {e}")

def cleanup_files_periodically():
    """Xóa hình ảnh định kỳ."""
    while True:
        try:
            cleanup_old_files()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        time.sleep(3600) 

thread = Thread(target=cleanup_files_periodically)
thread.daemon = True
thread.start()

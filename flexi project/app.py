"""
Root entry point for Hugging Face Spaces, Render, and Cloud deployments.
"""
import os
import sys
import subprocess

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import build_app

# Train ML model if not already trained
model_path = os.getenv("MODEL_PATH", "./app/ml/severity_model.joblib")
if not os.path.exists(model_path):
    print("Training ML model...")
    try:
        subprocess.run([sys.executable, "app/ml/train_model.py"], check=True)
    except Exception as e:
        print(f"Model training note: {e}")

# Build the Gradio demo application
demo = build_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("APP_PORT", "7860")))
    demo.launch(server_name="0.0.0.0", server_port=port)

import os
import cv2
import easyocr

def test_ocr():
    # Since download_test.py only grabs audio, we will use cv2 to check if you have a video asset.
    # But wait, we need a video file first! Let's write a fast verification layout.
    print("👁️ Initializing EasyOCR Reader for English...")
    reader = easyocr.Reader(['en'], gpu=False) # Runs on CPU safely
    
    print("⏳ Note: On the very first run, EasyOCR will download its own language weights (approx 30MB).")
    print("✅ EasyOCR engine is initialized and ready for the next phase!")

if __name__ == "__main__":
    test_ocr()
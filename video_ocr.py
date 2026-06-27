import os
import cv2
import easyocr

def run_video_ocr():
    video_path = "test_video.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Error: {video_path} not found. Please run download_test.py first.")
        return
        
    print("👁️ Loading EasyOCR engine...")
    reader = easyocr.Reader(['en'], gpu=False)
    
    # Open the video file using OpenCV
    cap = cv2.VideoCapture(video_path)
    
    # Get the frame rate (FPS) of the video
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: 
        fps = 30  # Fallback standard if metadata is missing
        
    # Calculate how many frames to skip to move forward exactly 2 seconds
    frame_interval = int(fps * 2)
    
    print(f"🎬 Video loaded successfully! FPS: {fps:.2f} | Sampling 1 frame every {frame_interval} frames.")
    print("🤖 Processing video frames... Please wait.")
    
    extracted_text_set = set() # Using a set automatically removes duplicate lines of text
    frame_count = 0
    sampled_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # End of video file reached
            
        # Check if this frame lands exactly on our 2-second interval
        if frame_count % frame_interval == 0:
            sampled_count += 1
            # Run OCR on the specific image frame
            results = reader.readtext(frame, detail=0)
            
            # Add non-empty text blocks to our set
            for text in results:
                cleaned_text = text.strip()
                if len(cleaned_text) > 3:  # Ignore tiny artifacts like periods or lone letters
                    extracted_text_set.add(cleaned_text)
                    
        frame_count += 1
        
    # Free up memory and close the video file reader
    cap.release()
    
    print("\n============== 👁️ VIDEO OCR EXTRACTION RESULT ============== \n")
    if extracted_text_set:
        # Join all unique text elements with a clean visual divider
        combined_ocr_text = " | ".join(extracted_text_set)
        print(combined_ocr_text)
    else:
        print("ℹ️ No prominent on-screen text overlays detected.")
    print("\n==============================================================")
    print(f"Done! Sampled {sampled_count} frames total.")

if __name__ == "__main__":
    run_video_ocr()
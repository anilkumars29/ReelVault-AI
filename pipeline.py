import os
import cv2
import json
import yt_dlp
import whisper
import easyocr
import ollama
import requests
import chromadb
import logging
from dotenv import load_dotenv

# 🔐 Load hidden credentials from the .env file
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
CHROMA_PATH = "./chroma_db"
LLM_MODEL = "llama3.2"  # 🏎️ Harmonized to the lightweight, fast model

def download_assets(url):
    print("\n🎬 [1/5] Extracting video and audio tracks via yt-dlp...")
    
    # Check if local cookies exist to prevent crash if file is missing
    cookie_path = 'cookies.txt' if os.path.exists('cookies.txt') else None
    if not cookie_path:
        print("⚠️ Warning: cookies.txt not found. Running anonymous extraction...")

    audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'cookiefile': cookie_path  # 🍪 Bypasses rate limits using your session
    }
    
    video_opts = {
        'format': 'best',
        'outtmpl': 'temp_video.mp4',
        'quiet': True,
        'cookiefile': cookie_path  # 🍪 Bypasses rate limits using your session
    }
    
    with yt_dlp.YoutubeDL(audio_opts) as ydl: ydl.download([url])
    with yt_dlp.YoutubeDL(video_opts) as ydl: ydl.download([url])
    return "temp_audio.mp3", "temp_video.mp4"

def transcribe_audio(audio_path):
    print("🗣️ [2/5] Running local speech-to-text via Whisper AI...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result.get("text", "").strip()

def extract_video_ocr(video_path):
    print("👁️ [3/5] Sampling frames every 2 seconds with optimized CPU preprocessing...")
    reader = easyocr.Reader(['en'], gpu=False)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_interval = int(fps * 2)
    
    ocr_set = set()
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        if frame_count % frame_interval == 0:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            height, width = gray_frame.shape
            target_width = 640
            if width > target_width:
                scale_ratio = target_width / width
                target_height = int(height * scale_ratio)
                processed_frame = cv2.resize(gray_frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
            else:
                processed_frame = gray_frame
            lines = reader.readtext(processed_frame, detail=0)
            for line in lines:
                if len(line.strip()) > 3: ocr_set.add(line.strip())
        frame_count += 1
    cap.release()
    return " | ".join(ocr_set)

def enrich_with_llm(transcript, ocr_text):
    print(f"🧠 [4/5] Structuring insights and action items using local {LLM_MODEL}...")
    prompt = f"""
    You are an elite technical strategist. Analyze the transcript and OCR text from this educational video.
    Transcript: {transcript}
    OCR Text: {ocr_text}
    
    Strictly extract and format your response into these exact fields:
    Title: [Compelling title]
    Summary: [1-sentence value proposition]
    Category: [Select ONE: AI, Machine Learning, Startups, Business, Real Estate, Productivity, Marketing, Finance, Fitness]
    Tags: [2-4 keywords separated by commas]
    Roadmap: [Provide a brief, 3-step actionable execution plan based on this content]
    """
    response = ollama.chat(model=LLM_MODEL, messages=[{'role': 'user', 'content': prompt}])
    lines = response['message']['content'].strip().split('\n')
    
    metadata = {"Title": "Untitled Reel", "Summary": "No summary generated", "Category": "AI", "Tags": [], "Roadmap": "No roadmap generated"}
    current_key = None
    roadmap_lines = []
    
    for line in lines:
        if line.startswith("Title:"): metadata["Title"] = line.replace("Title:", "").strip()
        elif line.startswith("Summary:"): metadata["Summary"] = line.replace("Summary:", "").strip()
        elif line.startswith("Category:"): metadata["Category"] = line.replace("Category:", "").strip()
        elif line.startswith("Tags:"): metadata["Tags"] = [t.strip() for t in line.replace("Tags:", "").split(',')]
        elif line.startswith("Roadmap:"):
            current_key = "Roadmap"
            roadmap_lines.append(line.replace("Roadmap:", "").strip())
        elif current_key == "Roadmap" and line.strip():
            roadmap_lines.append(line.strip())
            
    if roadmap_lines:
        metadata["Roadmap"] = " \n ".join(roadmap_lines)
    return metadata

def sync_to_storage(url, meta, full_text):
    print("🚀 [5/5] Syncing assets to Notion and local ChromaDB vector space...")
    # 1. Notion Sync
    notion_url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": meta["Title"]}}]},
            "Reel URL": {"url": url},
            "Summary": {"rich_text": [{"text": {"content": meta["Summary"]}}]},
            "Category": {"select": {"name": meta["Category"]}},
            "Tags": {"multi_select": [{"name": tag} for tag in meta["Tags"]]},
            "Roadmap": {"rich_text": [{"text": {"content": meta["Roadmap"]}}]}
        }
    }
    requests.post(notion_url, headers=headers, data=json.dumps(payload))
    
    # 2. ChromaDB Sync
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name="reels_archive")
    safe_id = f"reel_{hash(url)}"
    collection.add(documents=[full_text], metadatas=[{"title": meta["Title"], "url": url}], ids=[safe_id])

def process_pipeline(url):
    print(f"⚡ Starting ReelVault Execution Pipeline for URL: {url}")
    audio, video = download_assets(url)
    transcript = transcribe_audio(audio)
    ocr_text = extract_video_ocr(video)
    full_context = f"Transcript: {transcript} \n OCR: {ocr_text}"
    metadata = enrich_with_llm(transcript, ocr_text)
    sync_to_storage(url, metadata, full_context)
    if os.path.exists(audio): os.remove(audio)
    if os.path.exists(video): os.remove(video)
    print(f"✨ System Process Complete!")

    import logging

# Configure production-grade system logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("reelvault.log"), # Saves logs to a local file permanently
        logging.StreamHandler()              # Still displays them live in your PowerShell terminal
    ]
)
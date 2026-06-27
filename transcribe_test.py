import os
import whisper

def test_transcription():
    audio_path = "test_audio.mp3"
    
    # Quick safety check to make sure the previous file is there
    if not os.path.exists(audio_path):
        print(f"❌ Error: {audio_path} not found. Please run download_test.py first.")
        return
        
    print("🗣️ Loading Whisper AI Model (base)...")
    # 'base' strikes the perfect balance between processing speed and accuracy for standard laptops
    model = whisper.load_model("base")
    
    print("🤖 Processing audio and transcribing speech... (This may take a moment on the first run)")
    result = model.transcribe(audio_path)
    
    print("\n============== 🗣️ WHISPER TRANSCRIPT RESULT ============== \n")
    print(result.get("text", "❌ No text extracted."))
    print("\n==========================================================")

if __name__ == "__main__":
    test_transcription()
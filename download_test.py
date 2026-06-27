import os
import yt_dlp

def download_video_and_audio(reel_url):
    print("🎬 Downloading both Video and Audio assets...")
    
    # Configuration to get the audio track
    audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'test_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    
    # Configuration to get the video track
    video_opts = {
        'format': 'best',
        'outtmpl': 'test_video.mp4',
        'quiet': True
    }
    
    try:
        # Download Audio
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([reel_url])
            
        # Download Video
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([reel_url])
            
        print("✅ Success! Both 'test_audio.mp3' and 'test_video.mp4' are sitting in your project folder.")
        
    except Exception as e:
        print(f"❌ Asset capture error: {e}")

if __name__ == "__main__":
    url = "https://www.instagram.com/reel/DYjLcWHqH-j/"  # Using your same test link
    download_video_and_audio(url)
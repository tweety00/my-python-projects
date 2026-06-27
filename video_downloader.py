import yt_dlp

def download_video(url):
    options = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(options) as ydl:
        print("Downloading...")
        ydl.download([url])
        print("Done!")

url = input("Enter video URL: ")
download_video(url)

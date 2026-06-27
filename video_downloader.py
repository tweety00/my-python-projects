<<<<<<< HEAD
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
=======
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
>>>>>>> 58956b795e70543a61d4f3119d118043286404b7

import yt_dlp

def my_own_engine(link):
    print(f"⚙  Apna khud ka engine start ho raha hai: {link}")
    
    # Settings: Hamein video download nahi karni, bas uska direct link chahiye
    ydl_opts = {
        'format': 'best', # Best quality
        'quiet': True,    # Faltu logs mat dikhao
        'get_url': True,  # Video mat download karo, bas URL de do
        'no_warnings': True,
        # 'proxy': 'http://user:pass@ip:port' # Future me jab traffic badhega tab proxy lagana padega
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Ye magic line seedha Instagram se baat karegi
            info = ydl.extract_info(link, download=False)
            
            # Video ka direct URL nikalna
            video_url = info.get('url')
            
            print("\n🎉 SUCCESS! Ye lijiye direct video link (Bina kisi aur website ke):")
            print("-" * 50)
            print(video_url)
            print("-" * 50)
            
            return video_url

    except Exception as e:
        print(f"❌ Error aaya: {e}")
        # Agar Instagram login maange, to uska bhi jugad hota hai cookies se

# --- User Input ---
user_link = input("Instagram Link Paste Karein: ")
my_own_engine(user_link)

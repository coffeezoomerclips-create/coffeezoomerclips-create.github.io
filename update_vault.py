import os
import json
import urllib.request
import re

# Locked to your single official clips channel
CHANNEL_HANDLES = ['@coffeezoomerclips']
API_KEY = os.environ.get('YOUTUBE_API_KEY')

if not API_KEY:
    print("Error: YOUTUBE_API_KEY not found.")
    exit(1)

all_video_ids = []

for handle in CHANNEL_HANDLES:
    try:
        # 1. Ask YouTube for the channel's "Uploads" playlist
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={handle}&key={API_KEY}"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        
        if not data.get('items'):
            print(f"Could not find channel for {handle}")
            continue
            
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 2. Paginate through the playlist to get EVERY video ever uploaded
        next_page_token = ""
        while True:
            page_param = f"&pageToken={next_page_token}" if next_page_token else ""
            playlist_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={uploads_playlist_id}&key={API_KEY}{page_param}"
            
            playlist_response = urllib.request.urlopen(playlist_url)
            playlist_data = json.loads(playlist_response.read())
            
            for item in playlist_data.get('items', []):
                video_id = item['contentDetails']['videoId']
                all_video_ids.append(video_id)
                
            # Check if there is another page of videos. If not, break the loop.
            next_page_token = playlist_data.get('nextPageToken')
            if not next_page_token:
                break
            
    except Exception as e:
        print(f"Error fetching data for {handle}: {e}")

if not all_video_ids:
    print("No videos found. Exiting.")
    exit(1)

# Format the massive list for the website's JavaScript
js_array_string = json.dumps(all_video_ids)

# Open your live website code
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Automatically find the old clip list and replace it with the new master list
updated_html = re.sub(
    r'const clipPool = \[.*?\];', 
    f'const clipPool = {js_array_string};', 
    html_content, 
    flags=re.DOTALL
)

# Save the changes
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print(f"Successfully updated the site with {len(all_video_ids)} total clips!")
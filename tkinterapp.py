import tkinter as tk
from tkinter import ttk
import googleapiclient.discovery
import googleapiclient.errors

# Function to get video statistics
def get_video_statistics(youtube, video_id):
    video_request = youtube.videos().list(
        part="statistics",
        id=video_id
    )
    video_response = video_request.execute()
    return video_response['items'][0]['statistics']

# Function to get channel statistics
def get_channel_statistics(youtube, channel_id):
    channel_request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    channel_response = channel_request.execute()
    return channel_response['items'][0]['statistics']

# Function to execute YouTube search and display results
def youtube_search():
    api_key = "AIzaSyA46ehaE6ov71md0No8ZfIjfWFB4z-X4h8"  # Replace with your API key
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    query = search_entry.get()
    max_results = int(results_spinbox.get())

    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=query
    )
    response = request.execute()

    videos_data = []

    for item in response['items']:
        video_id = item['id']['videoId']
        channel_id = item['snippet']['channelId']

        video_stats = get_video_statistics(youtube, video_id)
        channel_stats = get_channel_statistics(youtube, channel_id)

        videos_data.append({
            'videoId': video_id,
            'viewCount': int(video_stats.get('viewCount', 0)),
            'likeCount': video_stats.get('likeCount'),
            'channelId': channel_id,
            'subscriberCount': channel_stats.get('subscriberCount')
        })

    sorted_videos = sorted(videos_data, key=lambda x: int(x['likeCount'] or 0), reverse=True)

    results_text.delete('1.0', tk.END)
    for video in sorted_videos:
        video_id = video['videoId']
        results_text.insert(tk.END, f"{video}\nhttps://www.youtube.com/watch?v={video_id}\n\n")

# Setting up the Tkinter window
root = tk.Tk()
root.title("YouTube Search App")

# Search entry
search_label = ttk.Label(root, text="Search Query:")
search_label.pack()
search_entry = ttk.Entry(root, width=50)
search_entry.pack()

# Results spinbox
results_label = ttk.Label(root, text="Number of Results:")
results_label.pack()
results_spinbox = ttk.Spinbox(root, from_=10, to=100, width=5, increment=1, value=32)
results_spinbox.pack()

# Search button
search_button = ttk.Button(root, text="Search", command=youtube_search)
search_button.pack()

# Results display
results_text = tk.Text(root, height=20, width=80)
results_text.pack()

root.mainloop()

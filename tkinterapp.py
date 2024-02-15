from tkinter.font import Font
from tkinter import ttk
import tkinter as tk
import webbrowser
import googleapiclient.discovery

# Function to open video link in the browser, now explicitly receiving the video link as a parameter
def open_video_link(video_link):
    webbrowser.open(video_link)

# Function to execute YouTube search and update the table
def youtube_search():
    api_key = "AIzaSyA46ehaE6ov71md0No8ZfIjfWFB4z-X4h8"  # Replace with your API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    query = search_entry.get()
    max_results = int(results_spinbox.get())

    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=query,
        type="video"
    )
    response = request.execute()

    # Step 1: Collect all video items into a list
    video_items = []
    for item in response['items']:
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['channelTitle']
        video_link = f"https://www.youtube.com/watch?v={video_id}"

        video_stats = youtube.videos().list(part="statistics", id=video_id).execute()['items'][0]['statistics']
        channel_stats = youtube.channels().list(part="statistics", id=channel_id).execute()['items'][0]['statistics']

        # Append a tuple with all necessary information, including like count for sorting
        video_items.append((
            video_title, 
            int(video_stats.get('likeCount', 0)),  # Convert likeCount to int, default to 0 if not present
            video_stats.get('viewCount'),
            channel_title,
            channel_stats.get('subscriberCount'),
            item['snippet']['description'],
            video_link  # Store video link in the last column, which will be hidden
        ))

    # Step 2: Sort the list by like count in descending order
    video_items.sort(key=lambda x: x[1], reverse=True)  # x[1] is the like count

    # Clear existing items in the magic table
    for item in magic_table.get_children():
        magic_table.delete(item)

    # Step 3: Iterate over the sorted list and insert each item into the magic table
    for video_item in video_items:
        magic_table.insert("", tk.END, values=video_item)

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

# Magic Table setup
columns = ("Video Name", "Like Count", "View Count", "Channel Name", "Subscriber Count", "Description", "URL")
magic_table = ttk.Treeview(root, columns=columns, show="headings")
magic_table.pack(expand=True, fill="both")

# Configuring column headings
for col in columns[:-1]:  # Exclude the URL column from headings
    magic_table.heading(col, text=col)
    magic_table.column(col, width=Font().measure(col.title()))

# Hiding the URL column
magic_table.column("URL", width=0, stretch=False, minwidth=0)

# Modified binding to pass the video link explicitly
def on_item_click(event):
    selected_item = magic_table.selection()[0]  # Get selected item
    video_link = magic_table.item(selected_item, 'values')[6]  # URL is the last value
    open_video_link(video_link)

magic_table.bind("<Double-1>", on_item_click)

root.mainloop()

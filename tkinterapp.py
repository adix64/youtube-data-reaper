import tkinter as tk; from tkinter.font import Font; from tkinter import ttk; from tkinter import PhotoImage
import requests; from PIL import Image, ImageTk; from io import BytesIO
import webbrowser; import googleapiclient.discovery

# Function to execute YouTube search and update the table
def youtube_search():
    api_key = "AIzaSyA46ehaE6ov71md0No8ZfIjfWFB4z-X4h8"  # Replace with your API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    request = youtube.search().list(part="snippet", maxResults=20, q=search_entry.get(), type="video")
    response = request.execute()
    # Collect all video IDs into a list, to make a videos().list() call to get details for all vids
    video_ids = [item['id']['videoId'] for item in response['items']]
    video_details_request = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids))
    video_details_response = video_details_request.execute()
    video_items = []
    for item in video_details_response['items']:
        video_id = item['id']
        video_title = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['channelTitle']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnailURL = item['snippet']['thumbnails']['medium']['url'] # could be either 'default', 'medium', 'high', 'standard' or 'maxres'
        tags = item['snippet']['tags'] if 'tags' in item['snippet'] else []
        tags_string = ', '.join(tags)
        
        video_stats = youtube.videos().list(part="statistics", id=video_id).execute()['items'][0]['statistics']
        channel_stats = youtube.channels().list(part="statistics", id=channel_id).execute()['items'][0]['statistics']

        viewCount = int(video_stats.get('viewCount', 0))
        likeCount = int(video_stats.get('likeCount', 0))
        subscriberCount = int(channel_stats.get('subscriberCount', 0))
        
        lvRatio = likeCount / viewCount if (viewCount > 0) else -1
        vsRatio = viewCount / subscriberCount if (subscriberCount > 0) else -1
        # Append a tuple with all relevant information
        video_items.append(( video_title, viewCount, likeCount, channel_title, subscriberCount, lvRatio, vsRatio,
            item['snippet']['description'], tags_string, thumbnailURL, video_link))

    # Sort the list by likeCount in descending order
    video_items.sort(key=lambda x: x[2], reverse=True)
    
    # Clear existing items in the YT_entries_table and then insert the new entries:
    for item in YT_entries_table.get_children(): YT_entries_table.delete(item)
    for video_item in video_items: YT_entries_table.insert("", tk.END, values=video_item)

# Setting up the Tkinter window
root = tk.Tk()
dark_background = '#2D2D2D'; text_color = '#FFFFFF'; lighter_dark_gray = '#434343'
root.configure(background=dark_background)

style = ttk.Style()
style.theme_use('clam')
style.configure('.', background=dark_background, foreground=text_color, font=('Consolas', 10), relief='flat')
style.configure('TButton', font=('Consolas', 10), background=dark_background, foreground=text_color, borderwidth=1)
style.configure('TLabel', font=('Consolas', 10), background=dark_background, foreground=text_color)
style.configure('TEntry', foreground=text_color, fieldbackground=dark_background, bordercolor=lighter_dark_gray)
style.configure('TFrame', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview', background=dark_background, fieldbackground=dark_background, foreground=text_color)
style.configure('PhotoImage', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview.Heading', background=lighter_dark_gray, foreground=text_color, font=('Helvetica', 10, 'bold'))

root.geometry('800x1000')
root.title("YouTube Data Reaper")

# Search entry frame
search_frame = tk.Frame(root)
search_frame.configure(background=dark_background);     search_frame.pack()

# Create a label to display the image
png_image = PhotoImage(file="reaper128x128.png")
image_label = ttk.Label(search_frame, image=png_image)
image_label.pack(side=tk.LEFT, padx=(0, 10))

search_entry = ttk.Entry(search_frame, width=80);       search_entry.pack(side=tk.LEFT)
search_entry.insert(0, "Batman Bruce Timm Drawing")

search_button = ttk.Button(search_frame, text="Search", command=youtube_search);    search_button.pack(side=tk.LEFT)

# YT_entries_table setup
columns = ("Video Name",  "Views", "Likes", "Channel Name", "Subscribers", "L/V", "V/S", "Description", "Tags", "ThumbnailURL", "URL")
YT_entries_table = ttk.Treeview(root, columns=columns, show="headings", height=20)
YT_entries_table.pack(expand=True, fill="both", padx=30)

# Configuring column headings
for col in columns:  # Exclude the URL column from headings
    YT_entries_table.heading(col, text=col)
    YT_entries_table.column(col, width=Font().measure(col.title()))

columnsToHide = ["Description", "Tags", "ThumbnailURL", "URL"]
for col in columnsToHide: YT_entries_table.column(col, width=0, stretch=False, minwidth=0)

def sort_column(column, reverse=False):
    # Define reverse as a mutable object so its state can be maintained across function calls
    reverse_dict = sort_column.reverse_dict
    # Toggle the sorting direction
    reverse = reverse_dict[column] = not reverse_dict.get(column, False)
    # Determine if column data is numeric or not
    try:
        float(YT_entries_table.set(YT_entries_table.get_children()[0], column))
        is_numeric = True
    except ValueError:
        is_numeric = False
    # Extract data with conversion if necessary
    data = [(YT_entries_table.set(k, column), k) for k in YT_entries_table.get_children('')]
    if is_numeric:
        data = [(float(a), b) for a, b in data]
    # Sort and rearrange
    data.sort(reverse=reverse)
    for index, (_, k) in enumerate(data):
        YT_entries_table.move(k, '', index)
    # Update headings to keep the sort order
    for col in YT_entries_table['columns']:
        YT_entries_table.heading(col, text=col, command=lambda c=col: sort_column(c, reverse_dict.get(col, False)))

# Initialize a dictionary to keep track of sort orders for each column
sort_column.reverse_dict = {}

# Set up column headings with sort command
for col in columns: YT_entries_table.heading(col, text=col, command=lambda c=col: sort_column(c))

for col in columns[1:-1]: YT_entries_table.column(col, anchor='center')

def on_table_item_clicked(event):
    selected_item = YT_entries_table.selection()[0]  # Get selected item
    video_link = YT_entries_table.item(selected_item, 'values')[-1]  # URL is the last value
    webbrowser.open(video_link)

YT_entries_table.bind("<Double-1>", on_table_item_clicked)

def create_readonly_text_widget(root, initial_text):
    text_widget = tk.Text(root, wrap="word", height=10, width=40, bg="#222222", fg="white")
    text_widget.insert("1.0", initial_text)
    text_widget.config(state="disabled")  # Make the text widget non-editable but selectable/copyable
    text_widget.pack(side="left", fill='both', expand=True, padx=15, pady=15)
    return text_widget
    
def set_text(text_widget, text):
    text_widget.config(state="normal")
    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")

################################ Frame for displaying video details: ################################
details_frame = ttk.Frame(root);    details_frame.pack(fill='both', expand=True, pady=(30, 0), padx=(30, 0))

thumbnail_frame = ttk.Frame(details_frame);     thumbnail_frame.pack(side='left', anchor='nw', fill='y')
thumbnail_label = ttk.Label(thumbnail_frame);       thumbnail_label.pack(anchor='nw')

video_details_frame = ttk.Frame(details_frame);    video_details_frame.pack(side='left', anchor='nw', fill='both', expand=True, padx=(10, 0), pady=(10, 0))
video_name_label = ttk.Label(video_details_frame, text='', width=50);   video_name_label.pack(anchor='nw')
video_views_label = ttk.Label(video_details_frame, text='');    video_views_label.pack(anchor='nw')
video_likes_label = ttk.Label(video_details_frame, text='');    video_likes_label.pack(anchor='nw')

video_description_text = create_readonly_text_widget(root, "")
video_tags_text = create_readonly_text_widget(root, "")
######################################################################################################

def on_treeview_select(event):
    selected_item = YT_entries_table.selection()[0]
    item_values = YT_entries_table.item(selected_item, 'values')
    video_name_label.config(text=f'Name: {item_values[0]}')
    set_text(video_description_text, f'Description: \n\n{item_values[7]}')
    video_views_label.config(text=f'Views: {item_values[1]}')
    video_likes_label.config(text=f'Likes: {item_values[2]}')
    set_text(video_tags_text, f'Tags: {item_values[8]}')
    
    thumbnail_url = item_values[-2]  # the last but one item in 'item_values' is the thumbnail URL
    try:
        img = Image.open(BytesIO(requests.get(thumbnail_url).content)) #; img.thumbnail((128, 128), Image.ANTIALIAS)  # Resize to fit the label, if necessary
        photo = ImageTk.PhotoImage(img)
        thumbnail_label.config(image=photo)
        thumbnail_label.image = photo  # Keep a reference
    except Exception as e:
        print(f"Failed to load thumbnail: {e}")

YT_entries_table.bind('<<TreeviewSelect>>', on_treeview_select)

root.mainloop()
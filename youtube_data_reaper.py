import tkinter as tk; from tkinter.font import Font; from tkinter import ttk; from tkinter import PhotoImage
import requests; from PIL import Image, ImageTk; from io import BytesIO
import webbrowser; import googleapiclient.discovery

# Function to execute YouTube search and update the table
def youtube_search():
    with open('PASTE_YOUR_API_KEY_HERE.txt', 'r') as file: api_key = ''.join(file.read().split())
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    request = youtube.search().list(part="snippet", maxResults=50, q=search_entry.get(), type="video", order=selected_option.get())
    response = request.execute()
    # Collect all video IDs into a list, to make a videos().list() call to get details for all vids
    video_ids = [item['id']['videoId'] for item in response['items']]
    video_details_request = youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
    video_details_response = video_details_request.execute()
    video_items = []
    for item in video_details_response['items']:
        video_id = item['id']
        video_title = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        duration = item['contentDetails']['duration']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnailURL = item['snippet']['thumbnails']['medium']['url'] # could be either 'default', 'medium', 'high', 'standard' or 'maxres'
        tags = item['snippet']['tags'] if 'tags' in item['snippet'] else []
        channel_title = item['snippet']['channelTitle']
        tags_string = ', '.join(tags)
        
        video_stats = youtube.videos().list(part="statistics", id=video_id).execute()['items'][0]['statistics']
        channel_stats = youtube.channels().list(part="statistics", id=channel_id).execute()['items'][0]['statistics']

        commentCount = int(video_stats.get('commentCount', 0))
        viewCount = int(video_stats.get('viewCount', 0))
        likeCount = int(video_stats.get('likeCount', 0))
        subscriberCount = int(channel_stats.get('subscriberCount', 0))
        channelViewCount = int(channel_stats.get('viewCount', 0))
        videoCount = int(channel_stats.get('videoCount', 0))
        
        lvRatio = likeCount / viewCount if (viewCount > 0) else -1
        vsRatio = viewCount / subscriberCount if (subscriberCount > 0) else -1
        viewRatio = viewCount / channelViewCount if (channelViewCount > 0) else -1
        # Append a tuple with all relevant information
        video_items.append((video_title, viewCount, likeCount, commentCount, 
                            channel_title, subscriberCount, channelViewCount, videoCount,
                            lvRatio, vsRatio, viewRatio,
                            item['snippet']['description'], tags_string, thumbnailURL, video_link))

    # Sort the list by likeCount in descending order
    # video_items.sort(key=lambda x: x[2], reverse=True)
    
    # Clear existing items in the YT_entries_table and then insert the new entries:
    for item in YT_entries_table.get_children(): YT_entries_table.delete(item)
    for video_item in video_items: YT_entries_table.insert("", tk.END, values=video_item)

# Setting up the Tkinter window
root = tk.Tk()
dark_background = '#2D2D2D'; darker_background = '#1D1D1D'; text_color = '#FFFFFF'; lighter_dark_gray = '#434343'
root.configure(background=dark_background)

style = ttk.Style()
style.theme_use('clam')
style.configure('.', background=dark_background, foreground=text_color, font=('Consolas', 10), relief='flat')
style.configure('TButton', font=('Consolas', 10), background=dark_background, foreground=text_color, borderwidth=1)
style.configure('TLabel', font=('Consolas', 10), background=dark_background, foreground=text_color)
style.configure('TEntry', foreground=text_color, fieldbackground=dark_background, bordercolor=lighter_dark_gray)
style.configure('TFrame', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview', background=darker_background, fieldbackground=dark_background, foreground=text_color)
style.configure('PhotoImage', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview.Heading', background=lighter_dark_gray, foreground=text_color, font=('Consolas', 10, 'bold'))

root.geometry('1000x900')
root.title("YouTube Data Reaper")

# Search entry frame
search_frame = tk.Frame(root)
search_frame.configure(background=dark_background);     search_frame.pack()
def open_YouTube_channel(event):
    webbrowser.open("https://www.youtube.com/channel/UC4_YtlZ-MU4qAsIkMHCTvMQ")
# Create a label to display the image
png_image = PhotoImage(file="icons/reaper128x128.png")
image_label = ttk.Label(search_frame, image=png_image)
image_label.bind("<Button-1>", open_YouTube_channel)
image_label.pack(side=tk.LEFT, padx=(0, 10))

search_entry = ttk.Entry(search_frame, width=80);       search_entry.pack(side=tk.LEFT)
search_entry.insert(0, "Batman Bruce Timm Drawing")

search_button = ttk.Button(search_frame, text="Search", command=youtube_search);    search_button.pack(side=tk.LEFT)

order_label = tk.Label(search_frame, text="YT Search Order:", bg=dark_background,fg='white')
order_label.pack(pady=(70,0), padx=50)
options = ['viewCount', 'date', 'rating', 'relevance']
selected_option = tk.StringVar(search_frame)
selected_option.set(options[0])  # Set the default value
option_menu = ttk.OptionMenu(search_frame, selected_option, options[0], *options)
option_menu.pack(pady=0, padx=50)

# YT_entries_table setup
columns = ("Video 🎬",  "Views 👁️", "Likes👍", "Comms💬", "Channel👤", 
            "Subscribers👥", "TotalViews👀", "Videos🎥", "L/V", "V/S", "V/TV", "Description", "Tags", "ThumbnailURL", "URL")
YT_entries_table = ttk.Treeview(root, columns=columns, show="headings", height=20)

YT_entries_table.pack(expand=True, fill="both", padx=30)

# Configuring column headings
for col in columns:  # Exclude the URL column from headings
    YT_entries_table.heading(col, text=col)
    YT_entries_table.column(col, width=Font().measure(col.title()))

columnsToHide = ["Description", "Tags", "ThumbnailURL", "URL"]
for col in columnsToHide: YT_entries_table.column(col, width=0, stretch=False, minwidth=0)

visible_column_widths = (("Video 🎬",180),  ("Views 👁️",93), ("Likes👍",67), ("Comms💬",57), ("Channel👤", 124), 
            ("Subscribers👥",99), ("TotalViews👀",101) , ("Videos🎥",68), ("L/V",41), ("V/S", 41), ("V/TV",41))
for (colName, colWidth) in visible_column_widths:
    YT_entries_table.column(colName, width=colWidth)

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
def make_and_pack_videoDetails_label(parent, font=("Segoe UI", 10, "normal"), color="white", pad = 0):
    label = ttk.Label(parent, text='', width=100, font=font, foreground=color);    label.pack(anchor='nw', pady = (pad,0))
    return label

details_frame = ttk.Frame(root);    details_frame.pack(fill='both', expand=True, pady=(30, 0), padx=(30, 0))

thumbnail_frame = ttk.Frame(details_frame);     thumbnail_frame.pack(side='left', anchor='nw', fill='y')
thumbnail_label = ttk.Label(thumbnail_frame);       thumbnail_label.pack(anchor='nw')

video_details_frame = ttk.Frame(details_frame);
video_details_frame.pack(side='left', anchor='nw', fill='both', expand=True, padx=(10, 0), pady=(10, 0))
video_name_label = make_and_pack_videoDetails_label(video_details_frame,("Helvetica", 12, "bold"), "#AAFFFF")
video_stats_label = make_and_pack_videoDetails_label(video_details_frame)
heuristic_stats_label = make_and_pack_videoDetails_label(video_details_frame)
video_ChannelName_label = make_and_pack_videoDetails_label(video_details_frame,("Helvetica", 12, "bold"), "#FFAAFF", 30)
channel_stats_label = make_and_pack_videoDetails_label(video_details_frame)

video_description_text = create_readonly_text_widget(root, "")
video_tags_text = create_readonly_text_widget(root, "")
######################################################################################################

def on_treeview_select(event):
    selected_item = YT_entries_table.selection()[0]
    item_values = YT_entries_table.item(selected_item, 'values')
    video_name_label.config(text=f'🎬 {item_values[0]}')
    video_stats_label.config(text=f'{item_values[1]} Views\t{item_values[2]} Likes \t {item_values[3]} Comments')
    heuristic_stats_label.config(text=f'Likes/Views (L/V) = {float(item_values[8]):.3f}\tViews/Subs (V/S) = {float(item_values[9]):.3f}\t Views/TotalViews (V/TV) = {float(item_values[10]):.3f}')
    video_ChannelName_label.config(text=f'👤 {item_values[4]}')
    channel_stats_label.config(text=f'{item_values[5]} Subscribers\t\t{item_values[6]} Views\t\t{item_values[7]} Videos')
    set_text(video_description_text, f'Description: \n\n{item_values[11]}')
    set_text(video_tags_text, f'Tags: {item_values[12]}')
    
    thumbnail_url = item_values[-2]  # the last but one item in 'item_values' is the thumbnail URL
    try:
        img = Image.open(BytesIO(requests.get(thumbnail_url).content)) #; img.thumbnail((128, 128), Image.ANTIALIAS)  # Resize to fit the label, if necessary
        photo = ImageTk.PhotoImage(img)
        thumbnail_label.config(image=photo)
        thumbnail_label.bind("<Button-1>", on_table_item_clicked)
        thumbnail_label.image = photo  # Keep a reference
    except Exception as e:
        print(f"Failed to load thumbnail: {e}")

YT_entries_table.bind('<<TreeviewSelect>>', on_treeview_select)

root.mainloop()
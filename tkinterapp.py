import tkinter as tk; from tkinter.font import Font; from tkinter import ttk; from tkinter import PhotoImage
import requests; from PIL import Image, ImageTk; from io import BytesIO
import webbrowser; import googleapiclient.discovery

# Function to execute YouTube search and update the table
def youtube_search():
    api_key = "AIzaSyA46ehaE6ov71md0No8ZfIjfWFB4z-X4h8"  # Replace with your API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    request = youtube.search().list(part="snippet", maxResults=100, q=search_entry.get(), type="video")
    response = request.execute()
    # Collect all video IDs into a list, to make a videos().list() call to get details for all vids
    video_ids = [item['id']['videoId'] for item in response['items']]
    video_details_request = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids))
    
    video_details_response = video_details_request.execute()
    print(video_details_response) 
    # Step 1: Collect all video items into a list
    video_items = []
    for item in video_details_response['items']:
        video_id = item['id']
        video_title = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['channelTitle']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnailURL = item['snippet']['thumbnails']['medium']['url'] # 'default', 'medium', 'high', 'standard', 'maxres'
        tags = item['snippet']['tags'] if 'tags' in item['snippet'] else []
        tags_string = ', '.join(tags)
        
        video_stats = youtube.videos().list(part="statistics", id=video_id).execute()['items'][0]['statistics']
        channel_stats = youtube.channels().list(part="statistics", id=channel_id).execute()['items'][0]['statistics']

        viewCount = int(video_stats.get('viewCount', 0))
        likeCount = int(video_stats.get('likeCount', 0))  # Convert likeCount to int, default to 0 if not present
        subscriberCount = int(channel_stats.get('subscriberCount', 0))
        
        lvRatio = likeCount / viewCount if (viewCount > 0) else -1
        vsRatio = viewCount / subscriberCount if (subscriberCount > 0) else -1
        # Append a tuple with all necessary information, including like count for sorting
        video_items.append(( video_title, viewCount, likeCount, channel_title, subscriberCount, lvRatio, vsRatio,
            item['snippet']['description'], tags_string, thumbnailURL, video_link))

    # Step 2: Sort the list by view count in descending order
    video_items.sort(key=lambda x: x[2], reverse=True)  # x[1] is the like count
    
    # Clear existing items in the magic table and then insert the new entries:
    for item in magic_table.get_children(): magic_table.delete(item)
    for video_item in video_items: magic_table.insert("", tk.END, values=video_item)

# Setting up the Tkinter window
root = tk.Tk()

# Initialize the style object
style = ttk.Style()
style.theme_use('clam')  # Set the theme to 'clam'
############################
# Initialize the style object
style = ttk.Style()
style.theme_use('clam')  # Use the 'clam' theme as a base for customization

dark_background = '#2D2D2D'; text_color = '#FFFFFF'; lighter_dark_gray = '#434343'

root.configure(background=dark_background)

# Configure global appearance
style.configure('.', background=dark_background, foreground=text_color, font=('Consolas', 10), relief='flat')
style.configure('TButton', font=('Consolas', 10), background=dark_background, foreground=text_color, borderwidth=1)
style.configure('TLabel', font=('Consolas', 10), background=dark_background, foreground=text_color)
style.configure('TEntry', foreground=text_color, fieldbackground=dark_background, bordercolor=lighter_dark_gray)
style.configure('TFrame', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview', background=dark_background, fieldbackground=dark_background, foreground=text_color)
style.configure('PhotoImage', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview.Heading', background=lighter_dark_gray, foreground=text_color, font=('Helvetica', 10, 'bold'))

############################

root.geometry('800x1000')  # Set the resolution to 800x600
# root.state('zoomed')  # This will maximize the window
root.title("YouTube Data Reaper")

# Search entry frame
search_frame = tk.Frame(root)  # Create a frame to hold the entry and button
search_frame.configure(background=dark_background)
search_frame.pack()

png_image = PhotoImage(file="reaper128x128.png")

# Create a label to display the image
image_label = ttk.Label(search_frame, image=png_image)
image_label.configure(background=dark_background)
image_label.pack(side=tk.LEFT, padx=(0, 10))  # Adjust padding as needed

search_entry = ttk.Entry(search_frame, width=80)
search_entry.insert(0, "Batman Bruce Timm Drawing")  # Set default search text
search_entry.pack(side=tk.LEFT)


search_button = ttk.Button(search_frame, text="Search", command=youtube_search)
search_button.pack(side=tk.LEFT)

# Magic Table setup
columns = ("Video Name",  "Views", "Likes", "Channel Name", "Subscribers", "L/V", "V/S", "Description", "Tags", "ThumbnailURL", "URL")
magic_table = ttk.Treeview(root, columns=columns, show="headings", height=20)
magic_table.pack(expand=True, fill="both", padx=30)

# Configuring column headings
for col in columns:  # Exclude the URL column from headings
    magic_table.heading(col, text=col)
    magic_table.column(col, width=Font().measure(col.title()))

# Hiding the URL column
magic_table.column("Description", width=0, stretch=False, minwidth=0)
magic_table.column("Tags", width=0, stretch=False, minwidth=0)
magic_table.column("ThumbnailURL", width=0, stretch=False, minwidth=0)
magic_table.column("URL", width=0, stretch=False, minwidth=0)


def sort_column(column, reverse=False):
    # Define reverse as a mutable object so its state can be maintained across function calls
    reverse_dict = sort_column.reverse_dict
    # Toggle the sorting direction
    reverse = reverse_dict[column] = not reverse_dict.get(column, False)
    # Determine if column data is numeric or not
    try:
        float(magic_table.set(magic_table.get_children()[0], column))
        is_numeric = True
    except ValueError:
        is_numeric = False
    # Extract data with conversion if necessary
    data = [(magic_table.set(k, column), k) for k in magic_table.get_children('')]
    if is_numeric:
        data = [(float(a), b) for a, b in data]
    # Sort and rearrange
    data.sort(reverse=reverse)
    for index, (_, k) in enumerate(data):
        magic_table.move(k, '', index)
    # Update headings to keep the sort order
    for col in magic_table['columns']:
        magic_table.heading(col, text=col, command=lambda c=col: sort_column(c, reverse_dict.get(col, False)))

# Initialize a dictionary to keep track of sort orders for each column
sort_column.reverse_dict = {}

# Set up column headings with sort command
for col in columns: magic_table.heading(col, text=col, command=lambda c=col: sort_column(c))

for col in columns[1:-1]: magic_table.column(col, anchor='center')

def on_table_item_clicked(event):
    selected_item = magic_table.selection()[0]  # Get selected item
    video_link = magic_table.item(selected_item, 'values')[-1]  # URL is the last value
    webbrowser.open(video_link)

magic_table.bind("<Double-1>", on_table_item_clicked)

def create_readonly_text_widget(root, initial_text):
    text_widget = tk.Text(root, wrap="word", height=10, width=40, bg="#222222", fg="white")
    text_widget.insert("1.0", initial_text)
    text_widget.config(state="disabled")  # Make the text widget non-editable but selectable/copyable
    text_widget.pack(side="left", fill='both', expand=True, padx=15, pady=15)
    return text_widget
    
def set_text(text_widget, text): #Clears the current content of the Text widget and inserts new text."""
    text_widget.config(state="normal")  # Temporarily enable the widget to modify the text
    text_widget.delete("1.0", "end")  # Clear existing text
    text_widget.insert("1.0", text)  # Insert new text
    text_widget.config(state="disabled")  # Disable the widget to prevent editing

################################ Frame for displaying video details: #####################################

details_frame = ttk.Frame(root);    details_frame.pack(fill='both', expand=True, pady=(30, 0), padx=(30, 0))

thumbnail_frame = ttk.Frame(details_frame);     thumbnail_frame.pack(side='left', anchor='nw', fill='y')#, pady=(10, 0), padx=(10, 0))

thumbnail_label = ttk.Label(thumbnail_frame);       thumbnail_label.pack(anchor='nw')

video_details_frame = ttk.Frame(details_frame);    video_details_frame.pack(side='left', anchor='nw', fill='both', expand=True, padx=(10, 0), pady=(10, 0))

video_name_label = ttk.Label(video_details_frame, text='', width=50);   video_name_label.pack(anchor='nw')

video_views_label = ttk.Label(video_details_frame, text='');    video_views_label.pack(anchor='nw')

video_likes_label = ttk.Label(video_details_frame, text='');    video_likes_label.pack(anchor='nw')


video_description_text = create_readonly_text_widget(root, "")
video_tags_text = create_readonly_text_widget(root, "")

######################################################################################################

def on_treeview_select(event):
    selected_item = magic_table.selection()[0]
    item_values = magic_table.item(selected_item, 'values')
    video_name_label.config(text=f'Name: {item_values[0]}')
    set_text(video_description_text, f'Description: \n\n{item_values[7]}')
    video_views_label.config(text=f'Views: {item_values[1]}')
    video_likes_label.config(text=f'Likes: {item_values[2]}')
    set_text(video_tags_text, f'Tags: {item_values[8]}')
    
    # For the thumbnail, fetch and display the image
    thumbnail_url = item_values[-2]  # Assuming the last item in 'item_values' is the thumbnail URL
    try:
        img = Image.open(BytesIO(requests.get(thumbnail_url).content)) #; img.thumbnail((128, 128), Image.ANTIALIAS)  # Resize to fit the label, if necessary
        photo = ImageTk.PhotoImage(img)
        thumbnail_label.config(image=photo)
        thumbnail_label.image = photo  # Keep a reference
    except Exception as e:
        print(f"Failed to load thumbnail: {e}")

magic_table.bind('<<TreeviewSelect>>', on_treeview_select)

root.mainloop()
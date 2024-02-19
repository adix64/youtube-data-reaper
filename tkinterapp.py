from tkinter.font import Font
from tkinter import ttk
import tkinter as tk
import webbrowser
import googleapiclient.discovery
from tkinter import PhotoImage, Label

# Function to open video link in the browser, now explicitly receiving the video link as a parameter
def open_video_link(video_link):
    webbrowser.open(video_link)

# Function to execute YouTube search and update the table
def youtube_search():
    api_key = "AIzaSyA46ehaE6ov71md0No8ZfIjfWFB4z-X4h8"  # Replace with your API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    query = search_entry.get()
    max_results = 100

    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=query,
        type="video"
    )
    response = request.execute()
    # Step 1: Collect all video IDs into a list
    video_ids = [item['id']['videoId'] for item in response['items']]

    # Step 2: Use the video IDs to make a videos().list() call to get details, including tags
    video_details_request = youtube.videos().list(
        part="snippet",
        id=",".join(video_ids)  # Join the list of video IDs into a comma-separated string
    )
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
        tags = item['snippet']['tags'] if 'tags' in item['snippet'] else []
        print(tags)
        tags_string = ', '.join(tags)
        
        video_stats = youtube.videos().list(part="statistics", id=video_id).execute()['items'][0]['statistics']
        channel_stats = youtube.channels().list(part="statistics", id=channel_id).execute()['items'][0]['statistics']

        viewCount = int(video_stats.get('viewCount', 0))
        likeCount = int(video_stats.get('likeCount', 0))  # Convert likeCount to int, default to 0 if not present
        subscriberCount = int(channel_stats.get('subscriberCount', 0))
        
        lvRatio = likeCount / viewCount if (viewCount > 0) else -1
        vsRatio = viewCount / subscriberCount if (subscriberCount > 0) else -1
        # Append a tuple with all necessary information, including like count for sorting
        video_items.append((
            video_title, 
            viewCount,
            likeCount,
            channel_title,
            subscriberCount,
            lvRatio, vsRatio,
            item['snippet']['description'],
            tags_string,
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

# Initialize the style object
style = ttk.Style()
style.theme_use('clam')  # Set the theme to 'clam'
############################
# Initialize the style object
style = ttk.Style()
style.theme_use('clam')  # Use the 'clam' theme as a base for customization

# Define the color scheme
dark_background = '#2D2D2D'  # Dark gray
accent_color = '#116699'  # Soft purple
text_color = '#FFFFFF'  # White
secondary_color = '#434343'  # Slightly lighter gray

root.configure(background=dark_background)

# Define the fonts
main_font = ('Helvetica', 10)
accent_font = ('Helvetica', 12, 'bold')

# Configure global appearance


style.configure('.', background=dark_background, foreground=text_color, font=main_font, relief='flat')
style.configure('TButton', font=accent_font, background=dark_background, foreground=text_color, borderwidth=1)
style.configure('TLabel', font=main_font, background=dark_background, foreground=text_color)
style.configure('TEntry', foreground=text_color, fieldbackground=dark_background, bordercolor=secondary_color)
style.configure('TFrame', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview', background=dark_background, fieldbackground=dark_background, foreground=text_color)
style.configure('PhotoImage', background=dark_background, fieldbackground=dark_background)
style.configure('Treeview.Heading', background=secondary_color, foreground=text_color, font=('Helvetica', 10, 'bold'))


############################

root.geometry('1280x720')  # Set the resolution to 800x600
root.state('zoomed')  # This will maximize the window
root.title("YouTube Search App")

# Search entry frame
search_frame = tk.Frame(root)  # Create a frame to hold the entry and button
search_frame.configure(background=dark_background)
search_frame.pack()

png_image = PhotoImage(file="reaper128x128.png")


# Create a label to display the image
image_label = Label(search_frame, image=png_image)
image_label.configure(background=dark_background)
image_label.pack(side=tk.LEFT, padx=(0, 10))  # Adjust padding as needed

#search_label = ttk.Label(search_frame, text="Search Query:")
#search_label.pack(side=tk.LEFT)

search_entry = ttk.Entry(search_frame, width=80)
search_entry.insert(0, "Batman Bruce Timm Drawing")  # Set default search text
search_entry.pack(side=tk.LEFT)


search_button = ttk.Button(search_frame, text="Search", command=youtube_search)
search_button.pack(side=tk.LEFT)

# Magic Table setup
columns = ("Video Name",  "Views", "Likes", "Channel Name", "Subscribers", "L/V", "V/S", "Description", "Tags", "URL")
magic_table = ttk.Treeview(root, columns=columns, show="headings")
magic_table.pack(expand=True, fill="both", padx=30)

# Configuring column headings
for col in columns:  # Exclude the URL column from headings
    magic_table.heading(col, text=col)
    magic_table.column(col, width=Font().measure(col.title()))

# Hiding the URL column
magic_table.column("URL", width=0, stretch=False, minwidth=0)


def sort_column(column, reverse=False):
    # Define reverse as a mutable object so its state can be maintained across function calls
    reverse_dict = sort_column.reverse_dict

    # Toggle the sorting direction
    reverse_dict[column] = not reverse_dict.get(column, False)
    reverse = reverse_dict[column]

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
        magic_table.heading(col, text=col,
                            command=lambda c=col: sort_column(c, reverse_dict.get(col, False)))

# Initialize a dictionary to keep track of sort orders for each column
sort_column.reverse_dict = {}

# Set up column headings with sort command
for col in columns:
    magic_table.heading(col, text=col, command=lambda c=col: sort_column(c))


for col in columns[1:-1]:  # Skip the first and last column
    magic_table.column(col, anchor='center')


# Modified binding to pass the video link explicitly
def on_item_click(event):
    selected_item = magic_table.selection()[0]  # Get selected item
    video_link = magic_table.item(selected_item, 'values')[-1]  # URL is the last value
    open_video_link(video_link)

magic_table.bind("<Double-1>", on_item_click)
def create_readonly_text(root, initial_text):
    """Creates a Text widget that is selectable and copyable but not editable, with black background, white text, and 15px padding, without a scrollbar."""
    text_widget = tk.Text(root, wrap="word", height=10, width=40, bg="black", fg="white")
    text_widget.insert("1.0", initial_text)
    text_widget.config(state="disabled")  # Make the text widget non-editable but selectable/copyable
    text_widget.pack(side="left", fill="both", expand=True, padx=15, pady=15)

    return text_widget
    
def set_text(text_widget, text):
    """Clears the current content of the Text widget and inserts new text."""
    text_widget.config(state="normal")  # Temporarily enable the widget to modify the text
    text_widget.delete("1.0", "end")  # Clear existing text
    text_widget.insert("1.0", text)  # Insert new text
    text_widget.config(state="disabled")  # Disable the widget to prevent editing
######################################################################################################
######################################################################################################
######################################################################################################
# Frame for displaying video details
details_frame = ttk.Frame(root)
details_frame.pack(fill='both', expand=True)

# Labels for displaying video details
thumbnail_label = Label(details_frame)
thumbnail_label.pack(pady=(10, 0))

video_name_label = ttk.Label(details_frame, text='', wraplength=300, width=1000)#, padx=30)
video_name_label.pack()

video_description_text = create_readonly_text(root, "")

video_views_label = ttk.Label(details_frame, text='')
video_views_label.pack()

video_likes_label = ttk.Label(details_frame, text='')
video_likes_label.pack()

video_tags_text = create_readonly_text(root, "")

######################################################################################################
######################################################################################################

def on_treeview_select(event):
    selected_item = magic_table.selection()[0]
    item_values = magic_table.item(selected_item, 'values')
    # Assuming the item values include the necessary video details in a specific order
    # Update the labels within the details frame with the selected video's details
    # This is a placeholder for how you might set the label texts; you'll need to adjust it based on your actual data structure
    video_name_label.config(text=f'Name: {item_values[0]}')
    set_text(video_description_text, f'Description: \n\n{item_values[7]}')
    video_views_label.config(text=f'Views: {item_values[1]}')
    video_likes_label.config(text=f'Likes: {item_values[2]}')
    set_text(video_tags_text, f'Tags: {item_values[8]}')
    # For the thumbnail, you'll need to fetch and display the image. This will require additional functionality not shown here.

magic_table.bind('<<TreeviewSelect>>', on_treeview_select)

root.mainloop()

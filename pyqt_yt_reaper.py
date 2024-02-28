import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt, QSize, pyqtSignal,QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices, QColor, QFont
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from datetime import datetime

import isodate  # To parse ISO 8601 duration strings
import qdarkstyle
from youtube_search import youtube_search


class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # Signal to be emitted when the label is clicked

    def __init__(self, parent=None):
        super(ClickableLabel, self).__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit the clicked signal

class YouTubeDataReaper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Data Reaper")
        self.setFixedSize(QSize(1000, 900))  # Set fixed size for the window


        self.networkManager = QNetworkAccessManager()
        self.networkManager.finished.connect(self.onThumbnailDownloaded)
        # Central Widget
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Main Layout
        self.layout = QVBoxLayout(self.centralWidget)

        # Label
        self.label = QLabel("Search:", self.centralWidget)
        self.layout.addWidget(self.label)

        # Search Area Layout (Horizontal)
        self.searchAreaLayout = QHBoxLayout()  # Create a QHBoxLayout for the search area

        # Image Label
        self.imageLabel = ClickableLabel(self.centralWidget)
        self.pixmap = QPixmap("icons/reaper128x128.png")  # Load the image
        self.imageLabel.setPixmap(self.pixmap)  # Set the pixmap for the label
        self.imageLabel.clicked.connect(self.openUrl)
        self.searchAreaLayout.addWidget(self.imageLabel)  # Add the image label to the horizontal layout

        # Line Edit (Entry)
        self.searchEntry = QLineEdit(self.centralWidget)
        self.searchEntry.setPlaceholderText("Type your search query here")
        self.searchAreaLayout.addWidget(self.searchEntry)  # Add to the horizontal layout

        # Button
        self.searchButton = QPushButton("Search", self.centralWidget)
        self.searchButton.clicked.connect(self.on_search_button_clicked)  # Connect signal to slot
        self.searchAreaLayout.addWidget(self.searchButton)  # Add to the horizontal layout

        # Add the search area layout to the main layout
        self.layout.addLayout(self.searchAreaLayout)

        self.video_items = []  # List to store VideoItem objects

        # Table Widget
        self.tableWidget = QTableWidget(self.centralWidget)
        self.layout.addWidget(self.tableWidget)
        self.setupTable()
        self.setupDetailedInfoSection()
        
    def setupDetailedInfoSection(self):
        self.detailedInfoLayout = QHBoxLayout()

        self.thumbnailLabel = ClickableLabel()
        self.thumbnailLabel.setFixedSize(120, 90)  # Adjust size as needed
        self.thumbnailLabel.clicked.connect(self.onThumbnailClicked)
        self.detailedInfoLayout.addWidget(self.thumbnailLabel)

        self.videoInfoLayout = QVBoxLayout()

        self.videoTitleLabel = QLabel("Video Title")
        self.videoTitleLabel.setWordWrap(True)
        self.videoInfoLayout.addWidget(self.videoTitleLabel)

        self.statsLabel = QLabel("Views | Likes | Comments")
        self.videoInfoLayout.addWidget(self.statsLabel)

        self.durationDateLabel = QLabel("Duration | Upload Date")
        self.videoInfoLayout.addWidget(self.durationDateLabel)

        self.channelNameLabel = QLabel("Channel Name")
        self.channelNameLabel.setWordWrap(True)
        self.videoInfoLayout.addWidget(self.channelNameLabel)

        self.channelStatsLabel = QLabel("Subscribers | Total Views | Videos")
        self.videoInfoLayout.addWidget(self.channelStatsLabel)

        self.detailedInfoLayout.addLayout(self.videoInfoLayout)
        self.layout.addLayout(self.detailedInfoLayout)
        
    

    def openUrl(self):
        QDesktopServices.openUrl(QUrl("https://www.youtube.com/@adix64"))  # Replace with your desired URL
    
    def setupTable(self):
        # Assuming your data includes these fields
        self.tableWidget.setColumnCount(13)  # Number of columns you want to display
        self.tableWidget.setHorizontalHeaderLabels(['Title', 'Views', 'Likes', 'Comments', 'Duration', 'Upload Date',
                                                    'Channel', 'Subscribers', 'Channel Views', 'Video Count', 'LV Ratio',
                                                    'VS Ratio', 'View Ratio'])
        # self.tableWidget.setMaximumHeight(500)  # Limit maximum height
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.sort_order = True  # Initial sort order
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.doubleClicked.connect(self.on_table_double_clicked)
        self.tableWidget.itemSelectionChanged.connect(self.updateDetailedInfo)

    
    def on_table_double_clicked(self, index):
        selected_video_item = self.video_items[index.row()]  # Access the VideoItem using the retrieved index
        QDesktopServices.openUrl(QUrl(selected_video_item.video_link))

    
    def on_search_button_clicked(self):
        self.video_items = youtube_search(self.searchEntry.text(), 'viewCount')
        self.populate_table()

    def on_header_clicked(self, column_index):
        if len(self.video_items) == 0:
            return
        # Mapping of column indexes to VideoItem attributes
        column_mapping = {
            0: 'video_title', 1: 'view_count', 2: 'like_count', 3: 'comment_count', 
            4: 'duration', 5: 'upload_date', 6: 'channel_title', 7: 'subscriber_count', 
            8: 'channel_view_count', 9: 'video_count', 10: 'lv_ratio', 11: 'vs_ratio', 
            12: 'view_ratio'
        }

        # Get the attribute corresponding to the clicked column
        sort_attribute = column_mapping.get(column_index)

        if sort_attribute:
            # Toggle sorting order
            self.sort_order = not self.sort_order

            # Sort the list based on the attribute and order
            self.video_items.sort(key=lambda item: getattr(item, sort_attribute), reverse=not self.sort_order)

            # Refresh the table with sorted items
            self.populate_table()

    def onThumbnailClicked(self):
        
        selectedRows = self.tableWidget.selectionModel().selectedRows()
        if selectedRows:
            selectedRow = selectedRows[0].row()
            videoItem = self.video_items[selectedRow]
            QDesktopServices.openUrl(QUrl(videoItem.video_link))
            
    def fetchThumbnail(self, url):
        request = QNetworkRequest(QUrl(url))
        self.networkManager.get(request)

    def onThumbnailDownloaded(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.thumbnailLabel.setFixedWidth(480)
            self.thumbnailLabel.setPixmap(pixmap.scaled(480, 360, Qt.AspectRatioMode.KeepAspectRatio))
            self.thumbnailLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        reply.deleteLater()

    def populate_table(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.video_items))
        for row, video in enumerate(self.video_items):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(video.video_title));
            self.tableWidget.setItem(row, 1, QTableWidgetItem(f"{video.view_count:,}"))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(f"{video.like_count:,}"))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(f"{video.comment_count:,}"))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(self.format_duration(video.duration)))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(video.upload_date))#.strftime("%d %B %Y")))
            self.tableWidget.setItem(row, 6, QTableWidgetItem(video.channel_title))
            self.tableWidget.setItem(row, 7, QTableWidgetItem(f"{video.subscriber_count:,}"))
            self.tableWidget.setItem(row, 8, QTableWidgetItem(f"{video.channel_view_count:,}"))
            self.tableWidget.setItem(row, 9, QTableWidgetItem(f"{video.video_count:,}"))
            self.tableWidget.setItem(row, 10, QTableWidgetItem(f"{video.lv_ratio:.2f}"))
            self.tableWidget.setItem(row, 11, QTableWidgetItem(f"{video.vs_ratio:.2f}"))
            self.tableWidget.setItem(row, 12, QTableWidgetItem(f"{video.view_ratio:.2f}"))
        self.color_gradient()

    def updateDetailedInfo(self):
        selectedRows = self.tableWidget.selectionModel().selectedRows()
        if selectedRows:
            selectedRow = selectedRows[0].row()
            videoItem = self.video_items[selectedRow]

            # Set thumbnail image
            pixmap = QPixmap()
            pixmap.loadFromData(self.fetchThumbnail(videoItem.thumbnail_url))  # You need to implement fetchThumbnail
            self.thumbnailLabel.setFixedWidth(480)
            self.thumbnailLabel.setPixmap(pixmap.scaled(480, 360, Qt.AspectRatioMode.KeepAspectRatio))  # Adjust scaling as needed
            self.thumbnailLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            
            
            # Set video title
            self.videoTitleLabel.setText(videoItem.video_title)
            self.videoTitleLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # Make title font larger and bold

            # Set stats (views, likes, comments)
            self.statsLabel.setText(f"{videoItem.view_count} Views\t{videoItem.like_count} Likes\t{videoItem.comment_count} Comments")
            self.statsLabel.setFont(QFont("Arial", 10))  # Adjust font size as needed

            # Set duration and upload date
            self.durationDateLabel.setText(f"Duration: {videoItem.duration} - Uploaded: {videoItem.upload_date}")
            self.durationDateLabel.setFont(QFont("Arial", 10))  # Adjust font size as needed

            # Set channel name
            self.channelNameLabel.setText(videoItem.channel_title)
            self.channelNameLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # Make channel name font larger and bold

            # Set channel stats (subscribers, total views, video count)
            self.channelStatsLabel.setText(f"Subscribers: {videoItem.subscriber_count}, Total Views: {videoItem.channel_view_count}, Videos: {videoItem.video_count}")
            self.channelStatsLabel.setFont(QFont("Arial", 10))  # Adjust font size as needed


    def format_duration(self, duration_str):
        duration = isodate.parse_duration(duration_str)
        total_seconds = duration.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{int(hours)}h{int(minutes)}min{int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}min{int(seconds)}s"
        else:
            return f"{int(seconds)}s"

    def color_gradient(self):
        for column in range(1, 4):  # Assuming the first column is not numerical and you want to color columns 1-12
            max_value = max([float(self.tableWidget.item(row, column).text().replace(',', '')) for row in range(self.tableWidget.rowCount())])
            min_value = min([float(self.tableWidget.item(row, column).text().replace(',', '')) for row in range(self.tableWidget.rowCount())])

            for row in range(self.tableWidget.rowCount()):
                value = float(self.tableWidget.item(row, column).text().replace(',', ''))
                intensity = (value - min_value) / (max_value - min_value) if max_value != min_value else 1
                color = QColor.fromRgbF(intensity, 0, 0, 1)  # Example gradient from red to blue
                self.tableWidget.item(row, column).setBackground(color)
# Create the application instance
app = QApplication([])
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))  # Specify PyQt6 API
window = YouTubeDataReaper()
window.show()
app.exec()

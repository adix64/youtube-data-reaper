import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor
from datetime import datetime
import isodate  # To parse ISO 8601 duration strings
import qdarkstyle
from youtube_search import youtube_search

class YouTubeDataReaper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Data Reaper")
        self.setFixedSize(QSize(1000, 900))  # Set fixed size for the window

        # Central Widget
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Layout
        self.layout = QVBoxLayout(self.centralWidget)

        # Label
        self.label = QLabel("Search:", self.centralWidget)
        self.layout.addWidget(self.label)

        # Line Edit (Entry)
        self.searchEntry = QLineEdit(self.centralWidget)
        self.searchEntry.setPlaceholderText("Batman Bruce Timm Drawing")
        self.layout.addWidget(self.searchEntry)

        # Button
        self.searchButton = QPushButton("Search", self.centralWidget)
        self.searchButton.clicked.connect(self.on_search_button_clicked)  # Connect signal to slot
        self.layout.addWidget(self.searchButton)
        
        # Table Widget
        self.tableWidget = QTableWidget(self.centralWidget)
        self.layout.addWidget(self.tableWidget)
        self.setupTable()


    def setupTable(self):
        # Assuming your data includes these fields
        self.tableWidget.setColumnCount(13)  # Number of columns you want to display
        self.tableWidget.setHorizontalHeaderLabels(['Title', 'Views', 'Likes', 'Comments', 'Duration', 'Upload Date',
                                                    'Channel', 'Subscribers', 'Channel Views', 'Video Count', 'LV Ratio',
                                                    'VS Ratio', 'View Ratio'])

    def on_search_button_clicked(self):
        searchResults = youtube_search(self.searchEntry.text(), 'viewCount')
        self.populate_table(searchResults)

    def populate_table(self, video_items):
        self.tableWidget.setRowCount(len(video_items))
        for row, video in enumerate(video_items):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(video.video_title))
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
                color = QColor.fromRgbF(intensity, 0, 1 - intensity, 1)  # Example gradient from red to blue
                self.tableWidget.item(row, column).setBackground(color)
# Create the application instance
app = QApplication([])
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))  # Specify PyQt6 API
window = YouTubeDataReaper()
window.show()
app.exec()

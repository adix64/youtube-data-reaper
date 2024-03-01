from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt, QSize, pyqtSignal,QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices, QColor, QFont
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from datetime import datetime; import isodate
import qdarkstyle
from youtube_search import youtube_search

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super(ClickableLabel, self).__init__(parent)
    def mousePressEvent(self, event):
        self.clicked.emit()

class YouTubeDataReaper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_items = []  # List to store VideoItem objects
        self.netMgr = QNetworkAccessManager(); self.netMgr.finished.connect(self.onThumbnailDownloaded)
        self.setWindowTitle("YouTube Data Reaper")
        self.setFixedSize(QSize(1100, 900))
# Central Widget
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
# Main Layout
        self.layout = QVBoxLayout(self.centralWidget)
# Search Area Layout (Horizontal)
        self.searchAreaLayout = QHBoxLayout()
# Image Label
        self.imageLabel = ClickableLabel(self.centralWidget)
        self.pixmap = QPixmap("icons/reaper128x128.png")
        self.imageLabel.setPixmap(self.pixmap)
        self.imageLabel.clicked.connect(self.openUrl)
        self.searchAreaLayout.addWidget(self.imageLabel)
# Line Edit (Entry)
        self.searchEntry = QLineEdit(self.centralWidget)
        self.searchEntry.setPlaceholderText("Type your search query here")
        self.searchAreaLayout.addWidget(self.searchEntry)
# Button
        self.searchButton = QPushButton("Search", self.centralWidget)
        self.searchButton.setFixedWidth(100); self.searchButton.setFixedHeight(30)
        self.searchButton.clicked.connect(self.on_search_button_clicked)
        self.searchAreaLayout.addWidget(self.searchButton)
# Combo Box
        self.optionBox = QComboBox()
        self.optionBox.addItems(['viewCount', 'date', 'rating', 'relevance'])  # Add your options
        self.searchAreaLayout.addWidget(self.optionBox)
# Add the search area layout to the main layout
        self.layout.addLayout(self.searchAreaLayout)
# Table Widget
        self.tableWidget = QTableWidget(self.centralWidget)
        self.layout.addWidget(self.tableWidget)
        self.setupTable()
        self.setupDetailedInfoSection()
        
    def setupDetailedInfoSection(self):
        self.detailedInfoLayout = QHBoxLayout()
        self.thumbnailLabel = ClickableLabel(); self.thumbnailLabel.clicked.connect(self.onThumbnailClicked)
        self.detailedInfoLayout.addWidget(self.thumbnailLabel)
        self.videoInfoLayout = QVBoxLayout()
        self.videoTitleLabel = QLabel("Video Title"); self.videoTitleLabel.setWordWrap(True)
        self.statsLabel = QLabel("Views | Likes | Comments")
        self.durationDateLabel = QLabel("Duration | Upload Date")
        self.channelNameLabel = QLabel("Channel Name"); self.channelNameLabel.setWordWrap(True)
        self.channelStatsLabel = QLabel("Subscribers | Total Views | Videos")
        for w in [self.videoTitleLabel, self.statsLabel, self.durationDateLabel, self.channelNameLabel, self.channelStatsLabel]:
            self.videoInfoLayout.addWidget(w)
        self.detailedInfoLayout.addLayout(self.videoInfoLayout)
        self.layout.addLayout(self.detailedInfoLayout)
        
    def openUrl(self):
        QDesktopServices.openUrl(QUrl("https://www.youtube.com/@adix64"))
    
    def setupTable(self):
        self.tableWidget.setColumnCount(13)        
        self.tableWidget.setHorizontalHeaderLabels(
            ['🎬 Video Title', '👁️Views', '👍Likes', '💬Comms', '⏲️Duration', '📅Uploaded',
             '👤Channel', '👥Subscribers', '👀Channel👁️', '🎥Vids', '👍/👁️', '👁️/👥', '👁️/👀']) #📉
        visible_column_widths = [180, 90, 90, 72,76, 80, 101, 95, 95, 60, 45, 45, 45]
        for i, width in enumerate(visible_column_widths): self.tableWidget.setColumnWidth(i, width)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.sort_order = True
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.doubleClicked.connect(self.on_table_double_clicked)
        self.tableWidget.itemSelectionChanged.connect(self.updateDetailedInfo)

    def on_table_double_clicked(self, index):
        selected_video_item = self.video_items[index.row()]
        QDesktopServices.openUrl(QUrl(selected_video_item.video_link))
    
    def on_search_button_clicked(self):
        self.video_items = youtube_search(self.searchEntry.text(), self.optionBox.currentText())
        self.populate_table()

    def on_header_clicked(self, column_index):
        if len(self.video_items) == 0: return
        column_mapping = [  'video_title', 'view_count', 'like_count', 'comment_count', 
                            'duration', 'upload_date', 'channel_title', 'subscriber_count', 
                            'channel_view_count', 'video_count', 'lv_ratio', 'vs_ratio', 'view_ratio']
        sort_attribute = column_mapping[column_index]
        if sort_attribute:
            self.sort_order = not self.sort_order
            self.video_items.sort(key=lambda item: getattr(item, sort_attribute), reverse=not self.sort_order)
            self.populate_table() # Refresh the table with sorted items

    def onThumbnailClicked(self):
        selectedRows = self.tableWidget.selectionModel().selectedRows()
        if selectedRows:
            selectedRow = selectedRows[0].row()
            videoItem = self.video_items[selectedRow]
            QDesktopServices.openUrl(QUrl(videoItem.video_link))
            
    def fetchThumbnail(self, url):
        request = QNetworkRequest(QUrl(url))
        self.netMgr.get(request)

    def onThumbnailDownloaded(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.thumbnailLabel.setPixmap(pixmap.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatio))
            self.thumbnailLabel.setFixedWidth(320); self.thumbnailLabel.setFixedHeight(180)
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
            item = self.video_items[selectedRow]
# Set thumbnail image
            pixmap = QPixmap()
            pixmap.loadFromData(self.fetchThumbnail(item.thumbnail_url))
# Set video title
            self.videoTitleLabel.setText(item.video_title)
            self.videoTitleLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))
# Set stats (views, likes, comments)
            self.statsLabel.setText(f"{item.view_count} Views\t{item.like_count} Likes\t{item.comment_count} Comments")
            self.statsLabel.setFont(QFont("Arial", 10))
# Set duration and upload date
            self.durationDateLabel.setText(f"Duration: {item.duration} - Uploaded: {item.upload_date}")
            self.durationDateLabel.setFont(QFont("Arial", 10))
# Set channel name
            self.channelNameLabel.setText(item.channel_title)
            self.channelNameLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
# Set channel stats (subscribers, total views, video count)
            self.channelStatsLabel.setText(
                f"{item.subscriber_count}Subscribers\t{item.channel_view_count} Views\t{item.video_count} Videos")
            self.channelStatsLabel.setFont(QFont("Arial", 10))

    def format_duration(self, duration_str):
        duration = isodate.parse_duration(duration_str)
        total_seconds = duration.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0: return f"{int(hours)}h{int(minutes)}min{int(seconds)}s"
        elif minutes > 0: return f"{int(minutes)}min{int(seconds)}s"
        else: return f"{int(seconds)}s"

    def color_gradient(self):
        colored_columns = [(1,QColor.fromRgbF(1,0,0,1)),(2,QColor.fromRgbF(0,.8,0,1)), (3,QColor.fromRgbF(0,0,1,1)),
                           (7,QColor.fromRgbF(.85,.6,0,1)), (8,QColor.fromRgbF(.75,0,.75,1)), (9,QColor.fromRgbF(.5,.5,.5,1)),
                           (10,QColor.fromRgbF(1,0,0,1)),(11,QColor.fromRgbF(0,.8,0,1)), (12,QColor.fromRgbF(0,0,1,1))]
        for column, clr in colored_columns:
            max_value = max([float(self.tableWidget.item(row, column).text().replace(',', '')) for row in range(self.tableWidget.rowCount())])
            min_value = min([float(self.tableWidget.item(row, column).text().replace(',', '')) for row in range(self.tableWidget.rowCount())])
            for row in range(self.tableWidget.rowCount()):
                value = float(self.tableWidget.item(row, column).text().replace(',', ''))
                intensity = (value - min_value) / (max_value - min_value) if max_value != min_value else 1
                color = QColor.fromRgbF(clr.redF() * intensity, clr.greenF() * intensity, clr.blueF() * intensity, 1) # Example gradient from red to blue
                self.tableWidget.item(row, column).setBackground(color)
        for row in range(self.tableWidget.rowCount()):
            self.tableWidget.item(row, 6).setBackground(QColor.fromRgbF(0,0,0,1))

app = QApplication([])
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
window = YouTubeDataReaper()
window.show()
app.exec()
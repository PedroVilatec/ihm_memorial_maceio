# -*- coding: utf-8 -*-
import subprocess
import sys, os
import vlc
import glob
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Q_ARG, QAbstractItemModel,
		QFileInfo, qFuzzyCompare, QMetaObject, QModelIndex, QObject, Qt,
		QThread, QTime, QUrl)
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette
from PyQt5.QtMultimedia import (QAbstractVideoBuffer, QMediaContent,
		QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
		QFormLayout, QHBoxLayout, QLabel, QListView, QMessageBox, QPushButton,
		QSizePolicy, QSlider, QStyle, QToolButton, QVBoxLayout, QWidget)
import btnStyle

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot, QTimer,  QPoint, QThread, pyqtSignal, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap, qRgb, QColor, QImage, QCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget,\
	 QAction, QTabWidget,QVBoxLayout, QLabel, QRadioButton, QHBoxLayout, QGroupBox, QMessageBox, QColorDialog, QScroller

_excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
	traceback_formated = traceback.format_exception(exctype, value, traceback)
	traceback_string = "".join(traceback_formated)
	print(traceback_string, file=sys.stderr)
	sys.exit(1)
sys.excepthook = exception_hook
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class PlaylistModel(QAbstractItemModel):

	Title, ColumnCount = range(2)

	def __init__(self, parent=None):
		super(PlaylistModel, self).__init__(parent)

		self.m_playlist = None

	def rowCount(self, parent=QModelIndex()):
		return self.m_playlist.mediaCount() if self.m_playlist is not None and not parent.isValid() else 0

	def columnCount(self, parent=QModelIndex()):
		return self.ColumnCount if not parent.isValid() else 0

	def index(self, row, column, parent=QModelIndex()):
		return self.createIndex(row, column) if self.m_playlist is not None and not parent.isValid() and row >= 0 and row < self.m_playlist.mediaCount() and column >= 0 and column < self.ColumnCount else QModelIndex()

	def parent(self, child):
		return QModelIndex()

	def data(self, index, role=Qt.DisplayRole):
		if index.isValid() and role == Qt.DisplayRole:
			if index.column() == self.Title:
				location = self.m_playlist.media(index.row()).canonicalUrl()
				return QFileInfo(location.path()).fileName()

			return self.m_data[index]

		return None

	def playlist(self):
		return self.m_playlist

	def setPlaylist(self, playlist):
		if self.m_playlist is not None:
			self.m_playlist.mediaAboutToBeInserted.disconnect(
					self.beginInsertItems)
			self.m_playlist.mediaInserted.disconnect(self.endInsertItems)
			self.m_playlist.mediaAboutToBeRemoved.disconnect(
					self.beginRemoveItems)
			self.m_playlist.mediaRemoved.disconnect(self.endRemoveItems)
			self.m_playlist.mediaChanged.disconnect(self.changeItems)

		self.beginResetModel()
		self.m_playlist = playlist

		if self.m_playlist is not None:
			self.m_playlist.mediaAboutToBeInserted.connect(
					self.beginInsertItems)
			self.m_playlist.mediaInserted.connect(self.endInsertItems)
			self.m_playlist.mediaAboutToBeRemoved.connect(
					self.beginRemoveItems)
			self.m_playlist.mediaRemoved.connect(self.endRemoveItems)
			self.m_playlist.mediaChanged.connect(self.changeItems)

		self.endResetModel()

	def beginInsertItems(self, start, end):
	   
		self.beginInsertRows(QModelIndex(), start, end)

	def endInsertItems(self):
	  
		self.endInsertRows()

	def beginRemoveItems(self, start, end):
		self.beginRemoveRows(QModelIndex(), start, end)

	def endRemoveItems(self):
		self.endRemoveRows()

	def changeItems(self, start, end):
		self.dataChanged.emit(self.index(start, 0),
				self.index(end, self.ColumnCount))
		
class Player(QWidget):

	fullScreenChanged = pyqtSignal(bool)
	signalLongPress = pyqtSignal(str, int)
	eject = pyqtSignal()

	def __init__(self, config,  parent=None):
		super(Player, self).__init__(parent)
		self.player = QMediaPlayer()
		self.playlist = QMediaPlaylist()
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(4000)            
		self.config = config
		self.colorDialog = None
		self.trackInfo = ""
		self.statusInfo = ""
		self.duration = 0
		self.longPress = False # pressionamento por três segundos de uma faixa de audio
		self.player.setPlaylist(self.playlist)      
		self.player.durationChanged.connect(self.durationChanged)
		self.player.positionChanged.connect(self.positionChanged)

		
		self.player.metaDataChanged.connect(self.metaDataChanged)
		self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)
		self.player.mediaStatusChanged.connect(self.statusChanged)
		self.player.bufferStatusChanged.connect(self.bufferingProgress)
		self.player.videoAvailableChanged.connect(self.videoAvailableChanged)
		self.player.error.connect(self.displayErrorMessage)

##        self.videoWidget = VideoWidget()
##        self.player.setVideoOutput(self.videoWidget)

		self.playlistModel = PlaylistModel()
		self.playlistModel.setPlaylist(self.playlist)

		self.playlistView = QListView()
		self.playlistView.setSpacing(2)
		QScroller.grabGesture(
			self.playlistView.viewport(), QScroller.LeftMouseButtonGesture
		)        
		self.playlistView.setStyleSheet(''' 
				
				background-color: white;
				font: 20px Arial ;
				
				color: blue;
				selection-color: white;
				selection-background-color: blue;
			}''')               
		self.playlistView.setModel(self.playlistModel)
		self.playlistView.setCurrentIndex(
				self.playlistModel.index(self.playlist.currentIndex(), 0))

		#~ self.playlistView.activated.connect(self.jump)
		self.playlistView.clicked.connect(self.jump)  
		self.playlistView.pressed.connect(self.pressed)
		self.playlistView.mouseReleaseEvent = self.mouseReleaseEvento
 

		self.slider = QSlider(Qt.Horizontal)
	 
		   


		self.labelDuration = QLabel()
		self.slider.sliderMoved.connect(self.seek) 
#######################################################################
		self.videoframe = QtWidgets.QFrame(
			frameShape=QtWidgets.QFrame.Box, frameShadow=QtWidgets.QFrame.Raised
		)
		self.vlc_instance = vlc.Instance('--loop')
		folder = os.path.join(ROOT_DIR,"IHM","musicas")
		print("folder", folder)
		
		self.files = []
		# ~ for ext in ('*.mp3', '*.wmv', '*.mp4'):
        # ~ lista = []
        # ~ for f in sorted(find_files(os.path.join(ROOT_DIR,"IHM") ,self.config['VIDEO_FILES'] + self.config['AUDIO_FILES'])):
            # ~ lista.append(f)		
		for ext in (self.config['VIDEO_FILES']+self.config['AUDIO_FILES']):
			print(ext)
			self.files.extend(glob.glob(os.path.join(folder, ext)))
			print("self.files", self.files)
		self.addToPlaylist(sorted(self.files))
		self.mediaList = self.vlc_instance.media_list_new(sorted(self.files))
		self.listPlayer = self.vlc_instance.media_list_player_new() #Create a new MediaListPlayer instance. 
		self.listPlayer.set_media_list(self.mediaList)
		self.mediaplayer = self.listPlayer.get_media_player()
		self.vlc_event_manager = self.mediaplayer.event_manager()
		self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, self.durationChanged_vlc)
		self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError, self.printError)
		self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self.playlistPositionChanged)
		# ~ self.vlc_event_manager.event_attach(vlc.EventType.MediaDurationChanged, self.positionChanged_vlc) 
			  
		if sys.platform.startswith("linux"):  # for Linux using the X Server
			self.mediaplayer.set_xwindow(self.videoframe.winId())
		elif sys.platform == "win32":  # for Windows
			self.mediaplayer.set_hwnd(self.videoframe.winId())
		elif sys.platform == "darwin":  # for MacOS
			self.mediaplayer.set_nsobject(self.videoframe.winId())
		# ~ filename = r"C:\Users\Public\Videos\Sample Videos\video_1.mp4"
		# ~ filename = r"C:\Users\Public\Videos\Sample Videos\13-ta-com-raiva-de-mim.mp3"
		# ~ self.media = self.instance.media_new(filename)
		# ~ self.mediaplayer.set_media(self.media)

		self.listPlayer.play_item_at_index(0)
		self.mediaplayer.audio_set_volume(100)
		self.player.setVolume(100)
					
			
#######################################################################
		# ~ self.slider.setRange(0, self.player.duration() / 1000)
		# ~ print("length", self.mediaplayer.get_length())
		# ~ self.slider.setRange(0, self.mediaplayer.get_length() / 1000)
		# ~ self.slider.setRange(0,100)


		openButton = QPushButton("Abrir", clicked=self.open_file)

		class_controls = PlayerControls(self.mediaplayer) #classe
		class_controls.setState(self.player.state())
		class_controls.setVolume(self.player.volume())
		class_controls.setMuted(class_controls.isMuted())
		class_controls.play.connect(self.mediaplayer.play)
		class_controls.pause.connect(self.mediaplayer.pause)
		
		class_controls.stop.connect(self.player.stop)
		class_controls.stop.connect(self.mediaplayer.stop)
		
		class_controls.stop.connect(self.stopped)
		
		# ~ class_controls.next.connect(self.playlist.next)
		class_controls.next.connect(self.listPlayer.next)
		class_controls.previous.connect(self.previousClicked)
		# ~ class_controls.previous.connect(self.listPlayer.previous)
		
		class_controls.changeVolume.connect(self.player.setVolume)
		class_controls.changeVolume.connect(self.mediaplayer.audio_set_volume)
		
		class_controls.changeMuting.connect(self.player.setMuted)
		class_controls.changeRate.connect(self.player.setPlaybackRate)
		class_controls.classControlEject.connect(self.playerEject)
##        class_controls.stop.connect(self.videoWidget.update)

		self.player.stateChanged.connect(class_controls.setState)
		self.player.volumeChanged.connect(class_controls.setVolume)
		self.player.mutedChanged.connect(class_controls.setMuted)

##        self.fullScreenButton = QPushButton("FullScreen")
##        self.fullScreenButton.setCheckable(True)

##        self.colorButton = QPushButton("Color Options...")
##        self.colorButton.setEnabled(False)
##        self.colorButton.clicked.connect(self.showColorDialog)

					
		displayLayout = QHBoxLayout()
##        displayLayout.addWidget(self.videoWidget, 2)
		displayLayout.addWidget(self.playlistView)
		displayLayout.addWidget(self.videoframe,2)

		controlLayout = QHBoxLayout()
		controlLayout.setContentsMargins(0, 0, 0, 0)
		#~ controlLayout.addWidget(openButton)
		#~ controlLayout.addStretch(1) #adiciona um espaço vazio
		controlLayout.addWidget(class_controls)
		#~ controlLayout.addStretch(1) #adiciona um espaço vazio
##        controlLayout.addWidget(self.fullScreenButton)
##        controlLayout.addWidget(self.colorButton)

		layout = QVBoxLayout()
		layout.addLayout(displayLayout)
		hLayout = QHBoxLayout()
		hLayout.addWidget(self.slider)
		hLayout.addWidget(self.labelDuration)
		layout.addLayout(hLayout)
		layout.addLayout(controlLayout)
		#~ layout.addLayout(histogramLayout)

		self.setLayout(layout)

		if not self.player.isAvailable():
			QMessageBox.warning(self, "Service not available",
					"The QMediaPlayer object does not have a valid service.\n"
					"Please check the media service plugins are installed.")

			class_controls.setEnabled(False)
			self.playlistView.setEnabled(False)
##            openButton.setEnabled(False)
##            self.colorButton.setEnabled(False)
##            self.fullScreenButton.setEnabled(False)

		self.metaDataChanged()
			   
		global play_list
					  
		#self.addToPlaylist(play_list)

	def printError(self):
		print("ERROR")
		
	def playerEject(self):
		self.eject.emit()
		
		# ~ f = self.ejecter
		# ~ 
		# ~ if midia_usb != "":                     
			# ~ msgBox = QMessageBox()
			# ~ msgBox.setWindowTitle('Ejetar '+ str(midia_usb)+" ?")
			# ~ msgBox.setText('''<h1><strong><span style="color: #0000ff;">\
			# ~ Deseja ejetar a m&iacute;dia?</span></strong></h1>''')
			
			# ~ bt1   = QPushButton('Cancelar')
			# ~ bt1.setStyleSheet(btnStyle.btn_style())
			# ~ bt1.setMinimumWidth(180)
			# ~ bt1.setMaximumWidth(180)
			# ~ bt1.setMinimumHeight(80)
			# ~ bt1.clicked.connect(self.abort_remove)
			# ~ msgBox.addButton(bt1, QMessageBox.YesRole)
			# ~ bt2   = QPushButton('Sim')
			# ~ bt2.setStyleSheet(btnStyle.btn_style())
			# ~ bt2.setMinimumWidth(180)
			# ~ bt2.setMaximumWidth(180)
			# ~ bt2.setMinimumHeight(80)
			# ~ bt2.clicked.connect(self.remove_midia)
			# ~ msgBox.addButton(bt2, QMessageBox.NoRole)
			# ~ flags = Qt.WindowFlags()
			# ~ flags |= Qt.SplashScreen
			# ~ msgBox.setWindowFlags(flags)   
			# ~ msg = msgBox.exec_()        
		# ~ print("eject")
		
	def volume_encoder(self, vol):
		'''
		Altera o volume através da classe no arquivo led-encoder
		'''
		self.player.setVolume(vol)
		self.mediaplayer.audio_set_volume(vol)
		
	def open_file(self):
		fileNames, _ = QFileDialog.getOpenFileNames(self, "ESCOLHA O ÁLBUM","/media/pi")
	
		self.addToPlaylist(fileNames)

	def addToPlaylist(self, fileNames):
		# ~ global play_list 
		# ~ print(fileNames)          
		for name in fileNames:
			fileInfo = QFileInfo(name)
			if fileInfo.exists():
								
				url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
				print("url", fileInfo.absoluteFilePath())
				if fileInfo.suffix().lower() == 'mp3':
					# ~ print(QMediaContent(url).filename())
					print(QMediaContent(url).canonicalUrl().fileName())
					self.playlist.addMedia(QMediaContent(url))
##                    self.playlist.load(url)
				else:
					self.playlist.addMedia(QMediaContent(url))
					print("passou 2")
			else:
				url = QUrl(name)
				if url.isValid():
					print("passou 3")
					self.playlist.addMedia(QMediaContent(url))

	def durationChanged(self, duration):
		duration /= 1000

		self.duration = duration
		self.slider.setMaximum(duration)
		
	   

	def positionChanged(self, progress):

		progress /= 1000
		if not self.slider.isSliderDown():
			self.slider.setValue(progress)


		self.updateDurationInfo(progress)

	def durationChanged_vlc(self, event):
		'''
		positionChanged
		'''
		# ~ print(self.mediaplayer.get_role()) #printa 2
		progress = event.u.new_time/1000
		if not self.slider.isSliderDown():
			self.slider.setValue(progress)           
		self.duration = self.mediaplayer.get_length() / 1000
		self.updateDurationInfo(progress)
		self.slider.setMaximum(self.duration) 
		
	def positionChanged_vlc(self, event):
		# ~ self.mediaplayer.get_time()/1000
		
		print("POSITION CHANGED", self.mediaplayer.get_length())
		
	def metaDataChanged(self):
		pass
		#~ if self.player.isMetaDataAvailable():
			#~ self.setTrackInfo("%s - %s" % (
					#~ self.player.metaData(QMediaMetaData.AlbumArtist),
					#~ self.player.metaData(QMediaMetaData.Title)))

	def previousClicked(self):
		# Go to the previous track if we are within the first 5 seconds of
		# playback.  Otherwise, seek to the beginning.
		# ~ print(, )
		if self.listPlayer.previous() > -1:
			print("PREVIOUS")
			index = self.mediaList.index_of_item(self.mediaplayer.get_media())			
			# ~ self.playlistView.setCurrentIndex(
				# ~ self.playlistModel.index(index, 0))
			# ~ print("INDEX PREVIOUS VLC"	, index)
		# ~ if self.mediaplayer.get_time() <= 5000:
			# ~ print("status previous vlc", self.listPlayer.previous())
			# ~ print("previous __getitem__ ", self.listPlayer.__getitem__)
			# ~ for row in self.listPlayer.__iter__():
				# ~ print("previous", row)

			# ~ self.playlist.setCurrentIndex(self.playlistView.currentIndex().row())
		# ~ else:
			# ~ self.mediaplayer.set_time(0)
			# ~ self.playlist.setCurrentIndex(self.playlistView.currentIndex().row())
			# ~ self.mediaplayer.play()
			
	def mouseReleaseEvento(self, event):
		'''
		Ao clicar na faixa por 4 segundos ocorrerá a possibilidade de realizar uma cerimonia com audio do ihm
		'''
		print("released")
		self.timer.stop() #desabilita o timer caso o pressionamento for menor que o tempo setado
		if self.longPress == False:
			nameMedia = self.playlistView.currentIndex().data()
			if self.playlistView.currentIndex().isValid():            
				# ~ if not any(nameMedia[-4:] in item for item in self.config["VIDEO_FILES"]):
					if self.playlistView.currentIndex().isValid():
						
						self.playerState = QMediaPlayer.StoppedState    
						self.playlist.setCurrentIndex(self.playlistView.currentIndex().row())
						self.listPlayer.play_item_at_index(self.playlistView.currentIndex().row())
						print("MEDIA LIST VLC COUNT", self.mediaList.count())
						# ~ for value in self.mediaList.__iter__():  
						    # ~ print("MEDIA LIST VLC COUNT", value)
						print("index medialist vlc e listview", self.mediaList.index_of_item(self.mediaplayer.get_media()), self.playlistView.currentIndex().row())
						# ~ print("MEDIA INSTANCE", self.mediaplayer.get_media())
						print("URL", self.mediaplayer.get_media().get_mrl())
						# ~ print("CHAPTER", self.mediaplayer.get_chapter())
						          
		
		self.longPress = False
	def stopped(self):
		print("passou")

	def mousePressEvento(self, ev):
		print("mouse")

	def pressed(self, index):
		print("LISTVIEW PRESSED")
		self.player.stop
		nameMedia = self.playlistView.currentIndex().data()
		if self.playlistView.currentIndex().isValid():
			if any(nameMedia[-4:] in item for item in self.config["VIDEO_FILES"]):
				location = self.playlist.media(index.row()).canonicalUrl()
				local_media = QFileInfo(location.path()).absoluteFilePath()
				# ~ # os.system('omxplayer --adev hdmi --win 0,0,640,480 ' + local_media)
				# ~ logging.basicConfig(level=logging.INFO)
				# ~ try:
					# ~ player_log = logging.getLogger("Player 1")
					# ~ player = OMXPlayer(local_media, args=[  '-o', 'local', '--no-osd','-b', '--win', '0 0 600 480',], dbus_name='org.mpris.MediaPlayer2.omxplayer1')
					# ~ player.set_aspect_mode('fill')
					# ~ # player.set_video_pos(0, 0, 680, 480)
				# ~ except NameError:# dbus.exceptions.DBusException:
					# ~ print("Reiniciando App")
					# ~ os.execv(sys.executable, ['python3'] + sys.argv)
				# ~ else:
					# ~ print("Iniciando")                
				print()

		self.timer.timeout.connect(self.verifica_longPress)
		self.timer.start()      
		self.indexMedia = index.row()
		self.nameMedia = index.data()
		
	@QtCore.pyqtSlot()
	def verifica_longPress(self):
		'''
		Caso se mantenha uma faixa no playlist pressionada por mais de 4 segundos
		'''
		# ~ print("
		self.signalLongPress.emit(self.nameMedia, self.indexMedia)
		self.timer.stop()
		self.longPress = True
  
			
	def msgBoxFunction(self, text,media, btn1, btn2, mqtt):
		msgBox = QMessageBox()
		msgBox.setText('''<h3><strong><span style="color: #0000ff;">\
			{}</span>&nbsp;<span style="color:red;">{}</span>&nbsp;<span style="color:#0000ff;">durante a cerimônia?</span></strong></h3>'''.format(text, media))
		if btn1 != "":
			bt1   = QPushButton(btn1)
			bt1.setStyleSheet(btnStyle.btn_style())
			bt1.setMinimumWidth(180)
			bt1.setMaximumWidth(180)
			bt1.setMinimumHeight(80)
			# ~ bt1.clicked.connect()
			msgBox.addButton(bt1, QMessageBox.YesRole)
		if btn2 != "":
			bt2   = QPushButton(btn2)
			bt2.setStyleSheet(btnStyle.btn_style())
			bt2.setMinimumWidth(180)
			bt2.setMaximumWidth(180)
			bt2.setMinimumHeight(80)
			# ~ bt2.clicked.connect()
			msgBox.addButton(bt2, QMessageBox.NoRole)
		flags = Qt.WindowFlags()
		flags |= Qt.SplashScreen
		msgBox.setWindowFlags(flags)
		if mqtt:
			mqttLocal.status_mqtt["msgWidget"] = msgBox
			mqttLocal.status_mqtt["msgDisplayed"] = True
			
		msg = msgBox.exec_()
		return msg   
		  
	def playCerimonia(self, index):
		self.playerState = QMediaPlayer.StoppedState    
		self.playlist.setCurrentIndex(index)
		self.player.play()
		self.player.play()      
			
	def jump(self, index):
		'''
		Ao clicar na faixa por 4 segundos ocorrerá a possibilidade de realizar uma cerimonia com audio do ihm
		'''
		print("JUMP")
		self.timer.stop() #desabilita o timer caso o pressionamento for menor que o tempo setado
		if self.longPress == False:
			if index.isValid():
				self.playerState = QMediaPlayer.StoppedState    
				self.playlist.setCurrentIndex(index.row()) #alterei para vlc
				self.listPlayer.play_item_at_index(index.row())
				# ~ self.player.play()
				# ~ self.player.play()            
		
		self.longPress = False

	def playlistPositionChanged(self, position):
		# ~ print("POSITION CHANGED", self.mediaList.index_of_item(self.listPlayer.get_media_player().get_media()))
		print("URL", self.mediaplayer.get_media().get_mrl())
		# ~ self.playlistView.setCurrentIndex(
				# ~ self.playlistModel.index(self.mediaList.index_of_item(self.listPlayer.get_media_player().get_media()), 0))

	def seek(self, seconds):
		if self.mediaplayer.is_seekable():
			self.mediaplayer.set_time(seconds * 1000)
		self.player.setPosition(seconds * 1000)

	def statusChanged(self, status):
		self.handleCursor(status)
		print("status", status)
		if status == QMediaPlayer.LoadingMedia:
			self.setStatusInfo("Loading...")
		elif status == QMediaPlayer.StalledMedia:
			self.setStatusInfo("Media Stalled")
		elif status == QMediaPlayer.EndOfMedia:
			QApplication.alert(self)
		elif status == QMediaPlayer.InvalidMedia:
			self.displayErrorMessage()
		else:
			self.setStatusInfo("")

	def handleCursor(self, status):
		if status in (QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.StalledMedia):
			self.setCursor(Qt.BusyCursor)
		else:
			self.unsetCursor()

	def bufferingProgress(self, progress):
		self.setStatusInfo("Buffering %d%" % progress)

	def videoAvailableChanged(self, available):
		
##        if available:
##            self.fullScreenButton.clicked.connect(
##                    self.videoWidget.setFullScreen)
##            self.videoWidget.fullScreenChanged.connect(
##                    self.fullScreenButton.setChecked)
##
##            if self.fullScreenButton.isChecked():
##                self.videoWidget.setFullScreen(True)
##        else:
##            self.fullScreenButton.clicked.disconnect(
##                    self.videoWidget.setFullScreen)
##            self.videoWidget.fullScreenChanged.disconnect(
##                    self.fullScreenButton.setChecked)
##
##            self.videoWidget.setFullScreen(False)
##
##        self.colorButton.setEnabled(available)
		  pass

	def setTrackInfo(self, info):
		self.trackInfo = info

		#~ if self.statusInfo != "":
			#~ self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
		#~ else:
			#~ self.setWindowTitle(self.trackInfo)

	def setStatusInfo(self, info):
		self.statusInfo = info

		#~ if self.statusInfo != "":
			#~ self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
		#~ else:
			#~ self.setWindowTitle(self.trackInfo)

	def displayErrorMessage(self):
		self.setStatusInfo(self.player.errorString())

	def updateDurationInfo(self, currentInfo):
		duration = self.duration
		if currentInfo or duration:
			currentTime = QTime((currentInfo/3600)%60, (currentInfo/60)%60,
					currentInfo%60, (currentInfo*1000)%1000)
			totalTime = QTime((duration/3600)%60, (duration/60)%60,
					duration%60, (duration*1000)%1000);

			format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
			tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
		else:
			tStr = ""
		self.labelDuration.setText(tStr)

 
class PlayerControls(QWidget):

	play = pyqtSignal()
	clear = pyqtSignal()
	pause = pyqtSignal()
	stop = pyqtSignal()
	next = pyqtSignal()
	classControlEject = pyqtSignal()
	previous = pyqtSignal()
	changeVolume = pyqtSignal(int)
	changeMuting = pyqtSignal(bool)
	changeRate = pyqtSignal(float)

	def __init__(self, player_vlc, parent=None):
		super(PlayerControls, self).__init__(parent)
		self.mediaplayer = player_vlc
		self.playerState = QMediaPlayer.StoppedState
		self.playerMuted = False
		self.playButton = QToolButton(clicked=self.playClicked)
		
		self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "play.png")))
		self.playButton.setIconSize(QtCore.QSize(90, 35))
 

		self.stopButton = QToolButton(clicked=self.stop)
		
		#~ self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
		# self.stopButton.setEnabled(False)
		self.stopButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "stop.png")))
		self.stopButton.setIconSize(QtCore.QSize(90, 35))  


		self.nextButton = QToolButton(clicked=self.next)
		self.nextButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "avancar.png")))
		self.nextButton.setIconSize(QtCore.QSize(90, 35))  
 

		self.previousButton = QToolButton(clicked=self.previous)                

		self.previousButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "retroceder.png")))
		self.previousButton.setIconSize(QtCore.QSize(90, 35)) 
		
		self.ejectButton = QToolButton(clicked=self.ejecter)

		self.ejectButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "ejetar.png")))
		self.ejectButton.setIconSize(QtCore.QSize(90, 35))                      

		self.muteButton = QToolButton(clicked=self.muteClicked) 
		self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "volume.png")))
		self.muteButton.setIconSize(QtCore.QSize(60, 20))                  
		self.volumeSlider = QSlider(Qt.Horizontal,
				valueChanged=self.changeVolume)
		self.volumeSlider.setMinimumSize(QtCore.QSize(180, 80))
		self.volumeSlider.setRange(0, 100)
		self.volumeSlider.setProperty("value", 20)
		self.volumeSlider.setSliderPosition(20)
		self.volumeSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
		self.volumeSlider.setTickInterval(25)        
		self.volumeSlider.setStyleSheet(''' QSlider::groove:horizontal {
				border: 1px solid;
				background-color: grey;
				height: 15px;
				margin: 10px;
			}
			
			QSlider::handle:horizontal {
				background-color: blue;
				border: 1px solid;
				border-style: outset;
				border-radius: 5px;
				height: 10px;
				width: 15px;
				margin: -30px 0px;
			}''')


		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.stopButton)
		layout.addWidget(self.previousButton)
		layout.addWidget(self.playButton)
		layout.addWidget(self.nextButton)
		layout.addWidget(self.ejectButton)
		layout.addWidget(self.muteButton)
		layout.addWidget(self.volumeSlider)
		#~ layout.addWidget(self.rateBox)
		self.setLayout(layout)
	def tab_iluminacao(self):
		pass

	def state(self):
		return self.playerState

	def setState(self,state):
		if state != self.playerState:
			self.playerState = state

			if state == QMediaPlayer.StoppedState:
				self.stopButton.setEnabled(False)
				self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "play.png")))
				#~ self.playButton.setIcon(
						#~ self.style().standardIcon(QStyle.SP_MediaPlay))
			elif state == QMediaPlayer.PlayingState:
				self.stopButton.setEnabled(True)
				self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "pause.png")))
				#~ self.playButton.setIcon(
						#~ self.style().standardIcon(QStyle.SP_MediaPause))
			elif state == QMediaPlayer.PausedState:
				self.stopButton.setEnabled(True)
				self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "play.png")))
				#~ self.playButton.setIcon(
						#~ self.style().standardIcon(QStyle.SP_MediaPlay))
			 

		   
	def abort_remove(self):
		global remove_midia     
		remove_midia = False
			
	def remove_midia(self):
		global remove_midia     
		global midia_usb       
		midia = midia_usb 
			   
		if midia != "":
			remove_midia = True 
			
	
	def volume(self):
		return self.volumeSlider.value()
		print("buscando o que eh")

	def setVolume(self, volume):
		self.volumeSlider.setValue(volume)

	def isMuted(self):
		return self.mediaplayer.audio_get_mute()

	def setMuted(self, muted):
		print("MUTED", muted)
		if muted:
			print(os.path.join(ROOT_DIR, "IHM", "btn", "mute.png"))
			#~ self.muteButton.setStyleSheet(btnStyle.style_player("/usr/share/APP/btn/mute.png"))
			self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "mute.png")))
			
		else:
			os.path.join(ROOT_DIR, "IHM", "btn", "volume.png")
			self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "IHM", "btn", "volume.png")))
			  
		#~ else:
			#~ self.muteButton.setIcon(
					#~ self.style().standardIcon(
							#~ QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume))
	def ejecter(self):
		self.classControlEject.emit()
		
	def playClicked(self):
		if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState) and \
		self.mediaplayer.get_state() in (vlc.State.Stopped, vlc.State.Paused, vlc.State.NothingSpecial):
			self.play.emit()
		elif self.playerState == QMediaPlayer.PlayingState or self.mediaplayer.get_state() == vlc.State.Playing:
			self.pause.emit()

	def muteClicked(self):
		
		self.mediaplayer.audio_toggle_mute()
		if self.mediaplayer.audio_get_mute():
			self.changeMuting.emit(True)		
		else:
			self.changeMuting.emit(False)
			
	def playbackRate(self):
		return self.rateBox.itemData(self.rateBox.currentIndex())

	def setPlaybackRate(self, rate):
		for i in range(self.rateBox.count()):
			if qFuzzyCompare(rate, self.rateBox.itemData(i)):
				self.rateBox.setCurrentIndex(i)
				return

		self.rateBox.addItem("%dx" % rate, rate)
		self.rateBox.setCurrentIndex(self.rateBox.count() - 1)

	def updateRate(self):
		self.changeRate.emit(self.playbackRate())

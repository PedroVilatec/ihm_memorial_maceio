# -*- coding: utf-8 -*-
import subprocess
import sys, os
import vlc
import glob
import fnmatch
import alsaaudio
import linecache
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Q_ARG, QAbstractItemModel,
		QFileInfo, qFuzzyCompare, QMetaObject, QModelIndex, QObject, Qt,
		QThread, QTime, QUrl)
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette
from PyQt5.QtMultimedia import (QAbstractVideoBuffer, QMediaContent,
		QMediaMetaData, QMediaPlayer, QMediaPlaylist, )
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
		QFormLayout, QHBoxLayout, QLabel, QListView, QMessageBox, QPushButton,
		QSizePolicy, QSlider, QStyle, QToolButton, QVBoxLayout, QWidget, QFrame)
import btnStyle
import time
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, QTimer,  QPoint, QThread, pyqtSignal, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap, qRgb, QColor, QImage, QCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget,\
	 QAction, QTabWidget,QVBoxLayout, QLabel, QRadioButton, QHBoxLayout, QGroupBox, QMessageBox, QColorDialog, QScroller

_excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
	 _excepthook(exctype, value, traceback)
	 sys.exit(0)
sys.excepthook = exception_hook

def printException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
	
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
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
	signalLongPress = pyqtSignal(dict)
	eject = pyqtSignal()
	def __init__(self, config, parent=None):
		super(Player, self).__init__(parent)
		self.playlist = QMediaPlaylist()
		self.colorDialog = None
		self.trackInfo = ""
		self.statusInfo = ""
		self.duration = 0
		self.config = config
		self.longPress = False # pressionamento por três segundos de uma faixa de audio

		self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)
		
		self.playlistModel = PlaylistModel()
		self.playlistModel.setPlaylist(self.playlist)
		self.vlc_instance = vlc.Instance()#'--verbose 3')
		self.vlc_instance.log_unset()
	
		self.listPlayer = self.vlc_instance.media_list_player_new() #Create a new MediaListPlayer instance.

#############################  CARREGA USB PLAYLIST  ############################

		self.update_playlist()
#############################  CARREGA USB PLAYLIST  ############################

		self.mediaPlayer = self.listPlayer.get_media_player()
		self.mediaPlayer.audio_set_volume(0)
		class_controls = PlayerControls(self.mediaPlayer)
		self.labelDuration = class_controls.labelDuration
		self.playlistView = class_controls.playlistView
		self.playlistView.setModel(self.playlistModel)
		self.playlistView.setCurrentIndex(
				self.playlistModel.index(self.playlist.currentIndex(), 0))
		QScroller.grabGesture(
			self.playlistView.viewport(), QScroller.LeftMouseButtonGesture
		)				

		#~ self.playlistView.activated.connect(self.jump)

		self.playlistView.clicked.connect(self.jump)  
		self.playlistView.pressed.connect(self.pressed)
		self.playlistView.mouseReleaseEvent = self.mouseReleaseEvento
		
		self.slider_progress = class_controls.slider_progress
		self.slider_progress.sliderMoved.connect(self.seek)		
		self.mediaplayer_vlc_event_manager = self.mediaPlayer.event_manager()
		self.listPlayer_vlc_event_manager = self.listPlayer.event_manager()
		self.listPlayer.set_playback_mode(vlc.PlaybackMode.loop)
		self.listPlayer_vlc_event_manager.event_attach(vlc.EventType.MediaListPlayerPlayed, self.playlistFinished)
		 
		self.mediaplayer_vlc_event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, self.durationChanged_vlc)
		self.mediaplayer_vlc_event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError, self.printError)
		self.mediaplayer_vlc_event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self.playlistPositionChanged)
		
		self.mediaplayer_vlc_event_manager.event_attach(vlc.EventType.MediaPlayerPaused, class_controls.setState)
		self.mediaplayer_vlc_event_manager.event_attach(vlc.EventType.MediaPlayerStopped, class_controls.setState)
		self.mediaplayer_vlc_event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, class_controls.setState)
		

		self.mediaplayer_vlc_event_manager.event_attach(vlc.EventType.MediaDurationChanged, self.positionChanged_vlc) 
		self.frameVideoPlayer = class_controls.frameVideoPlayer
		self.frameVideoPlayer.mousePressEvent = self.f
		if sys.platform.startswith("linux"):  # for Linux using the X Server
			self.alsa = alsaaudio.Mixer(alsaaudio.mixers()[0])
			self.alsa.setvolume(10)			
			self.mediaPlayer.set_xwindow(self.frameVideoPlayer.winId())
			
		elif sys.platform == "win32":  # for Windows
			self.mediaPlayer.set_hwnd(self.frameVideoPlayer.winId())
		elif sys.platform == "darwin":  # for MacOS
			self.mediaPlayer.set_nsobject(self.frameVideoPlayer.winId())

		# ~ self.listPlayer.play_item_at_index(0)
		
					
			
#######################################################################
		# ~ self.slider_progress.setRange(0, self.player.duration() / 1000)
		# ~ print("length", self.mediaPlayer.get_length())
		# ~ self.slider_progress.setRange(0, self.mediaPlayer.get_length() / 1000)
		# ~ self.slider_progress.setRange(0,100)



		class_controls.setMuted(class_controls.isMuted())
		class_controls.play.connect(self.mediaPlayer.play)
		class_controls.pause.connect(self.mediaPlayer.pause)
		class_controls.stop.connect(self.mediaPlayer.stop)
		class_controls.next.connect(self.listPlayer.next)
		class_controls.previous.connect(self.previousClicked)
		class_controls.changeVolume.connect(self.mediaPlayer.audio_set_volume)
		class_controls.classControlEject.connect(self.playerEject)
		
		controlLayout = QHBoxLayout()
		controlLayout.setContentsMargins(0, 0, 0, 0)
		controlLayout.addWidget(class_controls)
		layout = QVBoxLayout()
		layout.addLayout(controlLayout)
		self.setLayout(layout)
		self.metaDataChanged()
		self.frameVideoPlayer.hide()

	def update_playlist(self):
		folder = os.path.join(ROOT_DIR,"musicas")
		files = []
		for ext in (self.config['VIDEO_FILES']+self.config['AUDIO_FILES']):
			files.extend(glob.glob(os.path.join(folder, ext)))		
		self.playlist.clear()
		self.addToPlaylist(sorted(files))


	def f(self, press):
		if self.playlistView.isVisible():
			self.playlistView.hide()
		else:
			self.playlistView.show()

	def click_video_config(self):
		'''
		Processa os botões de controle da aba Vídeo
		'''
		if self.sender().objectName() == "refresh_button":
			self.refresh_video()
		# if self.sender().objectName() == "step_retroceder":

		# if self.sender().objectName() == "step_avancar":

	def playlistFinished(self, event):
		print("FINAL DO PLAYLIST", event)
		# ~ self.mediaPlayer.stop()
		# ~ self.listPlayer.play_item_at_index(0)
		# ~ print("PASSOU")
			
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
		# ~ self.player.setVolume(vol)
		self.mediaPlayer.audio_set_volume(vol)
		
	# def open_file(self):
	# 	fileNames, _ = QFileDialog.getOpenFileNames(self, "ESCOLHA O ÁLBUM","/media/pi")
	
	# 	self.addToPlaylist(fileNames)

	def addToPlaylist(self, fileNames):
		self.playlist.clear()
		self.mediaList = self.vlc_instance.media_list_new(sorted(fileNames))
		self.listPlayer.set_media_list(self.mediaList)
		for name in fileNames:
			fileInfo = QFileInfo(name)
			if fileInfo.exists():

				url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
				# ~ print("url", fileInfo.absoluteFilePath())
				if fileInfo.suffix().lower() == 'mp3':
					# ~ print(QMediaContent(url).filename())
					# ~ print(QMediaContent(url).canonicalUrl().fileName())
					self.playlist.addMedia(QMediaContent(url))
##                    self.playlist.load(url)
				else:
					self.playlist.addMedia(QMediaContent(url))
					# ~ print("passou 2")
			else:
				url = QUrl(name)
				if url.isValid():
					# ~ print("passou 3")
					self.playlist.addMedia(QMediaContent(url))

	def durationChanged(self, duration):
		duration /= 1000

		self.duration = duration
		self.slider_progress.setMaximum(duration)
		
	   

	def positionChanged(self, progress):

		progress /= 1000
		if not self.slider_progress.isSliderDown():
			self.slider_progress.setValue(progress)

		self.updateDurationInfo(progress)

	def durationChanged_vlc(self, event):
		'''
		positionChanged
		'''
		# ~ print(self.mediaPlayer.get_role()) #printa 2
		progress = event.u.new_time/1000
		if not self.slider_progress.isSliderDown():
			self.slider_progress.setValue(progress)
	
		self.duration = self.mediaPlayer.get_length() / 1000
		self.updateDurationInfo(progress)
		self.slider_progress.setMaximum(self.duration)
		
	def positionChanged_vlc(self, event):
		# ~ self.mediaPlayer.get_time()/1000
		
		print("POSITION CHANGED", self.mediaPlayer.get_length())
		
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
		print("get role", self.mediaPlayer.get_role())
		
		if self.mediaPlayer.get_time() <= 5000:
			print("previous", self.listPlayer.previous())
			print("previous 1", self.listPlayer.__getitem__)
			# ~ for row in self.listPlayer.__iter__():
				# ~ print("previous", row)
			# ~ self.playlistView.setCurrentIndex(
				# ~ self.playlistModel.index(position, 0))
			self.playlist.setCurrentIndex(self.playlistView.currentIndex().row())
		else:
			self.mediaPlayer.set_time(0)
			self.playlist.setCurrentIndex(self.playlistView.currentIndex().row())
			self.mediaPlayer.play()
			
	def mouseReleaseEvento(self, event):
		'''
		Ao clicar na faixa por 4 segundos ocorrerá a possibilidade de realizar uma cerimonia com audio do ihm
		'''
		try:
			self.time_press = False
			if self.longPress == False:
				nameMedia = self.playlistView.currentIndex().data()
				if self.playlistView.currentIndex().isValid():
					#if not any(nameMedia[-4:] in item for item in self.config["VIDEO_FILES"]):
						if self.playlistView.currentIndex().isValid():
							# print("MEDIA LIST VLC COUNT", self.mediaList.count())
							#for value in self.mediaList.__iter__():  
								#print("MEDIA LIST VLC COUNT", value)
							# print("index medialist vlc e listview", self.mediaList.index_of_item(self.mediaPlayer.get_media()), self.playlistView.currentIndex().row())							
							# ~ self.mediaPlayer.stop()
							self.listPlayer.play_item_at_index(self.playlistView.currentIndex().row())

							#print("MEDIA INSTANCE", self.mediaPlayer.get_media())
							# print("URL", self.mediaPlayer.get_media().get_mrl())
							#print("CHAPTER", self.mediaPlayer.get_chapter())
									  
			
			self.longPress = False
		except:
			printException()
	def stopped(self):
		print("passou")

	def mousePressEvento(self, ev):
		print("mouse")

	def pressed(self, index):
		try:
			self.time_press = True
			nameMedia = self.playlistView.currentIndex().data()
			if self.playlistView.currentIndex().isValid():
				# if any(nameMedia[-4:] in item for item in self.config["VIDEO_FILES"]):
					location = self.playlist.media(index.row()).canonicalUrl()
					self.location_media1 = QFileInfo(location.path()).absoluteFilePath()
			QTimer.singleShot(4000, self.verifica_longPress)
			self.indexMedia = index.row()
			self.nameMedia = index.data()
		
		except:
			printException()
		
	@QtCore.pyqtSlot()
	def verifica_longPress(self):
		'''
		Caso se mantenha uma faixa no playlist pressionada por mais de 4 segundos
		'''
		if self.time_press:
			self.signalLongPress.emit({"name":self.nameMedia, "index":self.indexMedia, "url":self.location_media1})
			self.longPressPress = True
  
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
		# ~ self.player.play()
		# ~ self.player.play()      
			
	def jump(self, index):
		'''
		Ao clicar na faixa por 4 segundos ocorrerá a possibilidade de realizar uma cerimonia com audio do ihm
		'''
		print("JUMP")
		if self.longPress == False:
			if index.isValid():
				self.listPlayer.play_item_at_index(index.row())    
		
		self.longPress = False

	def playlistPositionChanged(self, position):
		name_media = os.path.basename(self.mediaPlayer.get_media().get_mrl())
		self.frameVideoPlayer.hide()
		self.playlistView.show()
		for ext in (self.config['VIDEO_FILES']):
			if ext.split(".")[1] in name_media:
				self.frameVideoPlayer.show()
				self.playlistView.hide()

		self.playlistView.setCurrentIndex(
				self.playlistModel.index(self.mediaList.index_of_item(self.mediaPlayer.get_media()), 0))


	def seek(self, seconds):
		if self.mediaPlayer.is_seekable():
			try:
				self.mediaPlayer.set_time(seconds * 1000)
			except:
				printException()

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
			progress = currentTime.toString(format)
			tStr = progress + " / " + totalTime.toString(format)
		else:
			tStr = "00:00:00"
		self.labelDuration.setText(tStr)

 
class PlayerControls(QFrame):

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
		base = os.path.dirname(os.path.abspath(__file__))
		uic.loadUi(os.path.join(base, "UI", "frame_playlist.ui"), self)
		self.mediaPlayer = player_vlc
		self.playerState = QMediaPlayer.StoppedState
		self.playerMuted = False
		self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR,"btn", "round_play.png")))
		self.playButton.clicked.connect(self.playClicked)
		self.stopButton.clicked.connect(self.stop)
		self.stopButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR,"btn", "round_stop.png")))
		self.nextButton.clicked.connect(self.next)
		self.nextButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR,"btn", "round_next.png")))
		self.previousButton.clicked.connect(self.previous)
		self.previousButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR,"btn", "round_last.png")))
		self.ejectButton.clicked.connect(self.ejecter)
		self.ejectButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR,"btn", "round_eject.png")))
		self.muteButton.clicked.connect(self.muteClicked)
		self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR,"btn", "round_unmute.png")))
		self.repeatButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR,"btn", "round_repeat.png")))
		self.volumeSlider.valueChanged.connect(self.changeVolume)
		self.volumeSlider.valueChanged.connect(self.update_label_volume)

	def update_label_volume(self, volume):
		self.labelVolume.setText(str(volume))

	def tab_iluminacao(self):
		pass

	def state(self):
		return self.playerState

	def setState(self,states):
		state = self.mediaPlayer.get_state()
		if state == vlc.State.Stopped:
			self.stopButton.setEnabled(False)
			self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "btn", "round_play.png")))
		elif state == vlc.State.Playing:
			self.stopButton.setEnabled(True)
			self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "btn", "round_pause.png")))
		elif state == vlc.State.Paused:
			self.stopButton.setEnabled(True)
			self.playButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "btn", "round_play.png")))
			 

		   
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
		return self.playerMuted

	def setMuted(self, muted):
		print("muted", muted)
		if muted:
			self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "btn", "round_mute.png")))
			
		else:
			self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "btn", "round_unmute.png")))
			
	def ejecter(self):
		self.classControlEject.emit()
		
	def playClicked(self):
		if self.mediaPlayer.get_state() in (vlc.State.Stopped, vlc.State.Paused, vlc.State.NothingSpecial):
			self.play.emit()
		elif self.mediaPlayer.get_state() == vlc.State.Playing:
			self.pause.emit()
			
	def muteClicked(self):
		
		self.mediaPlayer.audio_toggle_mute()
		if self.mediaPlayer.audio_get_mute():
			self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "btn", "round_mute.png")))
			self.changeMuting.emit(True)
					
		else:
			self.muteButton.setStyleSheet(btnStyle.style_player(os.path.join(ROOT_DIR, "btn", "round_unmute.png")))
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
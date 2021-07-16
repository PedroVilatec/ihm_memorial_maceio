# -*- coding: utf-8 -*-
# ~ from dialog import MeuDialog

import json
import player_
import btnStyle
from operations.mqtt import MosquittoServer, Mosquitto
from instance.config_json import Config
from instance.cenarios import Cenas
import fnmatch
import filecmp
import schedule
import linecache
import traceback
from PyQt5.QtCore import Qt
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Q_ARG, QAbstractItemModel,
        QFileInfo, qFuzzyCompare, QMetaObject, QModelIndex, QObject, Qt,
        QThread, QTime, QUrl)
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette, QTouchEvent
from PyQt5.QtMultimedia import (QAbstractVideoBuffer, QMediaContent,
        QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
        QFormLayout, QHBoxLayout, QLabel, QListView, QMessageBox, QPushButton,
        QSizePolicy, QSlider, QStyle, QToolButton, QVBoxLayout, QWidget , QWhatsThis, QScroller)

import functools
import itertools
import random
import json
import sys
import os
import time
import re
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, QTimer,  QPoint, QThread, pyqtSignal, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap, qRgb, QColor, QImage, QCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget,\
     QAction, QTabWidget, QVBoxLayout, QLabel, QRadioButton, QHBoxLayout, QGroupBox, QMessageBox, QColorDialog
import subprocess
print(os.getpid())

conf = Config()
# ~ config = conf.json_config['CONFIG']
_excepthook = sys.excepthook

def exception_hook(exctype, value, traceback):
    traceback_formated = traceback.format_exception(exctype, value, traceback)
    traceback_string = "".join(traceback_formated)
    print(traceback_string, file=sys.stderr)
    sys.exit(1)
sys.excepthook = exception_hook

def printException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def find_files(dir_path: str=None, patterns: [str]=None) -> [str]:
    """
    Returns a generator yielding files matching the given patterns
    :type dir_path: str
    :type patterns: [str]
    :rtype : [str]
    :param dir_path: Directory to search for files/directories under. s to current dir.
    :param patterns: Patterns of files to search for. s to ["*"]. Example: ["*.json", "*.xml"]
    """
    path = dir_path or "."
    path_patterns = patterns or ["*"]

    for root_dir, dir_names, file_names in os.walk(path):
        filter_partial = functools.partial(fnmatch.filter, file_names)

        for file_name in itertools.chain(*map(filter_partial, path_patterns)):
            
            yield os.path.join(root_dir, file_name)

if sys.platform != 'win32':
    root = os.path.dirname(os.path.abspath(__file__))
    pattern = "*.py"
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                
                if not ".debris" in path:
                    try:
                        #os.system("rm " + os.path.join(path, name+"_")) #remover todos                
                        if not(filecmp.cmp (os.path.join(path, name) ,os.path.join(path, "."+name+"_"))):
                            os.system("sudo cp " + os.path.join(path, name)+" "+os.path.join(path, "." + name + "_"))
                            
                    except Exception as e:
                        os.system("sudo cp " + os.path.join(path, name)+" "+os.path.join(path, "." + name + "_"))
                        print("Novo arquivo criado: ",os.path.join(path, name))
    
class Ui(QtWidgets.QMainWindow):
    def __init__(self, xml):
        super(Ui, self).__init__()
        uic.loadUi(xml, self)
        self.counter = 0
        self.counter2 = 0
        self.cenaAtual = 1
        self.canal_sanca = 1
        self.canal_dimer = 1
        self.imgIndex = 1
        self.senhaEnabled = False
        self.msgClass = None
        self.midia_usb = ""
        self.conf = conf
        self.timeElapsed = time.time()
        self.timeStarted = time.time()
        self.config = self.conf.json_config['CONFIG']
        self.mqttLocal = Mosquitto(self.config["TOPICO_INT_IHM"], self.config["PORTA_MQTT"])
        self.mqttLocal.on_update_config = self.update_config
        self.mqttLocal.on_confirm_update_config = self.confirm_update_config
        self.mqttLocal.config = self.config
        self.mqttServer = MosquittoServer(self.config["TOPICO_EXT_IHM"])
        if not 'win' in sys.platform:
            smb_init = SmbThread()
            smb_init.start()
        self.cenas = Cenas()
        if sys.platform != 'win32':
            self.setCursor(Qt.BlankCursor)
        self.json_cenas = self.cenas.load_cenario()
        self.tabMusicas = self.findChild(QtWidgets.QWidget, 'tab_musicas')
        self.tabColor = self.findChild(QtWidgets.QFrame, 'frame_color')
        widget = QtWidgets.QColorDialog()
        widget.setWindowFlags(QtCore.Qt.Widget)
        widget.setOptions(
            QtWidgets.QColorDialog.DontUseNativeDialog |
            QtWidgets.QColorDialog.NoButtons)
        layout = QtWidgets.QGridLayout(self.tabColor)
        layout.addWidget(widget)
        widget.currentColorChanged.connect(self.color_pick)
        self.findChild(QtWidgets.QPushButton, 'btn_cancelar_edic').clicked.connect(self.cancela_cenario)
        
        self.findChild(QtWidgets.QPushButton, 'btn_change_cena_dir').clicked.connect(self.change_cena_dir)
        self.findChild(QtWidgets.QPushButton, 'btn_change_cena_esq').clicked.connect(self.change_cena_esq)

        self.tabWidget = self.findChild(QtWidgets.QTabWidget, 'tabWidget')
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabEnabled(2, False)
        self.tabWidget.removeTab(5)
        self.sliderDimer = self.findChild(QtWidgets.QSlider, "slider_dimer")
        self.sliderDimer.valueChanged.connect(self.dimFunction)
        
        self.button_cenario_esquerda = self.findChild(QtWidgets.QPushButton, 'cenario_esquerda') 
        self.button_cenario_esquerda.clicked.connect(self.moveEsq)
        self.button_cenario_direita = self.findChild(QtWidgets.QPushButton, 'cenario_direita')
        self.button_cenario_direita.clicked.connect(self.moveDir)           

        self.timer = QTimer()
        self.timer.setInterval(1000)       
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()                  
        

        self.widgetSenha = self.findChild(QtWidgets.QWidget, 'widget_senha')

        self.groupSistema = self.findChild(QtWidgets.QGroupBox, 'groupBox_sistema')
        self.groupMecanismo = self.findChild(QtWidgets.QGroupBox, 'groupBox_mecanismo')
        self.groupSistema.hide()
        self.groupMecanismo.hide()
        
        self.button_select_cenario = self.findChild(QtWidgets.QPushButton, 'select_cenario') 
        self.button_select_cenario.clicked.connect(self.changeScenario)     
        self.button_select_cenario.setText("Selecionar  " + str(self.imgIndex))
        
        self.button_bloqueioAba = self.findChild(QtWidgets.QPushButton, 'botao_bloqueio_aba')   
        self.button_bloqueioAba.clicked.connect(self.bloqueiaAba)
        
        self.findChild(QtWidgets.QPushButton, 'apaga_cenario').clicked.connect(self.apagar_leds)
        self.findChild(QtWidgets.QPushButton, 'salva_cena').clicked.connect(self.salva_cenario)
        self.senha = [9,1,4,5,1,6]
        self.button_clicked_senha = []
        self.buttons_senha = []
        self.listRadioButtonDim = [None] * 11
        
        for botao in range(11): # atribui chamada de função com o argumento do botão
            self.buttons_senha.append(self.findChild(QtWidgets.QPushButton, 'botao_{}'.format(botao)))
            self.buttons_senha[botao].clicked.connect(self.button_senha)
            
        for children in self.findChildren(QtWidgets.QWidget): 
            if isinstance(children, QtWidgets.QRadioButton):
                children.toggled.connect(self.radioButton)
                if "dim_" in children.objectName():
                    self.listRadioButtonDim[int(children.objectName().split("dim_")[1])] = children # atribui valores a lista de radiobutton                
                            
            if isinstance(children, QtWidgets.QPushButton):
                if "mqtt" in children.objectName():
                    children.clicked.connect(self.button_mqtt)
                if "color_led_" in children.objectName():
                    children.clicked.connect(self.change_radioButton)
                                
        self.update_frame()# atualiza o valor dos das luzes na tela
        self.label_img_cenario = self.findChild(QtWidgets.QLabel, 'label_img_cenario') 
        self.frameAudioUsb = self.findChild(QtWidgets.QFrame, 'frameAudio')
        self.frameAudioUsb.setStyleSheet( 'background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2198c0, stop: 1 #0d5ca6);')
        ## ~ self.frameAudioUsb.setGeometry(QtCore.QRect(0, 0, 1000, 530))
        ## ~ self.frameAudioUsb.setStyleSheet("border-color: rgb(239, 41, 41);")
        ## ~ self.frameAudioUsb.setFrameShape(QtWidgets.QFrame.StyledPanel)
        ## ~ self.frameAudioUsb.setFrameShadow(QtWidgets.QFrame.Raised)
        root = '/usr/share/APP/' 
                       
        lista = []
        for f in sorted(find_files(root , self.config['VIDEO_FILES'] + self.config['AUDIO_FILES'])):
            # ~ print(f)
            lista.append(f)
                  
        self.playerWidget = player_.Player()
        self.playerWidget.config = self.config     
        self.playerWidget.setWhatsThis("<html><head/><body><p>Aba &quot;sobre&quot; Player Widget.</p></body></html>")
        
        self.playerWidget.addToPlaylist(lista)
        histogramLayout = QHBoxLayout(self.frameAudioUsb)
        histogramLayout.addWidget(self.playerWidget)

        self.frameAudioLocal = QtWidgets.QFrame(self.tabMusicas)
        self.frameAudioLocal.setGeometry(QtCore.QRect(0, 0, 995, 520))
        self.frameAudioLocal.setStyleSheet("border-color: rgb(239, 41, 41);")
        self.frameAudioLocal.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameAudioLocal.setFrameShadow(QtWidgets.QFrame.Raised)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.gridLayoutWidget = QtWidgets.QWidget(self.frameAudioLocal) 
        self.frameAudioLocal.hide()
        self.m_rect_rain = QtCore.QRect(self.width() -5, 0, 5, 30)
        # ~ timer = QtCore.QTimer(self, timeout=self.update_rain, interval=100)
        # ~ timer.start()
        self.playerWidget.signalLongPress.connect(self.appSignalLongPress)
        self.playerWidget.eject.connect(self.eject)
        self.show()
        # ~ messagebox = TimerMessageBox(5, self)
        # ~ messagebox.exec_()
    def confirm_update_config(self):
        if self.msgClass is not None:
            self.msgClass.close()
        
    def update_config(self, cfg):
        self.conf.salva_config(cfg)
        self.config = cfg['CONFIG']
        self.msgClass = TimerMessageBox("Novas configurações recebidas","", "", mqtt=False, timeout = 3)
        a = self.msgClass.exec_()
        
        
    def eject(self):
        try:
            if self.midia_usb != "":
                msgBox = QMessageBox()
                msgBox.setWindowTitle('Ejetar '+ str(self.midia_usb)+" ?")
                msgBox.setText('''<h1><strong><span style="color: #0000ff;">\
                Deseja ejetar a m&iacute;dia?</span></strong></h1>''')
                bt1   = QPushButton('Sim')
                bt1.setStyleSheet(btnStyle.btn_style())
                bt1.setMinimumWidth(180)
                bt1.setMaximumWidth(180)
                bt1.setMinimumHeight(80)
                msgBox.addButton(bt1, QMessageBox.YesRole)
                bt2   = QPushButton('Cancelar')
                bt2.setStyleSheet(btnStyle.btn_style())
                bt2.setMinimumWidth(180)
                bt2.setMaximumWidth(180)
                bt2.setMinimumHeight(80)
                msgBox.addButton(bt2, QMessageBox.NoRole)
                flags = Qt.WindowFlags()
                flags |= Qt.SplashScreen
                msgBox.setWindowFlags(flags)
                msg = msgBox.exec_()
                if msg == 0:
                    self.playerWidget.playlist.clear()
                    p = subprocess.Popen("sudo eject /media/pi/"+self.midia_usb, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        close_fds=False)
                    self.midia_usb = p.stdout.read().decode('utf-8', "ignore").rstrip() #show response in 'status
                     
                if self.midia_usb == "":
                    msgBox = QMessageBox()
                    msgBox.setText('''<h1><strong><span style="color: #0000ff;">\
                    A mídia pode ser removida</span></strong></h1>''')
                    
                    bt1   = QPushButton('Ok')
                    bt1.setStyleSheet(btnStyle.btn_style())
                    bt1.setMinimumWidth(180)
                    bt1.setMaximumWidth(180)
                    bt1.setMinimumHeight(80)
                    msgBox.addButton(bt1, QMessageBox.YesRole)
                    flags = Qt.WindowFlags()
                    flags |= Qt.SplashScreen
                    msgBox.setWindowFlags(flags)   
                    msg = msgBox.exec_()
                    root = '/usr/share/APP/'                
                    lista = []
                    for f in find_files(root , self.config['VIDEO_FILES'] + self.config['AUDIO_FILES']):
                        lista.append(f)                
                    self.playerWidget.addToPlaylist(lista)
                else:
                    Box = QMessageBox()
                    msgBox.setText('''<h1><strong><span style="color: #0000ff;">\
                    O sistema não conseguiu ejetar a mídia</span></strong></h1>''')
                    bt1   = QPushButton('Ok')
                    bt1.setStyleSheet(btnStyle.btn_style())
                    bt1.setMinimumWidth(180)
                    bt1.setMaximumWidth(180)
                    bt1.setMinimumHeight(80)
                    msgBox.addButton(bt1, QMessageBox.YesRole)
                    flags = Qt.WindowFlags()
                    flags |= Qt.SplashScreen
                    msgBox.setWindowFlags(flags)   
                    msg = msgBox.exec_()
                    
        except Exception as e:
            print(e)                   
        
    def appSignalLongPress(self, nameMedia,indexMedia):
        if self.config is not None and self.senhaEnabled:
            if any(nameMedia[-4:] in item for item in self.config["VIDEO_FILES"]):
                a = self.msgBoxFunction('Deseja exibir </span>&nbsp;<span style="color:red;">{}</span>&nbsp;<span style="color:#0000ff;">durante a cerimônia?</span>'.format(nameMedia), "Sim", "Não", mqtt = False, timeout = None)
                if a == 0 and self.config is not None:
                    self.config['VIDEO_EXT']['URL'] = '/usr/share/APP/videos/' + nameMedia
                    self.config['VIDEO_IHM'] = True
                    self.sendConfig()       
                    
                    
            else:
                a = self.msgBoxFunction('Deseja reproduzir </span>&nbsp;<span style="color:red;">{}</span>&nbsp;<span style="color:#0000ff;">durante a cerimônia?</span>'.format(nameMedia), "Sim", "Não", mqtt = False, timeout = None)
                if a == 0:
                    self.config['AUDIO_IHM']=True
                    self.config['IHM_AUDIO']['INDEX']=indexMedia
                    self.config['IHM_AUDIO']['NAME']=nameMedia
                    self.sendConfig()
            
        
    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()
        
    def sendConfig(self):
        dataDict={'CONFIG':self.config}
        self.conf.salva_config(dataDict)
        dataDict["CONFIG"]["UPDATE"] = True
        dataDict = json.dumps(dataDict)
        self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], dataDict, qos=2)
        self.msgClass = TimerMessageBox("Enviando novas configurações","", "", mqtt=False, timeout = 3)
        a = self.msgClass.exec_()
        if self.msgClass.elapsedTime:
            self.msgBoxFunction("Envio das configurações falhou!","Ok", "", mqtt=False, timeout = None)
        # ~ self.box_msg = self.msgBoxFunction("Restaurando configurações","", "", mqtt=False, timeout = 5)
        else:
            self.msgBoxFunction("Configurações atualizadas","Ok", "", mqtt=False, timeout = None)
        self.msgClass = None        
        
    def drawPoints(self, qp):
      
        qp.setPen(Qt.red)
        size = self.size()
        
        for i in range(1000):
            x = random.randint(1, size.width()-1)
            y = random.randint(1, size.height()-1)
            qp.drawPoint(x, y) 
                    
                
    # ~ def paintEvent(self, a0):
        # ~ painter = QtGui.QPainter(self)
        # ~ # Draw a White Background
        # ~ painter.setPen(QtGui.QPen(QtCore.Qt.white, 50, QtCore.Qt.SolidLine))
        # ~ painter.setBrush(QtGui.QBrush(QtCore.Qt.white, QtCore.Qt.SolidPattern))
        # ~ painter.drawRect(self.rect())
        # ~ # Draw the rain
        # ~ painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine))
        # ~ painter.setBrush(QtGui.QBrush(QtCore.Qt.blue, QtCore.Qt.SolidPattern))
        # ~ painter.drawRect(self.m_rect_rain)
                        
    def responseThread(self, data):
        print(data)
        
    def salva_cenario(self):
        a = self.msgBoxFunction("Salvar cenário "+str(self.cenaAtual), "Sim", "Não", mqtt=False, timeout = None)
        if a == 0:
            self.cenas.salva_cenario(self.json_cenas)
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
        
    def msgBoxFunction(self, text, btn1, btn2, mqtt, timeout):
        self.msgBox = QMessageBox()
        self.msgBox.setText('''<h2><strong><span style="color: #0000ff;">\
            {}</span></strong></h>'''.format(text))
        flags = Qt.WindowFlags()
        flags |= Qt.SplashScreen
        self.msgBox.setWindowFlags(flags)            
        if timeout is not None:
            self.timer = QtCore.QTimer(self)
            self.timer.setInterval(timeout * 1000)
            self.timer.timeout.connect(self.saveTime)
            self.timer.start()             
        if btn1 == "" and btn1 == "":
            self.msgBox.setStandardButtons(QMessageBox.NoButton)
            
        
        else:
            if btn1 != "":
                bt1   = QPushButton(btn1)
                bt1.setStyleSheet(btnStyle.btn_style())
                bt1.setMinimumWidth(180)
                bt1.setMaximumWidth(180)
                bt1.setMinimumHeight(80)
                # ~ bt1.clicked.connect()
                self.msgBox.addButton(bt1, QMessageBox.YesRole)
            if btn2 != "":
                bt2   = QPushButton(btn2)
                bt2.setStyleSheet(btnStyle.btn_style())
                bt2.setMinimumWidth(180)
                bt2.setMaximumWidth(180)
                bt2.setMinimumHeight(80)
                # ~ bt2.clicked.connect()
                self.msgBox.addButton(bt2, QMessageBox.NoRole)

            if mqtt:
                self.mqttLocal.status_mqtt["msgWidget"] = self.msgBox
                self.mqttLocal.status_mqtt["msgDisplayed"] = True
        msg = self.msgBox.exec_()
        return msg     
    def cancela_cenario(self):
        msgBox = QMessageBox()
        #~ msgBox.setWindowTitle('Ejetar '+ str(self.midia_usb)+" ?")
        msgBox.setText('''<h2><strong><span style="color: #0000ff;">\
        Deseja desfazer as alterações?</span></strong></h2>''')
        
        bt1   = QPushButton('Sim')
        bt1.setStyleSheet(btnStyle.btn_style())
        bt1.setMinimumWidth(180)
        bt1.setMaximumWidth(180)
        bt1.setMinimumHeight(80)
        # ~ bt1.clicked.connect(self.confirm_unchange_scenario)
        msgBox.addButton(bt1, QMessageBox.YesRole)
        bt2   = QPushButton('Não')
        bt2.setStyleSheet(btnStyle.btn_style())
        bt2.setMinimumWidth(180)
        bt2.setMaximumWidth(180)
        bt2.setMinimumHeight(80)
        # ~ bt2.clicked.connect(self.unconfirm_change_scenario)
        msgBox.addButton(bt2, QMessageBox.NoRole)
        flags = Qt.WindowFlags()
        flags |= Qt.SplashScreen
        msgBox.setWindowFlags(flags)
        msg = msgBox.exec_()
        print(msg)
        if msg == 0:
            self.json_cenas = self.cenas.load_cenario()
            self.update_frame()
        else:
            print("no")
    def unconfirm_change_scenario(self):
        print("passou unchange")

                
    def confirm_unchange_scenario(self):
        print("passou")

    def change_radioButton(self):
        '''
        Altera a posicao do radiobutton das sancas se for clicado na cor
        '''
        if "color_led_" in self.sender().objectName():
            indice_toogle = self.sender().objectName().split("led_")[1]
            self.findChild(QtWidgets.QRadioButton, 'radioButton_sanca_'+indice_toogle).toggle()
            
        # ~ for children in self.findChildren(QtWidgets.QWidget): 
            # ~ if isinstance(children, QtWidgets.QRadioButton):
                # ~ if "sanca_" in children.objectName():
                    # ~ if children.objectName().split("sanca_")[1] == "1":
                        # ~ children.toggle()                                       
        
    def update_frame(self):
        '''
        Atualiza as informações do cenário atual
        ''' 
        json_aux = self.json_cenas
        counter = 1
        for children in self.findChildren(QtWidgets.QWidget):
            try:
                if isinstance(children, QtWidgets.QRadioButton):

                    if "dim_" in children.objectName():
                        indice = children.objectName().split("dim_")[1]
                        value = json_aux['CENA'+str(self.cenaAtual)]['DIMER']['CANAL'+str(indice)]['INTENSIDADE']
                        children.setText("Canal {} - {}%".format(indice, value))
                        
                        if children.objectName().split("dim_")[1] == "1":
                            self.sliderDimer.setValue(int(value))
                            children.toggle()                                           
                    if "sanca_" in children.objectName():               
                        self.canal_sanca = children.objectName().split("sanca_")[1]
                        children.setText(self.json_cenas['CENA'+str(self.cenaAtual)]['LEDS']['CANAL'+str(self.canal_sanca)]['NOME_SANCA'])
                        textButton = json_aux['CENA'+str(self.cenaAtual)]['LEDS']['CANAL'+str(self.canal_sanca)]['COR']
                        cor = textButton+',255'
                        cor = list(cor.split(','))
                        for i in range(len(cor)):
                            cor[i] = int(cor[i])
                        corButton = list(cor)
                        corFonte=corButton
                        corFonte[0]=255 - cor[0]
                        corFonte[1]=255 - cor[1]
                        corFonte[2]=255 - cor[2]
                        corFonte = tuple(corFonte)
                        botao = self.findChild(QtWidgets.QPushButton, 'color_led_'+ str(self.canal_sanca))
                        botao.setText(textButton)
                        botao.setStyleSheet(\
                                'background-color: rgb'+str(tuple(cor))+';'\
                                'color: rgb'+str(corFonte)+';'\
                                'border-style: outset;'\
                                'border-width: 1px;'\
                                'border-color: black;')                 
                        
                        if children.objectName().split("sanca_")[1] == "1":
                            self.canal_sanca = children.objectName().split("sanca_")[1]
                            children.toggle()
                            
            except Exception as e:
                printException()
        if self.mqttLocal.status_mqtt["status"] == False:
            if self.timeElapsed - self.timeStarted > 2:
                a = self.msgBoxFunction("Sem comunicação","Ok", "", mqtt=True, timeout = None)
            
        else:
            self.canal_sanca = 1        
            indice = str(self.cenaAtual)
            for k, v in json_aux.items():
                if 'CENA'+indice == k:
                    for k2, v2 in v.items():
                        if 'LEDS' in k2:
                            for k3, v3 in v2.items():
                                cmd = self.json_cenas[k][k2][k3]
                                cmd['COMANDO'] = 'L_LED,'+k3.split("CANAL")[1]+','+str(json_aux[k][k2][k3]['COR']) + '\n'
                                cmd = {'dim_led':cmd}
                                cmd = json.dumps(cmd)
                                self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)
                        if 'DIMER' in k2:
                            for k3, v3 in v2.items():
                                cmd = self.json_cenas[k][k2][k3]
                                cmd['COMANDO'] = 'L_DIMER,'+k3.split("CANAL")[1]+','+str(json_aux[k][k2][k3]['INTENSIDADE']) + '\n'
                                cmd = {'dimer':cmd}
                                cmd = json.dumps(cmd)
                                self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)
                                    

    def change_cena_dir(self):
        '''
        Altera o scenário que vai ser configurado pelo usuário.
        '''     
        if self.cenaAtual < 10:
            self.cenaAtual +=1
            self.findChild(QtWidgets.QLabel, 'label_cgf_cena').setText('<html><head/><body><p><span style=" font-size:36pt;">Cenário {} </span></p></body></html>'.format(self.cenaAtual))
            
        elif self.cenaAtual == 10:
            self.cenaAtual = 1
            self.findChild(QtWidgets.QLabel, 'label_cgf_cena').setText('<html><head/><body><p><span style=" font-size:36pt;">Cenário {} </span></p></body></html>'.format(self.cenaAtual))
        self.update_frame()
        
    def change_cena_esq(self):
        
        if self.cenaAtual > 1:
            self.cenaAtual -=1
            self.findChild(QtWidgets.QLabel, 'label_cgf_cena').setText('<html><head/><body><p><span style=" font-size:36pt;">Cenário {} </span></p></body></html>'.format(self.cenaAtual))

        elif self.cenaAtual == 1:
            self.cenaAtual = 10
            self.findChild(QtWidgets.QLabel, 'label_cgf_cena').setText('<html><head/><body><p><span style=" font-size:36pt;">Cenário {} </span></p></body></html>'.format(self.cenaAtual))
        self.update_frame() 
                
    def dimFunction(self, value):
        '''
        Seta os parâmetros a medida que for movido o slider do dimer.
        '''    
        if self.mqttLocal.status_mqtt["status"] == False:
            if self.timeElapsed - self.timeStarted > 2:
                a = self.msgBoxFunction("Sem comunicação","Ok", "", mqtt=True, timeout = None)
        else:
            self.findChild(QtWidgets.QLabel, 'label_pot_dic').setText("Potência dicróica {} - {}%".format(self.canal_dimer, value))
            self.json_cenas['CENA'+str(self.cenaAtual)]['DIMER']['CANAL'+str(self.canal_dimer)]['INTENSIDADE'] = value
            self.listRadioButtonDim[int(self.canal_dimer)].setText("Canal {} - {}%".format(self.canal_dimer, value))
            
            cmd = self.json_cenas['CENA'+str(self.cenaAtual)]['DIMER']['CANAL'+str(self.canal_dimer)]
            cmd['COMANDO']  = "R_DIMER,"+str(self.canal_dimer)+','+str(value)+'\n'
            cmd = {'dimer': cmd}
            cmd = json.dumps(cmd)
            self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)      
            
    def radioButton(self, toogle):
        '''
        Ao selecionar o radiobutton
        '''         
        if "dim_" in self.sender().objectName():
            if toogle == True:
                self.canal_dimer = self.sender().objectName().split("dim_")[1]
                value = self.json_cenas['CENA'+str(self.cenaAtual)]['DIMER']['CANAL'+str(self.canal_dimer)]['INTENSIDADE']
                self.sliderDimer.setValue(int(value))
                self.findChild(QtWidgets.QLabel, 'label_pot_dic').setText("Potência dicróica {} - {}%".format(self.canal_dimer, self.sliderDimer.value()))
            
        if "sanca_" in self.sender().objectName():
            if toogle == True:
                self.canal_sanca = self.sender().objectName().split("sanca_")[1]

    @pyqtSlot()
    def button_mqtt(self):
        if self.mqttLocal.status_mqtt["status"] == False:
            if self.timeElapsed - self.timeStarted > 2:
                a = self.msgBoxFunction("Sem comunicação","Ok", "", mqtt=True, timeout = None)
        else:
            name =  self.sender().objectName()
            cmd = name.split("mqtt_")[1] # extrai o nome findchild do botão para enviar o comando
            
            if "cerimoniaDefault" in cmd:
                a = self.msgBoxFunction("Deseja restaurar padrão?","Sim", "Não", mqtt=True, timeout = None)
                if a == 0:
                    restore = self.conf.reset_cenario()
                    self.config = restore['CONFIG']
                    self.sendConfig()

            elif "fumaca" in cmd:
                cmd = {"fumaca":"fum,12000"}
                cmd  = json.dumps(cmd)
                self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)       
            elif "mecanismo" in name:
                cmd = {"mecanismo":cmd}
                cmd  = json.dumps(cmd)
                self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)
            else:
    
                cmd = {cmd:cmd}
                cmd  = json.dumps(cmd)
                self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)
            # ~ print(cmd)

    @pyqtSlot() 
    def button_senha(self):
        if self.buttons_senha.index(self.sender()) == 10: #se pressionar o botão ok
            if self.senha == self.button_clicked_senha:
                self.tabWidget.setTabEnabled(2, True)
                self.senhaEnabled = True
                self.groupSistema.show()
                self.groupMecanismo.show()      
                self.widgetSenha.hide()
            else:
                self.button_clicked_senha=[]
                
            
        else:
            self.button_clicked_senha.append(self.buttons_senha.index(self.sender()))
        
    @pyqtSlot() 
    def bloqueiaAba(self):
        self.tabWidget.setTabEnabled(2, False)
        self.senhaEnabled = False
        self.groupSistema.hide()
        self.groupMecanismo.hide()      
        self.widgetSenha.show()
        self.button_clicked_senha=[]
        
    @pyqtSlot()     
    def apagar_leds(self):
        if self.mqttLocal.status_mqtt["status"] == False:
            if self.timeElapsed - self.timeStarted > 2:
                a = self.msgBoxFunction("Sem comunicação","Ok", "", mqtt=True, timeout = None)
        else:        
            cmd = {"APAGAR":"APAGAR\n"}
            cmd  = json.dumps(cmd)             
            self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)     
            
               
    def mudaImagem(self):
        _translate = QtCore.QCoreApplication.translate     
        
        try:    
            self.im = QImage("/usr/share/APP/img/imagem" + str(self.imgIndex) + ".jpg")           
            pixmap = QtGui.QPixmap(QtGui.QPixmap.fromImage(self.im))
            
            if pixmap.width() < 1 and pixmap.height() < 1:
                self.label_img_cenario.setText('<html><head/><body><p><span style=" font-size:36pt;">Cenária sdas do {} {} </span></p></body></html>'.format(self.imgIndex, "Pedro"))            

            else:

                pixmap = pixmap.scaled(1005, 400)
                self.label_img_cenario.setPixmap(pixmap)

        except Exception as e:
            print(e)


    def changeScenario(self, index):
        if self.mqttLocal.status_mqtt["status"] == False:
            if self.timeElapsed - self.timeStarted > 2:
                a = self.msgBoxFunction("Sem comunicação","Ok", "", mqtt=True, timeout = None)
        else:
            indice = str(self.imgIndex)
            json_aux = self.json_cenas
            for k, v in json_aux.items():
                if 'CENA'+indice == k:
                    for k2, v2 in v.items():
                        if 'LEDS' in k2:
                            for k3, v3 in v2.items():
                                cmd = self.json_cenas[k][k2][k3]
                                cmd['COMANDO'] = 'L_LED,'+k3.split("CANAL")[1]+','+str(json_aux[k][k2][k3]['COR']) + '\n'
                                cmd = {'dim_led':cmd}
                                cmd = json.dumps(cmd)
                                self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)
                                time.sleep(.05)
                        if 'DIMER' in k2:
                            for k3, v3 in v2.items():
                                cmd = self.json_cenas[k][k2][k3]
                                cmd['COMANDO'] = 'L_DIMER,'+k3.split("CANAL")[1]+','+str(json_aux[k][k2][k3]['INTENSIDADE']) + '\n'
                                cmd = {'dimer':cmd}
                                cmd = json.dumps(cmd)
                                self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)
                                time.sleep(.05)
                            
                            
    @pyqtSlot()
    def moveDir(self):
        if self.imgIndex < 10 :
            self.imgIndex = self.imgIndex + 1
            
            
            
            self.mudaImagem()
        elif self.imgIndex == 10:
            self.imgIndex = 1
            self.label_img_cenario.setText('<html><head/><body><p><span style=" font-size:36pt;">Cenário {} </span></p></body></html>'.format(self.imgIndex))
            self.mudaImagem()
            

    @pyqtSlot()
    def moveEsq(self):
        if(self.imgIndex > 1):
            self.imgIndex = self.imgIndex - 1
            self.mudaImagem()
            
        elif self.imgIndex == 1:
            self.imgIndex = 10
            self.mudaImagem()              
    @pyqtSlot()    
    def mudaImagem(self):
        _translate = QtCore.QCoreApplication.translate        
        try:
            self.button_select_cenario.setText("Selecionar  " + str(self.imgIndex))
            self.im = QImage("/usr/share/APP/img/imagem" + str(self.imgIndex) + ".jpg")           

            pixmap = QtGui.QPixmap(QtGui.QPixmap.fromImage(self.im))
            
            if pixmap.width() < 1 and pixmap.height() < 1:
                
                self.label_img_cenario.setText('<html><head/><body><p><span style=" font-size:36pt;">Cenário '+str(self.imgIndex)+'</span></p></body></html>')

            else:
                pixmap = pixmap.scaled(1005, 650)
                self.label_img_cenario.setPixmap(pixmap)
             
            
        except Exception as e:
            print(e)
            
    def color_pick(self, color):
        if self.mqttLocal.status_mqtt["status"] == False:
            if self.timeElapsed - self.timeStarted > 2:
                a = self.msgBoxFunction("Sem comunicação","Ok", "", mqtt=True, timeout = None)
        else:
            global cor
            cor = color.getRgb()
            setCor = str(cor)
            corButton = list(cor)
            corButton[0]=255 - corButton[0]
            corButton[1]=255 - corButton[1]
            corButton[2]=255 - corButton[2]
            corButton = tuple(corButton)
            botao = self.findChild(QtWidgets.QPushButton, 'color_led_'+ str(self.canal_sanca))
            botao.setStyleSheet(\
                    'background-color: rgb'+setCor+';'\
                    'color: rgb'+str(corButton)+';'\
                    'border-style: outset;'\
                    'border-width: 1px;'\
                    'border-color: black;')
            cor_cmd = str(cor[0:3]).replace("(","").replace(")","")
            self.json_cenas['CENA'+str(self.cenaAtual)]['LEDS']['CANAL'+str(self.canal_sanca)]['COR'] = cor_cmd 
            botao.setText(cor_cmd)
            cmd = self.json_cenas['CENA'+str(self.cenaAtual)]['LEDS']['CANAL'+str(self.canal_sanca)]
            cmd['COMANDO']  = "R_LED,"+str(self.canal_sanca)+','+cor_cmd+'\n'
            cmd = {'dim_led': cmd}
            cmd = json.dumps(cmd)
            self.mqttLocal.mqttc.publish(self.config['TOPICO_IN_SERVER'], cmd, qos=2)
            time.sleep(.05)
    
            

    def recurring_timer(self):
        self.timeElapsed = time.time()
        # ~ if self.msgClass is not None:
            # ~ self.msgClass.close_msgbox()
        # ~ try:
            
            # ~ if self.config['TIME'] + 2 < time.time():
                # ~ self.config['TIME'] = time.time() + 5
                # ~ print(self.config)
        # ~ except Exception as e:
            # ~ print(e)
            # ~ self.config['TIME'] = time.time() + 5
        if self.mqttLocal.status_mqtt["status"] == False and self.mqttLocal.status_mqtt["tempo"] < time.time() and self.mqttLocal.status_mqtt["msgDisplayed"] == False:
            self.mqttLocal.status_mqtt["tempo"] = time.time() + 60
            a = self.msgBoxFunction("Servidor não encontrado", "Ok", "", mqtt=True, timeout = None) 
            # ~ msgBox = QMessageBox()
            # ~ msgBox.setText('''<h1><strong><span style="color: #0000ff;">\
            # ~ Servidor não encontrado</span></strong></h1>''')            # ~ bt1   = QPushButton('Ok')
            # ~ bt1.setStyleSheet(btnStyle.btn_style())
            # ~ bt1.setMinimumWidth(180)
            # ~ bt1.setMaximumWidth(180)
            # ~ bt1.setMinimumHeight(80)
            # ~ msgBox.addButton(bt1, QMessageBox.YesRole)
            # ~ flags = Qt.WindowFlags()
            # ~ flags |= Qt.SplashScreen
            # ~ msgBox.setWindowFlags(flags)
            # ~ self.mqttLocal.status_mqtt["msgWidget"] = msgBox            
            # ~ msg = msgBox.exec_()
            if a == 0:
                self.mqttLocal.status_mqtt["tempo"] = time.time() + 60
                self.mqttLocal.status_mqtt["msgDisplayed"] = False
            else:
                print("no")            
            print("mqtt desconectado!")

        
        try:
            if len(os.listdir("/media/pi/")) > 0 and self.midia_usb == "":
                self.playerWidget.playlist.clear()
                time.sleep(3)
                self.midia_usb = os.listdir("/media/pi/")[0]
                if self.midia_usb != "":
                    root = '/media/pi/'                
                    lista = []
                    for f in find_files(root , self.config['VIDEO_FILES'] + self.config['AUDIO_FILES']):
                        lista.append(f)
                    self.playerWidget.addToPlaylist(lista)
                
        except:
            pass         
           
class SmbThread(QtCore.QThread):
    smbSignal = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(SmbThread, self).__init__(parent=parent)
        
    def run(self):
        while True:
             
            p = subprocess.Popen('sudo mount -t cifs //ECUMENICA.local/share /usr/share/APP/videos -o username=pi,password=nbr5410!', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        close_fds=False)
            turned = p.stdout.read().decode('utf-8', "ignore").rstrip() #show response in 'status
            if turned == "":
                print("Server samba conectado!")
                self.smbSignal.emit(turned)
                break
            else:
                print(turned)
                break
            # ~ time.sleep(10)
                
# ~ class Thread(QtCore.QThread):
    # ~ tempSignal = QtCore.pyqtSignal(str)
    
    # ~ def __init__(self, ser, parent=None):
        # ~ super(Thread, self).__init__(parent=parent)
        # ~ self.serial = ser
        
    # ~ def run(self):
        # ~ while True:
            # ~ string = self.serial.readline().decode("utf-8", "ignore").rstrip()
            # ~ if len(string) > 2:
                # ~ self.tempSignal.emit(string)                

                
class TimerMessageBox(QMessageBox):
    def __init__(self,  text, btn1, btn2, mqtt, timeout, parent=None):
        super(TimerMessageBox, self).__init__(parent)
        self.msgBox = self
        self.texto = '''<h2><strong><span style="color: #0000ff;">{}</span></strong></h2>'''.format(text)
        self.msgBox.setText(self.texto)
        flags = Qt.WindowFlags()
        flags |= Qt.SplashScreen
        self.msgBox.setWindowFlags(flags)        
        self.elapsedTime = False
        if timeout is not None:
            self.timer = QtCore.QTimer(self)
            self.timer.setInterval(timeout * 1000)
            self.timer.timeout.connect(self.saveTime)
            self.timer.start()             
        if btn1 == "" and btn1 == "":
            self.msgBox.setStandardButtons(QMessageBox.NoButton)
            
        
        else:
            if btn1 != "":
                bt1   = QPushButton(btn1)
                bt1.setStyleSheet(btnStyle.btn_style())
                bt1.setMinimumWidth(180)
                bt1.setMaximumWidth(180)
                bt1.setMinimumHeight(80)
                self.msgBox.addButton(bt1, QMessageBox.YesRole)
            if btn2 != "":
                bt2   = QPushButton(btn2)
                bt2.setStyleSheet(btnStyle.btn_style())
                bt2.setMinimumWidth(180)
                bt2.setMaximumWidth(180)
                bt2.setMinimumHeight(80)
                self.msgBox.addButton(bt2, QMessageBox.NoRole)
                
        self.time_to_wait = timeout
        self.timer2 = QtCore.QTimer(self)
        self.timer2.setInterval(timeout * 1000)
        self.timer2.timeout.connect(self.changeContent)
        self.timer2.start()
        
        self.counter_point = 1
        self.timer3 = QtCore.QTimer(self)
        self.timer3.setInterval(300)
        self.timer3.timeout.connect(self.update_text)
        self.timer3.start()        
        
    def close_msgbox(self):
        self.close()
        
    def update_text(self):
        if self.counter_point == 30:
            self.counter_point = 1
        self.setText(self.texto + '''<h2><strong><span style="color: #0000ff;">{}</span></strong></h2>'''.format("." * self.counter_point))
        self.counter_point +=1

        
    def changeContent(self):
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.elapsedTime = True
            self.close()
    
    def closeEvent(self, event):
        self.timer2.stop()
        self.timer3.stop()
        event.accept()
        
                                
class MeuDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__()
        self.dialog = QDialog(self)
        self.dialog.ui = uic.loadUi('qdialog.ui', self.dialog)
        # ~ flags = Qt.WindowFlags()
        # ~ flags |= Qt.X11BypassWindowManagerHint
        # ~ self.dialog.ui.setWindowFlags(flags)
        
if __name__ == '__main__':
    xml = ""
    app = QCoreApplication.instance()
    if app is None:
       app = QtWidgets.QApplication(sys.argv)
    else:
        print('QApplication instance already exists: %s' % str(app))

    root = '/usr/share/APP/' 
    print("*{}.ui".format(conf.json_config['CONFIG']['CEMITERIO']))             
    lista = [conf.json_config['CONFIG']['CEMITERIO']]
    for f in find_files(root , ["*{}.ui".format(conf.json_config['CONFIG']['CEMITERIO'])]):
        # ~ print(f)
        xml = f
    w = Ui(xml)
    w.showFullScreen()
    # ~ w.show()

    sys.exit(app.exec_())
        


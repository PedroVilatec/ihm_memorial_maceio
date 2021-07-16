from PyQt5.QtCore import pyqtSignal
# -*- coding: utf-8 -*-
import filecmp
from fnmatch import fnmatch
import linecache
import time, datetime
import os, sys
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.client as mqtt_server
import threading
#import signal
import json
from operations import saveFile
import urllib.request
from infra.check_internet import have_internet
import os, subprocess, time



def printException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class Mosquitto():
    receivedUpdate = pyqtSignal(bool)
    def __init__(self, client, porta):
        self.client = client
        self.porta_mqtt = porta
        self.mqttc = mqtt_server.Client(self.client)
        self.mqttc.on_message = self.on_message
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_connect = self.on_connect
        # mqttc.on_publish = on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        # Uncomment to enable debug messages
        # ~ self.mqttc.on_log = self.on_log
        self.inicio = time.time() + 20
        self.envia_telegram_single = None # variavel sentenciada para enviar telegramas
        self.envia_telegram_all = None # variavel sentenciada para enviar telegramas
        self.player = None
        self.local_connected = False
        
        self.lc_serial_port = None
        self.status_mqtt = {"status": False, "tempo": time.time() + 20, "msgDisplayed":False, "msgWidget":None}
        thread = threading.Thread(target=self.connect_mqtt)
        thread.start()  

        #~ thread1 = threading.Thread(target=self.verifica_online)
        #~ thread1.start()
    def on_log(self, mqttc, obj, level, string):
        print(string)

    def on_confirm_update_config(self):
        ...

    def on_update_config(self, cfg):
        ...

    def on_connect(self, mqttc, obj, flags, rc):
        self.status_mqtt["status"] = True
        self.status_mqtt["tempo"] = time.time()
        try:
            if self.status_mqtt["msgWidget"] is not None:
                # ~ self.status_mqtt["msgWidget"].setText('''<h1><strong><span style="color: #0000ff;">\
                            # ~ Conectado ao servidor </span></strong></h1>''')
                # ~ time.sleep(2)
                self.status_mqtt["msgWidget"].close()
        except Exception as e:
            print(e)    
        print("Conectado!", "rc: " + str(rc))   
        
    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("subscribed")
        
    def on_disconnect(self, client, userdata,  rc):
        self.status_mqtt["status"] = False
        self.status_mqtt["tempo"] = time.time()
        print("Mqtt desconectado")

    
    def connect_mqtt(self):
        while not self.local_connected:
            print("Conectando ao servidor local...")
            try:
                self.mqttc.connect("ECUMENICA.local", self.porta_mqtt, 60)
                # self.mqttc.connect("192.168.43.63", self.porta_mqtt, 60)
                self.mqttc.subscribe("capela/ihm", 0)
                print("conectado ao Servidor local !")
                thread = threading.Thread(target=self.mqttc.loop_forever)
                thread.start()
                self.local_connected = True
            except Exception as e:
                printException()
                print("Conexao local falhou")           
    
        
            time.sleep(1)       
                      
    
    def on_message(self, mqttc, obj, msg):
        
            try:
                self.turned = msg.payload.decode()
                data = json.loads(self.turned)
                for k,v in data.items():
                    if k == 'CONFIG':
                        if data['CONFIG']["UPDATE"] == False:
                            #self.receivedUpdate.emit(True)
                            #self.on_confirm_update_config()
                            self.on_update_config(data)
                            print("Atualizacoes recebidas")                    

                    if k == 'desligarApp':
                        print("desligar")

                        os.system("sudo poweroff")  
                        
                    
                    if k == 'display_off':
                        os.environ['DISPLAY'] = ":0"
                        subprocess.call('xset dpms force off', shell=True)  
                                            
                    if k == "sistema":
                        if v == "reset":
                            os.system("sudo reboot")
            except Exception as e:
                print(e)        

class MosquittoServer():
    def __init__(self, client):
        
        self.client = client
        self.mqttc_server = mqtt.Client(self.client)
        self.mqttc_server.on_message = self.on_message_server
        self.mqttc_server.on_subscribe = self.on_subscribe_server
        self.serverConnected = False
        self.serial_port = None
        self.player = None
        self.inicio = time.time() + 20
        self.send_telegram_single = "" # variavel sentenciada para enviar telegramas
        self.send_telegram_all = "" # variavel sentenciada para enviar telegramas
        thread = threading.Thread(target=self.connect_mqtt_server)
        thread.start()
    def on_subscribe_server(self, mqttc_server, obj, mid, granted_qos):
        print("Connected mqtt")
        
    def connect_mqtt_server(self):
            print("Conectando ao servidor externo...")
            try:
                self.mqttc_server.connect("201.46.55.138", 1883, 60)
    
            except Exception as e:
                self.mqttc_server.disconnect()
                print("Servidor externo não disponivel")
                
            else:
                self.mqttc_server.subscribe("capela/" + self.client, 0)
                thread2 = threading.Thread(target=self.mqttc_server.loop_forever)
                thread2.start()
                thread3 = threading.Thread(target=self.verifica_online_server)
                thread3.start()         
                self.serverConnected = True                 
                print("Conectado ao servidor externo mqtt...")
        
    def on_message_server(self, mqttc_server, obj, msg):
        try:
            self.turned = msg.payload.decode()
            data = json.loads(self.turned)
            for k,v in data.items():
                
                if k == 'display_off':
                    os.environ['DISPLAY'] = ":0"
                    subprocess.call('xset dpms force off', shell=True)  
                                        
                if k == "sistema":
                    if v == "reset":
                        os.system("sudo reboot")    
                        
        except Exception as e:
            print(e)

    
            
    def updateCodigo(self):
        '''
        Atualiza o codigo em caso de alteracao em qualquer arquito py
        '''
        if sys.platform != 'win32':
            root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))     
            pattern = "*.py"
            for path, subdirs, files in os.walk(root):
                for name in files:
                    if fnmatch(name, pattern):
                        if not ".debris" in path:
                            #print (os.path.join(path, name))
                            if not(filecmp.cmp (os.path.join(path, name) ,os.path.join(path, "."+name+"_"))):
                                os.execv(sys.executable, ['python3'] + sys.argv)                                        

    def verifica_online_server(self):
              
        while True:
            try:
                self.updateCodigo()
                dataDict = {"CLIENTE": self.client, "STATUS": { \
                    "STATUS CONEXAO": "On line", \
                    # ~ "STATUS_INVERSOR": status_inversor, \
                    # ~ "PRESSAO": pressao, \
                    }}
                dataDict = json.dumps(dataDict)
                if self.serverConnected:
                    self.mqttc_server.publish(self.client+"/retorno", dataDict, qos=0)
                time.sleep(10)
                
            except Exception as e:
                printException()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import linecache
import os, sys
import telepot
from requests import get
from random import randint
from time import sleep
from json import loads
from os import path, mkdir
import urllib.request

# ----------------------------------------------------------------------

def printException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    
class Bot():
    def __init__(self, cemiterio):


        self.cemiterio = cemiterio
        self.user_file = "telepot_data/users_telepot.py"
        self.bots = "telepot_data/bots.py"
        self.bot_file = os.path.join(os.path.dirname(__file__), self.bots)
        self.read_user = os.path.join(os.path.dirname(__file__), self.user_file)
        with open(self.read_user) as f:
            self.telepot_users = f.readlines()
            #print(self.telepot_users)
        with open(self.bot_file) as g:
            for line in g:
                line = line.rstrip()
                if self.cemiterio in line:
                    if line.split("=",1)[1] != "":
                        self.endereco_bot = line.split("=",1)[1]
                        self.bot = telepot.Bot(self.endereco_bot)
                        self.bot.message_loop(self.handle)

    # ----------------------------------------------------------------------

    
    def envia_telegram_pressao(self):

        arquivo = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'LOG'))
        arquivo = os.path.join(arquivo, "historico_pressao.txt")
        data = ""
        try:
            with io.open(arquivo,'r',encoding='utf8') as f:
                data = f.read()

                self.envia_telegram_all(data)
        except Exception as e:
            printException()

# ----------------------------------------------------------------------
            
    def envia_telegram_single(self, endereco, mensagem):

        self.bot.sendMessage(endereco, mensagem)
        if endereco != str(334240998):
            self.bot.sendMessage(334240998, mensagem)

# ----------------------------------------------------------------------
            
    def envia_telegram_all(self, mensagem):

        nao_enviados = []
        try:
            for line in self.telepot_users:
                line = line.rstrip()
                usuario = line.split("=",1)[0]
                endereco = line.split("=",1)[1]
    
                try:
    
                    sending = self.bot.sendMessage(endereco,mensagem)
                    pass
                except :
                    nao_enviados.append(usuario)
            return(nao_enviados)
        except Exception as err:
            print("telegram.py", err)
    
    # ----------------------------------------------------------------------
            
    def send(self, data):
        '''
        Funcao chamada na aplicacao principal
        '''

        pass

    # ----------------------------------------------------------------------
        
    def ret_telepot(self, a):
        '''
        Função pode ser chamada pela aplicação principal pelo argumento a
        '''
        self.send = a

    # ----------------------------------------------------------------------

    def textMsg(self, msg):


        self.send(msg)
        self.client = msg["message"]["from"]["first_name"]
        self.texto = msg["message"]["text"]
        self.endereco = msg["message"]["from"]["id"]
        encontrado = False
        for line in self.telepot_users:
            line = line.rstrip()
            endereco = line.split("=",1)[1]
            usuario = str(line.split("=",1)[0])
            if str(self.endereco) == str(endereco):
                encontrado = True
        if encontrado:#se o endereço constar na lista
            if self.texto == 'Teste':
                 self.envia_telegram_all("Teste de estanqueidade iniciado por "+ usuario)
                 ser.write(b'TESTE\n')
                 return
            elif self.texto == "Lista":
                ordem = 0;
                lista = ""
                for line in self.telepot_users:
                    ordem += 1
                    line = line.rstrip()
                    lista += str(ordem) + " - " + str(line.split("=",1)[0])+"\n"
                self.envia_telegram_all("Lista de usuários\n"+self.cemiterio+"\n"+lista)
                return
            elif endereco == str(334240998) and "Cadastra" in str(msg['text']):

                try:
                    self.envia_telegram_all("Cadastrado: " +self.client+", " + self.text.split(",")[2])
                    self.telepot_users.append(self.texto.split(",")[1] +"="+ self.texto.split(",")[2])
                    with open(self.read_user,'a+') as save:
                        save.write(self.texto.split(",")[1] +"=" + self.texto.split(",")[2]+"\n")


                except Exception as err:
                    print(err)
                    pass
                return

            elif endereco == str(334240998) and "Exclui" in str(msg['text']):
                ordem = 0
                try:
                    with open(self.read_user,"r+") as f:
                        new_f = f.readlines()
                        f.seek(0)
                        for line in new_f:
                            ordem += 1
                            if int(msg['text'].split(",")[1]) != ordem:
                                f.write(line)
                        f.truncate()
                        with open(self.read_user) as load:
                            self.telepot_users = load.readlines()
                except Exception as err:
                    print(err)
                    pass
                return

            else:
                self.envia_telegram_single(self.endereco, self.client+ ", '" + self.texto +"' comando não reconhecido\n"+\
                                      "Digite \"Teste\" para iniciar um\nteste de pressão\n"+\
                                      "\"Lista\" para mostrar todos os usuários\n")
                return
        else:
            self.envia_telegram_all("Mensage de usuário não cadastrado\nUsuário: "+str(self.client) +"\nEndereço: "+str(self.endereco)+"\nMensagem: "+self.texto)
        # ~ self.bot.sendMessage(self.endereco,self.client + ", ainda não sei o que fazer com \""+ self.texto+"\"")
        # ~ if self.endereco != 334240998:
            # ~ self.bot.sendMessage(334240998, self.client + mensagem)
        # ~ print(self.client, self.texto)
        # ~ for elements in msg:
            # ~ print(elements, msg[elements])

    # ----------------------------------------------------------------------
        
    def get_file_path(self, file_id):

        try:
            urllib.request.urlopen("http://google.com")
        except:
            print('SEM INTERNET PARA get_file_path TELEGRAM')

        else:
            get_path = get('https://api.telegram.org/bot{}/getFile?file_id={}'.format(self.endereco_bot, file_id))
            json_doc = loads(get_path.text)
            try:
                file_path = json_doc['result']['file_path']
            except Exception as e:  # Happens when the file size is bigger than the API condition
                print('Cannot download a file because the size is more than 20MB')
                return None

            return 'https://api.telegram.org/file/bot{}/{}'.format(self.endereco_bot, file_path)

    # ----------------------------------------------------------------------
    
    
    def get_file(self, msg_list, chat_id):

        try:
            urllib.request.urlopen("http://google.com")
        except:
            print('SEM INTERNET PARA get_file TELEGRAM')

        else:
        
            try:
                if len(msg_list) > 1:
                    msg_count = len(msg_list)

                    print('Total files: {}'.format(msg_count))
            except Exception as e:
                print(e)
            for msg in msg_list:


                if "text" in msg["message"]:
                    #print(elements, msg[elements])
                    self.textMsg(msg)
                try:
                    mp3id = msg['message']['audio']['file_id']
                except KeyError:

                    continue

                try:
                    singer = msg['message']['audio']['performer']

                except:

                    singer = 'Unknown'

                # Remove / and - characters to create directory
                singer = singer.replace('/', '-').strip()
                singer = singer.replace('<', '').strip()
                singer = singer.replace('>', '').strip()
                singer_dir = singer
                try:
                    print("passou 4")
                    song_name = msg['message']['audio']['title']
                except:
                    print("passou 5")
                    song_name = str(randint(120, 1900000000))

                if path.exists('{}/{}_{}.mp3'.format(singer_dir, singer, song_name)):
                    print("passou 6")
                    print('{} {} --> File exists'.format(singer, song_name))
                    continue

                print('Working on --> {} {}'.format(singer, song_name))
                # Get file download path
                print(self.endereco_bot)
                download_url = self.get_file_path(mp3id)
                mp3file = get(download_url)
                if download_url is None:
                    continue

                if not path.exists(singer_dir):
                    mkdir(singer_dir)

                try:
                    with open('{}/{}_{}.mp3'.format(singer_dir, singer, song_name), 'wb') as f:
                        f.write(mp3file.content)
                except FileNotFoundError:
                    with open('{}.mp3'.format(randint(120, 1900000000)), 'wb') as f:
                        f.write(mp3file.content)

                self.bot.sendMessage(chat_id, 'Done: {} {}'.format(singer, song_name))
                self.textMsg()

    # ----------------------------------------------------------------------

    def handle(self, msg):

        try:
            urllib.request.urlopen("http://google.com")
        except:
            print('SEM INTERNET PARA handle TELEGRAM')

        else:
            content_type, chat_type, chat_id = telepot.glance(msg)
            usermsg = self.bot.getUpdates(allowed_updates='message')
            self.get_file(usermsg, chat_id)

    # ----------------------------------------------------------------------
        

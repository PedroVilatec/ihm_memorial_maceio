# -*- coding: utf-8 -*-
import os, sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

def erroDispositivo(dispositivo, comando):
    dataSave = dispositivo + " " + comando + " " + str(time.strftime("%d/%m/%Y %H:%M:%S")+"\n")
    try:
        data = ''
        with open('./LOG/logMqtt.txt', "r") as f:
            data = f.read()

        with open('./LOG/logMqtt.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
         if os.path.exists('./LOG') == False:
              os.mkdir('./LOG')

         with open('./LOG/logMqtt.txt', "w") as f:
             f.write(dataSave)
             
def writeArquivo(dados, pasta, arquivo):
    dataSave = dados
    try:
        with open('./'+str(pasta)+'/'+str(arquivo), "w") as f:
            f.write(dataSave)

    except FileNotFoundError:
        if os.path.exists('./'+str(pasta)) == False:
            os.makedirs('./'+str(pasta))

        with open('./'+str(pasta)+'/'+str(arquivo), "w") as f:
            f.write(dataSave)

def readArquivo(pasta, arquivo):
    try:
        with open('./'+str(pasta)+'/'+str(arquivo), "r") as f:
            return f.read()

    except FileNotFoundError:
            print("erro saveFile.readArquivo")

def resultadoTeste(str):
    dataSave = str
    try: 
        data = ""
        with open('./LOG/teste_estanqueidade.txt', "r") as f:
            data = f.read()
        with open('./LOG/teste_estanqueidade.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('./LOG') == False:
            os.mkdir('./LOG')

        with open('./LOG/teste_estanqueidade.txt', "w") as f:
            f.write(dataSave)

def resultadoTroca(str):
    dataSave = str
    try:
        data = ""
        with open('./LOG/troca_gasosa.txt', "r") as f:
            data = f.read()
        with open('./LOG/troca_gasosa.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('./LOG') == False:
            os.mkdir('./LOG')

        with open('./LOG/troca_gasosa.txt', "w") as f:
            f.write(dataSave)


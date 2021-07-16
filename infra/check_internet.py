from urllib.request import urlopen
import socket

from eventlet.green import httplib

"""

Funções para checar se a raspberry está conectada ou não.

Todas elas realizam a mesma função. Basta escolher uma.

"""


def internet_on():
    try:
        urllib.urlopen('http://172.217.30.14', timeout=1)
        return True
    except urllib.URLError as err:
        return False


def internet(host="8.8.8.8", port=53, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except:
        return False


def have_internet(host='https://ip.42.pl'):
    try:
        urlopen(host, timeout=5)
        return 'Conectado'
    except Exception as e:
        return 'Sem conexão'

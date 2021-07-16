import time
import datetime

"""

Funções referentes à coleta da hora do sistema

"""


def converter_string_hora(string_hora, no_seconds=True):
    """
    Função que converte uma string no formato 'HH:MM' em um objeto datetime

    :param string_hora: String a ser convertida
    :param no_seconds: Flag para indicar se deseja os segundos ou não. True significa sem segundos.
    :return: Objeto datetime da string hora informada
    """
    try:
        hora_formatada = datetime.datetime.strptime(string_hora, "%H:%M").time()
        if no_seconds:
            return hora_formatada.strftime("%X")[:5]
        else:
            return hora_formatada.strftime("%X")
    except:
        return "Error"


def get_hora(no_seconds=True):
    """
    Função para coletar a hora do sistema.
    :param no_seconds: Flag para indicar se deseja os segundos ou não. True significa sem segundos.
    :return: Hora do sistema
    """
    try:
        if no_seconds:
            return time.strftime("%X")[:5]
        else:
            return time.strftime("%X")
    except:
        return "Error"

        ## TESTE
        # while True:
        #     hora = converte_string_hora("09:30")
        #     hora_sistema = time.strftime("%X")
        #     if(hora[:5] == hora_sistema[:5]):
        #         print("Oie.")
        #     else:
        #         print("Hora errada")

def dia_anterior():
    data = datetime.datetime.now()

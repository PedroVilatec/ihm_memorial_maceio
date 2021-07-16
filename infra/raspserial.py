def getSerial():
    """
    Função que coleta o código serial da raspberry, código que é único de cada unidade

    :return: Os 16 últimos caracteres do código serial
    """
    cpuSerial = '000000000000000'
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuSerial = line[10:26]
        f.close()
    except:
        cpuSerial = 'ERROR000000000'

    return cpuSerial

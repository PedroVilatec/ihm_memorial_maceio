import os
class Devices():
    CONTROLADORES = {
"ARDUINO":{\
                        "STATUS_FREQUENCIA":"NÃO CONECTADO",\
                        "STATUS_INVERSOR":"NÃO CONECTADO",\
                        "STATUS_H2S":"",\
                        "LH2S,1":"LH2S,1",\
                        "LH2S,0":"LH2S,0",\
                        "P_IN 1":"P_IN 1",\
                        "P_IN 0":"P_IN 0",\
                        "P_OUT 1":"P_OUT 1",\
                        "P_OUT 0":"P_OUT 0",\
                        },\
"NIVEL_TANQUE_CABINE_1E":{\
                      "STATUS_IP":"NÃO INICIADO",\
                      "STATUS_VALVULA_SOLENOIDE":"NÃO CONECTADO",\
                      "STATUS_NIVEL":"NÃO CONECTADO",\
                      "DESLIGA_ENCHE_TANQUE":"DESLIGA_ENCHE_TANQUE",\
                      "ENCHE_TANQUE":"ENCHE_TANQUE"},\

"EVAPORADOR_CABINE_1E":{
                        "STATUS_NIVEL":"NÃO CONECTADO",\
                         "STATUS_RESISTENCIA":"DESLIGADO",\
                         "STATUS_DURACAO_RESISTENCIA": "0",\
                        "STATUS_VALVULA": "0",\
                        "STATUS_IP": "0",\
                         "STATUS_CORRENTE_RESISTENCIA": "0",\
                         "LIGA_RESISTENCIA":"LIGA_RESISTENCIA",\
                         "ABRE_VALVULA":"ABRE_VALVULA",\
                        "FECHA_VALVULA":"FECHA_VALVULA",\
                         "DESLIGA_RESISTENCIA":"DESLIGA_RESISTENCIA"},\

#"VALVULA_CABINE_1E":{"STATUS_TEMPO_OPERACAO":"NÃO INICIADO", "STATUS_VALVULA_1E":"NÃO CONECTADO", "STATUS_FLUXO_DE_AR":"NÃO CONECTADO","ABRE_1E":"ABRE_1E", "FECHA_1E":"FECHA_1E"},
"VALVULA_CABINE_1E":{\
                     "STATUS_FLUXO_DE_AR":"NÃO CONECTADO",\
                     "STATUS_TOTAL_FLUXO_DE_AR":"NÃO CONECTADO",\
                     "STATUS_IP":"0",\
                      "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                      "STATUS_VALVULA_1E":"NÃO CONECTADO",\
                      "STATUS_TENSAO_MAF":"NÃO CONECTADO",\
                     "STATUS_ANALOG":"NÃO CONECTADO",\
                      "ABRE_1E":"ABRE_1E",\
                      "FECHA_1E":"FECHA_1E",\
                      "ERASE_MAF":"ERASE_MAF"},\

"ACESSO_MCC_1E":{\
                "STATUS_PORTA":"NÃO CONECTADO",\
                "STATUS_IP": "0",\
                "STATUS_TAG":"NÃO CONECTADO",\
                "ACIONA":"ABRE"},\

"COLETORA_BLOCO_1AB":{\
                    "STATUS_NIVEL":"NÃO CONECTADO",\
                    "STATUS_BOMBA":"DESLIGADO",\
                    "STATUS_DURACAO_BOMBA": "0",\
                    "STATUS_CORRENTE_BOMBA": "0",\
                    "STATUS_IP": "0",\
                    "LIGA_BOMBA":"LIGA_BOMBA",\
                    "DESLIGA_BOMBA":"DESLIGA_BOMBA"},\

"COLETORA_BLOCO_1C":{\
                    "STATUS_NIVEL":"NÃO CONECTADO",\
                    "STATUS_BOMBA":"DESLIGADO",\
                    "STATUS_DURACAO_BOMBA": "0",\
                    "STATUS_CORRENTE_BOMBA": "0",\
                    "STATUS_IP": "0",\
                    "LIGA_BOMBA":"LIGA_BOMBA",\
                    "STATUS_CORRENTE_BOMBA": "0",\
                    "STATUS_IP": "0",\
                    "LIGA_BOMBA":"LIGA_BOMBA",\
                    "DESLIGA_BOMBA":"DESLIGA_BOMBA"},\

"COLETORA_BLOCO_1D":{\
                    "STATUS_NIVEL":"NÃO CONECTADO",\
                    "STATUS_BOMBA":"DESLIGADO",\
                    "STATUS_DURACAO_BOMBA": "0",\
                    "STATUS_CORRENTE_BOMBA": "0",\
                    "STATUS_IP": "0",\
                    "LIGA_BOMBA":"LIGA_BOMBA",\
                    "STATUS_CORRENTE_BOMBA": "0",\
                    "STATUS_IP": "0",\
                    "LIGA_BOMBA":"LIGA_BOMBA",\
                    "DESLIGA_BOMBA":"DESLIGA_BOMBA"},\

"COLETORA_BLOCO_1GH":{\
                    "STATUS_NIVEL":"NÃO CONECTADO",\
                    "STATUS_BOMBA":"DESLIGADO",\
                    "STATUS_DURACAO_BOMBA": "0",\
                    "STATUS_CORRENTE_BOMBA": "0",\
                    "STATUS_IP": "0",\
                    "LIGA_BOMBA":"LIGA_BOMBA",\
                    "DESLIGA_BOMBA":"DESLIGA_BOMBA"},\

"COLETORA_BLOCO_1IJ":{\
                    "STATUS_NIVEL":"NÃO CONECTADO",\
                    "STATUS_BOMBA":"DESLIGADO",\
                    "STATUS_DURACAO_BOMBA": "0",\
                    "STATUS_CORRENTE_BOMBA": "0",\
                    "STATUS_IP": "0",\
                    "LIGA_BOMBA":"LIGA_BOMBA",\
                    "DESLIGA_BOMBA":"DESLIGA_BOMBA"},\


"LIGA_GERAL_ESP_RELES":{\
                        "STATUS_RELES":"NÃO CONECTADO",\
                        "STATUS_ESP":"NÃO CONECTADO",\
                        "LIGA_RELES":"LIGA_RELES",\
                        "STATUS_IP": "0",\
                        "LIGA_ESP":"LIGA_ESP",\
                        "DESLIGA_RELES":"DESLIGA_RELES",\
                        "DESLIGA_ESP":"DESLIGA_ESP"},\

"VALVULAS_AM_1A-1B":{\
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1A":"NÃO CONECTADO",\
                    "STATUS_VALVULA_1B":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1A":"ABRE_1A",
                    "FECHA_1A":"FECHA_1A",\
                    "ABRE_1B":"ABRE_1B",\
                    "FECHA_1B":"FECHA_1B"},

"VALVULAS_AM_1C":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1C":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1C":"ABRE_1C",\
                    "FECHA_1C":"FECHA_1C"},

"VALVULAS_AM_1D":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1D":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1D":"ABRE_1D",\
                    "FECHA_1D":"FECHA_1D"},

"VALVULAS_AM_1E-1F":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1E":"NÃO CONECTADO",\
                    "STATUS_VALVULA_1F":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1E":"ABRE_1E",\
                    "FECHA_1E":"FECHA_1E",\
                    "ABRE_1F":"ABRE_1F",\
                    "FECHA_1F":"FECHA_1F"},

"VALVULAS_AM_1G-1H":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO", \
                    "STATUS_VALVULA_1G":"NÃO CONECTADO",\
                    "STATUS_VALVULA_1H":"NÃO CONECTADO", \
                    "STATUS_IP": "0",\
                    "ABRE_1G":"ABRE_1G",\
                    "FECHA_1G":"FECHA_1G",\
                    "ABRE_1H":"ABRE_1H",\
                    "FECHA_1H":"FECHA_1H"},

"VALVULAS_AM_1I-1J":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1I":"NÃO CONECTADO",\
                    "STATUS_VALVULA_1J":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1J":"ABRE_1J",\
                    "FECHA_1J":"FECHA_1J",\
                    "ABRE_1I":"ABRE_1I",\
                    "FECHA_1I":"FECHA_1I"},

"VALVULAS_AZ_1A-1B":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1A":"NÃO CONECTADO",\
                    "STATUS_VALVULA_1B":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1A":"ABRE_1A",\
                    "FECHA_1A":"FECHA_1A",\
                    "ABRE_1B":"ABRE_1B",\
                    "FECHA_1B":"FECHA_1B"},

"VALVULAS_AZ_1C":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1C":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1C":"ABRE_1C",
                    "FECHA_1C":"FECHA_1C"},

"VALVULAS_AZ_1D":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1D":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1D":"ABRE_1D",\
                    "FECHA_1D":"FECHA_1D"},

#"VALVULAS_AZ_1C-1D":{"STATUS_TEMPO_OPERACAO":"NÃO INICIADO", "STATUS_VALVULA_1C":"NÃO CONECTADO", "STATUS_VALVULA_1D":"NÃO CONECTADO", "ABRE_1C":"ABRE_1EC", "FECHA_1C":"FECHA_1C",  "ABRE_1D":"ABRE_1D", "FECHA_1D":"FECHA_1D"},

"VALVULAS_AZ_1E-1F":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO", \
                    "STATUS_VALVULA_1E":"NÃO CONECTADO",\
                    "STATUS_VALVULA_1F":"NÃO CONECTADO",
                    "STATUS_IP": "0",\
                    "ABRE_1E":"ABRE_1E",\
                    "FECHA_1E":"FECHA_1E",\
                    "ABRE_1F":"ABRE_1F",\
                    "FECHA_1F":"FECHA_1F"},

"VALVULAS_AZ_1G-1H":{
                    "STATUS_VALVULA_1G":"NÃO CONECTADO",\
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1H":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1G":"ABRE_1G",\
                    "FECHA_1G":"FECHA_1G",\
                    "ABRE_1H":"ABRE_1H",\
                    "FECHA_1H":"FECHA_1H"},

"VALVULAS_AZ_1I-1J":{
                    "STATUS_TEMPO_OPERACAO":"NÃO INICIADO",\
                    "STATUS_VALVULA_1I":"NÃO CONECTADO",\
                    "STATUS_VALVULA_1J":"NÃO CONECTADO",\
                    "STATUS_IP": "0",\
                    "ABRE_1J":"ABRE_1J",\
                    "FECHA_1J":"FECHA_1J",\
                    "ABRE_1I":"ABRE_1I",\
                    "FECHA_1I":"FECHA_1I"},
}

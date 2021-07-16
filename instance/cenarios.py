import json
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Cenas():
	def __init__(self):
		self.json_cenas = {}
		try:
			with open(os.path.join(ROOT_DIR, "config", "cenas.json")) as json_file:
				self.json_cenas = json.load(json_file)
		except:
			self.cria_cenarios()
		
	def cria_cenarios(self):
		for cenas in range(10):
			cenas +=1
			js={'CANAL1':{'NOME_SANCA':'SANCAS DA FRENTE', 'COMANDO':'LED,1,','COR': "25,255,255", "DISPOSITIVO":"MEGA"}}
			leds={'LEDS':js}
			self.json_cenas['CENA'+str(cenas)]=leds
			self.json_cenas['CENA'+str(cenas)]['LEDS']['CANAL2']={'NOME_SANCA':'SANCAS DE TRÁS', 'COMANDO':'LED,2,','COR': "255,255,255", "DISPOSITIVO":"MEGA"}
			self.json_cenas['CENA'+str(cenas)]['LEDS']['CANAL3']={'NOME_SANCA':'PAREDES', 'COMANDO':'LED,3,','COR': "255,255,255", "DISPOSITIVO":"MEGA"}
			self.json_cenas['CENA'+str(cenas)]['LEDS']['CANAL4']={'NOME_SANCA':'CRUZ','COMANDO':'LED,4,','COR': "255,255,255", "DISPOSITIVO":"MEGA"}
			js={'CANAL1':{'NOME_DIM':'LONA', 'COMANDO':'DIMER,1,','INTENSIDADE': "100"}}
			leds={'DIMER':js}
			self.json_cenas['CENA'+str(cenas)]['DIMER']=js
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL2']={'NOME_DIM':'PAREDES', 'COMANDO':'DIMER,2,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL3']={'NOME_DIM':'TETO ESQUERDA', 'COMANDO':'DIMER,3,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL4']={'NOME_DIM':'TETO DIREITA', 'COMANDO':'DIMER,4,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL5']={'NOME_DIM':'TRILHO 1', 'COMANDO':'DIMER,5,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL6']={'NOME_DIM':'TRILHO 2', 'COMANDO':'DIMER,6,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL7']={'NOME_DIM':'TRILHO 3', 'COMANDO':'DIMER,7,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL8']={'NOME_DIM':'SANCA FUNDO', 'COMANDO':'DIMER,8,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL9']={'NOME_DIM':'', 'COMANDO':'DIMER,9,','INTENSIDADE': "100"}
			self.json_cenas['CENA'+str(cenas)]['DIMER']['CANAL10']={'NOME_DIM':'', 'COMANDO':'DIMER,10,','INTENSIDADE': "100"}
		
		with open(os.path.join(ROOT_DIR, "config", "cenas.json"), 'w') as outfile:
		# print(json.dumps(self.json_cenas, indent=2))
			json.dump(self.json_cenas, outfile)
	def load_cenario(self):
		cenas = {}
		try:
			with open(os.path.join(ROOT_DIR, "config", "cenas.json")) as json_file:
				cenas = json.load(json_file)
		except:
			self.cria_cenarios()
			with open(os.path.join(ROOT_DIR, "config", "cenas.json")) as json_file:
				cenas = json.load(json_file)

		return cenas
		
	def load_leds(self, cenario):
		cenario = 'CENA'+str(cenario)
		led_list = []
		for k,v in self.json_cenas.items():
			if k == cenario:
				for _list in self.json_cenas[k]:
					if 'LED' in _list:
						# ~ indice_dimer = _list.split(',')[1]
						led_list.append(self.json_cenas[k][_list])
		return led_list
		
		
	def load_dimer_values(self, cenario):
		cenario = 'CENA'+str(cenario)
		dim_list = []
		for k,v in self.json_cenas.items():
			if k == cenario:
				for _list in self.json_cenas[k]:
					if 'DIMER' in _list:
						# ~ indice_dimer = _list.split(',')[1]
						dim_list.append(int(self.json_cenas[k][_list]))
		return dim_list

	
	def salva_cenario(self, data):
		with open(os.path.join(ROOT_DIR, "config", "cenas.json"), 'w') as outfile:
			print(json.dumps(data , indent=2))
			json.dump(data, outfile)	
		
	
	def muda_cenario(self, cena, luminaria, valor):
		self.json_cenas[cena][luminaria] = valor	

from telegram import Bot
import time

telegram_bot = Bot("MORADA_2")
try:
	telegram_bot.envia_telegram_pressao()
except Exception as e:
	print(e)
def mensagemFromBot(mensagem):
	print("MENSAGEM ",mensagem)
telegram_bot.ret_telepot(mensagemFromBot)
while True:

	time.sleep(5)
	#print("Loop")


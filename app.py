import sys
from io import BytesIO

from flask import Flask,request,send_file
import telegram

from PrivateData import token_dic
from chatMachine import chatMachine

app = Flask(__name__)
bot = telegram.Bot(token=token_dic['telegram_bot'])
machine = chatMachine(bot)

def _set_webhook():
	status = bot.set_webhook('{}/hook'.format(token_dic['ngrok']))
	if not status:
		print('Webhook setup failed')
		sys.exit(1)
@app.route('/hook',methods=['POST'])
def webhook_handler():
	if request.method == 'POST':
		data=request.get_json(force=True)
		update=telegram.Update.de_json(data,bot)
		machine.Advance(update=update,data=data)
		return 'ok'

@app.route('/show-fsm',methods=['GET'])
def show_fsm():
	byte_io = BytesIO()
	machine.get_graph().draw(byte_io,prog='dot',format='png')
	byte_io.seek(0)
	return send_file(byte_io,attachment_filename='fsm.png',mimetype='image/png')

def download_fsm():
	machine.get_graph().draw('fsm.png',prog='dot')

if __name__=='__main__':
	_set_webhook()
	download_fsm()
	app.run()

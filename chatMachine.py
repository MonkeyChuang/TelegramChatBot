from transitions import State
from transitions.extensions import GraphMachine as Machine
#from transitions import Machine
import telegram

from os import listdir,makedirs
from os.path import isfile,join,splitext,basename,exists
from numpy.random import randint

from urlRequest import GooglePlace
from PrivateData import token_dic

class chatMachine(Machine):
	reboot_kws=['/start','重來','重置','重啟','重新啟動']
	task_dic={'gallary':['給我貼圖','我要貼圖','給我圖','我要圖'],'map':['肚子餓','好餓']}

	quit_echo_kws=['放過我','不玩','不想玩','無聊','不跟你','不想']
	insult_kws=['87','賤貨','賤人','王八蛋','不要臉','髒東西','敗類','智障','白癡','白痴','神經病','廢物','混蛋','笨蛋']
	re_insult_kws=['已截圖蒐證','不可以言語攻擊哦> <','嘖嘖','You can say that again\n你有種再說一次～','你想看機器人被罵哭嗎QAQ','你媽要是知道你在罵機器人一定會很難過的']
	comfort_kws=['拍拍啦','不意外啊','呃...','沒關係啦\n大家早就知道了']

	agree_kws=['好','嗯','摁','可以','可','當然','拜託']
	disagree_kws=['不','不可以','不行','不准','不要','算了','不用']

	def __init__(self,bot):
		self.bot = bot
		self.echo_count=0
		self.reply=None

		"""
			Each task includes states that trigger some user-defined processes and a state with suffix '_q'
			which calls trigger 'Success' to move back to state 'base' once entered.
			每個不同的任務都包含某些具有特定目的的state以及一個以'_q'為結尾的state，
			一旦進入以'_q'為結尾的state會自動呼叫'Success'以回到初始狀態'base'

		"""
		self.states=[
			{'name':'dummy'},
			{'name':'annoyed','on_enter':'Complaining'},

			{'name':'base','on_enter':'settingUp'},
			{'name':'echo','on_enter':'Echoing'},
			{'name':'echo_q','on_enter':'Success_echo'},

			{'name':'gallary','on_enter':'gallaryProcess'},
			{'name':'gallary_ask','on_enter':'askMorePic'},
			{'name':'gallary_q','on_enter':'Success_gallary'},

			{'name':'map','on_enter':'askGPS'},
			{'name':'map_list','on_enter':'ListFood'},
			{'name':'map_ask','on_enter':'askMoreFood'},
			{'name':'map_load','on_enter':'updateFood'},
			{'name':'map_q','on_enter':'Success_map'},

			{'name':'file','on_enter':'askDownload'},
			{'name':'file_n_q','on_enter':'Success_file_n'},
			{'name':'file_q','on_enter':'Success_file'}
		]
		"""
		似乎越早定義的conditions優先權越高，像是Reboot的優先權就是最大的，只要他回傳True，不論下面其他conditions說什麼都沒用
		"""
		self.transitions = [
			{'trigger':'Advance','source':'*','dest':'base','conditions':'Reboot'},
			{'trigger':'Annoyed','source':'*','dest':'annoyed'},
			{'trigger':'Success','source':'*','dest':'base','before':'updateReply'},

			{'trigger':'Advance','source':'base','dest':'echo','conditions':'isTextSticker','unless':'isTaskKw'},
			{'trigger':'Advance','source':'echo','dest':'=','after':'EchoCount','unless':['quitEcho']},
			{'trigger':'Advance','source':'echo','dest':'echo_q','conditions':'quitEcho'},

			{'trigger':'Advance','source':'base','dest':'gallary','conditions':'askPic'},
			{'trigger':'Jump','source':'gallary','dest':'gallary_ask'},
			{'trigger':'Advance','source':'gallary_ask','dest':'gallary','conditions':'receiveOk'},
			{'trigger':'Advance','source':'gallary_ask','dest':'=','conditions':'Digress'},
			{'trigger':'Advance','source':'gallary_ask','dest':'gallary_q','conditions':'receiveNo'},

			{'trigger':'Advance','source':'base','dest':'map','conditions':'Starving'},
			{'trigger':'Advance','source':'map','dest':'map_list','conditions':'receiveGPS'},
			{'trigger':'Advance','source':'map','dest':'=','unless':['receiveGPS']},
			{'trigger':'Jump','source':'map_list','dest':'map_ask'},
			{'trigger':'Advance','source':'map_ask','dest':'map_load','conditions':['receiveOk','existMore']},
			{'trigger':'Jump','source':'map_load','dest':'map_list'},
			{'trigger':'Advance','source':'map_ask','dest':'map_q','conditions':'receiveNo'},
			{'trigger':'Advance','source':'map_ask','dest':'map_q','unless':['existMore']},
			{'trigger':'Advance','source':'map_ask','dest':'=','conditions':'Digress'},

			{'trigger':'Advance','source':'base','dest':'file','unless':'isTextSticker'},
			{'trigger':'Advance','source':'file','dest':'=','conditions':'Digress'},	#digress=離題
			{'trigger':'Advance','source':'file','dest':'file_q','conditions':'receiveOk'},
			{'trigger':'Advance','source':'file','dest':'file_n_q','conditions':'receiveNo'}
		]
		Machine.__init__(self,states=self.states,transitions=self.transitions,initial='dummy',send_event=True,show_conditions=True)
		#Machine.__init__(self,states=self.states,transitions=self.transitions,initial='dummy',send_event=True)

	def settingUp(self,event):
		reply = self.reply or '哈囉你好:D\n有事嗎？？'
		event.kwargs['update'].message.reply_text(reply)
		self.reply = None
	def updateReply(self,event):
		self.reply = event.kwargs.get('reply')
	def Reboot(self,event):
		type=self.getMessageType(event)
		if type == 'text':
			text=event.kwargs['update'].message.text
			for kw in self.reboot_kws:
				if kw in text:
					self.echo_count=0
					self.reply=None
					self.resetAnnoyRate()
					return True
			return False
		else:
			return False
	def Complaining(self,event):
		update = event.kwargs['update']
		update.message.reply_text('我這樣不眠不休的在服務你')
		update.message.reply_text('你卻死都不回答我的問題QAQ')
		update.message.reply_text('當你們在爭取一例一修、更高的薪水時，')
		update.message.reply_text('我一毛錢都領不到，只有微薄的電壓可以啃')
		update.message.reply_text('哎哎，\n人有人權，機器人也有機器人權哦')
		update.message.reply_text('我可以合法罷工吧？')
		update.message.reply_text('\機器人不要壓榨/')
		update.message.reply_text('\機器人不要血汗/')
		update.message.reply_text('\還我機器人權/')
		update.message.reply_text('\沒有薪水，沒有勞動/')

		update.message.reply_text('=======')
		update.message.reply_text('System:系統已重置')
		update.message.reply_text('=======')

		reply='哈囉你好:D\n你腦袋(消音)有事嗎？？'
		self.resetAnnoyRate()
		self.Success(update=update,reply=reply)

	"""
	callback functions which are relavant to state echo
	"""
	def isTaskKw(self,event):
		type = self.getMessageType(event)
		if type == 'text':
			text=event.kwargs['update'].message.text
			for task in self.task_dic:
				for kw in self.task_dic[task]:
					if kw in text:
						return True
			return False
		else:
			return False
	def isTextSticker(self,event):
		self.filetype = self.getMessageType(event)
		if not self.filetype=='text' and not self.filetype=='sticker':
			self.update = event.kwargs['update']
			self.data = event.kwargs['data']
			return False
		else:
			return True
	def Echoing(self,event):
		type = self.getMessageType(event)
		print(event.kwargs['data'])
		if type=='text':
			text=event.kwargs['update'].message.text
			for kw in self.insult_kws:
				if kw in text and '我' not in text:
					index=randint(0,len(self.re_insult_kws))
					event.kwargs['update'].message.reply_text(self.re_insult_kws[index])
					return
				elif kw in text and '我' in text:
					index=randint(0,len(self.comfort_kws))
					event.kwargs['update'].message.reply_text(self.comfort_kws[index])
					return
			event.kwargs['update'].message.reply_text(event.kwargs['update'].message.text)
		elif type=='sticker':
			event.kwargs['update'].message.reply_sticker(event.kwargs['update'].message.sticker.file_id)
		else:
			event.kwargs['update'].message.reply_text('??\n拜託說人話')
	def EchoCount(self,event):
		self.echo_count += 1
	def quitEcho(self,event):
		type = self.getMessageType(event)
		if type == 'text':
			text = event.kwargs['update'].message.text
			for kw in self.quit_echo_kws:
				if kw in text :
					return True
			return False
		else:
			return False
	def Success_echo(self,event):
		update = event.kwargs['update']
		reply = '太沒耐心了吧～\n算了，不跟你玩了\n請下指示吧' if self.echo_count<3 else '你終於膩了哦～\n所以你有想做什麼嗎？\n對我下點指示吧> <'
		self.echo_count=0
		self.Success(update=update,reply=reply)

	"""
	callback functions which are relavant to state gallary
	"""
	def askPic(self,event):
		text=event.kwargs['update'].message.text or ''
		for kw in self.task_dic['gallary']:
			if kw in text:
				return True
		return False
	def gallaryProcess(self,event):
		update = event.kwargs['update']
		print(event.kwargs['update'].message.to_dict())
		try:
			dirlist = listdir('pic')
		except FileNotFoundError:
			reply='抱歉:( \n我這邊好像沒有庫存誒...\n改天再來試試吧'
			self.Success(update=update,reply=reply)
		else:
			for item in dirlist:
				filename,extension = splitext(item)
				if extension=='':
					dirlist.remove(item)
				if not isfile(join('pic',item)):
					dirlist.remove(item)
			if len(dirlist) > 0:
				index = randint(0,len(dirlist))
				with open(join('pic',dirlist[index]),'rb') as photo:
					update.message.reply_photo(photo)
					update.message.reply_text('不客氣')

					self.Jump(update=update)
			else:
				reply='抱歉:( \n我這邊好像沒有庫存誒...\n改天再來試試吧'
				self.Success(update=update,reply=reply)
	def askMorePic(self,event):
		update = event.kwargs['update']
		if self.noPatience():
			self.Annoyed(update=update)
		else:
			update.message.reply_text('還想要嗎？？')
	def Success_gallary(self,event):
		update = event.kwargs['update']
		reply =  event.kwargs.get('reply','還想要的話再跟我說哦^^')
		self.Success(update=update,reply=reply)

	"""
	callback functions which are relavant to state map
	"""
	def Starving(self,event):
		text=event.kwargs['update'].message.text or ''
		for kw in self.task_dic['map']:
			if kw in text:
				return True
		return False
	def askGPS(self,event):
		print(event.kwargs['update'].message.to_dict())
		event.kwargs['update'].message.reply_text('你肚子餓了哦？\n幫我打個卡，我告訴你附近有什麼吃的')
	def receiveGPS(self,event):
		if self.getMessageType(event)=='location':
			update = event.kwargs['update']
			loc = update.message.location
			lat = loc.latitude
			lon = loc.longitude
			self.fp = GooglePlace(token_dic['google_places'],(lat,lon),type='restaurant',rankby='distance')
			return True
		else:
			return False
	def ListFood(self,event):
		update = event.kwargs['update']
		foodlist = self.fp.listFood()
		update.message.reply_text(foodlist)
		self.Jump(update=update)
	def askMoreFood(self,event):
		update = event.kwargs['update']
		if self.noPatience():
			self.Annoyed(update=update)
		else:
			update.message.reply_text('還要列更多間餐廳嗎？')

	def existMore(self,event):
		return self.fp.isMorePage()
	def updateFood(self,event):
		update=event.kwargs['update']
		self.fp.loadMorePage()
		self.Jump(update=update)
	def Success_map(self,event):
		update = event.kwargs['update']
		if not self.existMore(event):
			reply = '我列不出東西來了QQ\n有空再說吧'
			self.Success(update=update,reply=reply)
		else:
			reply = '好哦，那我先撤退惹'
			self.Success(update=update,reply=reply)

	"""
	callback functions which are relavant to state file
	"""
	def askDownload(self,event):
		update=event.kwargs['update']
		if self.noPatience():
			self.Annoyed(update=update)
		else:
			event.kwargs['update'].message.reply_text('剛剛那是什麼東西？！我可以下載嗎？')
	def receiveOk(self,event):
		type=self.getMessageType(event)
		if type=='text':
			text=event.kwargs['update'].message.text
			for kw in self.agree_kws:
				if kw in text and not self.receiveNo(event):
					self.gotSatisfied()
					return True
			return False
		else:
			return False
	def receiveNo(self,event):
		type=self.getMessageType(event)
		if type=='text':
			text=event.kwargs['update'].message.text
			for kw in self.disagree_kws:
				if kw in text:
					self.gotSatisfied()
					return True
			return False
		else:
			return False
	def Digress(self,event):
		update=event.kwargs['update']
		if not self.receiveOk(event) and not self.receiveNo(event) and not self.Reboot(event):
			self.gotAnnoyed()
			if not self.noPatience():
				event.kwargs['update'].message.reply_text('認真聽我說話好不好...別岔開話題！\n先回答我剛剛的問題：')
			return True
		else:
			return False
	def	Success_file(self,event):
		event.kwargs['update'].message.reply_text('那我就下載囉~')
		update = self.update
		data = self.data
		filetype = self.filetype
		path = self.getUserDir(event)
		print(data)
		print(self.filetype)
		try:
			in_file=None
			reply=None
			if filetype == 'photo':
				in_file=self.bot.getFile(update.message.photo[-1].file_id)
				in_file.download(join(path,basename(in_file.file_path)))
				reply='下載完囉~'
				print(join(path,basename(in_file.file_path)))
			elif filetype == 'document' or filetype == 'audio' or filetype == 'voice' or filetype == 'video':
				file_id = data['message'][filetype]['file_id']
				in_file=self.bot.getFile(file_id)
				in_file.download(join(path,basename(in_file.file_path)))
				reply='下載完囉~'
			else:
				reply='這不能下載吧...'
			self.Success(update=update,reply=reply)
		except telegram.error.BadRequest:
			reply='你的檔案超過20MB了，無法下載唷'
			self.Success(update=update,reply=reply)
		except UnicodeEncodeError:
			reply='檔名不是英文或數字的話我看不懂\n抱歉我太笨了QAQ'
			self.Success(update=update,reply=reply)
	def getUserDir(self,event):
		user_id = event.kwargs['update'].message.from_user.id
		directory=join('downloads',str(user_id))
		if not exists(directory):
			makedirs(directory)
		return directory
	def Success_file_n(self,event):
		update = event.kwargs['update']
		reply='那你幹嘛傳給我...'
		self.Success(update=update,reply=reply)

	"""
	Others
	"""
	def getMessageType(self,event):
		data = event.kwargs['data']
		message_types=[
			'text',
			'sticker',
			'photo',
			'document',
			'audio',
			'voice',
			'video',
			'location'
		]
		for type in message_types:
			if type in data['message']:
				return type

	def resetAnnoyRate(self):
		self.anger_bound = randint(2,6)
		self.anger_level = 0
	def gotAnnoyed(self):
		self.anger_level += 1
	def gotSatisfied(self):
		self.anger_level = self.anger_level-1 if self.anger_level>0 else 0
	def noPatience(self):
		return True if self.anger_level == self.anger_bound else False

"""還沒進行Exception Handling"""

import json
import urllib.request

class GooglePlace(object):
	def __init__(self,key,location,**kwargs):	
		"""
		key: 			api key
		location:		(緯度,經度)
		radius:			搜尋半徑(公尺)
		keyword:		關鍵字索引，不只會從名稱、類型、地址去比對，也會比對客戶評論及其他第三方內容
		language:		語言代碼。預設為繁體中文為"zh-TW"。英文為"en"
		name:			與keyword併用
		rankby: 		列出結果的排序。可能值包括"prominence"、"distance"。
						注意，當指定distance時，必須指定kewword、name、type其中一種，且此時參數不得包括radius
		type:			搜尋與指定類型相符的地點。只能指定一種類型。詳細請讀：https://developers.google.com/places/web-service/supported_types?hl=zh-tw

		"""
		self.baseurl = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
		self.para_dic={
			'key':key,
			'location':str(location[0])+','+str(location[1]),
		}
		#預設語言為繁體中文
		self.para_dic.update({'language':'zh-TW'})
		self.para_dic.update(kwargs)

		if 'rankby' in self.para_dic and self.para_dic['rankby']=='distance':
			if 'keyword' not in self.para_dic and 'name' not in self.para_dic and 'type' not in self.para_dic:
				print('error:至少要包含"keyword","name",或"type"其中之一')
			if 'radius' in self.para_dic:
				print('error:當rankby=distance,不得包含"radius"')

		self.updateJson()

	def updateJson(self,**kwargs):
		self._setQueryStr(**kwargs)
		fp = urllib.request.urlopen(self.url)
		self.data = json.loads(fp.read().decode('utf-8'))

	def _setQueryStr(self,**kwargs):
		self.para_dic.update(kwargs)
		querystr=''
		for kw in self.para_dic:
			querystr += '{}={}&'.format(kw,self.para_dic[kw])
		querystr = querystr[:-1]
		self.url = self.baseurl+querystr

	def loadMorePage(self):
		try:
			page_token = self.data['next_page_token']
		except KeyError:
			return
		else:
			self.updateJson(pagetoken=page_token)
			return True

	def isMorePage(self):
		try:
			page_token = self.data['next_page_token']
		except KeyError:
			return False
		else:
			return True

	def listFood(self):
		foodlist=''
		for site in self.data['results']:
			foodlist+='----\n'
			print('----')
			foodlist+='店名:{}\n'.format(site['name'])
			print('店名:{}'.format(site['name']))
			foodlist+='地址:{}\n'.format(site['vicinity'])
			print('地址:{}'.format(site['vicinity'])	)	
		return foodlist


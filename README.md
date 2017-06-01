# Telegram ChatBot using Python
Its name is `LaplaceBot`.   
No need to question the derivation of its name 'cause it came up without any reason.
## Requirement
 python 3.5.2
### 套件/模組
- flask 0.12.2
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 6.0.0
- [transitions](https://github.com/tyarkoni/transitions) 0.5.2
- pygraphviz 1.3.1
- numpy 1.11.3

### Key/Token
在`PrivateData.py`中需要提供三筆資訊`telegram_bot`、`ngrok`、`google_places`：
1. telegram_bot：從Telegram的BotFather那邊得到的Bot API token
1. ngrok：由ngrok所產生的https URL。
1. google_places：由於這裡設計的`LaplaceBot`會藉由Google Places API提取使用者附近餐廳的資訊，所以需要到[這裡](https://developers.google.com/places/web-service/get-api-key?hl=zh-tw)申請API Key

```python
#PrivateData.py
token_dic={
	'telegram_bot':'<ChatBot API token>',
	'google_places':'<GooglePlaces API key>',
	'ngrok':'https://xxxxxxx.ngrok.io'
}
```

### 建立pic資料夾
在伺服器端(執行`app.py`的那層資料夾裡)建立`pic`資料夾，內部需存放適當張數的圖片(副檔名為'jpg','png',等等皆可)。
```bash
ls
pic     PrivateData.py		chatMachine.py  urlRequest.py    app.py
```
### 執行
```python
python app.py
```
## <a name='interact'></a>Interaction with Chat Bot
`LaplaceBot`大致提供了四種功能：`Echo`、`上傳圖片`、`搜尋周遭餐廳`、`下載檔案/圖片`。
### The Very Beginning
在你第一次進入與LaplaceBot的聊天室後，會自動送出`/start`訊息給機器人，而他這時就會回答「哈囉你好:D
有事嗎？？」。  

為了說明方便，我們接下來都稱這個最初的狀態為「初始狀態」。

要讓LaplaceBot執行以下四種功能前，首先要確認你當下正在初始狀態。如果不太確定你現在在哪個狀態裡，可以傳
> /start、重來、重置、重新啟動  

其中一句給機器人，他就會被重新啟動，並且回到初始狀態裡

### 搜尋周遭餐廳 (手持裝置才有的功能)
假如你現在肚子餓扁了，但你卻不知道附近有什麼吃的可以選擇。那就告訴LaplaceBot你肚子餓了吧！他會給你點意見的。
可惜他稍微笨了一點，你說的話裡至少要有
> 肚子餓、好餓

這兩個關鍵字，他才會知道你肚子餓了。
此時他會請求你「打卡」，也就是把你的Location傳給他，點擊下圖右下角的綠色圓圈即可
![](https://i.imgur.com/03dyy1F.jpg)

之後他會列出20間餐飲店選項給你(條列的順序是以與使用者傳送的GPS位置遠近相關，越前面的選項離使用者越近)，並且詢問你還要不要他列舉更多間。

這邊如果你沒有給他肯定或否定的回答，他會發現你離題了，並且再次提醒你要趕快給他一個答覆。

關於肯定句與否定句的關鍵字，請到[這裡](#keyword)

如果機器人所能提供的搜尋結果被表列完了，那你就無法再要求他回傳更多資訊，此時他就會告訴你「我列不出東西來了QQ
有空再說吧」並回到初始狀態。
如果你告訴機器人不用再繼續列舉，那他就會回答「好哦，那我先撤退惹」並回到初始狀態。

### 上傳圖片
你傳給機器人的話裡面只要包含以下關鍵字
> 給我貼圖、我要貼圖、給我圖、我要圖

他就會從伺服器端的pic資料夾中隨機上傳一張圖片給使用者，每上傳完一張之後他也會詢問使用者是否還需要他給你更多圖片，同樣的，他也會判斷你的答覆是否有離題。

關於肯定句與否定句的關鍵字，請到[這裡](#keyword)


如果伺服器端並沒有提供`pic`資料夾，或是`pic`資料夾中沒有任何圖片，那機器人就會誠實的說他沒有圖片可以給你，並且請你以後再來問他，然後回到初始狀態

### Echo
當你確定你在初始狀態後，如果你傳了與觸發上述兩種功能的用語無關的話或Stickers，機器人接下來就會不斷地模仿你對他說的話，直到你說出含有以下關鍵字的話
>放過我、不玩、不想玩、無聊、不跟你、不想

他才會停止，並回到初始狀態

請不要嘗試用言語辱罵機器人，如果他覺得你在罵他，他會抗議的。

### 下載檔案/圖片
如果你一句話都不說、一張sticker也不傳，只上傳一張圖片、檔案、影像...等等，給機器人，那他就會詢問他是否能把檔案下載下來。如果允許他下載，那該份檔案就會被下載至伺服器端的`downloads`資料夾裡的`<user-id>`，機器人會貼心地幫你把你傳的檔案存放在以你的使用者ID為名的資料夾當中，才不會和其他人上傳的東西搞混。要是你不讓他下載，他就會......當然就不會下載，只是會小小抱怨一下，接著回到初始狀態

同樣的，在這裡機器人也會偵測你說的話是否有離題，並且提醒你該回神了

> 注意: 上傳檔案的檔名最好是用ascii編碼能解讀的字元(英文、阿拉伯數字等等)，如果檔名裡有中文，有可能無法下載

關於肯定句與否定句的關鍵字，請到[這裡](#keyword)

## Reactions of LaplaceBot
### Don't aggravate him
除了`Echoing`這項功能以外，LaplaceBot 常常會詢問你是否要他提供更多資訊、圖片、或是是否允許他執行下載動作。如同在[Interaction with Chat Bot](#interact)段落提到的，要是你不給他一個適當的回覆，機器人會判定你已經離題了。

我們的LaplaceBot其實被賦予了一種情緒——憤怒，如果你一直離題，他的煩躁感就會一直上升，等到這煩躁感超過他的忍耐限度時，他會做出生氣的反應。相對的，如果你給予他適當的答覆，也就是給了肯定句或否定句，那他的煩躁感就可以被降下。


## Some Useful Keywords You Need to Know
### <a name="keyword"></a>肯定/否定句的關鍵字
- 肯定的回答的關鍵字
> 好、嗯、摁、可以、可、當然、拜託

- 否定的回答的關鍵字
>不、不可以、不行、不准、不要、算了、不用

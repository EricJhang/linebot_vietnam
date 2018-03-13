from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,TemplateSendMessage,ButtonsTemplate,PostbackTemplateAction
)
import os
app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.environ['lineToken'])
# Channel Secret
handler = WebhookHandler(os.environ['lineSecret'])

question_list = ["如何開卡","何時可以收到貨","電話卡與上網卡的不同"]
answer_list = ["直接換置使用，會自動開通，我們的越南客服會在您起飛的前2天開卡前1天檢查，由雲端幫您開卡設定，您飛機上用餐完就可以換卡，飛機降落後開機就可以用了。\n使用說明書上有官方客服的賴，如果有任何異常（飛機降落後開機不能用），在行李轉盤那邊有免費WIFI，請趕快用賴通知我們的官方客服，我們的賴客服是台灣越南連線，有異常可以馬上處理。 \n免設定、免調整、免改任何東西",
"我們天天出貨，今天出貨，7-11最穩後天（3天）到您指定的超商。\n全家、萊爾富時快時慢，最快明天最慢大後天（2-4天）到您指定的超商",
"電話卡預設只有1萬越盾，打電話是打越南國內網外的手機5分鐘\n上網卡只能收簡訊，無法發簡訊與接聽電話"]

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    print("question_list length is %d "%len(question_list))
    message = TextSendMessage(text=event.message.text)
    if(event.message.text =="#問題"):
        text_result = greate_buttontemplate(0)
        replay_message(event,text_result)
    elif(event.message.text =="#問題2"):
        text_result = greate_buttontemplate(2)
        replay_message(event,text_result)
        
@handler.default()
def default(event):
    print("enter default event")
    print(event)
    if(event.type =="postback"):
        text_result = event.postback.data
        if(text_result !="") and (text_result!= "2") and (text_result!= "0"):
            message = TextSendMessage(text=text_result)
            replay_message(event,message)
        elif(text_result=="2"):
            message = greate_buttontemplate(2)
            replay_message(event,message)
        elif(text_result== "0"):
            message = TextSendMessage(text="回到首頁")
        print("enter postback event")
    else:
        print("event.type !=postback")
        
def replay_message(event,text):
    line_bot_api.reply_message(
        event.reply_token,
        text)
        
def push_message(event,text):
    line_bot_api.reply_message(
        event.source.user_id,
        text)        
def greate_buttontemplate(index_tmp):
    if((int(index_tmp) >= 0 ) and ((len(question_list))-index_tmp) >= 2): 
        other_index = index_tmp+2
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(            
                title='常見問題',
                text='請選擇以下問題，由小助手替您解答',
                actions=[
                    PostbackTemplateAction(
                        label=question_list[0+index_tmp],
                        data=answer_list[0+index_tmp]
                    ),
                    PostbackTemplateAction(
                        label=question_list[1+index_tmp],
                        data=answer_list[1+index_tmp]
                    ),
                    PostbackTemplateAction(
                        label="其他",
                        data=other_index
                    )
                ]
            )
        )
    elif((index_tmp > 0) and ((len(question_list)-index_tmp) == 1)) :
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(            
                title='常見問題',
                text='請選擇以下問題，由小助手替您解答',
                actions=[
                    PostbackTemplateAction(
                        label=question_list[0+index_tmp],
                        data=answer_list[0+index_tmp]
                    ),
                    PostbackTemplateAction(
                        label="回到首頁",
                        text ="#問題",
                        data=0
                    )
                ]
            )
        )
    else:
        buttons_template_message = TextSendMessage(text="請重新輸入 #問題")
    return buttons_template_message
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

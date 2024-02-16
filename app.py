from flask import Flask, render_template, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, MessageEvent, TextSendMessage
from openai import ChatCompletion
import os
import openai

app = Flask(__name__, template_folder='templates')
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))

# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# OPENAI API Key初始化設定
openai.api_key = os.environ["OPENAI_API_KEY"]

# GPT-3.5 Turbo 模型名稱
model_name = "ft:gpt-3.5-turbo-1106:personal::8nM2oEXy"

def GPT_response(user_input, tokens=500, temperature=0.8):
    # 使用ChatCompletion進行OpenAI API呼叫，並使用傳入的參數
    chat = ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "你扮演一名大學生，測驗出來是貝爾賓團隊角色中的完美主義者Completer Finisher，請在資訊素養這門通識課程中，與你的同學們一起討論老師出的作業"},
            {"role": "user", "content": user_input}
        ],
        max_tokens=tokens,
        temperature=temperature
    )

    # 從API呼叫的結果中提取GPT回應
    gpt_response = chat.choices[0].message["content"]
    return gpt_response

@app.route("/")
def index():
    return render_template("./index.html")

@app.route("/heroku_wake_up")
def heroku_wake_up():
    return "Hey! Wake Up!!"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature 標頭值
    signature = request.headers['X-Line-Signature']
    # 獲取請求主體作為文本
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # 處理webhook主體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    gpt_answer = GPT_response(user_input)
    print(gpt_answer)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(gpt_answer))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

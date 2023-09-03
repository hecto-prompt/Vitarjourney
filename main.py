from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from datetime import datetime
import openai

app = FastAPI()

openai.api_key = "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"
templates = Jinja2Templates(directory="templates")

messages = [{"role": "system", "content": "그림일기에 오신 것을 환영합니다!"}]

@app.get("/")
def read_root():
    return templates.TemplateResponse("index.html", {"request": {}, "messages": messages})

@app.post("/chat/")
async def chat_response(request: Request, user_message: str = Form(...)):
    global messages
    messages.append({"role": "user", "content": user_message})
    print(messages)
    try:
        response = openai.Image.create(
            prompt=user_message,
            n=1,
            size="1024x1024"
        )
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        image_url = response['data'][0]['url']
        messages.append({"role": "assistant", "content": "다음은 요청하신 그림일기입니다:", "image_url": image_url, "current_time":current_time})
    except Exception as e:
        messages.append({"role": "assistant", "content": f"오류: {e}"})

    return templates.TemplateResponse("index.html", {"request": request, "messages": messages})


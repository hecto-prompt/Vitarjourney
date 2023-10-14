import logging

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from datetime import datetime
import openai
import os

from pydantic import BaseModel

app = FastAPI()

openai.api_key = os.environ.get("OPENAI_API_KEY")
templates = Jinja2Templates(directory="templates")

messages = [{"role": "system", "content": "VitaJourney에 오신 것을 환영합니다!"}]

@app.get("/")
def root():
    return templates.TemplateResponse("root.html", {"request": {}, "messages": messages})
@app.get("/chat")
async def chat_request():
    return templates.TemplateResponse("index.html", {"request": {}, "messages": messages})


@app.post("/chat")
async def chat_response(
    user_message: str = Form(...),
    height: float = Form(...),
    age: int = Form(...),
    current_weight: float = Form(...),
    target_weight: float = Form(...),
    duration: int = Form(...)
):
    global messages

    user_message: str = Form(...),
    height: float = Form(...),
    age: int = Form(...),
    current_weight: float = Form(...),
    target_weight: float = Form(...),
    duration: int = Form(...)

    user_info = (f" 키: {height} cm, 나이: {age} 세, "
                 f"현재 체중: {current_weight} kg, 원하는 체중: {target_weight} kg, 기간: {duration} 일")

    user_message += user_info

    messages.append({"role": "user", "content": user_message})
    print(messages)


    try:
        # 여기에서 사용자의 입력 정보(height, weight, target_weight)를 사용하여 BMI 계산 등을 수행할 수 있습니다.
        # BMI 계산 코드를 여기에 추가하십시오.

        response = openai.Image.create(
            prompt=user_message,
            n=1,
            size="1024x1024"
        )
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        image_url = response['data'][0]['url']
        text = response['data'][0]['text']


        messages.append(
            {"role": "assistant", "content": "다음은 요청하신 식단입니다:", "image_url": image_url, "text" : text, "current_time": current_time})
    except Exception as e:
        messages.append({"role": "assistant", "content": f"오류: {e}"})

    return templates.TemplateResponse("index.html", {"request": request, "messages": messages})

# 추가 폼 요소(height, weight, target_weight)를 템플릿에 추가해야 합니다.

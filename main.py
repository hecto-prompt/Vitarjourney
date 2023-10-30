import os
from datetime import datetime

import openai
from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from langchain.chains import LLMChain
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel

app = FastAPI(debug=True)

openai.api_key = os.environ.get("OPENAI_API_KEY")

templates = Jinja2Templates(directory="templates")

messages = [{"role": "system", "content": "VitaJourney에 오신 것을 환영합니다!"}]

class UserInfo(BaseModel):
    user_message: str
    height: float
    age: int
    current_weight: float
    target_weight: float
    duration: int

@app.get("/")
def root():
    return templates.TemplateResponse("root.html", {"request": {}, "messages": messages})


@app.post("/check")
async def check_info(
        height: int = Form(...),
        age: int = Form(...),
        current_weight: int = Form(...),
        target_weight: int = Form(...),
        duration: int = Form(...)
):
    print("Received input data:")
    print(f"Height (cm): {height}")
    print(f"Age: {age}")
    print(f"Current Weight (kg): {current_weight}")
    print(f"Target Weight (kg): {target_weight}")
    print(f"Duration (days): {duration}")
    return templates.TemplateResponse("index.html", {
        "request": {},
        "messages": messages,
        "height": height,
        "age": age,
        "current_weight": current_weight,
        "target_weight": target_weight,
        "duration": duration
    })
@app.post("/chat")
async def chat_response(
        user_message: str = Form(...),
        height: int = Form(...),
        age: int = Form(...),
        current_weight: int = Form(...),
        target_weight: int = Form(...),
        duration: int = Form(...),

):
    global messages

    print("Received input data:")
    print(f"Height (cm): {height}")
    print(f"Age: {age}")
    print(f"Current Weight (kg): {current_weight}")
    print(f"Target Weight (kg): {target_weight}")
    print(f"Duration (days): {duration}")

    user_text = (f" my infomation is Height: {height} cm, Age: {age} years, "
                 f"Current Weight: {current_weight} kg, Target Weight: {target_weight} kg, Duration: {duration} days, Please recommend Diet food receipt")

    good_qa_prompt = PromptTemplate(
        template=""""If my text does not contain any food, drink, or fruit, respond with 'No'. If it does, respond with 'Yes'

        Question: {question}

        """,
        input_variables=["question"],
    )

    llm = OpenAI(temperature=0)

    good_qa_chain = LLMChain(llm=llm, prompt=good_qa_prompt)

    judgment = good_qa_chain.run(question=user_message)

    def translate_to_korean_with_openai(text):
        prompt = f"Translate the following English text to Korean: '{text}'"
        response = openai.Completion.create(
            engine="davinci",  # 이 엔진 이름은 현재 사용하고 있는 엔진에 따라 변경될 수 있습니다.
            prompt=prompt,
            max_tokens=200
        )
        translated_text = response.choices[0].text.strip()
        return translated_text

    if judgment == '\nYes':

        user_message += user_text

        messages.append({"role": "user", "content": user_message})
        print(messages)

        try:
            # 여기에서 사용자의 입력 정보(height, weight, target_weight)를 사용하여 BMI 계산 등을 수행할 수 있습니다.
            # BMI 계산 코드를 여기에 추가하십시오.
            response_text = openai.Completion.create(
                engine="text-davinci-003",
                prompt=user_message,
                max_tokens=2000
            )

            text = response_text.choices[0].text
            translatedText = translate_to_korean_with_openai(text)

            response_image = openai.Image.create(
                prompt=text,
                n=1,
                size="1024x1024"
            )


            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            image_url = response_image['data'][0]['url']

            messages.append(
                {"role": "assistant", "content": "다음은 요청하신 식단입니다:", "text":translatedText, "image_url": image_url, "current_time": current_time})
        except Exception as e:
            if 'safety system' in str(e):
                messages.append({"role": "assistant", "content": f"safety system: {e}"})
            else:
                messages.append({"role": "assistant", "content": f"오류: {e}"})

        return templates.TemplateResponse("index.html", {
            "request":{},
            "height": height,
            "age": age,
            "current_weight": current_weight,
            "target_weight": target_weight,
            "duration": duration,
            "messages": messages
        })
    else:
        # 음식, 음료, 또는 과일과 관련이 없는 경우의 메시지 처리
        messages.append({"role": "assistant", "content": "제대로 된 값을 입력해주세요."})
        return templates.TemplateResponse("index.html", {
            "request":{},
            "height": height,
            "age": age,
            "current_weight": current_weight,
            "target_weight": target_weight,
            "duration": duration,
            "messages": messages
        })
# 추가 폼 요소(height, weight, target_weight)를 템플릿에 추가해야 합니다.

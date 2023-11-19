import os
from datetime import datetime

import openai
from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from langchain.chains import LLMChain
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import requests

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

    # user_text = (f" my infomation is Height: {height} cm, Age: {age} years, "
    #              f"Current Weight: {current_weight} kg, Target Weight: {target_weight} kg, Duration: {duration} days, Please recommend Diet food recipe for lunch within 500 words strictly. Don't explain about the recipe, just recommend the recipe. Recommend only one recipe.")
    user_text = (f" 내 키는: {height} cm, 나이는: {age} 살이고, "
                 f"현재 몸무게는: {current_weight} kg, 목표 몸무게는: {target_weight} kg, 기간은: {duration} 일동안이야, 700자 이내로 점심에 먹을만한 건강식 레시피를 추천해줘. 레시피에 대한 부가설명은 필요없고 레시피를 조리 순서대로 알려줘. 레시피는 하나만 추천해줘. 창의성은 0, 최대한 내가 전달한 식재료만 가지고 만들 수 있는 레시피로 추천해줘.")

    good_qa_prompt = PromptTemplate(
        template=""""내가 입력한 식재료 중 먹을 수 없는 것이 하나라도 들어있을 때는 'No'라는 단어를 보내줘. 모두 먹을 수 있는 재료라면 'Yes'라는 단어를 보내줘 'Yes'나 'No' 앞에 아무 단어도 붙이지 마.

        Question: {question}

        """,
        input_variables=["question"],
    )

    llm = OpenAI(temperature=0)

    good_qa_chain = LLMChain(llm=llm, prompt=good_qa_prompt)

    judgment = good_qa_chain.run(question=user_message).strip()
    print("judgment:",judgment)

    # 번역 함수
    # def translate_to_korean_with_openai(text):
    #     prompt = f"Translate the following English text to Korean within 800 words: '{text}'"
    #     try:
    #         response = openai.Completion.create(
    #             engine="text-davinci-003",
    #             prompt=prompt,
    #             max_tokens=2000
    #         )
    #         translated_text = response.choices[0].text.strip()
    #         print("Translated text:", translated_text)
    #     except Exception as e:
    #         print("Error during translation:", e)
    #         translated_text = ""
    #     return translated_text

    def translate_to_english_with_openai(text):
        prompt = f"Translate the following Korean text to English within 800 words: '{text}'"
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=2000
            )
            translated_text = response.choices[0].text.strip()
            print("Translated text:", translated_text)
        except Exception as e:
            print("Error during translation:", e)
            translated_text = ""
        return translated_text

    if judgment == 'Answer: Yes':

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
            translatedText = translate_to_english_with_openai(text)

            response_image = openai.Image.create(
                prompt=translatedText,
                n=1,
                size="1024x1024"
            )


            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            image_url = response_image['data'][0]['url']

            messages.append(
                {"role": "assistant", "content": "다음은 요청하신 식단입니다:", "text":text, "image_url": image_url, "current_time": current_time})
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

@app.get("/download_image/")
async def download_image(url: str):
    response = requests.get(url, stream=True)
    return StreamingResponse(response.iter_content(), media_type=response.headers['Content-Type'])

# 추가 폼 요소(height, weight, target_weight)를 템플릿에 추가해야 합니다.

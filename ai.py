import ai
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_advice(category):

    prompt = f"""
あなたはプログラミング学習を支援する先生です。

学習者の苦手分野は「{category}」です。

以下の条件でアドバイスしてください。

・100文字程度
・初心者向け
・優しい文章
・次に学ぶ内容も提案する
"""

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "system",
                "content": "あなたは優秀なプログラミング教師です。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    return response.choices[0].message.content

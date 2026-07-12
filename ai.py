import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
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

    response = client.models.generate_content(
        model="models/gemini-3.5-flash",
        contents=prompt,
    )

    return response.text


def generate_question(category):

    prompt = f"""
あなたはPython学習支援AIです。

初心者向けの4択問題を1問作成してください。

分野は「{category}」です。

以下のJSON形式のみで回答してください。

{{
    "question": "",
    "choices": [
        "",
        "",
        "",
        ""
    ],
    "answer": 0,
    "explanation": ""
}}

条件
・選択肢は4つ
・answerは0〜3の整数
・初心者向け
・JSON以外は絶対に出力しない
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash",
        contents=prompt,
    )

    return json.loads(response.text)


def generate_feedback(score, total, category):

    prompt = f"""
あなたは優しく優秀なプログラミング講師です。

学習者はAI問題を解きました。

結果
・正解数：{score}/{total}
・苦手分野：{category}

以下の条件で講評してください。

・100文字程度
・初心者向け
・励ます
・苦手分野の復習方法を提案する
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return response.text
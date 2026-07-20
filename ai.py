import os
import requests
import json
from dotenv import load_dotenv
import streamlit as st

# 環境変数（.env）の読み込み
load_dotenv()

def call_gemini_api(api_key, prompt):
    """Gemini APIを直接HTTPリクエストで呼び出す"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error(f"Gemini API エラー: {response.status_code}")
            st.write(response.text)
    except Exception as e:
        print(f"Gemini API 接続エラー: {e}")
    return None

def call_openai_api(api_key, prompt):
    """OpenAI APIを直接HTTPリクエストで呼び出す"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "あなたは優秀なプログラミング教師です。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
        else:
            print(f"OpenAI API エラー: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"OpenAI API 接続エラー: {e}")
    return None

def generate_mock_advice(category):
    """API呼び出しが失敗したときの親切なデフォルト回答"""
    return (
        f"【お知らせ: API接続エラー中のため定型アドバイス】\n"
        f"「{category}」ですね！難しく感じるかもしれませんが、まずは短いコードを動かすことから始めましょう。"
        f"次回は基礎文法を確認し、実際に手を動かす簡単な練習問題に進みましょう！"
    )

def generate_advice(category, provider="Gemini"):
    """
    指定された分野に対してアドバイスを生成する (Gemini or OpenAI)
    """
    prompt = f"""
あなたはプログラミング学習を支援する先生です。

学習者の苦手分野は「{category}」です。

以下の条件でアドバイスしてください。

・100文字程度
・初心者向け
・優しい文章
・次に学ぶ内容も提案する
"""

    result = None

    if provider == "Gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            result = call_gemini_api(api_key, prompt)

    elif provider == "OpenAI":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            result = call_openai_api(api_key, prompt)

    # 【重要】結果があればそれを返し、失敗・キー不足ならモックを返す処理を追加
    if result:
        return result
    else:
        return generate_mock_advice(category)

def generate_question(category, difficulty, provider="Gemini"):
    """
    指定されたカテゴリと難易度の4択問題を生成する (Gemini or OpenAI)。
    API接続失敗時はMOCK_QUESTIONSから問題を返す。
    """
    prompt = f"""
あなたはプログラミング学習を支援する先生です。

学習者の指定したカテゴリ: 「{category}」
難易度: 「{difficulty}」

これらに沿ったPythonの4択問題を1問作成し、以下のJSON形式のみで出力してください。Markdownのコードブロック（```json ... ```）は使用しないでください。

{{
  "title": "問題のタイトル（簡潔に）",
  "question": "問題の本文。コードを含む場合はMarkdownのコード表記を使用してください。",
  "options": [
    "選択肢1",
    "選択肢2",
    "選択肢3",
    "選択肢4"
  ],
  "answer_index": 正解の選択肢のインデックス番号（0から3の整数。例えば選択肢1が正解なら0）,
  "explanation": "なぜその選択肢が正解なのかの丁寧な解説（コードの説明を含める）"
}}
"""

    result = None
    if provider == "Gemini":
        api_key = os.getenv("GOOGLE_API_KEY") or DEFAULT_GEMINI_KEY
        if api_key:
            result = call_gemini_api(api_key, prompt)
    elif provider == "OpenAI":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            result = call_openai_api(api_key, prompt)

    if result:
        # JSON部分のクレンジング
        cleaned_result = result.strip()
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        elif cleaned_result.startswith("```"):
            cleaned_result = cleaned_result[3:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
        cleaned_result = cleaned_result.strip()

        try:
            parsed = json.loads(cleaned_result)
            # 必要なフィールドが揃っているか確認
            if all(k in parsed for k in ("title", "question", "options", "answer_index", "explanation")):
                # 型のチェックと補正
                if isinstance(parsed["options"], list) and len(parsed["options"]) >= 2:
                    parsed["answer_index"] = int(parsed["answer_index"])
                    return parsed
        except Exception as e:
            print(f"JSONパースエラー: {e}, 生のレスポンス: {result}")

    # フォールバック
    return get_mock_question(category, difficulty)

def get_mock_question(category, difficulty):
    """MOCK_QUESTIONSから該当する問題を安全に取得する"""
    cat_data = MOCK_QUESTIONS.get(category, MOCK_QUESTIONS["Python基礎"])
    diff_data = cat_data.get(difficulty, cat_data["初級"])
    return diff_data

MOCK_QUESTIONS = {
    "Python基礎": {
        "初級": {
            "title": "print関数の出力",
            "question": "次のコードを実行したときの出力結果として正しいものはどれですか？\\n\\n```python\\nprint('Hello', 'World', sep='-')\\n```",
            "options": ["Hello World", "HelloWorld", "Hello-World", "Hello\\nWorld"],
            "answer_index": 2,
            "explanation": "print関数で複数の値をカンマで区切って渡し、`sep='-'`を指定すると、それぞれの値の間にハイフンが入って出力されます。"
        },
        "中級": {
            "title": "文字列の結合と型変換",
            "question": "次のコードの出力結果として正しいものはどれですか？\\n\\n```python\\na = '10'\\nb = 5\\nprint(int(a) + b)\\n```",
            "options": ["105", "15", "エラーが発生する", "10"],
            "answer_index": 1,
            "explanation": "文字列 `'10'` を `int()` で数値の `10` に変換したあと、`5` を足しているため、結果は数値の `15` となります。"
        },
        "上級": {
            "title": "f-string の高度な書式設定",
            "question": "次のコードを実行したときの出力として正しいものはどれですか？\\n\\n```python\\nval = 12.3456\\nprint(f'{val:.2f}')\\n```",
            "options": ["12.35", "12.34", "12.3456", "12"],
            "answer_index": 0,
            "explanation": "`f'{val:.2f}'` は浮動小数点数を小数点以下2桁で四捨五入して表示する書式指定です。12.3456 の小数点第3位（5）が四捨五入され、12.35 となります。"
        }
    },
    "変数": {
        "初級": {
            "title": "変数の値の更新",
            "question": "次のコードを実行した後の変数 `x` の値はいくつですか？\\n\\n```python\\nx = 5\\nx = x + 3\\n```",
            "options": ["5", "3", "8", "15"],
            "answer_index": 2,
            "explanation": "`x = 5` で `x` に `5` が代入され、次に `x + 3`（つまり `5 + 3`）が計算されて `x` に再代入されるため、値は `8` になります。"
        },
        "中級": {
            "title": "複数変数の同時代入",
            "question": "次のコードを実行した後の変数 `a` と `b` の値はそれぞれどうなりますか？\\n\\n```python\\na, b = 1, 2\\na, b = b, a + b\\n```",
            "options": ["a=1, b=2", "a=2, b=3", "a=2, b=1", "a=3, b=2"],
            "answer_index": 1,
            "explanation": "Pythonでは `a, b = b, a + b` のように同時に値を代入できます。代入時の右辺の値は、更新前の `a`, `b` を基に評価されるため、`a` には `b` の値（2）が、`b` には `a + b`（1 + 2 = 3）が代入されます。"
        },
        "上級": {
            "title": "グローバル変数の書き換え",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nx = 10\\ndef modify():\\n    global x\\n    x = 20\\n\\nmodify()\\nprint(x)\\n```",
            "options": ["10", "20", "エラーが発生する", "None"],
            "answer_index": 1,
            "explanation": "関数内で `global x` と宣言することで、グローバルスコープにある変数 `x` を関数内から書き換えることができるようになります。"
        }
    },
    "条件分岐": {
        "初級": {
            "title": "if文の基本",
            "question": "次のコードを実行したときに出力されるメッセージはどれですか？\\n\\n```python\\nscore = 75\\nif score >= 80:\\n    print('合格')\\nelif score >= 60:\\n    print('追試')\\nelse:\\n    print('不合格')\\n```",
            "options": ["合格", "追試", "不合格", "何も出力されない"],
            "answer_index": 1,
            "explanation": "`score` の値は `75` です。最初の条件 `score >= 80` は偽になり、次の `elif score >= 60` が真になるため、「追試」が出力されます。"
        },
        "中級": {
            "title": "論理演算子の組み合わせ",
            "question": "次のコードを実行したときの出力はどれですか？\\n\\n```python\\na = True\\nb = False\\nc = True\\nif a and not b or c:\\n    print('A')\\nelse:\\n    print('B')\\n```",
            "options": ["A", "B", "エラー", "何も出力されない"],
            "answer_index": 0,
            "explanation": "`not b` は `True` となります。よって `a and not b` は `True and True` で `True` になります。その後、`or c` が評価されますが、すでに全体として `True` なので ifブロックの「A」が出力されます。"
        },
        "上級": {
            "title": "三項演算子（条件式）",
            "question": "次のコードと同等の動きをする条件分岐の書き方はどれですか？\\n\\n```python\\nresult = 'Pass' if score >= 60 else 'Fail'\\n```",
            "options": [
                "if score >= 60: result = 'Pass' else: result = 'Fail'",
                "result = score >= 60 ? 'Pass' : 'Fail'",
                "if score >= 60:\\n    result = 'Pass'\\nelse:\\n    result = 'Fail'",
                "score >= 60 and result = 'Pass' or result = 'Fail'"
            ],
            "answer_index": 2,
            "explanation": "`A if 条件 else B` は条件式（三項演算子）と呼ばれ、条件が真のときは `A`、偽のときは `B` を返します。これは標準的な if-else 文と同じ動きをします。"
        }
    },
    "繰り返し": {
        "初級": {
            "title": "range関数の動作",
            "question": "次のコードを実行したときに出力される数字の組み合わせはどれですか？\\n\\n```python\\nfor i in range(3):\\n    print(i, end=' ')\\n```",
            "options": ["1 2 3 ", "0 1 2 ", "0 1 2 3 ", "1 2 "],
            "answer_index": 1,
            "explanation": "`range(3)` は `0`, `1`, `2` の連番（0から始まり、3未満の整数）を生成します。よって「0 1 2 」が出力されます。"
        },
        "中級": {
            "title": "while文とbreak",
            "question": "次のコードを実行したとき、最後に出力される `count` の値はどれですか？\\n\\n```python\\ncount = 1\\nwhile count < 10:\\n    if count % 5 == 0:\\n        break\\n    count += 2\\nprint(count)\\n```",
            "options": ["5", "9", "11", "7"],
            "answer_index": 0,
            "explanation": "`count` は初期値 `1` から始まり、`3`, `5` と順に増えていきます。`count` が `5` になったとき、`count % 5 == 0` が真となり `break` でループを抜けるため、出力される値は `5` になります。"
        },
        "上級": {
            "title": "for-else文",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nfor i in range(3):\\n    if i == 4:\\n        break\\nelse:\\n    print('Finished')\\n```",
            "options": ["Finished", "何も出力されない", "iの値（0 1 2）とFinished", "エラーが発生する"],
            "answer_index": 0,
            "explanation": "Pythonの `for` ループには `else` ブロックを続けることができます。ループが `break` によって途中で終了しなかった場合に `else` 部分が実行されます。このコードでは `i` が `4` になることはなく `break` しないため、「Finished」が出力されます。"
        }
    },
    "関数": {
        "初級": {
            "title": "関数の戻り値",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\ndef add(a, b):\\n    return a + b\\n\\nresult = add(3, 4)\\nprint(result)\\n```",
            "options": ["7", "34", "3", "None"],
            "answer_index": 0,
            "explanation": "`add(3, 4)` を呼び出すと、引数 `a` に `3`、`b` に `4` が代入され、`return a + b` により `7` が返され、それが表示されます。"
        },
        "中級": {
            "title": "引数のデフォルト値",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\ndef greet(name, msg='Hello'):\\n    return f'{msg}, {name}!'\\n\\nprint(greet('Alice'))\\n```",
            "options": ["Alice, Hello!", "Hello, Alice!", "Hello, msg!", "エラーが発生する"],
            "answer_index": 1,
            "explanation": "引数 `msg` にはデフォルト値 `'Hello'` が設定されています。`greet('Alice')` のように第二引数を省略して呼び出した場合、デフォルト値が使われるため、出力は「Hello, Alice!」となります。"
        },
        "上級": {
            "title": "可変長引数 (*args)",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\ndef calc_sum(*args):\\n    return sum(args)\\n\\nprint(calc_sum(1, 2, 3, 4))\\n```",
            "options": ["10", "4", "[1, 2, 3, 4]", "エラーが発生する"],
            "answer_index": 0,
            "explanation": "引数の前に `*` をつける（`*args`）と、渡された複数の引数がタプルとしてまとめられます。`sum(args)` により `1 + 2 + 3 + 4` が計算され、`10` が返されます。"
        }
    },
    "リスト": {
        "初級": {
            "title": "リストの要素追加とインデックス",
            "question": "次のコードを実行したときに出力される値は何ですか？\\n\\n```python\\nfruits = ['apple', 'banana']\\nfruits.append('orange')\\nprint(fruits[2])\\n```",
            "options": ["apple", "banana", "orange", "エラーが発生する"],
            "answer_index": 2,
            "explanation": "`append('orange')` により、リストの末尾に `'orange'` が追加され、リストは `['apple', 'banana', 'orange']` になります。インデックスは `0` から始まるため、`fruits[2]` は追加された `'orange'` になります。"
        },
        "中級": {
            "title": "リストのスライス",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nnums = [10, 20, 30, 40, 50]\\nprint(nums[1:4])\\n```",
            "options": ["[20, 30, 40]", "[10, 20, 30]", "[20, 30, 40, 50]", "[30, 40]"],
            "answer_index": 0,
            "explanation": "スライス `[1:4]` はインデックス `1` から `4` の手前（インデックス `3`）までの要素を取り出します。よって、`nums[1]` (20), `nums[2]` (30), `nums[3]` (40) のリスト `[20, 30, 40]` が返されます。"
        },
        "上級": {
            "title": "リスト内包表記",
            "question": "次のコードと同じ結果を得られるリスト内包表記の記述はどれですか？\\n\\n```python\\nsquares = []\\nfor x in range(5):\\n    if x % 2 == 0:\\n        squares.append(x ** 2)\\n```",
            "options": [
                "squares = [x ** 2 for x in range(5)]",
                "squares = [x ** 2 for x in range(5) if x % 2 == 0]",
                "squares = [if x % 2 == 0: x ** 2 for x in range(5)]",
                "squares = [x ** 2 if x % 2 == 0 for x in range(5)]"
            ],
            "answer_index": 1,
            "explanation": "リスト内包表記で条件文（if）を伴う場合は、`[式 for 変数 in イテラブル if 条件]` のように記述します。"
        }
    },
    "辞書": {
        "初級": {
            "title": "辞書のキー値アクセス",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nuser = {'name': 'Taro', 'age': 20}\\nprint(user['name'])\\n```",
            "options": ["Taro", "name", "20", "エラーが発生する"],
            "answer_index": 0,
            "explanation": "辞書型から値を取り出すには `辞書[キー]` のように指定します。`user['name']` はキー `'name'` に対応する値 `'Taro'` を返します。"
        },
        "中級": {
            "title": "辞書のgetメソッド",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nuser = {'name': 'Taro'}\\nprint(user.get('age', '未設定'))\\n```",
            "options": ["None", "未設定", "エラーが発生する", "Taro"],
            "answer_index": 1,
            "explanation": "`get()` メソッドは、辞書に存在しないキーを指定した際にエラーにせず、第二引数に指定したデフォルト値を返します。辞書に `'age'` は登録されていないため、デフォルト値である `'未設定'` が出力されます。"
        },
        "上級": {
            "title": "辞書のループ処理 (items)",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nscores = {'Math': 90, 'Science': 80}\\nfor key, val in scores.items():\\n    if val < 85:\\n        print(key)\\n```",
            "options": ["Math", "Science", "80", "Math\\nScience"],
            "answer_index": 1,
            "explanation": "`scores.items()` は、辞書のキーと値をタプルペアとしてループで取り出すためのメソッドです。値が `85` 未満であるキーは `'Science'` （値 80）なので、出力は `'Science'` になります。"
        }
    },
    "クラス": {
        "初級": {
            "title": "クラスのインスタンス化",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nclass Dog:\\n    def __init__(self, name):\\n        self.name = name\\n\\nmy_dog = Dog('Pochi')\\nprint(my_dog.name)\\n```",
            "options": ["Dog", "Pochi", "name", "エラーが発生する"],
            "answer_index": 1,
            "explanation": "`Dog('Pochi')` を呼び出すと `__init__` コンストラクタが動き、インスタンス変数 `self.name` に `'Pochi'` が代入されます。`my_dog.name` でその変数にアクセスするため、出力は `'Pochi'` になります。"
        },
        "中級": {
            "title": "メソッドの定義と呼び出し",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nclass Calculator:\\n    def multiply(self, a, b):\\n        return a * b\\n\\ncalc = Calculator()\\nprint(calc.multiply(3, 4))\\n```",
            "options": ["7", "12", "multiply", "エラーが発生する"],
            "answer_index": 1,
            "explanation": "クラスメソッドを定義する際、第一引数にはインスタンス自身を指す `self` を渡します。実際に呼び出すとき（`calc.multiply(3, 4)`）は `self` を省略して引数を渡すため、`3 * 4` が計算されて `12` となります。"
        },
        "上級": {
            "title": "クラスの継承とsuper()",
            "question": "次のコードを実行したときの出力結果はどれですか？\\n\\n```python\\nclass Animal:\\n    def speak(self):\\n        return 'Some sound'\\n\\nclass Cat(Animal):\\n    def speak(self):\\n        return 'Meow'\\n\\nmy_cat = Cat()\\nprint(my_cat.speak())\\n```",
            "options": ["Some sound", "Meow", "Some sound\\nMeow", "エラーが発生する"],
            "answer_index": 1,
            "explanation": "子クラス（`Cat`）が親クラス（`Animal`）を継承し、親クラスと同じ名前のメソッド `speak` を定義すると「オーバーライド（上書き）」されます。したがって、`Cat` のインスタンスに対して `speak()` を呼び出すとオーバーライドされた `'Meow'` が返されます。"
        }
    }
}


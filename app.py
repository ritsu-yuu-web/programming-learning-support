import streamlit as st
import database
import ai

database.create_database()
stats = database.get_statistics()

#目標問題数の決定
goal = database.get_goal()

achievement_rate = min(
    stats["total_problems"] / goal["goal_problems"] * 100,
    100
)


remaining = max(
    goal["goal_problems"] - stats["total_problems"],
    0
)



st.set_page_config(
    page_title="プログラミング学習支援システム",
    page_icon="💻",
    layout="wide"
)

st.title("💻 プログラミング学習支援システム")


st.header("🏠 ホーム")

st.subheader("🎯 学習目標")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "目標問題数",
        f"{goal['goal_problems']}問"
    )

with col2:
    st.metric(
        "現在",
        f"{stats['total_problems']}問"
    )

with col3:
    st.metric(
        "残り",
        f"{remaining}問"
    )


st.subheader("📈 学習記録")

col1, col2 = st.columns(2)

with col1:
    st.metric(
    "達成率",
    f"{achievement_rate:.1f}%"
    )
    st.progress(achievement_rate / 100)

    if achievement_rate < 30:
        st.info("まずは学習を継続することを目標にしましょう！")

    elif achievement_rate < 70:
        st.success("順調です！この調子で学習を続けましょう！")

    else:
        st.balloons()
        st.success("目標達成まであと少しです！🎉")

    st.metric(
        "総学習時間",
        f"{stats['total_time']}分"
    )
with col2:
    st.metric("連続学習日数", "5日")
    st.metric(
        "総学習問題数",
        f"{stats['total_problems']}問"
    )
    
st.subheader("⚠️ 苦手分野")

weak_categories = database.get_weak_categories()

text = ""

for i, (category, accuracy) in enumerate(weak_categories[:3]):

    text += f"{i+1}位：{category}（正解率 {accuracy:.1f}%）\n"

st.warning(text)


st.subheader("🤖 おすすめ学習")

recommendations = {

    "Python基礎": {
        "message": "Pythonの基礎をもう一度確認しましょう！",
        "problems": [
            "① print関数を使って文字を表示する",
            "② input関数で入力を受け取る",
            "③ int型・float型・str型を使い分ける"
        ]
    },

    "変数": {
        "message": "変数とデータ型を復習しましょう！",
        "problems": [
            "① 変数へ値を代入する",
            "② 型変換（int・float・str）",
            "③ 変数を使った計算"
        ]
    },

    "条件分岐": {
        "message": "if文を使った条件分岐を練習しましょう！",
        "problems": [
            "① if文で条件分岐する",
            "② if-else文を書く",
            "③ if-elif-else文を書く"
        ]
    },

    "繰り返し": {
        "message": "繰り返し処理を練習しましょう！",
        "problems": [
            "① for文を使う",
            "② while文を使う",
            "③ range()を使った繰り返し"
        ]
    },

    "関数": {
        "message": "関数の理解を深めましょう！",
        "problems": [
            "① 引数を持つ関数を作る",
            "② 戻り値のある関数を作る",
            "③ 関数を組み合わせて使う"
        ]
    },

    "リスト": {
        "message": "リスト操作を復習しましょう！",
        "problems": [
            "① append()を使う",
            "② リストをfor文で繰り返す",
            "③ スライスを使う"
        ]
    },

    "辞書": {
        "message": "辞書型の使い方を確認しましょう！",
        "problems": [
            "① 辞書を作成する",
            "② get()メソッドを使う",
            "③ 辞書をfor文で繰り返す"
        ]
    },

    "クラス": {
        "message": "クラスの基礎を復習しましょう！",
        "problems": [
            "① クラスを定義する",
            "② __init__()を使う",
            "③ インスタンスを生成する"
        ]
    }

}

weak_categories = database.get_weak_categories()

weak_categories = database.get_weak_categories()

if len(weak_categories) > 0:

    category = weak_categories[0][0]

    st.info(f"あなたの苦手分野は「{category}」です。")

    st.success(recommendations[category]["message"])
    

    try:
        advice = ai.generate_advice(category)

    except Exception:
        advice = "現在AIアドバイスを取得できません。苦手分野を重点的に復習してみましょう。"

    st.subheader("🤖 AIアドバイス")

    st.info(advice)

    st.write("### 📚 おすすめ問題")

    for problem in recommendations[category]["problems"]:
        st.checkbox(problem)

else:
    st.success("まだ学習記録がありません。まずは問題を解いてみましょう！")


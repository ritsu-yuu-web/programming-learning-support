import streamlit as st
import database

st.title("📝 学習記録")

study_date = st.date_input("学習日")

study_time = st.number_input(
    "学習時間（分）",
    min_value=0
)

category = st.selectbox(
    "学習分野",
    [
        "Python基礎",
        "変数",
        "条件分岐",
        "繰り返し",
        "関数",
        "リスト",
        "辞書",
        "クラス"
    ]
)

problem_name = st.text_input("問題名")

result = st.radio(
    "結果",
    ["正解", "不正解"]
)

memo = st.text_area("メモ")

if st.button("保存"):

    database.save_log(
        study_date,
        study_time,
        category,
        problem_name,
        result,
        memo
    )

    st.success("学習記録を保存しました！")
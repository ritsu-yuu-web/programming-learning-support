import streamlit as st
import database
from datetime import date

st.set_page_config(page_title="学習記録", page_icon="📝", layout="wide")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("⚠️ ログインしていません。ホーム画面でログインを行ってください。")
    st.stop()

st.title("📝 学習記録")
st.write("今日取り組んだ課題の内容を記録しましょう。")

categories = [
    "Python基礎", "変数", "条件分岐", "繰り返し", 
    "関数", "リスト", "辞書", "クラス"
]

with st.form("log_form"):
    study_date = st.date_input("学習日", value=date.today())
    study_time = st.number_input("学習時間 (分)", min_value=1, max_value=480, value=30)
    category = st.selectbox("学習カテゴリ", categories)
    problem_name = st.text_input("問題名・課題名", placeholder="例: 変数を使った計算")
    result = st.radio("結果", ["○ (正解)", "× (不正解)"])
    memo = st.text_area("メモ・振り返り", placeholder="難しかった点や理解した点など")
    
    submitted = st.form_submit_button("記録を保存")
    if submitted:
        if not problem_name.strip():
            st.error("問題名を入力してください。")
        else:
            res_char = "○" if "○" in result else "×"
            database.save_log(st.session_state.user_id, study_date, study_time, category, problem_name, res_char, memo)
            st.success("学習記録を保存しました！")

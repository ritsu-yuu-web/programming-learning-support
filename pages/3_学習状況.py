import streamlit as st
import sqlite3
import pandas as pd
import os
import plotly.express as px


st.set_page_config(page_title="学習状況", page_icon="📈", layout="wide")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("⚠️ ログインしていません。ホーム画面でログインを行ってください。")
    st.stop()

st.title("📈 学習状況の可視化")
st.write("これまでの学習成果の可視化グラフです。")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "study.db")

def get_logs_df(user_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM study_logs WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df

try:
    df = get_logs_df(st.session_state.user_id)
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("カテゴリごとの学習時間")
            time_by_cat = (
                df.groupby("category")["study_time"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                time_by_cat,
                x="category",
                y="study_time",
                title="カテゴリごとの学習時間",
                labels={
                    "category": "カテゴリ",
                    "study_time": "学習時間（分）"
                }
            )

            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("結果（正解／不正解）の割合")
            result_counts = (
                df["result"]
                .value_counts()
                .reset_index()
            )
            
            result_counts.columns = ["result", "count"]
            
            fig = px.pie(
                result_counts,
                names="result",
                values="count",
                title="結果（正解／不正解）の割合",
                color="result",
                color_discrete_map={
                    "正解": "lightgreen",
                    "不正解": "lightcoral"
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("可視化するデータがまだありません。")
except Exception as e:
    st.info("学習データがまだありません。")

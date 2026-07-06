import streamlit as st
import database

st.title("🎯 目標設定")

goal = database.get_goal()

goal_problems = st.number_input(
    "目標問題数",
    min_value=1,
    value=goal["goal_problems"]
)

goal_time = st.number_input(
    "目標学習時間（分）",
    min_value=1,
    value=goal["goal_time"]
)

if st.button("保存"):

    database.save_goal(
        goal_problems,
        goal_time
    )

    st.success("目標を保存しました！")
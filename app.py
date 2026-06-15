import streamlit as st

st.title("プログラミング学習支援システム")

st.write("自主学習を支援するシステムです")

st.sidebar.title("メニュー")

page = st.sidebar.selectbox(
    "選択してください",
    ["ホーム", "学習記録", "学習状況", "AIフィードバック"]
)

st.header(page)

if page == "ホーム":
    st.write("ホーム画面")

elif page == "学習記録":
    st.write("学習記録画面")

elif page == "学習状況":
    st.write("学習状況画面")

elif page == "AIフィードバック":
    st.write("AIフィードバック画面")

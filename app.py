import streamlit as st

st.set_page_config(
    page_title="プログラミング学習支援システム",
    page_icon="💻",
    layout="wide"
)

st.title("💻 プログラミング学習支援システム")

st.sidebar.title("メニュー")

page = st.sidebar.selectbox(
    "選択してください",
    ["ホーム", "学習記録", "学習状況", "AIフィードバック"]
)

# ホーム画面
if page == "ホーム":

    st.header("🏠 ホーム")

    st.subheader("学習目標")
    st.info("Python基礎を習得する")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="今日の学習時間",
            value="45分"
        )

    with col2:
        st.metric(
            label="今週の学習時間",
            value="210分"
        )

    with col3:
        st.metric(
            label="連続学習日数",
            value="5日"
        )

    st.subheader("おすすめ学習")

    st.success(
        "関数の正答率が低いため、関数の基礎問題に取り組みましょう。"
    )

# 学習記録画面
elif page == "学習記録":
    st.header("📝 学習記録")

# 学習状況画面
elif page == "学習状況":
    st.header("📊 学習状況")

# AIフィードバック画面
elif page == "AIフィードバック":
    st.header("🤖 AIフィードバック")

import streamlit as st
import database
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 学習状況")

stats = database.get_statistics()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "総学習時間",
        f"{stats['total_time']}分"
    )

with col2:
    st.metric(
        "総問題数",
        stats["total_problems"]
    )

daily_data = database.get_daily_study_time()

df = pd.DataFrame(
    daily_data,
    columns=["日付", "学習時間"]
)

#学習時間の推移
st.subheader("📈 直近7日間の学習時間")

st.bar_chart(
    df,
    x="日付",
    y="学習時間"
)

#分野別達成率
st.subheader("📊 分野別達成率")

category = st.selectbox(
    "分野を選択",
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


result_stats = database.get_category_result_stats(category)

if len(result_stats) == 0:

    st.info("この分野の学習記録がありません")

else:

    labels = []
    sizes = []

    for result, count in result_stats:

        labels.append(result)
        sizes.append(count)

    fig, ax = plt.subplots()

    colors = []

    for label in labels:

        if label == "正解":
            colors.append("green")

        else:
            colors.append("red")

    ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%"
    )

    ax.set_title(f"{category} の達成率")

    st.pyplot(fig)


total = sum(sizes)

correct_count = 0

for result, count in result_stats:

    if result == "正解":
        correct_count = count

accuracy = round(correct_count / total * 100, 1)

st.metric(
    "達成率",
    f"{accuracy}%"
)

st.subheader("⚠️ 苦手分野")

weak_categories = database.get_weak_categories()

for i, (category, accuracy) in enumerate(weak_categories[:3]):

    st.warning(
        f"{i+1}位：{category}（正解率 {accuracy:.1f}%）"
    )
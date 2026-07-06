import streamlit as st
import database

st.title("📚 学習履歴")

logs = database.get_logs()

if len(logs) == 0:

    st.info("まだ学習記録がありません")

else:

    for log in logs:

        st.write(f"📅 日付：{log[0]}")
        st.write(f"📖 分野：{log[1]}")
        st.write(f"📝 問題名：{log[2]}")
        st.write(f"🎯 結果：{log[3]}")
        st.write(f"⏰ 学習時間：{log[4]}分")

        st.divider()
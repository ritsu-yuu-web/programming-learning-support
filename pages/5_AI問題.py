import streamlit as st
import ai
import database


st.title("🤖 AI問題")


if "question_number" not in st.session_state:
    st.session_state["question_number"] = 1

if "correct_count" not in st.session_state:
    st.session_state["correct_count"] = 0

if "test_finished" not in st.session_state:
    st.session_state["test_finished"] = False


if st.session_state["test_finished"]:

    st.title("🎉 テスト終了！")

    st.success(
        f"5問中 {st.session_state['correct_count']}問正解！"
    )

    rate = st.session_state["correct_count"] / 5 * 100

    st.metric("正答率", f"{rate:.0f}%")

    weak = database.get_weak_categories()

    if len(weak) > 0:
        category = weak[0][0]
    else:
        category = "Python基礎"

    try:
        feedback = ai.generate_feedback(
            st.session_state["correct_count"],
            5,
            category
        )

    except Exception:
        feedback = f"""
    現在AI講評を取得できませんでした。

    今回の正答率は {rate:.0f}% です。

    「{category}」を重点的に復習し、
    もう一度挑戦してみましょう！
    """


    st.subheader("🤖 AI講評")

    st.info(feedback)

    st.stop()


st.write(f"現在の正解数：{st.session_state['correct_count']}問")


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

if st.button("問題を生成"):

    try:
        question = ai.generate_question(category)

    except Exception:

        question = {
            "question": "Pythonで画面に文字を表示する関数は？",
            "choices": [
                "print()",
                "input()",
                "len()",
                "int()"
            ],
            "answer": "print()",
            "explanation": "print()は文字や変数を表示する関数です。"
        }

    st.session_state["question"] = question


if "question" in st.session_state:

    question = st.session_state["question"]

    st.subheader(f"📝 問題 {st.session_state['question_number']}/5")

    st.write(question["question"])


    answer = st.radio(
        "答えを選んでください",
        question["choices"]
    )


if st.button("回答する"):

    selected = question["choices"].index(answer)

    if selected == question["answer"]:
        
        database.save_ai_result(category, True)

        st.session_state["correct_count"] += 1

        st.success("🎉 正解です！")

    else:
        
        database.save_ai_result(category, False)

        st.error("❌ 不正解です。")

    st.info("💡 解説")

    st.write(question["explanation"])


if st.button("次の問題"):

    if st.session_state["question_number"] < 5:

        st.session_state["question_number"] += 1

        del st.session_state["question"]

        st.rerun()

    else:

        st.session_state["test_finished"] = True

        st.rerun()
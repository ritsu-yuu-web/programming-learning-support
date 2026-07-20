import streamlit as st
import database
import ai
from datetime import date

st.set_page_config(page_title="AI学習", page_icon="🤖", layout="wide")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("⚠️ ログインしていません。ホーム画面でログインを行ってください。")
    st.stop()

st.title("🤖 AI学習（インタラクティブ問題集）")
st.write("AIがあなたのレベルに合わせたオリジナルの問題を出題します。ここで実際に解答して学習しましょう！")

# セッション状態の初期化
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "saved_to_db" not in st.session_state:
    st.session_state.saved_to_db = False
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
    
if "question_list" not in st.session_state:
    st.session_state.question_list = None
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0

categories = [
    "Python基礎", "変数", "条件分岐", "繰り返し", 
    "関数", "リスト", "辞書", "クラス"
]
difficulties = ["初級", "中級", "上級"]

# 問題生成フォーム
if st.session_state.current_question is None:
    st.subheader("📋 問題の設定")
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("学習したいカテゴリ", categories)
    with col2:
        difficulty = st.selectbox("難易度", difficulties)
        
    generate_btn = st.button("🚀 問題を生成する", use_container_width=True)
    if generate_btn:
        with st.spinner("AIが問題を生成しています..."):
            question_list = ai.generate_questions(category, difficulty)

            if not question_list:
                st.error("問題生成に失敗しました。もう一度試してください。")
                st.stop()
                
            st.session_state.question_list = question_list
            st.session_state.current_index = 0
            st.session_state.correct_count = 0

            st.session_state.current_question = question_list[0]
            
            st.session_state.category = category
            st.session_state.difficulty = difficulty
            st.session_state.submitted = False
            st.session_state.saved_to_db = False
            st.session_state.selected_option = None
            st.rerun()

# 出題中
else:
    question_data = st.session_state.current_question
    category = st.session_state.category
    difficulty = st.session_state.difficulty
    
    st.info(f"📚 カテゴリ: {category}  |  📶 難易度: {difficulty}")
    
    st.subheader(
    f"問題 {st.session_state.current_index + 1} / 5"
    )

    st.markdown(f"### {question_data['title']}")
    st.markdown(question_data["question"])
    
    st.write("---")
    
    # 選択肢
    if not st.session_state.submitted:
        selected = st.radio(
            "正しいと思う選択肢を選んでください：",
            question_data["options"],
            index=None,
            key="radio_options"
        )
        st.session_state.selected_option = selected
        
        submit_btn = st.button("回答を送信", use_container_width=True)
        if submit_btn:
            if selected is None:
                st.warning("選択肢を選んでから送信してください。")
            else:
                st.session_state.submitted = True
                selected_idx = question_data["options"].index(selected)
                st.session_state.is_correct = (
                    selected_idx == question_data["answer_index"])
                if st.session_state.is_correct:
                    st.session_state.correct_count += 1
                st.rerun()
    else:
        # 回答送信後の表示
        selected = st.session_state.selected_option
        selected_idx = question_data["options"].index(selected)
        correct_idx = question_data["answer_index"]
        correct_option = question_data["options"][correct_idx]
        
        st.write("あなたの回答:", selected)
        
        if st.session_state.is_correct:
            st.balloons()
            st.success(f"🎉 正解です！ 正解: {correct_option}")
        else:
            st.error(f"❌ 残念！不正解です。 正解: {correct_option}")
            
        st.subheader("💡 AIによる解説")
        st.info(question_data["explanation"])
        
        st.write("---")
        
        # 学習結果のデータベース保存
        if not st.session_state.saved_to_db:
            save_btn = st.button("💾 この結果を学習記録（データベース）に保存する", use_container_width=True)
            if save_btn:
                res_char = "○" if st.session_state.is_correct else "×"
                memo_text = f"AI学習機能で出題された問題に挑戦しました。\n[問題]: {question_data['title']}\n[解説]: {question_data['explanation']}"
                # デフォルトの学習時間として5分を記録
                database.save_log(
                    user_id=st.session_state.user_id,
                    study_date=date.today(),
                    study_time=5,
                    category=category,
                    problem_name=f"[AI学習] {question_data['title']}",
                    result=res_char,
                    memo=memo_text
                )
                st.session_state.saved_to_db = True
                st.success("結果を学習履歴に保存しました！")
                st.rerun()
        else:
            st.success("✅ 学習結果は保存済みです。")
            
        next_btn = st.button("🔄 次の問題を解く", use_container_width=True)

        
        if next_btn:
         # 次の問題番号へ
            st.session_state.current_index += 1
        
            # まだ問題が残っている場合
            if st.session_state.current_index < len(st.session_state.question_list):
        
                st.session_state.current_question = \
                    st.session_state.question_list[
                        st.session_state.current_index
                    ]
        
                st.session_state.submitted = False
                st.session_state.saved_to_db = False
                st.session_state.selected_option = None
                
                if "radio_options" in st.session_state:
                    del st.session_state["radio_options"]
        
                st.rerun()
        
            # 5問終わった場合
            else:
        
                st.success(
                    f"🎉 5問終了！ {st.session_state.correct_count} / 5問正解"
                )
                
                feedback = ai.generate_feedback(
                    st.session_state.correct_count,
                    5,
                    category
                )
            
                st.subheader("🤖 AI講評")
                st.info(feedback)

                if st.button("もう一度挑戦する"):
                    st.session_state.current_question = None
                    st.session_state.question_list = None
                    st.session_state.current_index = 0
                    st.session_state.correct_count = 0
                    st.session_state.submitted = False
                    st.session_state.saved_to_db = False
                    st.session_state.selected_option = None
            
                    st.rerun()
                    
                st.stop()

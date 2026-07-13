import streamlit as st
import database
import ai

# ページ設定は一番最初に実行する必要がある
st.set_page_config(
    page_title="プログラミング学習支援システム",
    page_icon="💻",
    layout="wide"
)

database.create_database()

# ログイン状態のセッション初期化
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# 未ログイン時のログイン画面表示
if st.session_state.user_id is None:
    st.title("🔑 ログイン / 新規登録")
    st.write("プログラミング学習支援システムをご利用いただくには、ログインまたは新規登録が必要です。")
    
    tab1, tab2 = st.tabs(["ログイン", "新規ユーザー登録"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("ユーザー名")
            password = st.password_input("パスワード")
            submit = st.form_submit_button("ログイン", use_container_width=True)
            
            if submit:
                if not username.strip() or not password:
                    st.warning("ユーザー名とパスワードを入力してください。")
                else:
                    user_id = database.login_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("ログインに成功しました！")
                        st.rerun()
                    else:
                        st.error("ユーザー名またはパスワードが正しくありません。")
                        
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("希望ユーザー名")
            new_password = st.password_input("パスワード")
            confirm_password = st.password_input("パスワード（確認）")
            register = st.form_submit_button("アカウントを作成する", use_container_width=True)
            
            if register:
                if not new_username.strip() or not new_password:
                    st.warning("すべての項目を入力してください。")
                elif new_password != confirm_password:
                    st.error("パスワードが一致しません。")
                else:
                    success, res = database.register_user(new_username, new_password)
                    if success:
                        st.session_state.user_id = res
                        st.session_state.username = new_username
                        st.success("アカウントが作成され、自動ログインしました！")
                        st.rerun()
                    else:
                        st.error(res)
    st.stop()

# --- 以降、ログイン済みのメイン画面 ---

# サイドバーにログアウトボタンを追加
st.sidebar.write(f"👤 ログインユーザー: **{st.session_state.username}**")
if st.sidebar.button("ログアウト", use_container_width=True):
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()

# ユーザー別のデータ取得
stats = database.get_statistics(st.session_state.user_id)
goal = database.get_goal(st.session_state.user_id)

achievement_rate = min(
    stats["total_problems"] / goal["goal_problems"] * 100,
    100
) if goal["goal_problems"] > 0 else 0

remaining = max(
    goal["goal_problems"] - stats["total_problems"],
    0
)

st.title("💻 プログラミング学習支援システム")

st.header("🏠 ホーム")

st.subheader("🎯 学習目標")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "目標問題数",
        f"{goal['goal_problems']}問"
    )

with col2:
    st.metric(
        "現在",
        f"{stats['total_problems']}問"
    )

with col3:
    st.metric(
        "残り",
        f"{remaining}問"
    )

st.subheader("📈 学習記録")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "達成率",
        f"{achievement_rate:.1f}%"
    )
    st.progress(achievement_rate / 100)

    if achievement_rate < 30:
        st.info("まずは学習を継続することを目標にしましょう！")
    elif achievement_rate < 70:
        st.success("順調です！この調子で学習を続けましょう！")
    else:
        st.balloons()
        st.success("目標達成まであと少しです！🎉")

    st.metric(
        "総学習時間",
        f"{stats['total_time']}分"
    )
with col2:
    st.metric("連続学習日数", "5日")
    st.metric(
        "総学習問題数",
        f"{stats['total_problems']}問"
    )
    
st.subheader("⚠️ 苦手分野")

weak_categories = database.get_weak_categories(st.session_state.user_id)

text = ""

for i, (category, accuracy) in enumerate(weak_categories[:3]):
    text += f"{i+1}位：{category}（正解率 {accuracy:.1f}%）\n"

if text:
    st.warning(text)
else:
    st.info("まだ苦手分野データがありません。")

st.subheader("🤖 おすすめ学習")

recommendations = {
    "Python基礎": {
        "message": "Pythonの基礎をもう一度確認しましょう！",
        "problems": [
            "① print関数を使って文字を表示する",
            "② input関数で入力を受け取る",
            "③ int型・float型・str型を使い分ける"
        ]
    },
    "変数": {
        "message": "変数とデータ型を復習しましょう！",
        "problems": [
            "① 変数へ値を代入する",
            "② 型変換（int・float・str）",
            "③ 変数を使った計算"
        ]
    },
    "条件分岐": {
        "message": "if文を使った条件分岐を練習しましょう！",
        "problems": [
            "① if文で条件分岐する",
            "② if-else文を書く",
            "③ if-elif-else文を書く"
        ]
    },
    "繰り返し": {
        "message": "繰り返し処理を練習しましょう！",
        "problems": [
            "① for文を使う",
            "② while文を使う",
            "③ range()を使った繰り返し"
        ]
    },
    "関数": {
        "message": "関数の理解を深めましょう！",
        "problems": [
            "① 引数を持つ関数を作る",
            "② 戻り値のある関数を作る",
            "③ 関数を組み合わせて使う"
        ]
    },
    "リスト": {
        "message": "リスト操作を復習しましょう！",
        "problems": [
            "① append()を使う",
            "② リストをfor文で繰り返す",
            "③ スライスを使う"
        ]
    },
    "辞書": {
        "message": "辞書型の使い方を確認しましょう！",
        "problems": [
            "① 辞書を作成する",
            "② get()メソッドを使う",
            "③ 辞書をfor文で繰り返す"
        ]
    },
    "クラス": {
        "message": "クラスの基礎を復習しましょう！",
        "problems": [
            "① クラスを定義する",
            "② __init__()を使う",
            "③ インスタンスを生成する"
        ]
    }
}

if len(weak_categories) > 0:
    category = weak_categories[0][0]

    st.info(f"あなたの苦手分野は「{category}」です。")
    st.success(recommendations[category]["message"])
    advice = ai.generate_advice(category)
    st.subheader("🤖 AIアドバイス")
    st.info(advice)

    st.write("### 📚 おすすめ問題")
    for problem in recommendations[category]["problems"]:
        st.checkbox(problem)
else:
    st.success("まだ学習記録がありません。まずは問題を解いてみましょう！")



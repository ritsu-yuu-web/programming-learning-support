import sqlite3
import hashlib

def hash_password(password):
    """パスワードをSHA-256でハッシュ化する"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    # ユーザーテーブルの作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 学習ログテーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        study_date TEXT,
        study_time INTEGER,
        category TEXT,
        problem_name TEXT,
        result TEXT,
        memo TEXT
    )
    """)

    # 目標設定テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        goal_problems INTEGER,
        goal_time INTEGER
    )
    """)

    # 既存データベース向けのマイグレーション処理 (user_id カラム追加)
    cursor.execute("PRAGMA table_info(study_logs)")
    columns = [info[1] for info in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE study_logs ADD COLUMN user_id INTEGER")

    cursor.execute("PRAGMA table_info(goals)")
    columns = [info[1] for info in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE goals ADD COLUMN user_id INTEGER")

    conn.commit()
    conn.close()

def register_user(username, password):
    """新規ユーザーを登録する。登録完了時にデフォルトの学習目標も作成する。"""
    try:
        conn = sqlite3.connect("study.db")
        cursor = conn.cursor()
        pw_hash = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        user_id = cursor.lastrowid
        
        # 新規ユーザー用の初期目標を設定 (10問、300分)
        cursor.execute("INSERT OR IGNORE INTO goals (user_id, goal_problems, goal_time) VALUES (?, ?, ?)", (user_id, 10, 300))
        
        conn.commit()
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "このユーザー名は既に使われています。"
    except Exception as e:
        conn.close()
        return False, str(e)

def login_user(username, password):
    """ユーザー名とパスワードを検証し、成功した場合は user_id を返す"""
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()
    pw_hash = hash_password(password)
    cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def save_log(user_id, study_date, study_time, category, problem_name, result, memo):
    """学習ログを特定のユーザーIDに関連づけて保存する"""
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO study_logs(
        user_id,
        study_date,
        study_time,
        category,
        problem_name,
        result,
        memo
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        user_id,
        str(study_date),
        study_time,
        category,
        problem_name,
        result,
        memo
    ))

    conn.commit()
    conn.close()

def get_statistics(user_id):
    """特定のユーザーIDの学習ログから合計問題数と総学習時間を取得する"""
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(study_time) FROM study_logs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    total_problems = row[0] if row[0] is not None else 0
    total_time = row[1] if row[1] is not None else 0
    return {
        "total_problems": total_problems,
        "total_time": total_time
    }

def get_goal(user_id):
    """特定のユーザーIDに設定された目標（目標問題数など）を取得する"""
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()
    cursor.execute("SELECT goal_problems, goal_time FROM goals WHERE user_id = ? LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "goal_problems": row[0],
            "goal_time": row[1]
        }
    return {
        "goal_problems": 10,
        "goal_time": 300
    }

def get_weak_categories(user_id):
    """特定のユーザーIDのカテゴリごとに正解率を計算し、低い（苦手な）順にソートして返す"""
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT category, 
           COUNT(*) as total,
           SUM(CASE WHEN result = '○' THEN 1 ELSE 0 END) as correct
    FROM study_logs
    WHERE user_id = ?
    GROUP BY category
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    weak_list = []
    for row in rows:
        category = row[0]
        total = row[1]
        correct = row[2]
        accuracy = (correct / total * 100) if total > 0 else 0
        weak_list.append((category, accuracy))
        
    # 正解率の低い順（苦手な順）にソート
    weak_list.sort(key=lambda x: x[1])
    return weak_list

def update_goal(user_id, goal_problems, goal_time):
    """特定のユーザーIDの目標設定（目標問題数と目標学習時間）を更新または挿入する"""
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO goals (user_id, goal_problems, goal_time)
    VALUES (?, ?, ?)
    """, (user_id, goal_problems, goal_time))
    conn.commit()
    conn.close()

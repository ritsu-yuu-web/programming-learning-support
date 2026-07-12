import sqlite3

from datetime import datetime

def create_database():
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_date TEXT,
        study_time INTEGER,
        category TEXT,
        problem_name TEXT,
        result TEXT,
        memo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals(
        id INTEGER PRIMARY KEY,
        goal_problems INTEGER,
        goal_time INTEGER
    )
    """)

    conn.commit()
    conn.close()


def save_log(
    study_date,
    study_time,
    category,
    problem_name,
    result,
    memo
):
    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO study_logs(
        study_date,
        study_time,
        category,
        problem_name,
        result,
        memo
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        str(study_date),
        study_time,
        category,
        problem_name,
        result,
        memo
    ))

    conn.commit()
    conn.close()


TEST_VARIABLE = "hello"

def get_logs():

    conn = sqlite3.connect("study.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        study_date,
        category,
        problem_name,
        result,
        study_time
    FROM study_logs
    ORDER BY id DESC
    """)

    logs = cursor.fetchall()

    conn.close()

    return logs

def get_statistics():

    conn = sqlite3.connect("study.db")

    cursor = conn.cursor()

    # 総学習時間
    cursor.execute("""
    SELECT SUM(study_time)
    FROM study_logs
    """)

    total_time = cursor.fetchone()[0]

    # 総問題数
    cursor.execute("""
    SELECT COUNT(*)
    FROM study_logs
    """)

    total_problems = cursor.fetchone()[0]

    conn.close()

    return {
        "total_time": total_time if total_time else 0,
        "total_problems": total_problems
    }

#学習時間の推移
def get_daily_study_time():

    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        study_date,
        SUM(study_time)
    FROM study_logs
    GROUP BY study_date
    ORDER BY study_date DESC
    LIMIT 7
    """)

    data = cursor.fetchall()

    conn.close()

    return data[::-1]

#分野別達成率
def get_category_result_stats(category):

    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        result,
        COUNT(*)
    FROM study_logs
    WHERE category = ?
    GROUP BY result
    """, (category,))

    data = cursor.fetchall()

    conn.close()

    return data


#苦手分野を計算するための関数
def get_weak_categories():

    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        category,
        SUM(CASE WHEN result='正解' THEN 1 ELSE 0 END) as correct,
        COUNT(*) as total
    FROM study_logs
    GROUP BY category
    """)

    data = cursor.fetchall()

    conn.close()

    result_list = []

    for category, correct, total in data:

        accuracy = (correct / total) * 100

        result_list.append(
            (category, accuracy)
        )

    result_list.sort(
        key=lambda x: x[1]
    )

    return result_list


#保存関数
def save_goal(goal_problems, goal_time):

    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM goals
    """)

    cursor.execute("""
    INSERT INTO goals(
        goal_problems,
        goal_time
    )
    VALUES (?, ?)
    """,
    (
        goal_problems,
        goal_time
    ))

    conn.commit()
    conn.close()


#取得関数
def get_goal():

    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        goal_problems,
        goal_time
    FROM goals
    LIMIT 1
    """)

    goal = cursor.fetchone()

    conn.close()

    if goal is None:

        return {
            "goal_problems":100,
            "goal_time":1000
        }

    return {
        "goal_problems":goal[0],
        "goal_time":goal[1]
    }


#AI問題解答記録
def save_ai_result(category, is_correct):

    conn = sqlite3.connect("study.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO study_logs
        (study_date, study_time, category, problem_name, result, memo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d"),
        0,
        category,
        "AI生成問題",
        "正解" if is_correct else "不正解",
        "Gemini"
    ))

    conn.commit()
    conn.close()
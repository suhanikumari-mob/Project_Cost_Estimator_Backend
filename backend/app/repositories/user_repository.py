import sqlite3
import bcrypt

DB_PATH = "project.db"

def ensure_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER,
            email TEXT,
            thread_id INTEGER,
            project_name TEXT,
            response_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES Users(userid)
        )
    """)
    
    conn.commit()
    conn.close()

ensure_tables()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def register_user(name: str, email: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        hashed = hash_password(password)
        cur.execute("""
            INSERT INTO Users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, hashed))
        conn.commit()
        return {"success": True, "message": "User registered successfully"}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Email already exists"}
    finally:
        conn.close()


def check_emailpass(email: str, password: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT userid, name, email, password FROM Users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()

    if not user:
        return {"success": False}
    if not verify_password(password, user[3]):
        return {"success": False}

    return {"success": True, "userid": user[0], "name": user[1], "email": user[2]}


def save_project(userid: int, email: str, thread_id: int, project_name: str, response_json: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Projects (userid, email, thread_id, project_name, response_json)
            VALUES (?, ?, ?, ?, ?)
        """, (userid, email, thread_id, project_name, response_json))
        conn.commit()
        return {"success": True, "message": "Project saved successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def get_next_threadid(userid: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT MAX(CAST(thread_id AS INTEGER)) FROM Projects WHERE userid = ?
        """, (userid,))
        result = cur.fetchone()[0]
        return 1 if result is None else int(result) + 1
    except Exception:
        return 1
    finally:
        conn.close()


def get_threadids(userid: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT thread_id, project_name, timestamp
            FROM Projects
            WHERE userid = ?
            ORDER BY timestamp DESC
        """, (userid,))
        rows = cur.fetchall()
        return [
            {"thread_id": row[0], "project_name": row[1], "timestamp": row[2]}
            for row in rows
        ]
    except Exception:
        return []
    finally:
        conn.close()


def get_project_response(userid: int, thread_id: int) -> str | None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT response_json FROM Projects
            WHERE userid = ? AND thread_id = ?
        """, (userid, thread_id))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

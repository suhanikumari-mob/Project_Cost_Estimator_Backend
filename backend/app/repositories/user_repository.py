from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from pymongo import DESCENDING
import bcrypt
from app.core.config import settings
from datetime import datetime



client = AsyncIOMotorClient(settings.DB_PATH)
db = client[settings.DB_NAME]

users_collection = db["Users"]
projects_collection = db["Projects"]


async def ensure_tables():
    await users_collection.create_index("email", unique=True)
    await projects_collection.create_index([("userid", 1), ("thread_id", 1)])


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


async def register_user(name: str, email: str, password: str):
    try:
        last = await users_collection.find_one(sort=[("userid", DESCENDING)], projection={"userid": 1})
        next_userid = 1 if last is None else last["userid"] + 1

        await users_collection.insert_one({
            "userid": next_userid,
            "name": name,
            "email": email,
            "password": hash_password(password),
        })
        return {"success": True, "message": "User registered successfully"}
    except DuplicateKeyError:
        return {"success": False, "message": "Email already exists"}


async def check_emailpass(email: str, password: str) -> dict:
    user = await users_collection.find_one({"email": email})
    if not user:
        return {"success": False}
    if not verify_password(password, user["password"]):
        return {"success": False}
    return {
        "success": True,
        "userid": user["userid"],
        "name": user["name"],
        "email": user["email"],
    }


async def save_project(userid: int, email: str, thread_id: int, project_name: str, response_json: str):
    try:
        await projects_collection.insert_one({
            "userid": userid,
            "email": email,
            "thread_id": thread_id,
            "project_name": project_name,
            "response_json": response_json,
            "timestamp": datetime.utcnow(),
        })
        return {"success": True, "message": "Project saved successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


async def get_next_threadid(userid: int) -> int:
    doc = await projects_collection.find_one(
        {"userid": userid},
        sort=[("thread_id", DESCENDING)],
        projection={"thread_id": 1},
    )
    return 1 if doc is None else int(doc["thread_id"]) + 1


async def get_threadids(userid: int):
    cursor = projects_collection.find(
        {"userid": userid},
        projection={"thread_id": 1, "project_name": 1, "timestamp": 1, "_id": 0},
        sort=[("timestamp", DESCENDING)],
    )
    return [
        {"thread_id": row["thread_id"], "project_name": row["project_name"], "timestamp": row["timestamp"]}
        async for row in cursor
    ]


async def get_project_response(userid: int, thread_id: int) -> str | None:
    doc = await projects_collection.find_one(
        {"userid": userid, "thread_id": thread_id},
        projection={"response_json": 1, "_id": 0},
    )
    return doc["response_json"] if doc else None

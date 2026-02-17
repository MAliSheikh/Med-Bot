from typing import List, Optional
from bson import ObjectId
from db.conn import database


async def create_report(doc: dict) -> ObjectId:
    """Insert a report document and return the inserted id."""
    res = await database["reports"].insert_one(doc)
    return res.inserted_id


async def get_reports_by_user(user_id: str, limit: int = 100) -> List[dict]:
    """Return a list of reports for a given user id."""
    cursor = database["reports"].find({"user_id": user_id})
    reports = await cursor.to_list(length=limit)
    for report in reports:
        report["_id"] = str(report["_id"])
    return reports


async def get_report_by_id(report_id: str, user_id: str) -> Optional[dict]:
    """Return a single report by its id and owner user id."""
    if not ObjectId.is_valid(report_id):
        return None
    report = await database["reports"].find_one({"_id": ObjectId(report_id), "user_id": user_id})
    if report:
        report["_id"] = str(report["_id"])
    return report


async def delete_report_by_id(report_id: str, user_id: str) -> int:
    """Delete a report and return the deleted count (0 or 1)."""
    if not ObjectId.is_valid(report_id):
        return 0
    res = await database["reports"].delete_one({"_id": ObjectId(report_id), "user_id": user_id})
    return int(res.deleted_count)

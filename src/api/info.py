import sqlalchemy
import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import auth

from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)

class Timestamp(BaseModel):
    year: int
    month: str
    day: int # was str before
    hour: int

@router.post("/current_time")
def post_time(timestamp: Timestamp):
    """
    Share current time.
    """

    # with db.engine.begin() as connection:
    #     try:
    #         connection.execute(
    #             sqlalchemy.text(
    #                 "INSERT INTO ticks (day, hour) VALUES (:day, :hour)"
    #             ),

    #             [{
    #                 "day": timestamp.day,
    #                 "hour": timestamp.hour
    #             }]

    #         )
    #     except IntegrityError as e:
    #         return "OK"

    return "OK"


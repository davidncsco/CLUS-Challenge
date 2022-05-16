
from typing import Optional
from pydantic import BaseModel
    
class DemoQuestion(BaseModel):
    _id: str
    choices: list
    answer: list
    weight: Optional[int]
    filename: str

class User(BaseModel):
    email: str
    first: str
    last: str
    start: Optional[int]
    timetaken: Optional[int] = 0

class Car(BaseModel):
    _id: str
    number: int
    ip: str
    color: str
    speed: int = 1000
    position: int = 0
    start: Optional[int]
    userid: Optional[str]
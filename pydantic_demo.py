
from datetime import datetime
from pydantic import BaseModel,Field,ValidationError
from typing import List

class User(BaseModel):
    id: int
    name: str
    email: str 
    age: int = Field(ge=0, le=100)
    created_at: datetime | None
    department: List[str] | None
data1 = {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 50,
    "created_at": datetime.now(),
    "department": ["Engineering", "Research"]
}

try:
    user1 = User(**data1)
    print(user1.id,user1.name,user1.email,user1.created_at,user1.department)
    print(user1.model_dump())  #转换字典
except ValidationError as e:
    print(f"Error occurred: {e.errors()}")

from fastapi import FastAPI, Depends,Header,HTTPException

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons

async def user_common(q: str | None = None, skip: int = 0, limit: int = 100, username: str = "johndoe"):
    return {"q": q, "skip": skip, "limit": limit, "username": username}

@app.get("/users/{username}/")
async def read_user(user_commons: dict = Depends(user_common)):
    return user_commons

async def verify_token(x_token: str = Header(default=None)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    return {"user":"hyw"}

@app.get("/profile")
async def read_profile(token: dict = Depends(verify_token)):
    return {"资料": token["user"]}
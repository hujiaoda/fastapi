from fastapi import FastAPI, Query
from Routers.article import router as article_router
from Routers.users import router as users_router

app = FastAPI()
app.include_router(article_router)
app.include_router(users_router)


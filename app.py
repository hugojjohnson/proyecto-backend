from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from mongodb.database import init_db
import uvicorn

from book.routes import router as BookRouter
from auth.routes import router as AuthRouter
from auth.routes import verify_token
from main.routes import router as MainRouter

from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(AuthRouter, tags=["Auth"], prefix="/auth")
app.include_router(BookRouter, tags=["Books"], prefix="/books", dependencies=[Depends(verify_token)])
app.include_router(MainRouter, tags=["Main"], prefix="/main", dependencies=[Depends(verify_token)])


@app.on_event("startup")
async def start_db():
    await init_db()


@app.get("/", tags=["Root"])
async def index() -> dict:
    return {"message": "Welcome to your books app!"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3001, reload=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import llm

app = FastAPI()

# CORS 설정 (React에서 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우트 등록
app.include_router(llm.router, prefix="/api/llm")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (React에서의 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 라우트
@app.get("/")
def read_root():
    return {"message": "FastAPI 백엔드가 정상적으로 작동합니다!"}

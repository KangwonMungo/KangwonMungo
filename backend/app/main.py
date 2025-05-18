from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (React에서의 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용 (GET, POST, OPTIONS 등)
    allow_headers=["*"],  # 모든 요청 헤더 허용
)

# 기본 라우트
@app.get("/")
def read_root():
    return {"message": "FastAPI 백엔드가 정상적으로 작동합니다!"}


@app.post("/api/recommend")
async def recommend(request: Request):
    body = await request.json()
    question = body.get("question", "")
    
    # 여기서 실제 추천 로직 수행
    return {
        "response": f"'{question}'에 대해 이런 책을 추천합니다: \n1. 1984\n2. 동물농장\n3. 멋진 신세계"
    }
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import sys

from dotenv import load_dotenv
from google.generativeai import configure
import google.generativeai as genai
# Google Generative AI API 설정 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../rag')))

from service.conversation import *
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model_name = "gemini-2.0-flash"
client = genai.Client(api_key=api_key)


genai.configure(api_key=api_key)
conversation_history = {
        "keywords": [],
        "mood": [],
        "genre": [],
        "theme": [],
        "include_titles": [],
        "search_trigger": False,
        "generated_response": []
    }

app = FastAPI()

# CORS 설정 (React에서의 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용 (GET, POST, OPTIONS 등)
    allow_headers=["*"],  # 모든 요청 헤더 허용
)



class Book(BaseModel):
    title: str
    author: str
    keyword: List[str]
    isbn: str
    genre: str
    image_url: str
    introduction: str

# 임시 저장소
favorites: List[Book] = []

# 기본 라우트
@app.get("/")
def read_root():
    return {"message": "FastAPI 백엔드가 정상적으로 작동합니다!"}


@app.post("/api/recommend")
async def recommend(request: Request):
    body = await request.json()
    question = body.get("question", "")
    
    
    answer = query_to_answer(question)
    
    
    
    
    
    
    
    # 여기서 실제 추천 로직 수행
    return {
        "response": f"'{question}'에 대해 이런 책을 추천합니다: \n1. 1984\n2. 동물농장\n3. 멋진 신세계"
    }

# 관심 도서 추가
@app.post("/api/favorites")
def add_favorite(book: Book):
    if book not in favorites:
        favorites.append(book)
    return {"favorites": favorites}

# 관심 도서 조회
@app.get("/api/favorites")
def get_favorites():
    return {"favorites": favorites}

# 관심 도서 삭제
@app.delete("/api/favorites")
def remove_favorite(book: Book):
    if book in favorites:
        favorites.remove(book)
    return {"favorites": favorites}


def query_to_answer(query: str) -> str:
    book_preference_info = get_keywords_from_llm(query, conversation_history, model_name) 

    # 누적되는 필드
    for key in ["keywords", "mood", "genre", "theme", "include_titles"]:
        if key in book_preference_info:
            conversation_history[key] = list(set(conversation_history[key]) | set(book_preference_info[key]))
        
    # 그대로 덮어 쓸 필드
    for key in ["search_trigger", "generated_response"]:
        if key in book_preference_info:
            conversation_history[key] = book_preference_info[key]


    if conversation_history["search_trigger"]:
            search_query = generated_search_query(conversation_history, model_name)
            #Rag에서 검색된 결과를 가져오는 함수 호출
    else:
        return 
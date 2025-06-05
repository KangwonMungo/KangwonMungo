from fastapi import FastAPI,Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

from dotenv import load_dotenv
import google.generativeai as genai
from rag.conversation import get_keywords_from_llm, generated_search_query, reset_conversation_history, get_recommendation
from rag import vector_store
from rag.chunking import chunk_file_by_line


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model_name = "gemini-2.0-flash"

genai.configure(api_key=api_key)
conversation_history = reset_conversation_history()

PATH = "aladin_bestseller.json"
NUM = 5  # 추천할 도서의 개수

# chunking
all_chunks = chunk_file_by_line(PATH)

# 벡터 스토어 생성
collections = vector_store.store_chroma(all_chunks)

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
    #List[dict] 반환
    return query_to_answer(question)
    
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
def remove_favorite(title: str = Query(...)):
    global favorites
    favorites = [book for book in favorites if book.title != title]
    return {"favorites": favorites}

# 추천된 책들의 ISBN을 저장
isbns = [] 

def query_to_answer(query: str) -> List[dict]:
    global conversation_history
    book_preference_info = get_keywords_from_llm(query, conversation_history, model_name) 

    if book_preference_info["search_trigger"]:
            print("search_trigger 활성화, 검색 쿼리 생성 시작")
            search_query = generated_search_query(book_preference_info, model_name)

            print(f"생성된 검색 쿼리 {search_query}")
            retrieved_books = vector_store.retrieve_chroma(collections, search_query, num=NUM, exclude_isbns=isbns)         
            retrieved_books= retrieved_books[:NUM]

            recommendation_response = get_recommendation(retrieved_books, search_query, model_name)
            print(f"최종 recommendation_response 생성 {recommendation_response}")
            
            for book in recommendation_response:
                isbn = book.get("isbn", "")
                isbns.append(isbn)
            # 최종 추천 응답 생성 후, conversation_history 초기화    
            conversation_history = reset_conversation_history()
           
            return recommendation_response
    else:
        print("search_trigger' 비활성화, LLM 응답만 반환")
        print(conversation_history.get("generated_response", "generated_response 없음"))

    return [{
        "title": conversation_history.get("generated_response", "응답 없음"),
        "author": "",
        "summary": "",
        "recommendation": "",
        "isbn": "",
        "image": "",
    }]
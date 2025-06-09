from fastapi import FastAPI,Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../rag')))



from rag.conversation import ConversationService, reset_conversation_history
from rag import vector_store
from rag.chunking import chunk_file_by_line

 

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model_name = "gemini-2.0-flash"
client = genai.Client(api_key=api_key)

conversation_service = ConversationService(client, model_name)
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
    image: str
    introduction: str

# 임시 저장소
favorites: List[Book] = []

# 기본 라우트
@app.get("/")
def read_root():
    return {"message": "FastAPI 백엔드가 정상적으로 작동합니다!"}


@app.post("/api/conversations")
async def chat(request: Request):
    body = await request.json()
    question = body.get("question", "")
    
    #List[dict] 반환
    return query_to_answer(question)
    

@app.get("/api/recommendations")
def recommend():
    recommendation_response = get_book_recommendations()
    return recommendation_response

# 관심 도서 추가
@app.post("/api/favorites")
def add_favorite(book: Book):
    print("📥 받은 book:", book)
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

def get_book_recommendations() -> List[dict]:
    """책 추천 검색 및 최종 추천 응답 생성 로직"""
    global isbns, conversation_history

    print("search_trigger 활성화, 검색 쿼리 생성 시작")
    search_query = conversation_service.generate_search_query(conversation_history)
    print(f"생성된 검색 쿼리: {search_query}")

    retrieved_books = vector_store.retrieve_chroma(collections, search_query, num=NUM, exclude_isbns=isbns)
    retrieved_books = retrieved_books[:NUM]

    recommendation_response = conversation_service.get_recommendation(retrieved_books, search_query)
    print(f"최종 recommendation_response 생성: {recommendation_response}")

    # 추천된 책들의 ISBN 업데이트
    for book in recommendation_response:
        isbn = book.get("isbn", "")
        if isbn and isbn not in isbns:
            isbns.append(isbn)

    return recommendation_response

def query_to_answer(query: str) -> List[dict]:
    global conversation_history

    conversation_history['favorites'] = list(set(book.genre for book in favorites if book.genre))
    print(f"키워드 추출 전: {conversation_history}")
    book_preference_info = conversation_service.get_keywords_from_llm(query, conversation_history) 

    conversation_history = book_preference_info
    print(f"키워드 추출 후: {conversation_history}")
    

    recommendation_response = get_book_recommendations()

    print(book_preference_info.get("generated_response", "generated_response 없음"))

    first_image = recommendation_response[0]["image"] if recommendation_response and "image" in recommendation_response[0] else ""

    return [{
        "title": book_preference_info["generated_response"],
        "author": book_preference_info["search_trigger"],
        "summary": "",
        "recommendation": "",
        "isbn": "",
        "image": first_image,
    }]


@app.delete("/api/favorites/clear")
def clear_favorites():
    global favorites
    favorites = []
    return {"favorites": favorites}

from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import sys

from dotenv import load_dotenv
from google.generativeai import configure, genai
# Google Generative AI API 설정 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../rag')))



from rag.conversation import get_keywords_from_llm, generated_search_query, reset_conversation_history, get_recommendation
from rag import vector_store
from rag.chunking import chunk_file_by_line

 

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model_name = "gemini-2.0-flash"
client = genai.Client(api_key=api_key)


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
def remove_favorite(book: Book):
    if book in favorites:
        favorites.remove(book)
    return {"favorites": favorites}

# 추천된 책들의 ISBN을 저장
isbns = [] 

def query_to_answer(query: str) -> List[dict]:
    book_preference_info = get_keywords_from_llm(query, conversation_history, model_name) 

   


    # "keywords": [],
    # "mood": [],
    # "genre": [],
    # "theme": [],
    # "include_titles": [],
    # "search_trigger": false,
    # "generated_response": ""
    
    if book_preference_info["search_trigger"]:
            search_query = generated_search_query(book_preference_info, model_name)
    
            retrieved_books = vector_store.retrieve_chroma(collections, search_query, num=NUM, exclude_isbns=isbns)
            
            retrieved_books= retrieved_books[:NUM]
            

#             [{
#     "title": "어린 왕자",
#     "author": "앙투안 드 생텍쥐페리",
#     "summary": "사막에 불시착한 조종사가 만난 어린 왕자와의 철학적인 이야기...",
#     "recommendation": "순수함과 인생에 대한 통찰을 동시에 느낄 수 있는 작품입니다.",
#     "isbn": "9788952759600",
#     "image": "url",
#   },]
            recommendation_response = get_recommendation(retrieved_books, search_query, model_name)

            for book in recommendation_response:
                isbn = book.get("isbn", "")
                isbns.append(isbn)
           

            return recommendation_response
    

    return [{
        "title": conversation_history["generated_response"],
        "author": "",
        "summary": "",
        "recommendation": "",
        "isbn": "",
        "image": "",
    }]
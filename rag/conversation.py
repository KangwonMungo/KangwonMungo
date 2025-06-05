from typing import Dict, List
#from google import genai
#from google.genai import types
from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from .prompts import (
    SYSTEM_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION,
    SYSTEM_PROMPT_FOR_SEARCH_QUERY_GENERATION,
    USER_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION,
    USER_PROMPT_FOR_SEARCH_QUERY_GENERATION,
    SYSTEM_PROMPT_FOR_BOOK_RECOMMENDATION,
    USER_PROMPT_FOR_BOOK_RECOMMENDATION
)
from . import vector_store
from .chunking import chunk_file_by_line

"""
사용자와의 대화에서 도서 추천에 필요한 정보를 LLM을 통해 추출하고,
적절한 추천 응답을 생성하는 기능을 제공하는 모듈
"""

book_preference_extraction_format = """
{
  "keywords": [],
  "mood": [],
  "genre": [],
  "theme": [],
  "include_titles": [],
  "search_trigger": false,
  "generated_response": ""
}
""".strip()

def reset_conversation_history() -> dict:
    """
    대화 기록을 초기화하는 함수.
    Returns:
        dict: 초기화된 대화 기록 딕셔너리.
    """

    obj = json.loads(book_preference_extraction_format)

    return obj

def update_conversation_history(origin_conversation_history: dict, new_info: dict) -> dict:
    """
    대화 기록에 새로운 정보를 추가하는 함수.
    Args:
        origin_conversation_history (dict): 이전 대화 내용 및 추출된 키워드 정보.
        new_info (dict): 새로 추출된 키워드 정보.
    """

    # 누적되는 필드
    for key in ["keywords", "mood", "genre", "theme", "include_titles"]:
        if key in new_info and new_info[key]:
            origin_conversation_history[key] = list(set(origin_conversation_history[key]) | set(new_info[key]))

    # 그대로 덮어 쓸 필드
    for key in ["search_trigger", "generated_response"]:
        if key in new_info and new_info[key]:
            origin_conversation_history[key] = new_info[key]

    return origin_conversation_history

def get_keywords_from_llm(user_input: str, conversation_history: dict, model_name: str) -> dict:
    """
    LLM을 사용하여 사용자 입력에서 사용자의 도서 선호 대한 키워드 추출.
    Args:
        user_input (str): 사용자의 입력 메시지.
        conversation_history (dict): 이전 대화에서 추출한 키워드.
        model_name (str): 사용할 Gemini 모델명.
    Returns:
        dict: 추출된 키워드, 분위기, 장르 등의 정보가 담긴 딕셔너리.
    """
    #model = genai.GenerativeModel(model_name)
    model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION)

    prompt = USER_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION.format(
        user_input=user_input,
        conversation_history=json.dumps(conversation_history, ensure_ascii=False, indent=2),
        book_preference_extraction_format=book_preference_extraction_format
    )

    response = model.generate_content(
        #model=model,
        contents=prompt,
        generation_config=GenerationConfig(
            #system_instruction=SYSTEM_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION,
            temperature= 0.4,
            response_mime_type= 'application/json',
            #seed=42,
            #cached_content=None
        ),
    )
    extracted_book_preference_info = json.loads(response.text)

    conversation_history = update_conversation_history(conversation_history, extracted_book_preference_info) # 대화 기록 업데이트

    return conversation_history

def generated_search_query(conversation_history: dict, model_name: str) -> dict:
    """
    대화 기록을 기반으로 검색 쿼리를 생성.
    Args:
        conversation_history (dict): 이전 대화 내용 및 추출된 키워드 정보.
        model_name (str): 사용할 Gemini 모델명.
    Returns:
        str: 생성된 검색 쿼리.
    """

    # 추출한 필드 목록
    fields = {
        "keywords": "키워드",
        "mood": "분위기",
        "genre": "장르",
        "theme": "주제"
    }

    # 대화 기록에서 필드별로 추출된 키워드 정보를 문자열로 변환
    extracted_preferences = [
        f"{field_name} : {', '.join(conversation_history.get(field, []))}"
        for field, field_name in fields.items()
        if conversation_history.get(field, [])
    ]
    extracted_preferences = "\n".join(extracted_preferences)

    # 검색 쿼리 생성 프롬프트
    prompt = USER_PROMPT_FOR_SEARCH_QUERY_GENERATION.format(
        extracted_preferences=extracted_preferences
    )

    # 모델 생성
    model = genai.GenerativeModel(model_name=model_name,system_instruction=SYSTEM_PROMPT_FOR_SEARCH_QUERY_GENERATION)

    response = model.generate_content(
        # model=model,
        contents=prompt,
        generation_config=GenerationConfig(
            #system_instruction=SYSTEM_PROMPT_FOR_SEARCH_QUERY_GENERATION,
            temperature= 0.7,
            #seed=42,
            #cached_content=None,
            response_mime_type= 'application/json',
        ),
    )
    generated_search_query = json.loads(response.text)

    return generated_search_query
    
def print_conversation_history(conversation_history: dict) -> None:
    """
    이전 대화 내용에서 추출된 키워드 정보를 출력하는 함수.
    Args:
        conversation_history (dict): 이전 대화 내용 및 추출된 키워드 정보.
    """

    print("대화 기록:")
    for key, value in conversation_history.items():
        print(f"{key}: {value}")
    print("-" * 50)

def get_recommendation(retrieved_books: list, search_query: dict, model_name: str) -> List[Dict[str, str]]:
    """
    사용자에게 추천할 도서에 대한 응답을 생성하는 함수.
    Args:
        retrieved_books (list) : 검색된 책 리스트
        search_query (dict): 사용자 검색 정보
        model_name (str): 사용할 Gemini 모델명
    Returns:
        list: 추천할 도서의 [제목, 작가, 내용 요약, 추천 이유](dict)를 담은 리스트.
    """
    # 모델 생성
    model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT_FOR_BOOK_RECOMMENDATION)

    prompt = USER_PROMPT_FOR_BOOK_RECOMMENDATION.format(
        retrieved_books=retrieved_books,
        search_query=json.dumps(search_query, ensure_ascii=False, indent=2)
    )

    response = model.generate_content(
        # model=model,
        contents=prompt,
        generation_config=GenerationConfig(
            #system_instruction=SYSTEM_PROMPT_FOR_BOOK_RECOMMENDATION,
            temperature= 0.0,
            #seed=42,
            #cached_content=None,
            response_mime_type= 'application/json',
        ),
    )

    try:
        recommendation_response = json.loads(response.text)
    except json.JSONDecodeError:
        print("추천 결과 파싱 실패. 모델 응답:", response.text)
        return []

    for rec_response, book in zip(recommendation_response, retrieved_books):
        isbn = book.get('isbn', '')
        image = book.get('image', '')

        if isinstance(isbn, tuple) and len(isbn) > 0:
            rec_response['isbn'] = str(isbn[0])
        else:
            rec_response['isbn'] = str(isbn)
        
        rec_response['image'] = image

    return recommendation_response

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    model_name = "gemini-2.0-flash"
    PATH = "aladin_bestseller.json"
    NUM = 5  # 추천할 도서의 개수

    # chunking
    all_chunks = chunk_file_by_line(PATH) 

    # 벡터 스토어 생성 
    collections = vector_store.store_chroma(all_chunks)

    # 대화 정보 초기화
    conversation_history = reset_conversation_history()

    # 사용자 입력을 통해 대화 시작
    while True:
        user_input = input("사용자 입력 (종료하려면 'exit' 입력): ")
        if user_input.lower() == 'exit':
            print("대화를 종료합니다.")
            break

        # LLM을 통해 키워드 추출 및 대화 기록 업데이트
        book_preference_info = get_keywords_from_llm(user_input, conversation_history, model_name)  

        # 대화 기록 출력
        print_conversation_history(book_preference_info)

        # 검색 트리거가 활성화된 경우
        if book_preference_info["search_trigger"]:
            print("검색 트리거가 활성화되었습니다. 도서 검색 쿼리를 만듭니다.")
    
            # 1. 뽑아낸 키워드(book_preference_info)로 검색 query 생성
            search_query = generated_search_query(book_preference_info, model_name)
            print(f"생성된 검색 쿼리:\n{json.dumps(search_query, indent=2, ensure_ascii=False)}")

            # 제외할 책 목록 가져오기
            exclude_isbns = []

            # 2. search_query를 사용하여 RAG 검색 수행 후 검색 결과 가져오기
            retrieved_books = vector_store.retrieve_chroma(collections, search_query, num=NUM)
            
            # 3. 책 추천 응답 생성
            recommendation_response = get_recommendation(retrieved_books[:NUM], search_query, model_name)

            # 이미 추천된 책에 대한 isbn 추가하는 것 잊지 말기!
            # 사용자에게 추천 후 이 isbn이 선호 or 비선호 목록에 들어갈 수도!
            
            # 도서 추천 목록 확인
            print("추천 도서 목록:")
            print("-" * 50)
            output = "\n\n".join([
                f"{idx}. {book.get('title', '제목 없음')} by {book.get('author', '작가 정보 없음')}\n"
                f"   요약: {book.get('summary', '요약 없음')}\n"
                f"   추천 이유: {book.get('recommendation', '추천 이유 없음')}\n"
                f"   isbn : {book.get('isbn', '')}\n"
                f"   image_url : {book.get('image', '')}\n"
                for idx, book in enumerate(recommendation_response, start=1)
            ])
            print(output)
            print("-" * 50)

import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
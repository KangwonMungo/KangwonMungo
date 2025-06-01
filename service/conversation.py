import random
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

from prompts import (
    SYSTEM_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION,
    SYSTEM_PROMPT_FOR_SEARCH_QUERY_GENERATION,
    USER_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION,
    USER_PROMPT_FOR_SEARCH_QUERY_GENERATION
)

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

def get_keywords_from_llm(user_input: str, conversation_history: dict, model: str) -> dict:
    """
    LLM을 사용하여 사용자 입력에서 사용자의 도서 선호 대한 키워드 추출.
    Args:
        user_input (str): 사용자의 입력 메시지.
        conversation_history (dict): 이전 대화에서 추출한 키워드.
        model (str): 사용할 Gemini 모델명.
    Returns:
        dict: 추출된 키워드, 분위기, 장르 등의 정보가 담긴 딕셔너리.
    """

    prompt = USER_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION.format(
        user_input=user_input,
        conversation_history=json.dumps(conversation_history, ensure_ascii=False, indent=2),
        book_preference_extraction_format=book_preference_extraction_format
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION,
            temperature= 0.4,
            response_mime_type= 'application/json',
            seed=42,
            cached_content=None
        ),
    )
    extracted_book_preference_info = json.loads(response.text)
    
    return extracted_book_preference_info

def generated_search_query(conversation_history: dict, model: str) -> dict:
    """
    대화 기록을 기반으로 검색 쿼리를 생성.
    Args:
        conversation_history (dict): 이전 대화 내용 및 추출된 키워드 정보.
        model (str): 사용할 Gemini 모델명.
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

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT_FOR_SEARCH_QUERY_GENERATION,
            temperature= 0.7,
            seed=42,
            cached_content=None,
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

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = "gemini-2.0-flash"
    client = genai.Client(api_key=api_key)

    # 대화 정보 초기화
    conversation_history = reset_conversation_history()

    # 사용자 입력을 통해 대화 시작
    while True:
        user_input = input("사용자 입력 (종료하려면 'exit' 입력): ")
        if user_input.lower() == 'exit':
            print("대화를 종료합니다.")
            break

        # LLM을 통해 키워드 추출
        book_preference_info = get_keywords_from_llm(user_input, conversation_history, model_name)  
        
        # 대화 기록에 추출된 정보 업데이트
        conversation_history = update_conversation_history(conversation_history, book_preference_info)

        # 대화 기록 출력
        print_conversation_history(conversation_history)

        # 검색 트리거가 활성화된 경우
        if conversation_history["search_trigger"]:
            print("검색 트리거가 활성화되었습니다. 도서 검색 쿼리를 만듭니다.")

            # 1. 뽑아낸 키워드(conversation_history)를 query로 만들기
            search_query = generated_search_query(conversation_history, model_name)
            print(f"생성된 검색 쿼리:\n{json.dumps(search_query, indent=2, ensure_ascii=False)}")

            # 2. search_query를 사용하여 RAG 검색 수행

            # 3. 검색 결과를 기반으로 추천 응답 생성
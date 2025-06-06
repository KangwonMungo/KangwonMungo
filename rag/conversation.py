from typing import Dict, List
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

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

    print("conversation_hitory 업데이트 완료!")

    return origin_conversation_history

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

class ConversationService:
    def __init__(self, client, model: str):
        """
        클래스가 처음 생성될 때 client 초기화.
        """
        self.client = client
        self.model = model
        print(f"ConversationService가 초기화되었습니다.\n'{model}' 모델을 사용합니다.")

    def _generate_llm_response(self, prompt: str, system_instruction: str, temperature: float) -> dict:
        """
        Args:
            prompt (str): 모델에 전달할 메인 프롬프트 문자열.
            system_instruction (str): 모델의 역할이나 행동을 지시하는 시스템 명령어.
            temperature (float) [0.0~1.0]: 답변의 무작위성을 제어하는 값. 

        Returns:
            dict: 성공 시, 모델이 생성한 JSON 응답을 파싱한 딕셔너리.
                  실패 시, `{'error': '에러 메시지'}` 형태의 딕셔너리.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature= temperature,
                    response_mime_type= 'application/json',
                    seed=42,
                ),
            )
            return json.loads(response.text)
        
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}\n모델 응답: {response.text}")
            return {"error": "Invalid JSON response"}
        except Exception as e:
            print(f"API 호출 중 알 수 없는 오류 발생: {e}")
            return {"error": "API call failed"}

    def get_keywords_from_llm(self, user_input: str, conversation_history: dict) -> dict:
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

        extracted_book_preference_info = self._generate_llm_response(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT_FOR_BOOK_PREFERENCE_EXTRACTION,
            temperature=0.4
        )

        if "error" in extracted_book_preference_info:
            print("Error: 키워드 추출 중... 이전 대화 기록을 그대로 반환합니다.")
            return conversation_history
        
        # 대화 기록 업데이트
        conversation_history = update_conversation_history(conversation_history, extracted_book_preference_info)

        return conversation_history

    def generate_search_query(self, conversation_history: dict) -> dict:
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

        generated_search_query = self._generate_llm_response(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT_FOR_SEARCH_QUERY_GENERATION,
            temperature=0.7
        )

        if "error" in generated_search_query:
            print("Error: 검색 쿼리 생성 중... 빈 딕셔너리를 반환합니다.")
            return {}

        return generated_search_query
    
    def get_recommendation(self, retrieved_books: list, search_query: dict) -> List[Dict[str, str]]:
        """
        사용자에게 추천할 도서에 대한 응답을 생성하는 함수.
        Args:
            retrieved_books (list) : 검색된 책 리스트
            search_query (dict): 사용자 검색 정보
            model (str): 사용할 Gemini 모델명
        Returns:
            list: 추천할 도서의 [제목, 작가, 내용 요약, 추천 이유, isbn, 장르, image_url](dict)를 담은 리스트.
        """
        print(f"생성된 책 :\n{retrieved_books}\n")
        prompt = USER_PROMPT_FOR_BOOK_RECOMMENDATION.format(
            retrieved_books=retrieved_books,
            search_query=json.dumps(search_query, ensure_ascii=False, indent=2)
        )

        recommendation_response = self._generate_llm_response(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT_FOR_BOOK_RECOMMENDATION,
            temperature=0.0
        )

        if "error" in recommendation_response:
            print("Error: 추천 결과 생성 중... 빈 리스트를 반환합니다.")
            return []


        for rec_response, book in zip(recommendation_response, retrieved_books):
            isbn = book.get('isbn', '')
            image = book.get('image', '')
            genre = book.get('genre', '')

            if isinstance(isbn, tuple):
                rec_response['isbn'] = str(isbn[0]) if isbn else ''
            else:
                rec_response['isbn'] = str(isbn)

            rec_response['genre'] = genre.split(",")[0].strip() if genre else ''
            rec_response['image'] = image

        return recommendation_response

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.0-flash"

    service = ConversationService(client, model_name)
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
        book_preference_info = service.get_keywords_from_llm(user_input, conversation_history)  

        # 대화 기록 출력
        print_conversation_history(book_preference_info)

        # 검색 트리거가 활성화된 경우
        if book_preference_info["search_trigger"]:
            print("검색 트리거가 활성화되었습니다. 도서 검색 쿼리를 만듭니다.")
            
            # 1. 뽑아낸 키워드(book_preference_info)로 검색 query 생성
            search_query = service.generate_search_query(book_preference_info)
            print(f"생성된 검색 쿼리:\n{json.dumps(search_query, indent=2, ensure_ascii=False)}")

            # 2. search_query를 사용하여 RAG 검색 수행 후 검색 결과 가져오기
            retrieved_books = vector_store.retrieve_chroma(collections, search_query, num=NUM)

            # 3. 책 추천 응답 생성
            recommendation_response = service.get_recommendation(retrieved_books[:NUM], search_query)
            
            # 도서 추천 목록 확인
            print("추천 도서 목록:")
            print("-" * 50)
            output = "\n\n".join([
                f"{idx}. {book.get('title', '제목 없음')} by {book.get('author', '작가 정보 없음')}\n"
                f"   요약: {book.get('summary', '요약 없음')}\n"
                f"   추천 이유: {book.get('recommendation', '추천 이유 없음')}\n"
                f"   isbn : {book.get('isbn', '')}\n"
                f"   image_url : {book.get('image', '')}\n"
                f"   genre : {book.get('genre','')}"
                for idx, book in enumerate(recommendation_response, start=1)
            ])
            print(output)
            print("-" * 50)
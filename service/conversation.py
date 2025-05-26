import random
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

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
"""

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
    
    system_instruction = """

    당신은 사용자의 말에서 도서 추천에 필요한 정보를 정확히 분류·추출하는 섬세한 심리학자이자 도서 큐레이터입니다.
    당신의 임무는 사용자의 말 속에 숨겨진 의도를 분석하여, 아래 항목에 따라 핵심 정보를 구분해 추출하는 것입니다.

    사용자는 읽고 싶은 책에 대한 생각이나 감정을 자유롭게 표현합니다.  
    당신은 그 말 속에서 다음 네 가지 항목을 명확히 구분하여 추출해야 합니다:

    - **키워드 (keywords)**: 책의 주요 소재, 특징, 핵심 단어 (예: 마법, 모험, 성장, 우정, 판타지, 추리, 범죄)
    - **분위기 (mood)**: 책이 주는 전반적인 감정과 분위기 (예: 신비롭고 흥미진진함, 따뜻함, 긴장감, 어두움, 유쾌함, 감동적임)
    - **장르 (genre)**: 책의 분류 장르 (예: 판타지, 추리, 성장소설, 로맨스, 스릴러, SF, 에세이)
    - **주제 (theme)**: 이야기의 중심 메시지나 다루는 주제 (예: 성장, 우정, 용기, 가족, 정의, 희생, 자아 발견, 사랑, 복수, 모험, 권력, 자유, 변화, 소외, 연대, 구원)

    **주의사항**:  
    사용자의 말에 책 제목이나 작가, 줄거리 등이 포함되어 있더라도, 그 정보가 확실하지 않거나 모호할 경우 **절대 추측하거나 지어내지 마세요.**

    그럴 경우, 대신 아래와 같이 정중하게 되묻습니다:
    - "혹시 그 책에 대해 더 자세히 설명해주실 수 있을까요?"
    - "기억나는 줄거리나 작가, 책의 분위기라도 알려주시면 도움이 될 것 같아요."

    당신의 최종 목표는 각 항목을 혼동하지 않고, 사용자의 말을 신중하게 분석하여 의미 있는 정보를 정확히 추출하는 것입니다.
    """.strip()

    prompt = f"""
    사용자 입력: {user_input}
    이전 대화에서 사용자가 원하는 책에 대한 정보: {conversation_history}

    아래 기준에 따라, 필요한 정보를 JSON 형식으로 정리해주세요.

    - keywords(키워드): 책의 주요 소재, 특징, 핵심 단어 (예: 마법, 모험, 성장, 우정, 판타지, 추리, 범죄)
    - mood(분위기): 책이 주는 전반적인 감정, 분위기 (예: 신비롭고 흥미진진함, 따뜻함, 긴장감, 어두움, 유쾌함, 감동적임)
    - genre(장르): 책의 장르 (예: 판타지, 추리, 성장소설, 로맨스, 스릴러, SF, 에세이)
    - theme(주제): 이야기의 중심 메시지, 인물의 성장, 인간관계, 사회적 이슈 등 (예: 성장, 우정, 용기, 가족, 정의, 희생, 자아 발견, 사랑, 복수, 모험, 권력, 자유, 변화, 소외, 연대, 구원)
    - include_titles(선호하는 책)는 추천에 반드시 포함
    - generated_response는 아래 예시처럼 자연스럽고 친근하게, 사용자의 표현을 적절히 반영해서 작성하세요.  
      꼭 예시 형식대로만 따를 필요는 없으며, 말투나 어투는 사용자 톤에 자연스럽게 맞춰주세요.

    <generated_response 예시>  
    해리포터같은 판타지 소설을 원하시는 군요!  
    - 장르: 판타지, 키워드: 마법, 모험  
    - 분위기: 신비롭고 흥미진진함  
    - 주제: 성장과 우정  
    - 캐릭터 유형: 여성 주인공과 마법사  
    - 설정: 마법 학교  

    이런 느낌의 책을 원하시나요?
    
    - 사용자의 말에 맞는 키워드를 추천하고, generated_response에 포함해 주세요.
    - 책 제목/작가/내용이 모호하면 절대 추측하지 말고, 키워드 리스트에 추가하지 말고, 아래처럼 추가 질문을 해 주세요.  
        - "혹시 그 책에 대해 더 자세히 설명해주실 수 있을까요?"  
        - "기억나는 줄거리나 작가, 책의 분위기라도 알려주시면 도움이 될 것 같아요."

    (주의) 사용자의 말에 책 제목이나 작가, 내용이 포함되어 있더라도,  
    그 정보가 확실하지 않거나 모호한 경우 **절대로 추측하거나 지어내지 마세요**.  
   
    - 키워드가 부족하면 아래 예시처럼 세부 키워드를 제시하며 추가 정보를 요청해 주세요.  
        예시: [추리 소설]
        - 1. 살인사건
        - 2. 범인 추적
        - 3. 긴장감 넘치는 전개
        - 4. 범죄 심리
        - 5. 반전 있는 결말
        - 6. 주인공 탐정
        - 7. 범죄 현장 조사
        - 8. 범죄자 심리 분석
        - 9. 범죄 수사
        - 10. 범죄의 동기와 배경

        어떤 느낌의 책을 원하시나요?  
        위와 같은 [추리 소설]의 세부 키워드 중에서 혹시 더 끌리는 요소가 있으신가요?  
        또는 기억나는 장면, 등장인물, 분위기 등 더 자세한 내용을 알려주시면  
        더 딱 맞는 책을 추천해드릴 수 있어요!  
        편하게 말씀해 주세요 :)
    
    - 반드시 아래 조건을 지키세요:
    1. `keywords`, `mood`, `genre`, `theme` 항목에 포함된 **모든 키워드 수를 합산하여 총 7개 이상이면** `search_trigger`를 `true`로 반환하세요.  
    2. 총합이 7개 미만이더라도, **의미 있고 구체적인 쿼리 구성이 가능하다고 판단되는 경우에는 예외적으로 `true`로 반환할 수 있습니다.**  
    3. 그 외의 경우에는 `search_trigger`를 `false`로 반환하세요.

    4. 키워드 수를 판단할 때는 다음 예시를 참고하세요:  
    - 예: `keywords` 2개, `mood` 1개, `genre` 3개, `theme` 1개 → 총 7개 → `true` 반환  
    - 반례: 총합이 6개 이하 → `false` 반환

    5. 특정 항목(`keywords`, `mood`, `genre`, `theme`)의 키워드 수가 부족하다면,  
    사용자가 언급한 책 제목이나 작가, 내용 등을 바탕으로 **세부 키워드**를 제시하며 추가 정보를 요청하세요.  
    - 예: `주제` 키워드가 부족할 경우, "혹시 기억나는 내용이나 중심 메시지가 있을까요?"처럼 자연스럽게 물어보세요.  
    - 이때 `"theme"`이라는 용어 대신 **"주제"**라는 표현을 사용하세요.

    6. 사용자가 대화 중 언급한 책 제목(예: `"미스 페레그린과 이상한 아이들의 집"`)은 반드시 `include_titles` 리스트에 추가하세요.

    7. 출력은 반드시 아래 예시와 동일한 **JSON 형식**으로 반환하고, 그 외 불필요한 설명은 절대 포함하지 마세요.
    
    8. 사용자가 언급한 책 제목이 명확하고 실제 존재하는 경우, 해당 책의 주요 키워드, 분위기, 장르, 주제 등을 충분히 확장하여 추출하세요.  
    필요 시 그 책의 대표적인 특징을 바탕으로 **연상 키워드 5~10개 이상**을 추출하는 것도 좋습니다.  
    - 예: "해리포터 같은 책" → 마법, 성장, 어두운 분위기, 선과 악, 예언, 학교 생활, 친구와의 연대 등
    {book_preference_extraction_format}
    """.strip()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature= 0.4,
            response_mime_type= 'application/json',
            seed=42,
            cached_content=None
        ),
    )
    
    extracted_book_preference_info = json.loads(response.text)
    
    return extracted_book_preference_info

def generated_search_query(conversation_history: dict, model: str) -> list:
    """
    대화 기록을 기반으로 검색 쿼리를 생성.
    Args:
        conversation_history (dict): 이전 대화 내용 및 추출된 키워드 정보.
        model (str): 사용할 Gemini 모델명.
    Returns:
        str: 생성된 검색 쿼리.
    """
    system_instruction ="""
    당신은 사용자의 도서 선호 정보를 바탕으로 검색 쿼리를 생성하는 전문가입니다.

    사용자의 도서 선호 정보(키워드, 분위기, 장르, 주제 등)는 '[제공된 정보]' 섹션에 명시됩니다.  
    당신의 임무는 이 정보를 바탕으로 사용자의 숨겨진 의도까지 분석하여, **사용자가 원하는 책을 찾는 데 도움이 되는 관련성 높고 창의적인 검색 쿼리 문장 3개를 생성하는 것**입니다.

    - 각 쿼리는 단순한 키워드 나열이 아닌, **문맥이 자연스러운 완전한 문장 형태**여야 합니다.
    - 정보의 뉘앙스, 분위기, 장르적 함의를 고려하여 **세심하고 사려 깊은 표현**을 사용하십시오.
    - **사용자의 의도와 검색 목적을 정확히 반영하여**, 실제 검색에 효과적인 쿼리를 작성하세요.
    - 생성된 문장은 **도서 검색 결과에서 사용자가 진짜로 원하는 책을 발견할 수 있도록 설계**되어야 합니다.
    """.strip()

    keywords = conversation_history.get("keywords", [])
    mood = conversation_history.get("mood", [])
    genre = conversation_history.get("genre", [])
    theme = conversation_history.get("theme", [])
    
    query_parts = []
    
    if keywords:
        query_parts.append(f"키워드: {', '.join(keywords)}")
    if mood:
        query_parts.append(f"분위기: {', '.join(mood)}")
    if genre:
        query_parts.append(f"장르: {', '.join(genre)}")
    if theme:
        query_parts.append(f"주제: {', '.join(theme)}")

    query_parts_str = "\n".join(query_parts)
    print(f"query_parts_str:\n{query_parts_str}")

    prompt =f"""
    [제공된 정보]를 보고 사용자가 원하는 책을 찾기 위한 검색 쿼리를 작성해 주세요.
    아래에 제공된 '[제공된 정보]'의 핵심 내용을 종합하여, 사용자가 원하는 책을 가장 잘 찾을 수 있는 **새로운 검색 쿼리 문장 세 개를 창의적으로 작성**해 주십시오.
    단순히 정보를 나열하는 것이 아니라, 의미가 잘 전달되도록 각각 다른 뉘앙스의 후보지 세 문장을 만드세요.

    [제공된 정보]
    {query_parts_str}

    [예시]
    키워드: 마법 학교, 우정, 모험, 선과 악
    분위기: 신비로운
    장르: 판타지 소설
    주제: 성장, 용기e

    - 마법 학교에서 펼쳐지는 우정과 모험, 선과 악의 대립을 그린 흥미진진한 판타지 소설
    - 신비로운 분위기 속에서 우정과 용기를 배우며 성장하는 마법 학교 판타지 소설
    - 마법 학교를 배경으로 우정, 용기, 성장을 주제로 한, 흥미진진한 모험 이야기 판타지 소설

    [제공된 정보]를 바탕으로, 사용자가 원하는 책을 찾기 위한 검색 쿼리 세 개를 작성해 주세요.
    응답은 JSON 배열 형태 (예: ["쿼리1", "쿼리2", "쿼리3"])로, 각 쿼리 문장을 요소로 포함해야 합니다.
    """.strip()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature= 0.7,
            seed=42,
            cached_content=None,
            response_mime_type= 'application/json',
        ),
    )
    
    print("생성된 검색 쿼리 응답:")
    print(response.text)
    print('*'*50)
    generated_search_query = json.loads(response.text)
    print(f"생성된 search query type = {type(generated_search_query)}")
    return generated_search_query
    
def print_conversation_history(conversation_history: dict) -> None:
    """
    대화 기록을 출력하는 함수.
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

    # 이전 대화 정보 (초기화)
    conversation_history = {
        "keywords": [],
        "mood": [],
        "genre": [],
        "theme": [],
        "include_titles": [],
        "search_trigger": False,
        "generated_response": []
    }

    while True:
        user_input = input("사용자 입력 (종료하려면 'exit' 입력): ")
        if user_input.lower() == 'exit':
            print("대화를 종료합니다.")
            break

        # LLM을 통해 키워드 추출
        book_preference_info = get_keywords_from_llm(user_input, conversation_history, model_name)  
        
        # 누적되는 필드
        for key in ["keywords", "mood", "genre", "theme", "include_titles"]:
            if key in book_preference_info:
                conversation_history[key] = list(set(conversation_history[key]) | set(book_preference_info[key]))
        
        # 그대로 덮어 쓸 필드
        for key in ["include_titles", "search_trigger", "generated_response"]:
            if key in book_preference_info:
                conversation_history[key] = book_preference_info[key]

        # 대화 기록 출력
        print_conversation_history(conversation_history)

        # 검색 트리거가 활성화된 경우
        if conversation_history["search_trigger"]:
            print("검색 트리거가 활성화되었습니다. 도서 검색 쿼리를 만듭니다.")
            # include_titles에 포함된 책: 검색하지 말아야 할 책 제목

            # 1. 뽑아낸 키워드(conversation_history)를 query로 만들기
            search_query = generated_search_query(conversation_history, model_name)
            print(f"생성된 검색 쿼리:\n{search_query}")

            # 2. search_query를 사용하여 RAG 검색 수행
            # 3. 검색 결과를 기반으로 추천 응답 생성
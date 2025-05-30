import json

from dotenv import load_dotenv
from typing import List, Dict, Any
from vector_store import store_chroma, retrieve_chroma
from kiwipiepy import Kiwi

#pip install kiwipiepy

MAX_CHUNK_SIZE = 500 # 300~600자 사이에서 조정 필요 
CHUNK_OVERLAP = 2 # 1~3 사이에서 조정 필요
NUM = 10

kiwi = Kiwi()
load_dotenv()


def initialize_chunk(introduction: str, max_chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    하나의 긴 책 소개를 문장 단위로 분할하여 청크 리스트로 반환
    
    Args:
        introduction (str): 책 소개 텍스트
        max_chunk_size (int): 각 청크의 최대 문자 길이
        chunk_overlap (int): 맥락 이어지도록 겹칠 문장 개수 

    Returns:
        List[str]: 분리된 청크 리스트
    """
    # 1. KiwiPyPy를 사용하여 한국어 문장 분리
    sentences_list = kiwi.split_into_sents(introduction.strip())
    #  Sentence 객체의 실제 텍스트는 .text에 있음 
    sentences = [s.text.strip() for s in sentences_list if s.text.strip()]

    chunks = [] # 모든 청크들이 저장
    current_chunk = [] # 현재 청크를 구성하는 문장들
    current_chunk_len = 0 # 현재 청크의 문자 길이

    for i, sentence in enumerate(sentences):
        sentence_len = len(sentence)

        # 현재 문장을 추가했을 때 max_chunk_size를 초과하는지 확인 및 현재 청크에 문장이 있을 경우, 공백을 추가
        if current_chunk_len + sentence_len + (1 if current_chunk else 0) > max_chunk_size:
            # 현재까지 모은 문장들을 하나의 청크로 추가
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            # 이전 문장들을 chunk_overlap 만큼 가져와 다음 청크의 시작으로 사용 (오버랩 처리)
            overlap_index = max(0, len(current_chunk) - chunk_overlap)
            current_chunk = list(current_chunk[overlap_index:])
            current_chunk_len = sum(len(sentence) for sentence in current_chunk) + (len(current_chunk) - 1 if len(current_chunk) > 0 else 0)

        # 단일 문장 자체가 max_chunk_size를 넘는 경우, 해당 문장을 하나의 청크로 처리
        if sentence_len > max_chunk_size:
            if current_chunk: # 현재 모아둔 청크가 있다면 먼저 추가하고 초기화
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_chunk_len = 0
            chunks.append(sentence) # 긴 문장 자체를 하나의 청크로 추가
            continue # 다음 문장으로 넘어감

        # 현재 문장 추가
        current_chunk.append(sentence)
        current_chunk_len += sentence_len + (1 if len(current_chunk) > 1 else 0) # 단어 사이 공백 추가

    # 마지막 남은 청크 추가
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def chunk_file_by_line(path: str) ->  List[Dict[str, Any]]:
    all_chunk_data = []
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            book_data = json.load(file)

        for book_index, book in enumerate(book_data):
            title = book.get('title', '')
            author = book.get('author', '')
            keyword = book.get('keyword', []) 
            genre = book.get('genre', [])     
            image = book.get('image', '')
            introduction = book.get('introduction', '')
            isbn = book.get('isbn', '')

            chunks = initialize_chunk(introduction=introduction, max_chunk_size=MAX_CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP) # 이후에 조정 필요

            meta_data = {
                "title": title,
                "author": author,
                "keyword": keyword,
                "genre": genre,
                "image": image,
                "isbn": isbn,
            }

            chunk_data = [{
                "chunk_index": f"{book_index}-{chunk_index}", # 하나의 책 소개당 여러 개의 청크를 가지므로, 인덱스 여러 개 필요
                "introduction": chunk,
                **meta_data
            } for chunk_index, chunk in enumerate(chunks)]

            all_chunk_data.extend(chunk_data)
    except Exception as e:
        print(f"오류 발생: {e}")

    return all_chunk_data


def print_all_chunk_data(all_chunk_data: List[Dict[str, Any]]) -> None:
    if all_chunk_data:
        for i, chunk in enumerate(all_chunk_data):
            print(f"\nProcessed Chunk {i}:")
            print(f"  Title: {chunk.get('title', '')}")
            print(f"  Author: {chunk.get('author', '')}")
            print(f"  Keyword: {chunk.get('keyword', [])}")
            print(f"  Genre: {chunk.get('genre', [])}")
            print(f"  Image URL: {chunk.get('image', '')}")
            print(f"  ISBN: {chunk.get('isbn', '')}")
            print(f"  Chunk Index: {chunk.get('chunk_index', '')}")
            print(f"  Introduction Chunk: {chunk.get('introduction', '')}")
    else:
        print("생성된 Chunk 데이터가 없습니다.")


if __name__ == "__main__":
    PATH = "aladin_bestseller.json"

    try:
        # 1. chunking
        all_chunks = chunk_file_by_line(PATH) 
        # print(f"\n생성된 총 청크(행) 개수: {len(all_chunks)}")
        # print_all_chunk_data(all_chunks)
        # print('='*50)

        # 2. 벡터 스토어 생성 
        #collections = store_chroma(all_chunks)
        #print('='*50)

        # 3. Retriever
        query = "판타지 소설 추천"
        #retrieved_documents = retrieve_chroma(collections, query, num=NUM)
        #print('='*50)
        
        # 4. prompt

    except FileNotFoundError:
        print(f"Error: '{PATH}'을 찾을 수 없음. 경로 확인 바람.") 
    except Exception as e:
        print(f"{PATH} 파일을 읽는 중 오류 발생: {e}")
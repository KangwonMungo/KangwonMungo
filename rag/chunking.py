import json
import kss
from dotenv import load_dotenv
from typing import List, Dict, Any

COLLECTION_NAME = "book_collection"

load_dotenv()

def chunk_sentences(sentence_list, chunk_size):
    chunks = []

    if not sentence_list:
        return chunks

    if chunk_size <= 0 and sentence_list:
        chunks.append(" ".join(sentence_list))
        return chunks

    for i in range(0, len(sentence_list), chunk_size):
        selected_sentences_list = sentence_list[i:i + chunk_size]
        sentence_chunk = " ".join(selected_sentences_list)
        chunks.append(sentence_chunk)
    
    return chunks


def chunk_file_by_line(path: str) ->  List[Dict[str, Any]]:
    all_chunk_data = []
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            book_data = json.load(file)

        for index, book in enumerate(book_data):
            title = book.get('title', '')
            author = book.get('author', '')
            keyword = book.get('keyword', []) 
            genre = book.get('genre', [])     
            image = book.get('image', '')
            introduction = book.get('introduction', '')
            isbn = book.get('isbn', '')

            meta_data = {
                "title": title,
                "author": author,
                "keyword": keyword,
                "genre": genre,
                "image": image,
                "isbn": isbn,
            }

            chunk_data = {
                "chunk_index": index,
                "introduction": introduction,
                **meta_data
            }
            all_chunk_data.append(chunk_data)
    except Exception as e:
        print(f"오류 발생: {e}")

    return all_chunk_data


def chunk_file(path: str, chunk_size: int) ->  List[Dict[str, Any]]:
    all_chunk_data = []

    try:
        with open(path, 'r', encoding='utf-8') as file:
            book_data = json.load(file)

        for book in book_data:
            title = book.get('title', '')
            author = book.get('author', '')
            keyword = book.get('keyword', []) 
            genre = book.get('genre', [])     
            image = book.get('image', '')
            introduction = book.get('introduction', '')
            isbn = book.get('isbn', '')

            meta_data = {
                "title": title,
                "author": author,
                "keyword": keyword,
                "genre": genre,
                "image": image,
                "isbn": isbn,
            }

            if introduction:
                try:
                    sentences = kss.split_sentences(introduction)
                    introduction_chunks = chunk_sentences(sentences, chunk_size)
                except Exception as e:
                    print(f"[{title}] 문장 분리 실패: {e}")
                    introduction_chunks = [introduction]
            else:
                introduction_chunks = [""]

            for i, chunk in enumerate(introduction_chunks):
                chunk_data = {
                    "chunk_index": i + 1,
                    "introduction": chunk,
                    **meta_data
                }
                all_chunk_data.append(chunk_data)
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
    CHUNK_SIZE = 2
    
    try:
        # 1. chunking
        all_chunks = chunk_file(PATH, CHUNK_SIZE)
        print(f"\n생성된 총 청크(행) 개수: {len(all_chunks)}")
        print_all_chunk_data(all_chunks)
        print('='*50)

        # 2. 벡터 스토어 저장

        # 3. Retriever
        
        # 4. Reranker
        

        # 5. prompt

    except FileNotFoundError:
        print(f"Error: '{PATH}'을 찾을 수 없음. 경로 확인 바람.") 
    except Exception as e:
        print(f"{PATH} 파일을 읽는 중 오류 발생: {e}")
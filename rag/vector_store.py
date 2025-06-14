import os
import chromadb
import time

from dotenv import load_dotenv
from typing import List, Dict, Any
from chromadb.utils import embedding_functions
from chromadb.api.models.Collection import Collection
from tqdm import tqdm

# pip install chromadb
# pip install python-dotenv
# pip install openai
# pip install tqdm

COLLECTION_NAME = "book_collection"
BATCH_SIZE = 80 

load_dotenv()

def store_chroma(chunks: List[Dict[str, Any]]):
    """
    청크 데이터를 ChromaDB에 저장 및 임베딩 

    Args:
        chunks (List[Dict[str, Any]]): 각 책 소개가 분할된 청크 데이터 리스트
                            
    Returns:
        Collection: 데이터가 저장된 ChromaDB 컬렉션
    """
    # 1. 클라이언트 생성 
    client = chromadb.PersistentClient(path="chroma_db")

    embedding_func = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-large")
    
    # 2. 기존 컬렉션이 없으면 생성, 있으면 가져옴
    try:
        collections = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func,
        )
        print(f"기존 컬렉션 '{COLLECTION_NAME}'을 로드했습니다")
        return collections
    
    except Exception as e:
        print(f"컬렉션 '{COLLECTION_NAME}'이 존재하지 않아 새로 생성합니다 ({e})")
        collections = client.create_collection( 
            name=COLLECTION_NAME,
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"}
        )

    documents = []
    metadatas = []
    documents_ids = []

    # 컬렉션에 새로운 documents, metadata를 추가
    for chunk in chunks:
        # 'introduction'을 문서 내용으로 사용 
        documents.append(chunk["introduction"])

        # 'introduction'을 제외한 모든 부분을 메타데이터로 사용
        metadata = chunk.copy()
        del metadata["introduction"]

         # 메타데이터는 리스트 형식이면 안되므로 문자열로 처리      
        metadata["keyword"] = ", ".join(map(str, metadata.get("keyword", [])))
        metadata["genre"] = ", ".join(map(str, metadata.get("genre", [])))
        metadatas.append(metadata)

        # ids 값은 문자형이어야 함
        ids = str(chunk["chunk_index"])
        documents_ids.append(ids)
    
    # 배치 단위로 ChromaDB에 추가
    total_chunks = len(documents)
    for i in tqdm(range(0, total_chunks, BATCH_SIZE)):
        try:
            collections.add(
                documents=documents[i:i + BATCH_SIZE ],
                metadatas=metadatas[i:i + BATCH_SIZE ],
                ids=documents_ids[i:i + BATCH_SIZE ]
            )
            print(f"현재 배치에 {len(documents[i:i + BATCH_SIZE])}개 추가 완료")
            time.sleep(0.1) # 짧은 대기 시간 
        except Exception as e:
            print(f"문서 {i} ~ {i + len(documents) - 1} 추가 중 오류 발생: {e}")
            
    print(f"ChromaDB에 문서 {len(documents)}개 추가 후, 저장 완료")
    
    return collections


def retrieve_chroma(collection: Collection, llm_query: Dict[str, Any], num: int, exclude_isbns: List[str] = None) -> List[Dict[str, Any]]:
    """
    ChromaDB에서 LLM이 생성한 쿼리 정보를 사용하여 유사한 문서를 검색
    중복을 제거하여 책 단위로 반환하며, 장르/키워드 가중치를 부여

    Args:
        collection (Collection): 데이터가 저장된 ChromaDB 컬렉션
        llm_query (Dict[str, Any]): LLM이 생성한 검색 쿼리 정보
        num (int): 추천할 책의 개수
        exclude_isbns (List[str]) : 검색에서 제외할 책의 ISBN 리스트
    
    Returns:
        List[Dict[str, Any]]: 검색된 책 정보 리스트
    """
    query_text = llm_query.get("query", "")
    genre_weight = llm_query.get("genre_weight", [])
    keyword_weight = llm_query.get("keyword_weight", [])

    if not query_text:
        print("LLM이 생성한 쿼리가 존재하지 않습니다")
        return []
    if exclude_isbns is None:
        exclude_isbns = []

    # 1. 쿼리 확장: LLM이 생성한 쿼리 + 장르 + 키워드를 모두 포함시켜 임베딩 정확도를 높임
    expanded_query_text = query_text
    # 장르와 키워드를 여러 번 반복하여 가중치 부여
    if genre_weight:
        expanded_query_text += " " + " ".join(f"{g} {g} {g}" for g in genre_weight) 
    if keyword_weight:
        expanded_query_text += " " + " ".join(f"{k} {k}" for k in keyword_weight) 
    # 최종 expanded_query_text 자체를 한 번 더 추가하여 가중치 부여
    expanded_query_text += " " + expanded_query_text

    # 2. ChromaDB에서 확장된 쿼리로 문서 검색
    results = collection.query(
        query_texts=[expanded_query_text], # 확장된 쿼리
        n_results=num * 10, 
        include=["documents", "metadatas", "distances"],
    )

    retrieved_books = {} # ISBN을 키로 사용하여 중복을 제거하고 책 단위로 정보를 저장

    if results["documents"]:
        for i in range(len(results["documents"][0])):
            document = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            isbn = metadata.get("isbn")
            if not isbn:
                continue
            # 제외 목록에 있는 ISBN이 검색 결과에 포함된 경우, 건너뜀
            if isbn in exclude_isbns: 
                continue  

            # 3. 메타데이터 기반 가중치 조정 
            weights = 0.0

            # 장르 가중치 부여: LLM이 추출한 장르 중 책의 장르 문자열에 포함되는지 확인
            book_genre = metadata.get("genre", "").lower()
            for genre in genre_weight:
                if genre.lower() in book_genre:
                    weights -= 0.60 # 가중치 조정 필요, 기존 0.6
                    break

            # 키워드 가중치 부여
            book_keyword = metadata.get("keyword", "").lower()
            book_introduction = document.lower() 
            for keyword in keyword_weight:
                # 책의 키워드 또는 소개 내용에 키워드가 있다면 가중치 부여
                if keyword.lower() in book_keyword or \
                   keyword.lower() in book_introduction:
                    weights -= 0.3 # 가중치 조정 필요, 기존 0.3 
                    break

            final_distance = distance + weights
            final_distance = max(0.0, final_distance) # 0보다 작아지지 않게 함

            if isbn not in retrieved_books:
                retrieved_books[isbn] = {
                    "title": metadata.get("title"),
                    "author": metadata.get("author"),
                    "keyword": metadata.get("keyword"),
                    "genre": metadata.get("genre"),
                    "image": metadata.get("image"),
                    "isbn": isbn,
                    "introduction": document,
                    "distance": final_distance
                }
            else:
                if final_distance < retrieved_books[isbn]["distance"]:
                    retrieved_books[isbn]["introduction"] = document
                    retrieved_books[isbn]["distance"] = final_distance

    # 유사도(distance) 기준으로 정렬
    sorted_books = sorted(retrieved_books.values(), key=lambda x: x["distance"])

    return sorted_books
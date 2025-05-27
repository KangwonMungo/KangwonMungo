import os
import chromadb
from dotenv import load_dotenv
from typing import List, Dict, Any
from chromadb.utils import embedding_functions
from chromadb.api.models.Collection import Collection

# pip install chromadb
# pip install python-dotenv
# pip install openai

COLLECTION_NAME = "book_collection"

load_dotenv()

def store_chroma(chunks: List[Dict[str, Any]]):
    """
    청크 데이터를 ChromaDB에 저장 및 임베딩 
    """
    # 1. 클라이언트 생성 
    client = chromadb.PersistentClient(path="chroma_db")

    embedding_func = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-large")
    
     # 2. 기존 컬렉션 삭제 
    try: 
        client.delete_collection(name=COLLECTION_NAME) 
        print(f"기존 컬렉션 '{COLLECTION_NAME}' 삭제") 
    except Exception as e: 
        print(f"기존 컬렉션 삭제 중 오류 발생 {e}") 
        pass 
    
    # 3. 기존 컬렉션을 가져오고, 없으면 생성 
    collections = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"})    
    
    documents = []
    metadatas = []
    documents_ids = []

    # 4. 컬렉션에 새로운 documents, metadata를 추가
    for chunk in chunks:
        # 'introduction'을 문서 내용으로 사용 
        documents.append(chunk["introduction"])

        # 'introduction'을 제외한 모든 부분을 메타데이터로 사용
        metadata = chunk.copy()
        del metadata["introduction"]

        # 메타데이터는 리스트 형식이면 안되므로 문자열로 처리 
        if metadata["keyword"]:
            metadata["keyword"] = ", ".join(map(str, metadata["keyword"]))
        else:
            metadata["keyword"] = ""  

        if metadata["genre"]:
            metadata["genre"] = ", ".join(map(str, metadata["genre"]))
        else:
            metadata["genre"] = ""             

        metadatas.append(metadata)

        # ids 값은 문자형이어야 함
        ids = str(chunk["chunk_index"])
        documents_ids.append(ids)

    collections.add(
        documents=documents,
        metadatas=metadatas,
        ids=documents_ids
    )

    print(f"ChromaDB에 문서 {len(documents)}개 추가 후, 저장 완료")
    
    return collections

def retrieve_chroma(collection: Collection, query: str, num: int):
    """
    ChromaDB에서 쿼리와 유사한 문서를 검색
    """
    results = collection.query(
        query_texts=[query], # 쿼리를 리스트 형태로 전달 
        n_results=num,
        include=["documents", "metadatas", "distances"]
    )

    retrieved_documents = []

    if results["documents"]:
        # 검색 결과가 있으면, 문서 리스트에 접근
        for i in range(len(results["documents"][0])):
            document = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            retrieved_documents.append({
                "document": document,
                "metadata": metadata,
                "distance": distance
            })

            print(f"제목: {metadata.get("title")}")
            print(f"작가: {metadata.get("author")}")
            print(f"키워드: {metadata.get("keyword")}")
            print(f"장르: {metadata.get("genre")}")
            print(f"내용: {document[:200]}...\n") # 긴 내용은 일부만 출력
            print(f"유사도 거리: {distance:.4f}\n")
    else:
        print("ChromaDB에서 검색된 문서가 없습니다") 
    
    return retrieved_documents
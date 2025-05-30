import os
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import tiktoken
from dotenv import load_dotenv
import google.generativeai as genai
from litellm import completion
from litellm import embedding
from tqdm import tqdm
from rag.chunking import chunk_file_by_line

# 도서 정보의 text 형식
def build_document_format(book:Dict[str, Any]) -> str:
    result_string = f"제목: {book['title']}\n"
    result_string += f"작가: {book['author']}\n"
    result_string += f"키워드: {', '.join(book['keywords'])}\n"
    result_string += f"장르: {', '.join(book['genres'])}\n"
    result_string += f"책 소개: {book['introduction']}\n"
    return result_string.strip()

# 토큰 계산 함수
def print_calculated_tokens(all_chunks:List[Dict[str, Any]]) -> None:
    tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")

    num_tokens = []
    for chunk in all_chunks:
        input_string = build_document_format(chunk)

        tokens = tokenizer.encode(input_string)
        num_tokens.append(len(tokens))

    num_tokens = np.array(num_tokens)

    print(f"Mean: {num_tokens.mean()}, Std: {num_tokens.std()}")
    print(f"Min: {num_tokens.min()}")
    print(f"Max: {num_tokens.max()}")
    print(f"Top 1%: {np.percentile(num_tokens, 99)}")
    print(f"Top 5%: {np.percentile(num_tokens, 95)}")
    print(f"Top 10%: {np.percentile(num_tokens, 90)}")
    print(f"Token Sum: {num_tokens.sum()}")

# 청크 데이터를 text 형식으로 만든 문자열 리스트
def trans_chunk_to_text(all_chunks: List[Dict[str, Any]]) -> List[str]:
    texts_to_embed = []
    for chunk in all_chunks:
        text = build_document_format(chunk)
        texts_to_embed.append(text)

    return texts_to_embed


def make_book_embedding(book_texts: List[str], model_name):
    embeddings_list = []

    with tqdm(total=len(book_texts), desc="Embedding Progress") as pbar:
        for i, text in enumerate(book_texts):
            try:
                response = embedding(
                    model=model_name,
                    input=[text],
                )
                embeddings_list.append(response.data[0]["embedding"])
                pbar.update(1)

            except Exception as e:
                print(f"\nError: chunk {i+1}: {e}")
                break
        
    book_embeddings = np.array(embeddings_list)

    return book_embeddings


def make_query_embeding(query: str, model_name: str):
    try:
        response = embedding(
            model=model_name,
            input=[query],
        )
        if response.data and len(response.data) > 0:
            query_embedding = np.array(response.data[0]["embedding"])
        else:
            return np.array([])
            
    except Exception as e:
        print(f"\n쿼리 임베딩 중 오류 발생: {e}")
        return np.array([])
    
    return query_embedding


def create_prompts(query, top_indices, all_chunks):
    SYSTEM_PROMPT = """
    너는 사용자의 독서 취향을 파악하여 가장 적합한 도서를 추천해 주는 친절하고 전문적인 사서야.
    너는 반드시 제공된 '관련 도서' 정보만을 활용해야 해.
    이를 기반으로 내가 원하는 책을 추천할 때 책내용을 바탕으로 추천한 이유를 같이 말해야 해.
    """.strip()

    document_strings = ""
    for i, top_index in enumerate(top_indices):
        document_strings += f"[{i+1}번째 도서]\n"
        document_strings += build_document_format(all_chunks[top_index])
        document_strings += "\n\n"

    document_strings = document_strings.strip()

    USER_PROMPT = f"""
    {query}

    # 관련 도서
    {document_strings}
    유사도 높은 책 순서대로 내가 좋아할 만한 도서 5권을 추천해.
    """.strip()

    return SYSTEM_PROMPT, USER_PROMPT


def make_completion(system_prompt: str, user_prompt: str, model_name: str):
    output = completion(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )
    print(f"output's type: {type(output.choices[0].message.content)}")
    return output.choices[0].message.content


def calc_similarity(book_embeddings, query_embedding, all_chunks):
    TOP_K = 5

    cosine_sims = book_embeddings.dot(query_embedding)
    top_indices = np.argsort(cosine_sims)[::-1][:TOP_K]

    for i in top_indices:
        print(f"제목: {all_chunks[i]['title']}")
        print(f"유사도: {cosine_sims[i]}")
        print()

    return cosine_sims, top_indices


if __name__ == '__main__':
    load_dotenv()

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    CSV_PATH = "../aladin_bestseller.csv"

    book_df = pd.read_csv(CSV_PATH, dtype=str)
    all_chunks = chunk_file_by_line(book_df)    

    print(f"chunk 개수: {len(all_chunks)}")

    tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
    embedding_model = "text-embedding-3-large" # "gemini/text-embedding-004" # "gemini-embedding-exp-03-07"
    completion_model = "gemini/gemini-2.0-flash"

    # 임베딩할 도서 chunk들을 텍스트 형식으로 변환
    book_texts = trans_chunk_to_text(all_chunks)

    # 도서 임베딩 생성
    book_embeddings = make_book_embedding(book_texts, embedding_model)

    # query 임베딩 생성
    query = "해리포터같은 책 읽고 싶어"
    query_embedding = make_query_embeding(query, embedding_model)

    # 유사도 계산
    cosine_sims, top_indices = calc_similarity(book_embeddings, query_embedding, all_chunks)

    # system prompt& user prompt 생성
    SYSTEM_PROMPT, USER_PROMPT = create_prompts(query, top_indices, all_chunks)

    # completion (litellm 사용)
    output = make_completion(SYSTEM_PROMPT, USER_PROMPT, completion_model)
    print("--- 추천 결과 ---")
    print(output)
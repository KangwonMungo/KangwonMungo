import pandas as pd
import re
from typing import List, Dict, Set, Any


def parse_list_from_string(s: str) -> List[str]:
    if s == "" or s.strip() == "[]":
        return []
    
    str_list = re.findall(r"'(.*?)'", s)
    return str_list


def parse_set_from_string(s: str) -> Set[str]:
    if s == "" or s.strip() == "{}":
        return set()
    
    str_list = re.findall(r"'(.*?)'", s)
    str_set = set(str_list)
    return str_set


def chunk_file_by_line(book_df: pd.DataFrame) ->  List[Dict[str, Any]]:
    all_chunk_data = []
    
    for index, row in book_df.iterrows():
        try:
            title = str(row.get('title', ''))
            author = str(row.get('author', ''))
            keyword_str = str(row.get('keyword', '[]'))
            genre_str = str(row.get('genre', '{}'))
            introduction = str(row.get('introduction', ''))
        except KeyError as e:
            print(f"컬럼({e})가 없습니다.")
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue

        keywords = parse_list_from_string(keyword_str)

        genre_set = parse_set_from_string(genre_str)
        genres = list(genre_set if genre_set else [])

        meta_data = {
            "title": title,
            "author": author,
            "keywords": keywords,
            "genres": genres,
        }

        chunk_data = {
            "chunk_index": index+1,
            "introduction": introduction,
            **meta_data
        }
        all_chunk_data.append(chunk_data)

    return all_chunk_data


def print_all_chunk_data(all_chunk_data: List[Dict[str, Any]]) -> None:
    if all_chunk_data:
        for i, chunk in enumerate(all_chunk_data):
            print(f"\nProcessed Chunk {i+1}:")
            print(f"  Title: {chunk.get('title', '')}")
            print(f"  Author: {chunk.get('author', '')}")
            print(f"  Keywords: {chunk.get('keywords', [])}")
            print(f"  Genres: {chunk.get('genres', [])}")
            print(f"  Chunk Index: {chunk.get('chunk_index', '')}")
            print(f"  Introduction Chunk: {chunk.get('introduction', '')}")
    else:
        print("생성된 Chunk 데이터가 없습니다.")


if __name__ == "__main__":
    CSV_PATH = "../aladin_bestseller.csv"

    try:
        book_df = pd.read_csv(CSV_PATH, dtype=str)
        print(f"파일 읽기 완료. 총 {len(book_df)} 행.")
        print('='*50)
        # chunking
        all_chunks = chunk_file_by_line(book_df)
        print(f"\n생성된 총 청크(행) 개수: {len(all_chunks)}")
        print_all_chunk_data(all_chunks)
        print('='*50)

    except FileNotFoundError:
        print(f"Error: '{CSV_PATH}'을 찾을 수 없음. 경로 확인 바람.")
    except pd.errors.EmptyDataError:
         print(f"Error: '{CSV_PATH}'이 비어있음.")
    except Exception as e:
        print(f"{CSV_PATH} 파일을 읽는 중 오류 발생: {e}")
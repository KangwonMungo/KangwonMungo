import pandas as pd
import re
import kss

CHUNK_SIZE = 2
INPUT_CSV_PATH = "./aladin_bestseller.csv"

all_chunk_data = []

# CSV 파일 열기
try:
    book_csv = pd.read_csv("./aladin_bestseller.csv", dtype=str) ### 파일 경로 확인
except FileNotFoundError:
    print("Error: aladin_bestseller.csv 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"CSV 파일을 읽는 중 오류 발생: {e}")
    exit()


# "[]" 형식 문자열 -> list
def parse_list_from_string(s):
    if s == "" or s.strip() == "[]": # 빈 문자열, "[]"
        return []
    
    str_list = re.findall(r"'(.*?)'", s) # ''(작은 따옴표) 안에 있는 모든 문자열이 담긴 리스트 반환
    return str_list


# "{}" 형식 문자열 -> set
def parse_set_from_string(s):
    if s == "" or s.strip() == "{}": # 빈 문자열, "{}"
        return set()
    
    str_list = re.findall(r"'(.*?)'", s)
    str_set = set(str_list)
    return str_set


# chunking 함수 - 문장 'CHUNK_SIZE'개씩 chunking
def chunk_sentences(sentence_list, chunk_size):
    all_chunks = []
    
    if not sentence_list: # 빈 리스트
        return all_chunks

    for i in range(0, len(sentence_list), chunk_size):
        selected_sentences_list = sentence_list[i:i + chunk_size] # 리스트 슬라이싱: 인덱스 범위를 넘어가도 오류 없이 가능한 끝까지 가져옴
        sentence_chunk = " ".join(selected_sentences_list)
        all_chunks.append(sentence_chunk)
    
    # 청크가 만들어지지 않은 경우 (e.g. 길이가 1인데 chunk_sizer가 2)
    if not all_chunks:
        all_chunks.append(" ".join(sentence_list)) # 하나의 청크로 만들기
    return all_chunks


def chunk_file_by_line():
    global all_chunk_data
    all_chunk_data = []
    
    for index, row in book_csv.iterrows():
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


def print_all_chunk_data():
    global all_chunk_data
    # 만들어진 chunk 확인
    if all_chunk_data:
        for i, data_item in enumerate(all_chunk_data):
            print(f"\nProcessed Chunk {i+1}:")
            print(f"  Title: {data_item.get('title', '')}")
            print(f"  Author: {data_item.get('author', '')}")
            print(f"  Keywords: {data_item.get('keywords', [])}")
            print(f"  Genres: {data_item.get('genres', [])}")
            print(f"  Chunk Index: {data_item.get('chunk_index', '')}")
            print(f"  Introduction Chunk: {data_item.get('introduction', '')}")
    else:
        print("생성된 Chunk 데이터가 없습니다.")

if __name__ == "__main__":
    chunk_file_by_line()
    print_all_chunk_data()
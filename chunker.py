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


def chunk_file():
    global all_chunk_data
    all_chunk_data = []

    for index, row in book_csv.iterrows():
        # data 컬럼 파싱 - row.get('컬럼', '기본값')
        try:
            title = str(row.get('title', ''))
            author = str(row.get('author', ''))
            keyword_str = str(row.get('keyword', '[]'))
            genre_str = str(row.get('genre', '{}'))
            introduction_str = str(row.get('introduction', ''))
        except KeyError as e:
            print(f"컬럼({e})가 없습니다.")
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue

        # 1-1. keyword 파싱
        keywords = parse_list_from_string(keyword_str) # "[]" -> []

        # 1-2. genre 파싱
        genre_set = parse_set_from_string(genre_str) # "{}" -> {}
        genres = list(genre_set if genre_set else []) # set을 list로 변환

        # 2. Introduction 텍스트 chunking
        introduction_chunks = [] # 'CHUNK_SIZE'개의 문장을 묶은 chunk들이 담을 리스트

        if introduction_str != "": # introduction 내용이 있으면, 없으면 그대로 빈 리스트
            try:
                # 문장 분리
                sentence_list = kss.split_sentences(introduction_str) # 문장 리스트 - 한 문장이 하나의 요소
            except Exception as e:
                print(f"문장 분리 실패: {e}")
                sentence_list = [introduction_str] # 분리 실패 시 하나의 문장으로

            # 분리된 문장이 있으면 chunking
            if sentence_list != []:
                introduction_chunks = chunk_sentences(sentence_list, CHUNK_SIZE) # [] or chunk 리스트 반환

            # 만약, chunk가 만들어지지 않은 경우
            if not introduction_chunks:
                introduction_chunks = [introduction_str] # 하나의 chunk로 만들기
        else:
            introduction_chunks = [""]
        
        # 3. 각 chunk에 메타데이터 연결하여 최종 데이터 생성
        # 현재 도서의 메타데이터
        meta_data = {
            "title": title,
            "author": author,
            "keywords": keywords,
            "genres": genres, # set -> list
        }

        for i, introduction_chunk in enumerate(introduction_chunks):
            chunk_data = {
                "chunk_index": i + 1,
                "introduction_chunk": introduction_chunk,
                **meta_data # 책 공통 메타데이터
            }
            all_chunk_data.append(chunk_data)
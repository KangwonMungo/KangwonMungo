import pandas as pd
import re
import kss

CHUNK_SIZE = 2
INPUT_CSV_PATH = "./aladin_bestseller.csv"

all_chunk_data_with_metadata = []

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
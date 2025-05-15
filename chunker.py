import pandas as pd
import re
import kss

CHUNK_SIZE = 2
INPUT_CSV_PATH = "./aladin_bestseller.csv"

all_chunk_data_with_metadata = []

try:
    book_csv = pd.read_csv("./aladin_bestseller.csv", dtype=str) ### 파일 경로 확인
except FileNotFoundError:
    print("Error: aladin_bestseller.csv 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"CSV 파일을 읽는 중 오류 발생: {e}")
    exit()
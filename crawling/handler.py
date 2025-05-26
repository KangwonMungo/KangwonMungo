import pandas as pd
import json

def process_bestseller(weekly_data: dict):
    """
    주차(week)별 베스트셀러 데이터를 받아서 ISBN으로 중복된 도서를 제거하고
    최종적으로 고유한 도서 정보 데이터들을 생성하여 json 파일로 저장하는 함수

    Args:
        weekly_data (dict): 주차를 키(int)로 하고,
                            해당 주차(week)의 도서 정보 리스트를 값으로 가지는 딕셔너리                         

    Returns:
        고유한 도서 정보 데이터를 'aladin_bestseller.json' 파일로 저장
    """
    try:
        all_books = {}
        
        for week, book_list in weekly_data.items():
            for book in book_list:
                # ISBN으로 중복 판단
                isbn = book.get("isbn")
                if isbn:
                    key = isbn.strip()
                if key not in all_books:
                    all_books[key] = book

        if all_books:
            books = list(all_books.values())
            processed_books = []
            for book_info in books:
                processed_book = {}
                for key, value in book_info.items():
                    if pd.isna(value): # NaN 처리
                        processed_book[key] = ""
                    elif isinstance(value, set): 
                        processed_book[key] = list(value)
                    else:
                        processed_book[key] = value
                processed_books.append(processed_book)
            with open("aladin_bestseller.json", "w", encoding="utf-8") as file:
                json.dump(processed_books, file, ensure_ascii=False, indent=4)
            print(f"총 {len(all_books)}개의 도서가 저장되었습니다")
        
        # if all_books:
        #     df = pd.DataFrame(list(all_books.values()))  # 딕셔너리의 값을 리스트로 변환하여 dataframe 생성
        #     df.to_csv("aladin_bestseller.csv", encoding="utf-8-sig", index=False)
        #     print(f"총 {len(df)}개의 도서가 저장되었습니다")
    
    except TypeError as e:
        print(f"타입 오류 발생{type(e)}")
    except Exception as e:
        print(f"최종 도서 데이터 오류 발생 {type(e)}")
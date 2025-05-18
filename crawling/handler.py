import pandas as pd

"""
주차별 주간 베스트 데이터들을 중복이 있는지 비교하여
최종 도서 데이터를 만들고 CSV 파일로 저장 
"""
def process_bestseller(weekly_data):
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
            df = pd.DataFrame(list(all_books.values()))  # 딕셔너리의 값을 리스트로 변환하여 dataframe 생성
            df.to_csv("aladin_bestseller.csv", encoding="utf-8-sig", index=False)
            print(f"총 {len(df)}개의 도서가 저장되었습니다")
    
    except TypeError:
        print({type(e)})
    except Exception as e:
        print(f"최종 도서 데이터 오류 발생 {type(e)}")
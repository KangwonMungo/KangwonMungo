import threading
from crawler import crawl_bestseller
from handler import process_bestseller
from date import get_current_dates

"""
각 주차(week)별로 크롤링된 베스트셀러 데이터를 저장하는 딕셔너리 
키는 주차(week) 번호, 값은 해당 주차의 도서 정보 리스트
예 : all_weekly_data[1]에는 1주차 데이터가 저장
"""
all_weekly_data = {} 

def crawl_weekly(current_year: int, current_month: int, week: int):
    """
    현재 날짜(연도+월+주차)를 기준으로 1주차부터 현재 주차(week)까지 
    알라딘 베스트셀러 데이터를 크롤링하여 all_weekly_data에 저장

    Args:
        year (int): 크롤링할 연도
        month (int): 크롤링할 월
        week (int): 크롤링할 주차(week)
    """    
    try:
        weekly_data = crawl_bestseller(page_num=6, year=current_year, month=current_month, week=week)
        all_weekly_data[week] = weekly_data
    except Exception as e:
        print(f"[{week}주차 크롤링 오류 발생: {e}]")

if __name__ == '__main__':
    current_year, current_month, current_week = get_current_dates()
    threads = []

    for week in range(1, 5):
        if week <= current_week:
            thread = threading.Thread(target=crawl_weekly, args=(current_year, current_month, week,))
            threads.append(thread)
            thread.start()
        else:
            print("아직 크롤링할 수 없습니다")
            break

    for thread in threads:
        thread.join()
        print("스레드가 종료되었습니다")

    process_bestseller(all_weekly_data)
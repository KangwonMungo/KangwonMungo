import threading
from crawler import crawl_bestseller
from handler import process_bestseller
from date import get_current_dates

# weekly_data_all[1]에는 1주차 데이터가 접근되는 식 
all_weekly_data = {} 

"""
현재 주(week)차 기준으로 n개의 스레드를 만들어
베스트셀러 데이터 크롤링을 병렬처리하는 함수 
"""
def crawl_weekly(year, month, week):
    try:
        weekly_data = crawl_bestseller(page_num=6, year=year, month=month, week=week)
        all_weekly_data[week] = weekly_data
    except Exception as e:
        print(f"[{week}주차 크롤링 오류 발생: {e}]")

if __name__ == '__main__':
    year, month, current_week = get_current_dates()
    threads = []

    for week in range(1, 5):
        if week <= current_week:
            thread = threading.Thread(target=crawl_weekly, args=(year, month, week,))
            threads.append(thread)
            thread.start()
        else:
            print("아직 크롤링할 수 없습니다")
            break

    for thread in threads:
        thread.join()
        print("스레드가 종료되었습니다")

    process_bestseller(all_weekly_data)
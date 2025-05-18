import datetime

"""
현재 년도와 월, 현재 주(week)차를 반환하는 함수 
"""
def get_current_dates():
    now = datetime.datetime.now()
    first_day = now.replace(day=1) # 이번 달의 1일 날짜
    first_weekday = first_day.weekday() # 이번 달의 첫날이 무슨 요일인지, 월요일=0 ~ 일요일=6
    day = now.day # 지금 날짜 

    # 첫 번째 월요일 날짜
    first_monday_day = 1
    if first_weekday > 0:
        first_monday_day += (7 - first_weekday)

    # 현재 날짜와 첫 번째 월요일 날짜 차이
    day_diff = day - first_monday_day

    if day_diff < 0:
        week = 0  # 첫 번째 월요일 이전 날짜는 0주차로 처리
    else:
        week = (day_diff // 7) + 1

    return now.year, now.month, week
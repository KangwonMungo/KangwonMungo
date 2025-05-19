import datetime

def get_current_dates():
    """
    현재 년도와 월, 현재 주차(week)를 반환하는 함수 
    주차(week) 계산은 해당 월의 첫번째 월요일을 기준

    Returns:
        tuple : 현재 년도(int), 현재 월(int), 현재 주차(int)를 담은 튜플
    """
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day
    
    first_day = now.replace(day=1) # 이번 달의 1일 날짜
    first_weekday = first_day.weekday() # 이번 달의 첫 번째 날이 무슨 요일인지, (월요일=0 ~ 일요일=6)

    # 1. 이번 달의 첫 번째 월요일 날짜를 계산
    first_monday_day = 1
    if first_weekday > 0:
        first_monday_day += (7 - first_weekday)

    # 2. 현재 날짜와 이번 달의 첫 번째 월요일 날짜 차이를 계산 
    day_diff = current_day - first_monday_day

    # 3. 날짜 차이를 이용하여 현재 주차를 계산
    if day_diff < 0:
        current_week = 0
    else:
        current_week = (day_diff // 7) + 1

    return current_year, current_month, current_week
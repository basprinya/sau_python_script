import requests
from datetime import date, datetime
import datetime

# ดึงรายชื่อนักเรียนมาตรวจสอบ
def timeStamp(res):
    print(res)

# ตรวจสอบเวลาที่ต้องเข้าเรียน
def checkDateTime(res):
    today = date.today()
    for item in res:

        # ตรวจสอบวันที่
        if str(today) == str(item['date']):

            # ตรวจสอบ time
            time_rp = datetime.datetime.now().time().strftime('%H:%M:%S')
            time_db_start = item['time_start']
            time_db_end = item['time_end']

            # ตรวจสอบเวลาเช็คชื่อ
            if time_rp >= time_db_start and time_rp <= time_db_end:
                timeStamp(res)
            else:
                print('เช็คชื่อไม่ได้')
        else:
            print('ไม่ตรง')

response = requests.get("http://localhost:30000/api/checks")
if response.status_code == 200:
    res = response.json()
    checkDateTime(res)
else:
    print(response.status_code)
    print(response.json())



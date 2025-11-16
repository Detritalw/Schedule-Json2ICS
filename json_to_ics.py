import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz

# --- 配置 ---
TIMEZONE = 'Asia/Shanghai'
ICS_FILENAME = '2025_school_schedule_with_weekly_review.ics'
START_DATE = datetime(2025, 10, 27)  # 10月27日起执行

# --- 严格按正式表格整理的课程时间（包含第十六节“周周清”）---
general_schedule = [
    {"period": "第一节",   "start_time": "07:40", "end_time": "08:20"},
    {"period": "第二节",   "start_time": "08:30", "end_time": "09:10"},
    {"period": "第三节",   "start_time": "09:20", "end_time": "10:00"},
    {"period": "第四节",   "start_time": "10:10", "end_time": "10:50"},
    {"period": "第五节",   "start_time": "11:00", "end_time": "11:30"},
    {"period": "第六节",   "start_time": "12:00", "end_time": "12:30"},
    {"period": "第七节",   "start_time": "13:40", "end_time": "14:20"},
    {"period": "第八节",   "start_time": "14:30", "end_time": "15:10"},
    {"period": "第九节",   "start_time": "15:25", "end_time": "15:55"},
    {"period": "第十节",   "start_time": "16:05", "end_time": "16:35"},
    {"period": "第十一节", "start_time": "16:40", "end_time": "17:10"},
    {"period": "第十二节", "start_time": "18:00", "end_time": "18:40"},
    {"period": "第十三节", "start_time": "18:50", "end_time": "19:30"},
    {"period": "第十四节", "start_time": "19:45", "end_time": "20:15"},
    {"period": "第十五节", "start_time": "20:25", "end_time": "20:55"},
    {"period": "第十六节", "start_time": "21:05", "end_time": "21:50"}  # 周周清（高一高二）
]

# --- 创建日历 ---
cal = Calendar()
cal.add('prodid', '-//2025 School Schedule with Weekly Review//')
cal.add('version', '2.0')
tz = pytz.timezone(TIMEZONE)

# --- 生成周一至周五课程 ---
for day_offset in range(5):
    current_day = START_DATE + timedelta(days=day_offset)
    for item in general_schedule:
        start_dt = tz.localize(datetime(
            current_day.year, current_day.month, current_day.day,
            int(item['start_time'].split(':')[0]),
            int(item['start_time'].split(':')[1])
        ))
        end_dt = tz.localize(datetime(
            current_day.year, current_day.month, current_day.day,
            int(item['end_time'].split(':')[0]),
            int(item['end_time'].split(':')[1])
        ))
        
        event = Event()
        event.add('summary', item['period'])
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('dtstamp', datetime.now(tz))
        event.add('uid', f"{start_dt.isoformat()}-{item['period']}@2025")
        cal.add_component(event)

# --- 生成周六课程（第一至七节）---
saturday = START_DATE + timedelta(days=5)
for item in general_schedule[:7]:
    start_dt = tz.localize(datetime(
        saturday.year, saturday.month, saturday.day,
        int(item['start_time'].split(':')[0]),
        int(item['start_time'].split(':')[1])
    ))
    end_dt = tz.localize(datetime(
        saturday.year, saturday.month, saturday.day,
        int(item['end_time'].split(':')[0]),
        int(item['end_time'].split(':')[1])
    ))
    
    event = Event()
    event.add('summary', f"{item['period']} (周六)")
    event.add('dtstart', start_dt)
    event.add('dtend', end_dt)
    event.add('dtstamp', datetime.now(tz))
    event.add('uid', f"{start_dt.isoformat()}-sat-{item['period']}@2025")
    cal.add_component(event)

# --- 生成周日课程（第十二至十六节）---
sunday = START_DATE + timedelta(days=6)
for item in general_schedule[11:]:
    start_dt = tz.localize(datetime(
        sunday.year, sunday.month, sunday.day,
        int(item['start_time'].split(':')[0]),
        int(item['start_time'].split(':')[1])
    ))
    end_dt = tz.localize(datetime(
        sunday.year, sunday.month, sunday.day,
        int(item['end_time'].split(':')[0]),
        int(item['end_time'].split(':')[1])
    ))
    
    event = Event()
    event.add('summary', f"{item['period']} (周日)")
    event.add('dtstart', start_dt)
    event.add('dtend', end_dt)
    event.add('dtstamp', datetime.now(tz))
    event.add('uid', f"{start_dt.isoformat()}-sun-{item['period']}@2025")
    cal.add_component(event)

# --- 保存文件 ---
with open(ICS_FILENAME, 'wb') as f:
    f.write(cal.to_ical())

print(f"✅ 已生成 ICS 文件: {ICS_FILENAME}")
print(f"  • 课程表从 {START_DATE.strftime('%Y-%m-%d')} 开始执行")
print("  • 周一至周五：完整16节课程（含第十六节“周周清”）")
print("  • 周六：第一节至第七节 (14:20结束)")
print("  • 周日：第十二节至第十六节 (18:00开始，21:50结束)")
print("\n💡 提示：第十六节“周周清”已按高一高二时间（21:05-21:50）导入")
print("如需高三版本（21:05-22:00），请告知，我可立即为您生成。")
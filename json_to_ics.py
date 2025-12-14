import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz
import os

# --- 配置 ---
TIMEZONE = 'Asia/Shanghai'
ICS_FILENAME = '2025_high_school_weekly_schedule.ics'
START_DATE = datetime(2025, 10, 27)  # 10月27日起执行
END_DATE = datetime(2026, 1, 20)     # 学期结束日期（请根据实际情况修改）

# --- 加载时间配置 ---
def load_time_schedule():
    try:
        with open('time_schedule.json', 'r', encoding='utf-8') as f:
            time_data = json.load(f)
            # 转换时间格式从列表到元组
            return {k: tuple(v) for k, v in time_data.items()}
    except FileNotFoundError:
        print("❌ 找不到 time_schedule.json 文件")
        return None
    except json.JSONDecodeError:
        print("❌ time_schedule.json 文件格式错误")
        return None

# --- 加载课程配置 ---
def load_course_schedule():
    try:
        with open('course_schedule.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 course_schedule.json 文件")
        return None
    except json.JSONDecodeError:
        print("❌ course_schedule.json 文件格式错误")
        return None

# 加载配置
daily_schedule = load_time_schedule()
class_schedule = load_course_schedule()

if not daily_schedule or not class_schedule:
    print("请确保 time_schedule.json 和 course_schedule.json 文件存在且格式正确")
    exit(1)

# --- 创建日历 ---
cal = Calendar()
cal.add('prodid', '-//2025 High School Weekly Schedule//')
cal.add('version', '2.0')
cal.add('x-wr-calname', '课表')  # 设置日历导入时的显示名称
tz = pytz.timezone(TIMEZONE)

# --- 生成周一至周五的课程（每周重复）---
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
day_names = ["周一", "周二", "周三", "周四", "周五"]

for day_offset in range(5):
    current_day_name = day_names[day_offset]
    current_day = START_DATE + timedelta(days=day_offset)
    
    for period in daily_schedule:
        if period not in class_schedule[current_day_name]:
            continue  # 如果该节无课程，则跳过
        
        subject_teacher = class_schedule[current_day_name][period]
        start_time_str, end_time_str = daily_schedule[period]
        
        start_dt = tz.localize(datetime(
            current_day.year, current_day.month, current_day.day,
            int(start_time_str.split(':')[0]),
            int(start_time_str.split(':')[1])
        ))
        end_dt = tz.localize(datetime(
            current_day.year, current_day.month, current_day.day,
            int(end_time_str.split(':')[0]),
            int(end_time_str.split(':')[1])
        ))
        
        event = Event()
        event.add('summary', subject_teacher)
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('dtstamp', datetime.now(tz))
        event.add('uid', f"{start_dt.isoformat()}-{period}@{current_day_name}")
        
        # 设置每周重复
        event.add('rrule', {'freq': 'WEEKLY', 'until': END_DATE})
        
        cal.add_component(event)

# --- 生成周六课程（第一至七节，不重复）---
saturday = START_DATE + timedelta(days=5)
for period in list(daily_schedule.keys())[:7]:  # 第一至七节
    start_time_str, end_time_str = daily_schedule[period]
    
    start_dt = tz.localize(datetime(
        saturday.year, saturday.month, saturday.day,
        int(start_time_str.split(':')[0]),
        int(start_time_str.split(':')[1])
    ))
    end_dt = tz.localize(datetime(
        saturday.year, saturday.month, saturday.day,
        int(end_time_str.split(':')[0]),
        int(end_time_str.split(':')[1])
    ))
    
    event = Event()
    event.add('summary', f"{period} (周六)")
    event.add('dtstart', start_dt)
    event.add('dtend', end_dt)
    event.add('dtstamp', datetime.now(tz))
    event.add('uid', f"{start_dt.isoformat()}-sat-{period}")
    cal.add_component(event)

# --- 生成周日课程（第十二至十六节，不重复）---
sunday = START_DATE + timedelta(days=6)
for period in list(daily_schedule.keys())[11:]:  # 第十二至十六节
    start_time_str, end_time_str = daily_schedule[period]
    
    start_dt = tz.localize(datetime(
        sunday.year, sunday.month, sunday.day,
        int(start_time_str.split(':')[0]),
        int(start_time_str.split(':')[1])
    ))
    end_dt = tz.localize(datetime(
        sunday.year, sunday.month, sunday.day,
        int(end_time_str.split(':')[0]),
        int(end_time_str.split(':')[1])
    ))
    
    event = Event()
    event.add('summary', f"{period} (周日)")
    event.add('dtstart', start_dt)
    event.add('dtend', end_dt)
    event.add('dtstamp', datetime.now(tz))
    event.add('uid', f"{start_dt.isoformat()}-sun-{period}")
    cal.add_component(event)

# --- 保存文件 ---
with open(ICS_FILENAME, 'wb') as f:
    f.write(cal.to_ical())

print(f"✅ 已生成 ICS 文件: {ICS_FILENAME}")
print(f"  • 课程表从 {START_DATE.strftime('%Y-%m-%d')} 开始，每周重复至 {END_DATE.strftime('%Y-%m-%d')}")
print("  • 周一至周五：每节课仅显示科目（不显示老师）")
print("  • 周六：第一节至第七节 (14:20结束)")
print("  • 周日：第十二节至第十六节 (18:00开始，21:50结束)")
print("\n💡 提示：所有工作日课程已设置为“每周重复”，周末课程为单次事件。")
print("💡 配置：课程和时间数据已从独立的 JSON 文件加载")
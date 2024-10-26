from flask import Blueprint, render_template, request, session, redirect, url_for
from datetime import datetime, timedelta
from .ReadCSV import read_rooms_from_csv, read_doctors_from_csv, read_time_slots_from_csv, read_specialties_from_csv, read_schedule_from_csv
import pandas as pd
import csv
import os

user_bp = Blueprint('user', __name__, template_folder='../Views/user')

def read_doctors_and_users():
    # Đường dẫn đến file doctors.csv
    doctors_csv_path = os.path.join(os.path.dirname(__file__), '../Models/doctors.csv')
    # Đường dẫn đến file users.csv
    users_csv_path = os.path.join(os.path.dirname(__file__), '../Models/user.csv')

    doctors_df = pd.read_csv(doctors_csv_path)
    users_df = pd.read_csv(users_csv_path)
    
    # Gộp DataFrame
    merged_df = pd.merge(doctors_df, users_df, left_on='user_id', right_on='id', how='inner')
    # Chọn các cột cần thiết
    result = merged_df[['doctor_id', 'name', 'specialty_name', 'username', 'password']]
    # Chuyển đổi DataFrame thành danh sách các từ điển
    return result.to_dict(orient='records')

# Hàm lấy lịch hàng tháng chia theo 4 tuần
def get_week_starts(year, month):
    # Ngày đầu tiên của tháng
    first_day = datetime(year, month, 1)
    # Tìm ngày bắt đầu của tuần chứa ngày đầu tiên của tháng
    first_week_start = first_day - timedelta(days=first_day.weekday())
    # Tạo danh sách ngày bắt đầu của 4 tuần trong tháng
    return [first_week_start + timedelta(weeks=i) for i in range(4)]

# Hàm lấy lịch của bác sĩ theo tháng
def get_monthly_schedule(doctor_id, year, month):
    # Đường dẫn đến file chứa lịch trình
    schedule_file_path = os.path.join(os.path.dirname(__file__), '../Models/schedule.csv')
    schedule_data = read_schedule_from_csv(schedule_file_path)

    # Xác định ngày bắt đầu của từng tuần trong tháng
    week_starts = get_week_starts(year, month)
    weekly_schedule = [{"Sáng": [None] * 7, "Chiều": [None] * 7, "Tối": [None] * 7} for _ in range(4)]

    # Đọc các tệp CSV cho room và time slot
    room_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
    time_slot_file_path = os.path.join(os.path.dirname(__file__), '../Models/time_slots.csv')
    rooms = read_rooms_from_csv(room_file_path)
    time_slots = read_time_slots_from_csv(time_slot_file_path)

    # Tạo từ điển để tìm room và time slot nhanh hơn
    room_dict = {room['room_id']: room for room in rooms}
    time_slot_dict = {slot['slot_id']: slot for slot in time_slots}

    # Lọc lịch của bác sĩ theo doctor_id, month, và year
    filtered_schedule = [
        row for row in schedule_data 
        if int(row['doctor_id']) == doctor_id and int(row['year']) == year and int(row['month']) == month
    ]

    # Duyệt qua từng bản ghi trong lịch đã lọc
    for row in filtered_schedule:
        day = int(row['day'])
        date = datetime(year, month, day)

        # Kiểm tra tuần nào mà ngày đó nằm trong
        for i, week_start in enumerate(week_starts):
            if week_start <= date < week_start + timedelta(days=7):
                time_slot_id = row['time_slot_id']
                room_id = row['room_id']

                # Tìm thông tin phòng và ca trực tương ứng
                room_info = room_dict.get(room_id, {"room_type": "Unknown"})
                time_slot_info = time_slot_dict.get(time_slot_id, {"time_slot": "Unknown"})

                # Tên ca trực (Sáng, Chiều, Tối) dựa trên `time_slot`
                time_slot_name = time_slot_info['time_slot']

                # Xác định thứ trong tuần
                column_index = (date.weekday()) % 7  # Thứ Hai = 0, ..., Chủ Nhật = 6

                # Đảm bảo dữ liệu vào đúng ô trong bảng
                weekly_schedule[i][time_slot_name][column_index] = {
                    "date": date.strftime("%d/%m/%Y"),
                    "room_type": room_info['room_type']
                }

    return weekly_schedule

@user_bp.route('/')
def user():
    if 'user' in session:
        logged_in_username = session['user']  # Lấy username từ session
        doctors_data = read_doctors_and_users()
        # Lọc chỉ thông tin của người dùng đã đăng nhập
        user_doctor_data = [doctor for doctor in doctors_data if doctor['username'] == logged_in_username]
        
        if user_doctor_data:
            session['doctor_id'] = user_doctor_data[0]['doctor_id']  # Lưu doctor_id vào session
            # Chuyển hướng đến lịch của bác sĩ
            return redirect(url_for('user.user_schedule', doctor_id=session['doctor_id'], week_index=0))
    else:
        user_doctor_data = []

    return render_template('Profile_users.html', doctors=user_doctor_data, username=logged_in_username)

# Trang lịch trình của bác sĩ theo tuần
@user_bp.route('/schedule/month/<int:week_index>')
def user_schedule(week_index):
    doctor_id = session.get('doctor_id')  # Lấy doctor_id từ session
    if not doctor_id:
        return redirect(url_for('user.user'))  # Nếu không có doctor_id, chuyển hướng về trang đăng nhập

    # Lấy năm và tháng từ query parameters, mặc định là năm và tháng hiện tại
    year = request.args.get('year', datetime.today().year, type=int)
    month = request.args.get('month', datetime.today().month, type=int)

    # Lấy lịch theo tháng chia theo tuần
    monthly_schedule = get_monthly_schedule(doctor_id, year, month)

    # Kiểm tra tuần hợp lệ
    if week_index < 0 or week_index >= len(monthly_schedule):
        week_index = 0  # Mặc định về tuần đầu tiên nếu chỉ số ngoài phạm vi

    weekly_schedule = monthly_schedule[week_index]

    # Đọc danh sách bác sĩ để tìm tên bác sĩ
    doctors_file_path = os.path.join(os.path.dirname(__file__), '../Models/doctors.csv')
    doctors = read_doctors_from_csv(doctors_file_path)
    doctor_name = next((doctor['name'] for doctor in doctors if int(doctor['doctor_id']) == doctor_id), "Unknown Doctor")

    return render_template(
        'schedule.html',
        weekly_schedule=weekly_schedule,
        year=year,
        month=month,
        week_index=week_index,
        doctor_id=doctor_id,
        doctor_name=doctor_name,
        last_week=(week_index == len(monthly_schedule) - 1),
        first_week=(week_index == 0)
    )

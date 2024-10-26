from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
import csv
import os

# Khởi tạo Blueprint cho admin
admin_bp = Blueprint('admin', __name__, template_folder='../Views/admin')

# Định nghĩa hàm để đọc file CSV
def read_csv(file_path):
    data = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"File {file_path} không tồn tại.")
    return data

def read_rooms_from_csv(file_path):
    rooms = read_csv(file_path)
    return [
        {'room_id': row['room_id'], 'room_type': row['room_type'], 'specialty_id': row['specialty_id']}
        for row in rooms
    ]

def read_doctors_from_csv(file_path):
    doctors = read_csv(file_path)
    return [
        {'doctor_id': row['doctor_id'], 'name': row['name'], 'specialty_name': row['specialty_name'], 'user_id': row['user_id']}
        for row in doctors
    ]

def read_time_slots_from_csv(file_path):
    return read_csv(file_path)

def read_specialties_from_csv(file_path):
    specialties = read_csv(file_path)
    return {row['specialty_id']: row['specialty_name'] for row in specialties}

def read_schedule_from_csv(file_path):
    return read_csv(file_path)

# Hàm lấy danh sách bác sĩ theo room_id
def get_all_doctors(room_id):
    doctors_file_path = os.path.join(os.path.dirname(__file__), '../Models/doctors.csv')
    doctors = read_doctors_from_csv(doctors_file_path)
    room_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
    rooms = read_rooms_from_csv(room_file_path)
    specialties_file_path = os.path.join(os.path.dirname(__file__), '../Models/specialtys.csv')
    specialties = read_specialties_from_csv(specialties_file_path)

    specialty_id = next((room['specialty_id'] for room in rooms if room['room_id'] == str(room_id)), None)

    if specialty_id is None:
        print(f"Không tìm thấy specialty_id cho room_id: {room_id}")
        return []

    specialty_name = specialties.get(specialty_id)
    filtered_doctors = [doctor for doctor in doctors if doctor['specialty_name'] == specialty_name]
    
    return filtered_doctors

# Hàm lấy thông tin phòng theo room_id
def get_room_by_id(room_id):
    csv_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
    rooms = read_rooms_from_csv(csv_file_path)
    return next((room for room in rooms if room['room_id'] == str(room_id)), None)

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
    schedule_file_path = os.path.join(os.path.dirname(__file__), '../Models/schedule.csv')
    schedule_data = read_schedule_from_csv(schedule_file_path)

    # Xác định tuần bắt đầu trong tháng
    week_starts = get_week_starts(year, month)
    weekly_schedule = [{"Sáng": [], "Chiều": [], "Tối": []} for _ in range(4)]  # Giả định có 4 tuần

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

                # Đọc thông tin phòng và ca trực từ các file
                room_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
                time_slot_file_path = os.path.join(os.path.dirname(__file__), '../Models/time_slots.csv')
                rooms = read_rooms_from_csv(room_file_path)
                time_slots = read_time_slots_from_csv(time_slot_file_path)

                # Tìm thông tin phòng và ca trực tương ứng
                room_info = next((room for room in rooms if room['room_id'] == room_id), None)
                time_slot_info = next((slot for slot in time_slots if slot['slot_id'] == time_slot_id), None)

                time_slot_name = time_slot_info['time_slot'] if time_slot_info else "Unknown"
                weekly_schedule[i][time_slot_name].append({
                    "date": date.strftime("%d/%m/%Y"),
                    "room_type": room_info['room_type'] if room_info else "Unknown"
                })

    return weekly_schedule

# Trang Dashboard của Admin
@admin_bp.route('/')
def dashboardadmin():
    return render_template('admin_dashboard.html')

# Trang Quản lý người dùng (manage_users)
@admin_bp.route('/manage_users')
def manage_users():
    csv_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
    rooms = read_rooms_from_csv(csv_file_path)
    return render_template('manage_user.html', rooms=rooms)

# Trang chi tiết bác sĩ theo phòng
@admin_bp.route('/manage_users/<int:room_id>')
def doctors_by_room(room_id):
    doctors_in_room = get_all_doctors(room_id)
    room = get_room_by_id(room_id)
    # Truyền thêm datetime vào template để sử dụng trong Jinja2
    return render_template('doctor_details.html', room=room, doctors=doctors_in_room, datetime=datetime)

# Trang lịch trình của bác sĩ theo tuần
@admin_bp.route('/doctor_schedule/<int:doctor_id>/month/<int:week_index>')
def doctor_weekly_schedule(doctor_id, week_index):
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
        'doctor_schedule.html',
        weekly_schedule=weekly_schedule,
        year=year,
        month=month,
        week_index=week_index,
        doctor_id=doctor_id,
        doctor_name=doctor_name,
        last_week=(week_index == len(monthly_schedule) - 1),
        first_week=(week_index == 0)
    )
from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from .ReadCSV import read_rooms_from_csv, read_doctors_from_csv, read_time_slots_from_csv, read_specialties_from_csv, read_schedule_from_csv
import csv
import os

# Khởi tạo Blueprint cho admin
admin_bp = Blueprint('admin', __name__, template_folder='../Views/admin')

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
    # Đường dẫn đến file chứa lịch trình
    schedule_file_path = os.path.join(os.path.dirname(__file__), '../Models/schedule.csv')
    schedule_data = read_schedule_from_csv(schedule_file_path)

    # Lọc thông tin tháng và năm cho bác sĩ cụ thể
    filtered_data = [row for row in schedule_data if int(row['doctor_id']) == doctor_id]

    # Kiểm tra xem có dữ liệu cho bác sĩ này không
    if not filtered_data:
        # Nếu không có, bạn có thể trả về thông báo hoặc giá trị mặc định
        return "Không tìm thấy lịch trình cho bác sĩ này.", 404

    # Lấy tháng và năm từ dữ liệu đã lọc
    year = filtered_data[0]['year']  # Lấy năm từ bản ghi đầu tiên
    month = filtered_data[0]['month']  # Lấy tháng từ bản ghi đầu tiên

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

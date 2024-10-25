from flask import Blueprint, render_template
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

# Hàm để lấy lịch làm việc của bác sĩ theo doctor_id
def get_doctor_schedule(doctor_id, room_id):
    # Đọc tất cả các file CSV
    doctors_file_path = os.path.join(os.path.dirname(__file__), '../Models/doctors.csv')
    rooms_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
    time_slots_file_path = os.path.join(os.path.dirname(__file__), '../Models/time_slots.csv')
    schedule_file_path = os.path.join(os.path.dirname(__file__), '../Models/schedule.csv')

    doctors = read_doctors_from_csv(doctors_file_path)
    rooms = read_rooms_from_csv(rooms_file_path)
    time_slots = read_csv(time_slots_file_path)
    schedules = read_csv(schedule_file_path)

    doctor = next((doc for doc in doctors if doc['doctor_id'] == str(doctor_id)), None)
    room = next((r for r in rooms if r['room_id'] == str(room_id)), None)

    if not doctor or not room:
        return None, None, None

    # Khởi tạo schedule_data với tuần
    schedule_data = {week: {day: {'Sáng': [], 'Chiều': [], 'Tối': []} for day in range(1, 8)} for week in range(1, 6)}

    for entry in schedules:
        if entry['doctor_id'] == str(doctor_id) and entry['room_id'] == str(room_id):
            day = int(entry['day'])
            week = (day - 1) // 7 + 1  # Xác định tuần theo ngày trong tháng
            day_of_week = (day - 1) % 7 + 1  # Xác định ngày trong tuần
            time_slot_id = entry['time_slot_id']
            time_slot = next((slot for slot in time_slots if slot['slot_id'] == time_slot_id), None)
            if time_slot:
                schedule_data[week][day_of_week][time_slot['time_slot']].append(entry)

    return doctor, room, schedule_data

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
    return render_template('doctor_details.html', room=room, doctors=doctors_in_room)

# Trang lịch bác sĩ
@admin_bp.route('/doctor_schedule/<int:doctor_id>/<int:room_id>')
def doctor_schedule(doctor_id, room_id):
    doctor, room, schedule_data = get_doctor_schedule(doctor_id, room_id)

    if not doctor:
        return "Không tìm thấy thông tin bác sĩ", 404

    return render_template('doctor_schedule.html', doctor=doctor, room=room, schedule_data=schedule_data)

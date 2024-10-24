from flask import Blueprint, render_template, url_for
import csv
import os

# Khởi tạo Blueprint cho admin
admin_bp = Blueprint('admin', __name__, template_folder='../Views/admin')

# Định nghĩa hàm để đọc file CSV
def read_rooms_from_csv(file_path):
    rooms = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rooms.append({
                    'room_id': row['room_id'],
                    'room_type': row['room_type']
                })
    except FileNotFoundError:
        print(f"File {file_path} không tồn tại.")
    return rooms

# Hàm để lấy danh sách bác sĩ
def get_all_doctors():
    return [
        {'doctor_id': 1, 'name': "Bác sĩ A", 'specialty': "Khoa Nội tổng hợp", 'room_id': 1, 'time_slot': "Sáng"},
        {'doctor_id': 2, 'name': "Bác sĩ B", 'specialty': "Khoa Nội tim mạch", 'room_id': 2, 'time_slot': "Chiều"},
        # Thêm các bác sĩ khác
    ]

def get_room_by_id(room_id):
    csv_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')  
    rooms = read_rooms_from_csv(csv_file_path)  # Truyền file_path vào đây
    for room in rooms:
        if room['room_id'] == room_id:
            return room
    return None

# Trang Dashboard của Admin
@admin_bp.route('/')
def dashboardadmin():
    return render_template('admin_dashboard.html')

# Trang Quản lý người dùng (manage_users)
@admin_bp.route('/manage_users')
def manage_users():
    # Đường dẫn tới file rooms.csv
    csv_file_path = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')

    # Đọc dữ liệu từ file CSV
    rooms = read_rooms_from_csv(csv_file_path)

    # Truyền dữ liệu rooms tới template manage_user.html
    return render_template('manage_user.html', rooms=rooms)

# Trang Quản lý lịch bác sĩ
@admin_bp.route('/doctor_schedule')
def schedule():
    return render_template('schedule.html')

# Trang xem chi tiết bác sĩ theo khoa
@admin_bp.route('/manage_users/<int:room_id>')
def doctors_by_room(room_id):
    # Lọc danh sách bác sĩ theo phòng
    doctors_in_room = [doctor for doctor in get_all_doctors() if doctor['room_id'] == room_id]
    room = get_room_by_id(room_id)

    return render_template('doctor_details.html', room=room, doctors=doctors_in_room)

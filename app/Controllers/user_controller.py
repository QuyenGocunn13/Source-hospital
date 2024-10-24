from flask import Blueprint, render_template, session
import pandas as pd
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
    result = merged_df[['doctor_id', 'name', 'specialty', 'username', 'password']]
    # Chuyển đổi DataFrame thành danh sách các từ điển
    return result.to_dict(orient='records')

def read_schedule():
    # Đường dẫn đến file schedule.csv
    schedule_csv_path = os.path.join(os.path.dirname(__file__), '../Models/schedule.csv')
    # Đọc file CSV
    schedule_df = pd.read_csv(schedule_csv_path)
    # Chọn các cột cần thiết
    result = schedule_df[['doctor_id', 'room_id', 'time_slot_id', 'day']]
    # Chuyển đổi DataFrame thành danh sách các từ điển
    return result.to_dict(orient='records')

@user_bp.route('/')
def user():
    if 'user' in session:
        logged_in_username = session['user']  # Lấy username từ session
        doctors_data = read_doctors_and_users()
        # Lọc chỉ thông tin của người dùng đã đăng nhập
        user_doctor_data = [doctor for doctor in doctors_data if doctor['username'] == logged_in_username]
    else:
        user_doctor_data = []

    return render_template('Profile_users.html', doctors=user_doctor_data, username=logged_in_username)

@user_bp.route('/schedule')
def schedule():
    # Đọc lịch từ file schedule.csv
    schedule_data = read_schedule()
    return render_template('schedule.html', schedule=schedule_data)
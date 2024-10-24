import os
import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bp = Blueprint('auth', __name__, template_folder='../Views/Auth')

# Hàm để kiểm tra username và password từ file CSV
def validate_login(username, password):
    # Xác định đường dẫn tuyệt đối tới file CSV trong folder Models
    csv_file_path = os.path.join(os.path.dirname(__file__), '../Models/user.csv')
    
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['username'] == username and row['password'] == password:
                return True, row['role']  # Trả về True nếu tìm thấy, kèm theo vai trò
    return False, None

# Trang đăng nhập
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Kiểm tra đăng nhập từ file CSV
        valid, role = validate_login(username, password)
        if valid:
            session['user'] = username  # Lưu thông tin người dùng vào session
            session['role'] = role  # Lưu vai trò vào session
            flash('Đăng nhập thành công!', 'success')

            # Chuyển hướng dựa trên vai trò
            if role == 'admin':
                return redirect(url_for('admin.dashboardadmin'))
            elif role == 'bacsi':
                return redirect(url_for('user.user'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')

    return render_template('Login.html')

# Xử lý đăng xuất
@auth_bp.route('/logout')
def logout():
    session.pop('user', None)  # Xóa thông tin người dùng khỏi session
    session.pop('role', None)  # Xóa vai trò
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('shared.index'))

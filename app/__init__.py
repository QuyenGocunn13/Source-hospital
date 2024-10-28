import os
from flask import Flask, redirect, url_for, render_template
from datetime import datetime
from Controllers.shared_controller import shared_bp
from Controllers.admin_controller import admin_bp
from Controllers.user_controller import user_bp
from Controllers.auth_controller import auth_bp  

def create_app():
    app = Flask(__name__)

    # Đặt secret_key cho ứng dụng Flask
    app.secret_key = os.urandom(24) 

    # Đăng ký các Blueprint
    app.register_blueprint(shared_bp, url_prefix='/shared')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')  
    
    # Đúng cách: không cần truyền tên filter dưới dạng chuỗi
    @app.add_template_filter
    def format_date(value, format="%d/%m/%Y"):
        try:
            # Nếu giá trị là chuỗi, chuyển sang datetime object
            if isinstance(value, str):
                value = datetime.strptime(value, '%Y-%m-%d') 
            return value.strftime(format)
        except ValueError:
            return value

    @app.route('/')
    def home():
        return redirect(url_for('shared.index'))

    @app.route('/rooms')
    def rooms():
        file_path = os.path.join(app.root_path, 'Models', 'rooms.csv')
        return render_template('/Admin/manage_user.html', rooms=rooms)

    return app

import os
from flask import Flask, redirect, url_for, render_template
from Controllers.shared_controller import shared_bp
from Controllers.admin_controller import admin_bp
from Controllers.user_controller import user_bp
from Controllers.auth_controller import auth_bp  

def create_app():
    app = Flask(__name__)
    app = Flask(__name__, static_folder='app/Assets')

    # Đặt secret_key cho ứng dụng Flask
    app.secret_key = os.urandom(24)  # Hoặc bạn có thể tự đặt một chuỗi ngẫu nhiên, vd: 'my_secret_key'

    # Đăng ký các Blueprint
    app.register_blueprint(shared_bp, url_prefix='/shared')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')  

    @app.route('/')
    def home():
        return redirect(url_for('shared.index'))

    @app.route('/rooms')
    def rooms():
        # Lấy đường dẫn đầy đủ đến file CSV
        file_path = os.path.join(app.root_path, 'Models', 'rooms.csv')
        return render_template('/Admin/manage_user.html', rooms=rooms)

    return app

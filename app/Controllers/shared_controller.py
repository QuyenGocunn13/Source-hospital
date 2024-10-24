from flask import Blueprint, render_template

shared_bp = Blueprint('shared', __name__, template_folder='../Views/Shared')

@shared_bp.route('/')
def index():
    return render_template('Index.html')

@shared_bp.route('/about')
def about():
    return render_template('About.html')

@shared_bp.route('/contact')
def contact(): 
    return render_template('Contact.html')

@shared_bp.route('/dichvu')
def dichvu():  
    return render_template('Dichvu.html')

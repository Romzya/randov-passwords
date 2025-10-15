
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
import random
import string

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# Храним пользователей в переменной (вместо фиксированного списка)
users = [
    {'username': 'admin', 'password': 'admin', 'role': 'admin'},
    {'username': 'user', 'password': 'user', 'role': 'user'}
]

def generate_password(length, difficulty):
    """Генерация пароля в зависимости от сложности"""
    if difficulty == 'easy':
        characters = string.ascii_letters
    else:
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/generate', methods=['POST'])
def generate_password_ajax():
    try:
        data = request.get_json()
        length = int(data.get('length', 12))
        difficulty = data.get('difficulty', 'easy')

        if length < 4:
            length = 4
        elif length > 50:
            length = 50

        password = generate_password(length, difficulty)

        return jsonify({
            'success': True,
            'password': password,
            'length': length,
            'difficulty': difficulty
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def load_users():
    return users

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Сначала регистрация
@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        for user in users:
            if user['username'] == username:
                flash('Имя пользователя уже существует', 'error')
                return redirect(url_for('register'))

        users.append({'username': username, 'password': password, 'role': 'user'})
        flash('Регистрация успешна! Теперь войдите в систему', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = user['username']
                session['role'] = user.get('role', 'user')
                flash(f'Добро пожаловать, {username}!', 'success')
                return redirect(url_for('index'))

        flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                           username=session.get('username'),
                           role=session.get('role'))

@app.route('/admin')
@login_required
def admin():
    if session.get('role') != 'admin':
        flash('У вас нет прав для доступа к этой странице', 'error')
        return redirect(url_for('index'))
    return render_template('admin.html', username=session.get('username'))

@app.route('/index')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import string
import secrets
import hashlib
import os
import re

app = Flask(__name__)
app.secret_key = 'im_gay'  # Замените на случайный ключ

USERS_FILE = 'users.txt'

def hash_password(password):
    """Хеширование пароля с использованием salt"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key

def verify_password(stored_password, provided_password):
    """Проверка пароля"""
    salt = stored_password[:32]
    stored_key = stored_password[32:]
    key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return key == stored_key

def load_users():
    """Загрузка пользователей из файла"""
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    username, password_hash_hex = line.strip().split(':', 1)
                    users[username] = bytes.fromhex(password_hash_hex)
    return users

def save_user(username, password_hash):
    """Сохранение пользователя в файл"""
    with open(USERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}:{password_hash.hex()}\n")

def is_valid_username(username):
    """Проверка валидности имени пользователя"""
    if len(username) < 1 or len(username) > 99999:
        return False
    return bool(re.match('^[a-zA-Z0-9_]+$', username))

def is_valid_password(password):
    """Проверка валидности пароля"""
    if len(password) < 1:
        return False
    return True

def generate_password(length=12, use_uppercase=True, use_lowercase=True, 
                     use_numbers=True, use_special=True, special_chars="!@#$%^&*"):
    """
    Генерация случайного пароля с заданными параметрами
    """
    characters = ""
    
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_special:
        characters += special_chars
    
    if not characters:
        return "Выберите хотя бы один тип символов"
    
    # Используем secrets для криптографически безопасной генерации
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        if username in users and verify_password(users[username], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Валидация
        if not is_valid_username(username):
            return render_template('register.html', error='Имя пользователя должно содержать от 3 до 20 символов (только буквы, цифры и подчеркивания)')
        
        if not is_valid_password(password):
            return render_template('register.html', error='Пароль должен содержать минимум 6 символов')

        if password != confirm_password:
            return render_template('register.html', error='Пароли не совпадают')
                
        users = load_users()
        

        if username in users:
            return render_template('register.html', error='Пользователь с таким именем уже существует')
        
        password_hash = hash_password(password)
        save_user(username, password_hash)
        
        session['username'] = username
        return redirect(url_for('login'))
    return render_template('register.html')
    

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
def generate():
    if 'username' not in session:
        return jsonify({'error': 'Требуется авторизация'})
    
    try:
        data = request.get_json()
        
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', True)
        use_lowercase = data.get('lowercase', True)
        use_numbers = data.get('numbers', True)
        use_special = data.get('special', True)
        special_chars = data.get('special_chars', "!@#$%^&*")
        
        # Валидация длины
        if length < 4:
            return jsonify({'error': 'Длина пароля должна быть не менее 4 символов'})
        if length > 128:
            return jsonify({'error': 'Длина пароля должна быть не более 128 символов'})
        
        password = generate_password(
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_numbers=use_numbers,
            use_special=use_special,
            special_chars=special_chars
        )
        
        return jsonify({'password': password})
    
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации: {str(e)}'})

@app.route('/generate_multiple', methods=['POST'])
def generate_multiple():
    if 'username' not in session:
        return jsonify({'error': 'Требуется авторизация'})
    
    try:
        data = request.get_json()
        
        count = int(data.get('count', 5))
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', True)
        use_lowercase = data.get('lowercase', True)
        use_numbers = data.get('numbers', True)
        use_special = data.get('special', True)
        special_chars = data.get('special_chars', "!@#$%^&*")
        
        if count < 1 or count > 20:
            return jsonify({'error': 'Количество паролей должно быть от 1 до 20'})
        
        passwords = []
        for _ in range(count):
            password = generate_password(
                length=length,
                use_uppercase=use_uppercase,
                use_lowercase=use_lowercase,
                use_numbers=use_numbers,
                use_special=use_special,
                special_chars=special_chars
            )
            passwords.append(password)
        
        return jsonify({'passwords': passwords})
    
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5123')

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import hashlib
import os
import json

USERS_FILE = 'users.txt'

class AuthHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        
        elif self.path == '/login.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('login.html', 'rb') as f:
                self.wfile.write(f.read())
        
        elif self.path == '/register.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('register.html', 'rb') as f:
                self.wfile.write(f.read())
        
        elif self.path == '/password_generator.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('password_generator.html', 'rb') as f:
                self.wfile.write(f.read())
        
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/register':
            self.handle_register()
        elif self.path == '/login':
            self.handle_login()
        else:
            self.send_error(404, "Not found")
    
    def handle_register(self):
        """Обработка регистрации"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]
        email = data.get('email', [''])[0]
        
        if not username or not password or not email:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('Все поля обязательны для заполнения')
            return
        
        # Хеширование пароля
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Проверка существования пользователя
        if self.user_exists(username):
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('Пользователь с таким именем уже существует')
            return
        
        # Сохранение пользователя
        user_data = {
            'username': username,
            'password': hashed_password,
            'email': email
        }
        
        self.save_user(user_data)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('Регистрация успешна! <a href="/login.html">Войти</a>')
    
    def handle_login(self):
        """Обработка входа"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]
        
        if not username or not password:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('Все поля обязательны для заполнения')
            return
# Хеширование введенного пароля
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Проверка учетных данных
        if self.verify_user(username, hashed_password):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('Вход выполнен успешно! <a href="/">На главную</a>')
        else:
            self.send_response(401)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('Неверное имя пользователя или пароль')
    
    def user_exists(self, username):
        """Проверка существования пользователя"""
        if not os.path.exists(USERS_FILE):
            return False
        
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    user_data = json.loads(line.strip())
                    if user_data.get('username') == username:
                        return True
                except json.JSONDecodeError:
                    continue
        return False
    
    def save_user(self, user_data):
        """Сохранение пользователя в файл"""
        with open(USERS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(user_data) + '\n')
    
    def verify_user(self, username, hashed_password):
        """Проверка учетных данных пользователя"""
        if not os.path.exists(USERS_FILE):
            return False
        
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    user_data = json.loads(line.strip())
                    if (user_data.get('username') == username and 
                        user_data.get('password') == hashed_password):
                        return True
                except json.JSONDecodeError:
                    continue
        return False
    
    def log_message(self, format, *args):
        """Отключение логов в консоль"""
        pass

def run_server():
    """Запуск сервера"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, AuthHandler)
    print('Сервер запущен на http://localhost:8000')
    print('Нажмите Ctrl+C для остановки сервера')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nСервер остановлен')
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
from flask import Flask, render_template, request, redirect, url_for, session, flash
import random, string
from datetime import datetime
import uuid
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-12345'

DB_NAME = 'college.db'

def create_users_table():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Пользователи (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    users = [
        ('admin', 'admin123', 'Администратор', 'admin'),
        ('user1', 'user123', 'Иван Иванов', 'user'),
        ('user2', 'user123', 'Мария Петрова', 'user')
    ]

    cursor.executemany('INSERT OR IGNORE INTO Пользователи (username, password, name, role) VALUES (?, ?, ?, ?)', users)

    connection.commit()
    connection.close()

def get_user_by_username(username):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute('''
    SELECT username, password, name, role
    FROM Пользователи
    WHERE username = ?
    ''', (username,))

    user = cursor.fetchone()
    connection.close()

    if user:
        return {
            'username': user[0],
            'password': user[1],  # пароль в открытом виде
            'name': user[2],
            'role': user[3]
        }
    return None

create_users_table()

def generate_password(length):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember_me = 'remember' in request.form

            user = get_user_by_username(username)

            if user and user['password'] == password:
                session['username'] = username
                session['user_info'] = user
                session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                session['session_id'] = str(uuid.uuid4())[:8]

                if remember_me:
                    session.permanent = True
                    flash('Сессия будет сохранена на 30 минут', 'info')
                else:
                    session.permanent = False

                flash(f'Вы успешно вошли в систему, {user["name"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверное имя пользователя или пароль', 'error')

        return render_template('index.html', show_login=True)

    password = ""
    if request.method == 'POST':
        try:
            length = int(request.form.get('length', 12))
            if length <= 0:
                password = "Длина пароля должна быть больше 0"
            else:
                password = generate_password(length)
        except ValueError:
            password = "Ошибка: введите целое число"

    return render_template('index.html',
                           show_login=False,
                           password=password,
                           user=session.get('user_info'),
                           login_time=session.get('login_time'))

@app.route('/logout')
def logout():
    username = session.get('username', 'Гость')
    session.clear()
    flash(f'Вы вышли из системы. До свидания, {username}!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

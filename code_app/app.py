from flask import Flask, render_template, request, redirect, url_for, session, flash
import random, string
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-12345'

users = {
    'admin': {'password': 'admin123', 'name': 'Администратор', 'role': 'admin'},
    'user1': {'password': 'user123', 'name': 'Иван Иванов', 'role': 'user'},
    'user2': {'password': 'user123', 'name': 'Мария Петрова', 'role': 'user'}
}


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

            if username in users and users[username]['password'] == password:
                session['username'] = username
                session['user_info'] = users[username]
                session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                session['session_id'] = str(uuid.uuid4())[:8]

                if remember_me:
                    session.permanent = True
                    flash('Сессия будет сохранена на 30 минут', 'info')
                else:
                    session.permanent = False

                flash(f'Вы успешно вошли в систему, {users[username]["name"]}!', 'success')
                # Перенаправляем на эту же страницу, но уже авторизованным
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
    """Выход из системы"""
    username = session.get('username', 'Гость')
    session.clear()
    flash(f'Вы вышли из системы. До свидания, {username}!', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
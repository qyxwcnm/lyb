from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import HOST, PORT, DEBUG, SECRET_KEY, MSG_FILE, USER_FILE

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 自动初始化文件
for f in [MSG_FILE, USER_FILE]:
    if not os.path.exists(f):
        with open(f, 'w', encoding='utf-8') as fobj:
            json.dump([], fobj, ensure_ascii=False, indent=2)

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 分页
def paginate(items, page=1, per_page=10):
    total = len(items)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], page, pages

# ----------------------
# 前台
# ----------------------
@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    messages = load_json(MSG_FILE)
    messages = messages[::-1]
    msgs, page, pages = paginate(messages, page)
    return render_template('index.html', messages=msgs,
                           user=session.get('user'),
                           page=page, pages=pages)

@app.route('/add', methods=['POST'])
def add_msg():
    name = request.form.get('name', '匿名').strip()
    content = request.form.get('content', '').strip()
    if not content:
        return jsonify({'code': 1, 'msg': '内容不能为空'})
    msg = {
        'id': len(load_json(MSG_FILE)) + 1,
        'name': name,
        'content': content,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    data = load_json(MSG_FILE)
    data.append(msg)
    save_json(MSG_FILE, data)
    return jsonify({'code': 0, 'msg': '发布成功'})

# ----------------------
# 注册
# ----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    if not username or not password:
        return jsonify({'code': 1, 'msg': '账号密码不能为空'})
    users = load_json(USER_FILE)
    for u in users:
        if u['username'] == username:
            return jsonify({'code': 1, 'msg': '账号已存在'})
    pwd_hash = generate_password_hash(password)
    users.append({
        'username': username,
        'password': pwd_hash,
        'is_admin': False
    })
    save_json(USER_FILE, users)
    return jsonify({'code': 0, 'msg': '注册成功，请登录'})

# ----------------------
# 登录
# ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    users = load_json(USER_FILE)
    for u in users:
        if u['username'] == username:
            if check_password_hash(u['password'], password):
                session['user'] = username
                session['is_admin'] = u.get('is_admin', False)
                return jsonify({'code': 0, 'msg': '登录成功', 'url': url_for('admin')})
    return jsonify({'code': 1, 'msg': '账号或密码错误'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ----------------------
# 管理后台 —— 【仅管理员可进】
# ----------------------
@app.route('/admin')
@app.route('/admin/page/<int:page>')
def admin(page=1):
    # 必须登录 + 必须是管理员
    if 'user' not in session or not session.get('is_admin'):
        return "⚠️ 无权限！只有管理员可以进入后台"

    msgs = load_json(MSG_FILE)[::-1]
    data, page, pages = paginate(msgs, page)
    return render_template('admin.html',
                           messages=data,
                           user=session['user'],
                           is_admin=session.get('is_admin', False),
                           page=page, pages=pages)

# ----------------------
# 删除留言 —— 【仅管理员可删】
# ----------------------
@app.route('/delete/<int:msg_id>')
def delete(msg_id):
    if 'user' not in session or not session.get('is_admin'):
        return "⚠️ 无权限！只有管理员可以删除"
    
    data = load_json(MSG_FILE)
    data = [m for m in data if m['id'] != msg_id]
    save_json(MSG_FILE, data)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)

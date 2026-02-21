// 提交留言
function submitMsg() {
  let name = document.getElementById('name').value.trim();
  let content = document.getElementById('content').value.trim();
  if (!content) {
    alert('请输入内容');
    return;
  }
  fetch('/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'name=' + encodeURIComponent(name) + '&content=' + encodeURIComponent(content)
  }).then(res => res.json())
    .then(data => {
      alert(data.msg);
      if (data.code === 0) location.reload();
    });
}

// 登录
function login() {
  let u = document.getElementById('username').value;
  let p = document.getElementById('password').value;
  fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'username=' + u + '&password=' + p
  }).then(res => res.json())
    .then(data => {
      alert(data.msg);
      if (data.code === 0) location.href = data.url;
    });
}

// 注册
function register() {
  let u = document.getElementById('username').value;
  let p = document.getElementById('password').value;
  fetch('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'username=' + u + '&password=' + p
  }).then(res => res.json())
    .then(data => {
      alert(data.msg);
      if (data.code === 0) location.href = '/login';
    });
}

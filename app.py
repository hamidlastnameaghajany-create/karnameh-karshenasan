from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from functools import wraps
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'demo-secret-key-change-in-production')

# ============================================================
# DEMO: کاربران بدون رمز (بعداً با Excel بجای این)
# ============================================================
MANAGERS = ['حمیدرضا آقاجانی', 'مهدیس جابری', 'امیررضا ایمانی', 'مینا مومنی']

# لیست کارشناسان — از داخل DASH_DATA
AGENTS_FROM_SHEET = [
  'محدثه یزدان پرست', 'فاطمه نفری', 'نسترن کاظمی', 'زهرا محمدی', 'شیما چراغی',
  'نگین عساکره', 'پرهام مرادی', 'مهسا ابراهیمی', 'نغمه امیری نیا', 'نفیسه محمودی',
  'پریماه پازوکی', 'آریانا هاجری', 'نرگس مرادی', 'مبینا حاجبی', 'روناک منجی پور',
  'فاطمه حسینی', 'فاطمه رجب بلوکات', 'منا محمدیوسفی', 'میلاد پارسا', 'علی ابراهیمی',
  'پریسا جعفری', 'انیس حسین زاده', 'پرستو احمدپور', 'رز برجاس', 'زینب شریفی',
  'محمد حسین سعیدی', 'فاطمه مغانلو', 'مشکات سیفی', 'شروین شعبانی', 'فاطمه عامری',
  'علیرضا محمدآبادی', 'عطا آهمند', 'محمد کشتکار', 'محمد متین بزرگمهر', 'محمد نوری',
  'محمدرضا مجیری', 'محمدکشتگار', 'عسل منصوری'
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_data():
    """return (name, role) from session"""
    if 'user' in session:
        return session['user'], session.get('role')
    return None, None

# ============================================================
# Login Pages
# ============================================================
LOGIN_HTML = '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ازکی · ورود کارنامه عملکرد</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  :root{ --bg:#141A26; --brand:#0096FF; --text:#EDF1F7; --text-dim:#8D97AC; }
  *{ box-sizing:border-box; }
  html,body{ margin:0; padding:0; background:var(--bg); color:var(--text);
    font-family:'Vazirmatn', sans-serif; min-height:100vh; }
  body{ display:flex; align-items:center; justify-content:center; padding:24px; }
  .login-outer{ width:100%; max-width:600px; }
  .logo-row{ display:flex; justify-content:center; margin-bottom:10px; }
  .logo{ display:flex; align-items:center; gap:10px; }
  .logo-mark{ width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg, var(--brand), #0067B5);
    display:flex; align-items:center; justify-content:center; box-shadow:0 4px 14px rgba(0,150,255,0.35); }
  .logo-word{ font-weight:800; font-size:17px; letter-spacing:.3px; }
  .login-tagline{ text-align:center; color:var(--text-dim); font-size:13px; margin-bottom:34px; }
  .role-grid{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  @media (max-width:560px){ .role-grid{ grid-template-columns:1fr; } }
  .role-card{ background:#1B2334; border:1px solid #2B3650; border-radius:16px; padding:28px 20px;
    text-align:center; cursor:pointer; transition:.18s ease; }
  .role-card:hover{ border-color:var(--brand); transform:translateY(-3px); box-shadow:0 10px 28px rgba(0,150,255,0.16); }
  .role-card .icon{ width:54px; height:54px; border-radius:14px; background:rgba(0,150,255,0.13);
    display:flex; align-items:center; justify-content:center; margin:0 auto 16px; }
  .role-card .icon svg{ width:26px; height:26px; color:var(--brand); }
  .role-card h3{ font-size:15.5px; margin:0 0 8px; font-weight:700; }
  .role-card p{ font-size:12px; color:var(--text-dim); margin:0; line-height:1.85; }
  .agent-panel{ background:#1B2334; border:1px solid #2B3650; border-radius:16px; padding:30px 26px; display:none; }
  .agent-panel.show{ display:block; }
  .back-link{ display:inline-flex; align-items:center; gap:6px; color:var(--text-dim);
    font-size:12.5px; cursor:pointer; margin-bottom:18px; border:none; background:none; padding:0; }
  .back-link:hover{ color:var(--brand); }
  .form-group{ display:flex; gap:10px; flex-wrap:wrap; }
  .form-group select{ flex:1; min-width:200px; background:#10151F; border:1px solid #2B3650;
    border-radius:10px; padding:10px 13px; color:var(--text); font-family:'Vazirmatn'; font-size:13px; }
  .form-group select:focus{ outline:2px solid var(--brand); outline-offset:1px; }
  .primary-btn{ background:linear-gradient(135deg, var(--brand), #0075C4);
    color:#fff; border:none; border-radius:10px; padding:11px 22px;
    font-size:13.5px; font-weight:700; cursor:pointer; transition:.15s; font-family:'Vazirmatn'; }
  .primary-btn:hover{ filter:brightness(1.08); }
</style>
</head>
<body>
<div class="login-outer">
  <div class="logo-row">
    <div class="logo">
      <div class="logo-mark">
        <svg viewBox="0 0 24 24" fill="none"><path d="M12 3l7 3.5v5c0 4.7-3 8.9-7 10.5-4-1.6-7-5.8-7-10.5v-5L12 3z" fill="white"/><path d="M9.3 12.2l2 2 3.6-4.2" stroke="#0067B5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <div class="logo-word">ازکی <b style="color:var(--brand);">| کارنامه</b></div>
    </div>
  </div>
  <div class="login-tagline">داشبرد کارنامه عملکردی — انتخاب کنید به عنوان چه نقشی وارد می‌شوید</div>

  <div id="roleChooser" class="role-grid">
    <form method="POST" action="/login" style="display:contents;">
      <button type="submit" name="role" value="manager" class="role-card" style="border:none;padding:0;text-align:left;display:flex;flex-direction:column;align-items:center;background:inherit;cursor:pointer;">
        <div class="icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19V9l8-5 8 5v10" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 19v-6h6v6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="9" r="1.4"/></svg>
        </div>
        <h3>ورود مدیریتی</h3>
        <p>مشاهده و مقایسه عملکرد تمام کارشناسان</p>
      </button>
    </form>
    <button id="agentBtn" class="role-card" style="border:none;padding:0;text-align:left;display:flex;flex-direction:column;align-items:center;background:inherit;">
      <div class="icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="8" r="3.4"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7" stroke-linecap="round"/></svg>
      </div>
      <h3>ورود کارشناس</h3>
      <p>مشاهده کارنامه شخصی و عملکرد خودتان</p>
    </button>
  </div>

  <div id="agentPanel" class="agent-panel">
    <button class="back-link" id="backBtn">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6" stroke-linecap="round" stroke-linejoin="round"/></svg>
      بازگشت
    </button>
    <form method="POST" action="/login">
      <h3 style="margin-top:0;">اسم خودتان را از لیست انتخاب کنید</h3>
      <div class="form-group">
        <select name="agent" id="agentSelect" required>
          <option value="">-- انتخاب کنید --</option>
          AGENT_OPTIONS_PLACEHOLDER
        </select>
        <button type="submit" name="role" value="agent" class="primary-btn">ورود</button>
      </div>
    </form>
  </div>
</div>

<script>
document.getElementById('agentBtn').addEventListener('click', () => {
  document.getElementById('roleChooser').style.display = 'none';
  document.getElementById('agentPanel').classList.add('show');
});
document.getElementById('backBtn').addEventListener('click', (e) => {
  e.preventDefault();
  document.getElementById('roleChooser').style.display = 'grid';
  document.getElementById('agentPanel').classList.remove('show');
});
</script>
</body>
</html>'''

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'manager':
            session['user'] = 'مدیر'
            session['role'] = 'manager'
            return redirect(url_for('dashboard'))
        elif role == 'agent':
            agent = request.form.get('agent')
            if agent in AGENTS_FROM_SHEET:
                session['user'] = agent
                session['role'] = 'agent'
                return redirect(url_for('dashboard'))
    
    agent_opts = '\n'.join(f'<option value="{a}">{a}</option>' for a in sorted(AGENTS_FROM_SHEET, key=lambda x: x))
    html = LOGIN_HTML.replace('AGENT_OPTIONS_PLACEHOLDER', agent_opts)
    return render_template_string(html)

# ============================================================
# Dashboard
# ============================================================
@app.route('/dashboard')
@login_required
def dashboard():
    user, role = get_user_data()
    
    # ساختن HTML داشبورد
    with open('/home/claude/final_dashboard3.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # اضافه کردن session/role info در HTML
    inject_js = f'''
    <script>
        window.AUTH_USER = "{user}";
        window.AUTH_ROLE = "{role}";
        window.AUTH_MANAGERS = {json.dumps(MANAGERS)};
    </script>
    '''
    
    # اضافه کردن logout link
    logout_js = '''
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const logoutBtns = document.querySelectorAll('#logoutBtn');
            logoutBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    fetch('/logout', {method: 'POST'})
                        .then(() => window.location.href = '/login');
                });
            });
        });
    </script>
    '''
    
    # درج اطلاعات auth قبل از closing body
    html = html.replace('</body>', inject_js + logout_js + '</body>')
    
    return render_template_string(html)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return 'OK', 200

# ============================================================
# API endpoints (اختیاری برای بعد)
# ============================================================
@app.route('/api/user')
@login_required
def get_user():
    user, role = get_user_data()
    return jsonify({'user': user, 'role': role})

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

import os, sqlite3, secrets
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

ROOT=Path(__file__).resolve().parent
DB=ROOT/'shop.db'
UPLOAD=ROOT/'static'/'uploads'; UPLOAD.mkdir(parents=True,exist_ok=True)
app=Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['MAX_CONTENT_LENGTH']=5*1024*1024
ALLOWED={'jpg','jpeg','png','webp'}
DEFAULT={
'shop_name':'PUBLIC SERVICE POINT','owner_name':'Sabid Ali','tagline':'আপনার বিশ্বস্ত ডিজিটাল সার্ভিস সেন্টার',
'phone':'8250117043','whatsapp':'8250117043','email':'','address':'Shivpur, Tapan, Dakshin Dinajpur, West Bengal',
'hours':'দোকানের সময় Admin Panel থেকে আপডেট করুন','facebook_url':'',
'about':'অনলাইন ফর্ম, প্রিন্টিং, স্ক্যানিং এবং বিভিন্ন ডিজিটাল পরিষেবার জন্য আমাদের সঙ্গে যোগাযোগ করুন।',
'owner_photo':'','hero_title':'আপনার প্রয়োজনীয় ডিজিটাল পরিষেবা, এক জায়গায়',
'hero_text':'অনলাইন আবেদন, প্রিন্ট, স্ক্যান, PAN, Aadhaar-সংক্রান্ত সহায়তা এবং আরও অনেক পরিষেবা।'}
CATS=[('Online Services','অনলাইন পরিষেবা'),('Print & Document','প্রিন্ট ও ডকুমেন্ট'),('ID Card & Photo','আইডি কার্ড ও ছবি'),('Government Forms','সরকারি ফর্ম ও আবেদন'),('Other Services','অন্যান্য পরিষেবা')]
SERVICES=[
('Online Form Fill-up','অনলাইন ফর্ম পূরণ','Online Services','বিভিন্ন অনলাইন আবেদন ফর্ম পূরণে সহায়তা।'),
('PAN Card Apply / Correction','PAN কার্ড আবেদন / সংশোধন','Government Forms','PAN আবেদন ও সংশোধন সংক্রান্ত সহায়তা।'),
('Aadhaar Download Assistance','আধার ডাউনলোডে সহায়তা','Government Forms','অনুমোদিত পদ্ধতিতে আধার ডাউনলোড সংক্রান্ত সহায়তা।'),
('Aadhaar Update Guidance','আধার আপডেট সংক্রান্ত নির্দেশনা','Government Forms','আধার আপডেটের নিয়ম ও প্রক্রিয়া সম্পর্কে সহায়তা।'),
('Voter Card Services','ভোটার কার্ড পরিষেবা','Government Forms','ভোটার কার্ডের আবেদন/সংশোধন সংক্রান্ত সহায়তা।'),
('Scholarship & Admission Forms','স্কলারশিপ ও ভর্তি ফর্ম','Government Forms','স্কলারশিপ এবং ভর্তি সংক্রান্ত অনলাইন ফর্ম পূরণ।'),
('Passport Form Assistance','পাসপোর্ট ফর্মে সহায়তা','Government Forms','পাসপোর্ট আবেদন ফর্ম পূরণ ও ডকুমেন্ট আপলোডে সহায়তা।'),
('Ration Card Services','রেশন কার্ড পরিষেবা','Government Forms','রেশন কার্ড সংক্রান্ত অনলাইন পরিষেবায় সহায়তা।'),
('Black & White Print','সাদা-কালো প্রিন্ট','Print & Document','A4 ও প্রয়োজনীয় ডকুমেন্ট প্রিন্ট।'),
('Colour Print','কালার প্রিন্ট','Print & Document','কালার ডকুমেন্ট ও ফর্ম প্রিন্ট।'),
('Document Scan','ডকুমেন্ট স্ক্যান','Print & Document','ডকুমেন্ট স্ক্যান করে ডিজিটাল কপি তৈরি।'),
('Photocopy','ফটোকপি','Print & Document','প্রয়োজনীয় কাগজপত্রের ফটোকপি।'),
('Lamination','ল্যামিনেশন','Print & Document','ডকুমেন্ট ও ছবির ল্যামিনেশন।'),
('PDF Create / Merge','PDF তৈরি / একত্র করা','Print & Document','ডকুমেন্ট থেকে PDF তৈরি, পেজ সাজানো ও মার্জ।'),
('Passport Size Photo','পাসপোর্ট সাইজ ছবি','ID Card & Photo','পাসপোর্ট সাইজ ছবি তৈরি ও প্রিন্ট।'),
('Photo Print','ফটো প্রিন্ট','ID Card & Photo','প্রয়োজনীয় সাইজে ছবি প্রিন্ট।'),
('ID Card / PVC Card Printing','আইডি কার্ড / PVC কার্ড প্রিন্টিং','ID Card & Photo','উপযুক্ত ডিজাইন ও উপকরণে বৈধ আইডি কার্ড/কার্ড প্রিন্টিং।'),
('Spiral Binding','স্পাইরাল বাইন্ডিং','Print & Document','প্রজেক্ট, নোটস ও ডকুমেন্ট বাইন্ডিং।'),
('Document Upload Assistance','ডকুমেন্ট আপলোডে সহায়তা','Online Services','অনলাইন আবেদনে প্রয়োজনীয় ফাইল আপলোডে সহায়তা।'),
('Custom Online Services','অন্যান্য অনলাইন পরিষেবা','Other Services','পরিষেবার প্রাপ্যতা ও নিয়ম জানতে দোকানে যোগাযোগ করুন।')]

def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
 c=db(); c.executescript('''CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE NOT NULL,display_name TEXT NOT NULL,sort_order INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS services(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,display_name TEXT NOT NULL,category TEXT NOT NULL,description TEXT DEFAULT '',price TEXT DEFAULT '',active INTEGER DEFAULT 1,sort_order INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY AUTOINCREMENT,customer_name TEXT NOT NULL,rating INTEGER NOT NULL,message TEXT NOT NULL,approved INTEGER DEFAULT 0,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
 CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,phone TEXT DEFAULT '',message TEXT NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,read INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS admin_users(username TEXT PRIMARY KEY,password_hash TEXT NOT NULL);''')
 for k,v in DEFAULT.items(): c.execute('INSERT OR IGNORE INTO settings VALUES(?,?)',(k,v))
 for i,(n,d) in enumerate(CATS): c.execute('INSERT OR IGNORE INTO categories(name,display_name,sort_order) VALUES(?,?,?)',(n,d,i))
 if c.execute('SELECT COUNT(*) FROM services').fetchone()[0]==0:
  for i,(n,d,cat,desc) in enumerate(SERVICES): c.execute('INSERT INTO services(name,display_name,category,description,sort_order) VALUES(?,?,?,?,?)',(n,d,cat,desc,i))
 if c.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]==0:
  
    if os.getenv('ADMIN_PASSWORD'):
        c.execute(
            'INSERT INTO admin_users VALUES(?,?)',
            (
                os.getenv('ADMIN_USERNAME', 'admin'),
                generate_password_hash(os.getenv('ADMIN_PASSWORD'))
            )
        )

 c.commit(); c.close()

def settings():
 c=db(); d={r['key']:r['value'] for r in c.execute('SELECT key,value FROM settings')}; c.close(); return {**DEFAULT,**d}
def token():
 if '_csrf' not in session: session['_csrf']=secrets.token_urlsafe(24)
 return session['_csrf']
app.jinja_env.globals['csrf_token']=token
@app.before_request
def csrf_check():
 if request.method=='POST' and (not session.get('_csrf') or not secrets.compare_digest(session.get('_csrf',''),request.form.get('_csrf',''))): abort(400,'Security token missing or expired. Refresh and try again.')
def admin_only(fn):
 @wraps(fn)
 def inner(*a,**kw):
  if not session.get('admin_user'): return redirect(url_for('login'))
  return fn(*a,**kw)
 return inner
@app.context_processor
def globals(): return {'site':settings(),'admin_logged_in':bool(session.get('admin_user'))}
@app.route('/')
def home():
 c=db(); cats=c.execute('SELECT * FROM categories ORDER BY sort_order,display_name').fetchall(); services=c.execute('SELECT * FROM services WHERE active=1 ORDER BY sort_order,display_name').fetchall(); reviews=c.execute('SELECT * FROM reviews WHERE approved=1 ORDER BY id DESC LIMIT 6').fetchall(); c.close()
 grouped=[(cat,[s for s in services if s['category']==cat['name']]) for cat in cats]; grouped=[x for x in grouped if x[1]]
 return render_template('index.html',grouped=grouped,reviews=reviews)
@app.route('/contact',methods=['POST'])
def contact():
 n=request.form.get('name','').strip()[:100]; p=request.form.get('phone','').strip()[:40]; m=request.form.get('message','').strip()[:2000]
 if not n or not m: flash('নাম এবং মেসেজ লিখুন।','error')
 else:
  c=db(); c.execute('INSERT INTO messages(name,phone,message) VALUES(?,?,?)',(n,p,m)); c.commit(); c.close(); flash('ধন্যবাদ! আপনার মেসেজ জমা হয়েছে।','success')
 return redirect(url_for('home')+'#contact')
@app.route('/review',methods=['POST'])
def review():
 n=request.form.get('customer_name','').strip()[:100]; m=request.form.get('message','').strip()[:1000]
 try: rating=max(1,min(5,int(request.form.get('rating','5'))))
 except ValueError: rating=5
 if n and m:
  c=db(); c.execute('INSERT INTO reviews(customer_name,rating,message) VALUES(?,?,?)',(n,rating,m)); c.commit(); c.close(); flash('মতামত জমা হয়েছে। প্রকাশের আগে যাচাই করা হবে।','success')
 else: flash('নাম এবং মতামত লিখুন।','error')
 return redirect(url_for('home')+'#reviews')
@app.route('/admin/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  c=db(); u=c.execute('SELECT * FROM admin_users WHERE username=?',(request.form.get('username','').strip(),)).fetchone(); c.close()
  if u and check_password_hash(u['password_hash'],request.form.get('password','')): session['admin_user']=u['username']; session.pop('_csrf',None); flash('Login successful.','success'); return redirect(url_for('admin'))
  flash('Username অথবা password সঠিক নয়।','error')
 return render_template('admin_login.html')
@app.route('/admin/logout',methods=['POST'])
@admin_only
def logout(): session.clear(); return redirect(url_for('home'))
@app.route('/admin')
@admin_only
def admin():
 c=db(); counts={'services':c.execute('SELECT COUNT(*) FROM services').fetchone()[0],'reviews':c.execute('SELECT COUNT(*) FROM reviews WHERE approved=0').fetchone()[0],'messages':c.execute('SELECT COUNT(*) FROM messages WHERE read=0').fetchone()[0]}; c.close(); return render_template('admin_dashboard.html',counts=counts)
@app.route('/admin/settings',methods=['GET','POST'])
@admin_only
def admin_settings():
 if request.method=='POST':
  c=db()
  for k in DEFAULT:
   if k!='owner_photo': c.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(k,request.form.get(k,'').strip()))
  f=request.files.get('owner_photo')
  if f and f.filename:
   filename=secure_filename(f.filename); ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
   if ext not in ALLOWED: flash('Photo JPG, PNG বা WEBP ফরম্যাটে দিন।','error')
   else:
    safe='owner_'+secrets.token_hex(8)+'.'+ext; f.save(UPLOAD/safe); c.execute("INSERT INTO settings(key,value) VALUES('owner_photo',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(safe,))
  c.commit(); c.close(); flash('Website information save হয়েছে।','success'); return redirect(url_for('admin_settings'))
 return render_template('admin_settings.html',settings=settings())
@app.route('/admin/services')
@admin_only
def admin_services():
 c=db(); services=c.execute('SELECT * FROM services ORDER BY category,sort_order,display_name').fetchall(); cats=c.execute('SELECT * FROM categories ORDER BY sort_order,display_name').fetchall(); c.close(); return render_template('admin_services.html',services=services,categories=cats)
@app.route('/admin/services/save',methods=['POST'])
@admin_only
def save_service():
 sid=request.form.get('id','').strip(); vals=(request.form.get('name','').strip()[:120],request.form.get('display_name','').strip()[:120],request.form.get('category','').strip()[:100],request.form.get('description','').strip()[:500],request.form.get('price','').strip()[:100],1 if request.form.get('active')=='on' else 0)
 if not vals[0] or not vals[1] or not vals[2]: flash('Service name, display name ও category আবশ্যক।','error'); return redirect(url_for('admin_services'))
 c=db()
 if sid: c.execute('UPDATE services SET name=?,display_name=?,category=?,description=?,price=?,active=? WHERE id=?',(*vals,sid))
 else: c.execute('INSERT INTO services(name,display_name,category,description,price,active) VALUES(?,?,?,?,?,?)',vals)
 c.commit(); c.close(); flash('Service save হয়েছে।','success'); return redirect(url_for('admin_services'))
@app.route('/admin/services/delete/<int:sid>',methods=['POST'])
@admin_only
def delete_service(sid):
 c=db(); c.execute('DELETE FROM services WHERE id=?',(sid,)); c.commit(); c.close(); flash('Service delete হয়েছে।','success'); return redirect(url_for('admin_services'))
@app.route('/admin/categories/save',methods=['POST'])
@admin_only
def save_category():
 n=request.form.get('name','').strip()[:100]; d=request.form.get('display_name','').strip()[:100]; c=db()
 try:
  if n and d: c.execute('INSERT INTO categories(name,display_name) VALUES(?,?)',(n,d)); c.commit(); flash('Category যোগ হয়েছে।','success')
 except sqlite3.IntegrityError: flash('এই category আগে থেকেই আছে।','error')
 c.close(); return redirect(url_for('admin_services'))
@app.route('/admin/reviews')
@admin_only
def admin_reviews():
 c=db(); rows=c.execute('SELECT * FROM reviews ORDER BY approved,id DESC').fetchall(); c.close(); return render_template('admin_reviews.html',reviews=rows)
@app.route('/admin/reviews/<int:rid>/<action>',methods=['POST'])
@admin_only
def review_action(rid,action):
 c=db()
 if action=='approve': c.execute('UPDATE reviews SET approved=1 WHERE id=?',(rid,))
 elif action=='hide': c.execute('UPDATE reviews SET approved=0 WHERE id=?',(rid,))
 elif action=='delete': c.execute('DELETE FROM reviews WHERE id=?',(rid,))
 c.commit(); c.close(); return redirect(url_for('admin_reviews'))
@app.route('/admin/messages')
@admin_only
def admin_messages():
 c=db(); rows=c.execute('SELECT * FROM messages ORDER BY read,id DESC').fetchall(); c.close(); return render_template('admin_messages.html',messages=rows)
@app.route('/admin/messages/<int:mid>/read',methods=['POST'])
@admin_only
def message_read(mid):
 c=db(); c.execute('UPDATE messages SET read=1 WHERE id=?',(mid,)); c.commit(); c.close(); return redirect(url_for('admin_messages'))
@app.errorhandler(413)
def too_large(_): return 'File too large. Maximum upload size is 5 MB.',413
init_db()
if __name__ == '__main__':
    app.run(debug=False)

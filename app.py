import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
# セキュリティ用の機能をインポート
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# 🚨 注目：GitHub公開用に、個人情報を含まない開発用キーにしています
app.secret_key = 'dev-secret-key-selection-app-2026'

# 💡 Renderでも絶対に迷子にならない安全なパスに固定します
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shukatsu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 💡 【超重要】ボタンが押された瞬間に強制的にテーブルを作る魔法
# ==========================================
@app.before_request
def create_tables():
    db.create_all()

# ==========================================
# 📊 データベースのテーブル（モデル）定義
# ==========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)                      # 自動で割り振られる背番号
    username = db.Column(db.String(80), unique=True, nullable=False)  # ユーザー名（被りNG）
    email = db.Column(db.String(120), nullable=False)                 # メールアドレス
    password = db.Column(db.String(120), nullable=False)

    # 基本情報のデータ
    phone = db.Column(db.String(30), nullable=True)
    postal = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(120), nullable=True)
    high_school = db.Column(db.String(10), nullable=True)     # 高校 卒業年月
    university_in = db.Column(db.String(10), nullable=True)   # 大学 入学年月
    university_out = db.Column(db.String(10), nullable=True)  # 大学 卒業年月

    # スキルのデータ
    license1 = db.Column(db.String(120), nullable=True)
    license2 = db.Column(db.String(120), nullable=True)
    license3 = db.Column(db.String(120), nullable=True)
    
    # 自己分析データ
    personality_strength = db.Column(db.Text)  # 性格と強み
    weakness_control = db.Column(db.Text)      # 弱みと意識
    gatutika = db.Column(db.Text)              # ガクチカ
    hardship = db.Column(db.Text)              # 困難と乗り跨え方
    future_vision = db.Column(db.Text)         # 将来どんな自分でありたい
    pros = db.Column(db.Text)                  # 長所
    cons = db.Column(db.Text)                  # 短所
    team_experience = db.Column(db.Text)       # チームでの経験
    memo = db.Column(db.Text)                  # メモ


class CompanyES(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # ユーザーと紐付け
    
    company_name = db.Column(db.String(100), nullable=False)  # 企業名
    status = db.Column(db.String(50), default="選考中")        # 選考ステータス
    deadline = db.Column(db.String(50))                       # 締め切り日
    es_question = db.Column(db.Text)                          # ESのお題
    es_answer = db.Column(db.Text)                            # 自分が書いた回答
    memo = db.Column(db.Text)                                 # メモ
    policy = db.Column(db.Text)                               # 企業の方針・理念
    intern_info = db.Column(db.Text)                          # インターン情報


# ==========================================
# 🗺️ ルーティング（各画面の処理）
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_email = request.form["mail"]
        password = request.form["pass"]

        # 入力されたメールアドレスを持つユーザーがいるか探す
        user = User.query.filter_by(email=login_email).first()

        # パスワードの答え合わせ
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            print(f"ログイン成功: {user.username}")
            return redirect(url_for("Dashboard"))
        else:
            return "<h1>エラー: メールアドレスまたはパスワードが間違っています</h1>"
            
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        mail = request.form["mail"]
        password = request.form["pass"]
        repassword = request.form["repass"]

        if password != repassword:
            return "<h1>エラー: パスワードが一致しません</h1>"
            
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return
@app.route('/init-db')
def init_db():
    db.create_all()
    return "<h1>データベースの作成が完了しました！アプリに戻って登録してください。</h1>"
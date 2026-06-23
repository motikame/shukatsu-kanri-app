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
    hardship = db.Column(db.Text)              # 困難と乗り越え方
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
            return "<h1>エラー: そのユーザー名は既に存在します</h1>"
        
        # パスワードを暗号化
        hashed_password = generate_password_hash(password)
        
        # データベースに新規登録
        new_user = User(username=username, email=mail, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        print(f"SQLに登録成功: {username}")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/Dashboard")
def Dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
        
    current_user = User.query.get(user_id)
    # ログイン中のユーザーの企業データを全件取得
    user_companies = CompanyES.query.filter_by(user_id=user_id).all()
    
    return render_template("Dashboard.html", user=current_user, companies=user_companies)


@app.route("/basic", methods=["GET", "POST"])
def basic():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    
    current_user = User.query.get(user_id)

    if current_user is None:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        current_user.phone = request.form["phone"]
        current_user.postal = request.form["postal"]
        current_user.address = request.form["address"]
        current_user.high_school = request.form["high_school"]
        current_user.university_in = request.form["university_in"]
        current_user.university_out = request.form["university_out"]
        current_user.license1 = request.form["license1"]
        current_user.license2 = request.form["license2"]
        current_user.license3 = request.form["license3"]
        
        db.session.commit()
        return redirect(url_for("basic"))

    return render_template("basic.html", user=current_user)


@app.route("/analysis", methods=["GET", "POST"])
def analysis():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    
    current_user = User.query.get(user_id)
    if current_user is None:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        current_user.personality_strength = request.form["personality_strength"]
        current_user.weakness_control = request.form["weakness_control"]
        current_user.gatutika = request.form["gatutika"]
        current_user.hardship = request.form["hardship"]
        current_user.future_vision = request.form["future_vision"]
        current_user.pros = request.form["pros"]
        current_user.cons = request.form["cons"]
        current_user.team_experience = request.form["team_experience"]
        current_user.memo = request.form["memo"]
        
        db.session.commit()
        return redirect(url_for("Dashboard")) 

    return render_template("Self-analysis.html", analysis=current_user)


@app.route("/company/edit/<int:company_id>", methods=["GET", "POST"])
def edit_company(company_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    
    # 新規登録(0)か編集(1以上)かを切り替え
    if company_id == 0:
        es_data = None
    else:
        es_data = CompanyES.query.filter_by(id=company_id, user_id=user_id).first()
        if not es_data:
            return "企業データが見つかりません", 404

    if request.method == "POST":
        if company_id == 0:
            # 新規登録の処理（方針やインターン情報もしっかりキャッチして保存する）
            es_data = CompanyES(
                user_id=user_id, 
                company_name=request.form["company_name"],
                status="選考中",
                policy=request.form["policy"],
                intern_info=request.form["intern_info"]
            )
            db.session.add(es_data)
        else:
            # 既存編集の処理（すべての変更を上書き）
            es_data.company_name = request.form["company_name"]
            es_data.policy = request.form["policy"]
            es_data.intern_info = request.form["intern_info"]
            
        db.session.commit() # データベースの書き換えを確定
        return redirect(url_for("Dashboard"))
        
    return render_template("company.html", es_data=es_data, company_id=company_id)


@app.route("/company/delete/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    
    # 削除したい企業データをデータベースから探す
    company = CompanyES.query.filter_by(id=company_id, user_id=user_id).first()
    
    if company:
        db.session.delete(company) # データベースから削除
        db.session.commit()        # 変更を確定！
        print(f"企業データを削除しました: {company.company_name}")
        
    return redirect(url_for("Dashboard"))


# ==========================================
# 💡 データベース手動作成用の隠しコマンドURL
# ==========================================
@app.route('/init-db')
def init_db():
    db.create_all()
    return "<h1>データベースの作成が完了しました！アプリに戻って登録してください。</h1>"


# ==========================================
# 🚀 アプリケーション起動
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
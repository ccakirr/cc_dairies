from flask import Flask, render_template, flash, redirect,url_for,session,logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

#kullanıcı giriş decorator' ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için giriş yapınız!","danger")
            return (redirect(url_for("login")))
    return decorated_function

class RegisterForm(Form):
    username = StringField("Kullanıcı Adı", validators=[validators.Length(min=4, max=8)])
    email = StringField("Email", validators=[validators.Email(message=" Lütfen geçerli bir Email adresi girin.")])
    password = PasswordField("Şifre", validators=[
        validators.DataRequired("Lütfen parola belirleyin"),
        validators.EqualTo(fieldname="confirm", message="Parolalar uyuşmuyor")
    ])
    confirm = PasswordField("Parola doğrula")

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Şifre")

class ArticleForm(Form):
    header = StringField("Başlık", validators=[validators.DataRequired()])
    content = TextAreaField("Konu", validators=[validators.DataRequired()])

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "cc_dairies"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.secret_key = "ccdairies"

mysql = MySQL(app)
@app.route("/")
def index():
    return(render_template("index.html"))

@app.route("/about")
def about():
    return(render_template("about.html"))

@app.route("/register", methods = ["POST", "GET"])
def register():
    form = RegisterForm(request.form)
    if (request.method == "POST" and form.validate()):
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(form.password.data)
        cursor = mysql.connection.cursor()
        cursor.execute("Insert into users(username, email, password) Values(%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla Kayıt Oldunuz.", "success")
        return (redirect(url_for("login")))
    else:
        return render_template("register.html",form = form)

@app.route("/login", methods = ["POST","GET"])
def login():
    form = LoginForm(request.form)
    if(request.method == "POST" and form.validate()):
        username = form.username.data
        password = form.password.data
        cursor = mysql.connection.cursor()
        data = cursor.execute("Select * from users where username = %s", (username,))
        if (data > 0):
            data_by_username = cursor.fetchone()
            if (sha256_crypt.verify(password, data_by_username["password"])):
                flash("Başarıyla giriş yapıldı.","success")
                session["logged_in"] = True
                session["username"] = username
                return(redirect(url_for("index")))
            else:
                flash("Hatalı parola.","danger")
                return (redirect(url_for("login")))
        else:
            flash("Hatalı kullanıcı adı.","danger")
            return redirect(url_for("login"))
    return (render_template("login.html",form=form))
@app.route("/dashboard")
@login_required
def dashboard():
    return(render_template("dashboard.html"))
@app.route("/logout")
def logout():
    session.clear()
    flash("Başarıyla çıkış yapıldı.", "success")
    return (redirect(url_for("index")))

@app.route("/addarticle", methods = ["GET","POST"])
@login_required
def add_article():
    form = ArticleForm(request.form)
    if (request.method == "POST" and form.validate()):
        author = session["username"]
        header = form.header.data
        content = form.content.data
        cursor = mysql.connection.cursor()
        cursor.execute("Insert into articles(header, author, content) values(%s, %s, %s)", (header, author, content,))
        mysql.connection.commit()
        cursor.close()
        flash("Makale başarıyla eklendi.","success")
        return(redirect(url_for("dashboard")))
    return (render_template("addarticle.html",form = form))

@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    res = cursor.execute("Select * from articles Where article_id between 1 and 10")
    if (res > 0):
        articles = cursor.fetchall()
        return(render_template("articles.html", articles = articles))
    else:
        flash("Gösterilecek makale bulunamadı.","danger")
        return(render_template("articles.html", articles=[]))

if(__name__ == "__main__"):
    app.run(debug=True)

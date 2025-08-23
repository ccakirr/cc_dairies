from flask import Flask, render_template, flash, redirect,url_for,session,logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

class RegisterForm(Form):
    username = StringField("Kullanıcı Adı", validators=[validators.Length(min=4, max=8)])
    email = StringField("Email", validators=[validators.Email(message=" Lütfen geçerli bir Email adresi girin.")])
    password = PasswordField("Şifre", validators=[
        validators.DataRequired("Lütfen parola belirleyin"),
        validators.EqualTo(fieldname="confirm", message="Parolalar uyuşmuyor")
    ])
    confirm = PasswordField("Parola doğrula")

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
        return (redirect(url_for("index")))
    else:
        return render_template("register.html",form = form)

if(__name__ == "__main__"):
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField, CKEditor
import datetime
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Post(db.Model):
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(50), nullable=False)
    date = mapped_column(String(50), nullable=False)
    body = mapped_column(String(50), nullable=False)
    author = mapped_column(String(50), nullable=False)
    subtitle = mapped_column(String(50), nullable=False)
    img_url = mapped_column(String(50), nullable=False)

with app.app_context():
    db.create_all()

# new-post
class NewPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    body = CKEditorField('Body of the post')
    submit = SubmitField('Create post')

def send_email(name, email, phone, message):
    sender = "roselinedemoacct@gmail.com"
    password = "nwaqugdcshamlern"
    recipients = "roselineodunze14@gmail.com"

    msg = MIMEText(f"Name: {name}\n Email: {email} \n Phone: {phone}\n Message: {message}")
    msg['Subject'] = "Contact Questions"
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())


@app.route('/')
def home():
    with app.app_context():
        all_posts = Post.query.order_by(Post.date.desc()).all()
    return render_template("index.html", posts=all_posts)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/post/<int:index>')
def post(index):
    requested_post = Post.query.get(index)
    return render_template("post.html", data=requested_post)

@app.route('/new-post', methods=["GET","POST"])
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        x = datetime.datetime.now()
        year = x.strftime("%Y")
        day = x.strftime("%d")
        month = x.strftime("%B")
        full_date = f"{month} {day}, {year}"
        body = form.body.data
        title = form.title.data
        subtitle = form.subtitle.data
        author = form.author.data
        img_url = form.img_url.data
        date = full_date
        with app.app_context():
            new_post = Post(
                title=title,
                date=date,
                body=body,
                author=author,
                img_url=img_url,
                subtitle=subtitle,
            )
            db.session.add(new_post)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("make-post.html", form=form)

@app.route("/edit-post/<int:index>", methods=["GET","POST"])
def edit_post(index):
    requested_post = Post.query.get(index)
    form = NewPost(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        img_url=requested_post.img_url,
        author=requested_post.author,
        body=requested_post.body
    )
    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        author = form.author.data
        img_url = form.img_url.data
        body = form.body.data
        with app.app_context():
            new_edit = Post.query.get(index)
            new_edit.title = title
            new_edit.subtitle = subtitle
            new_edit.author = author
            new_edit.img_url = img_url
            new_edit.body = body
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("make-post.html", form=form, is_edit=True)


@app.route("/delete/<int:index>")
def delete(index):
    requested_post = Post.query.get(index)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/login', methods=["POST"])
def receive_data():
    name = request.form["fullname"]
    email = request.form["email"]
    phone = request.form["phone"]
    message = request.form["message"]
    send_email(name, email, phone, message)
    return "Message sent successfully ✅"

if __name__ == "__main__":
    app.run(debug=True)

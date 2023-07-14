from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

app=Flask(__name__)
HEX_SEC_KEY= 'd5fb8c4fa8bd46638dadc4e751e0d68d'

app.config['SECRET_KEY']=HEX_SEC_KEY

with open('config.json','r') as c:
    params=json.load(c)['params']
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///kabh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = "465",
    MAIL_USE_SSL = True,
    MAIL_USERNAME =params["gmail-name"],
    MAIL_PASSWORD ='plxfcmolghaexmtm' ,
    )

mail=Mail(app)


class Contact(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False)
    message=db.Column(db.String(50),nullable=False)
    date=db.Column(db.DateTime,default=datetime.utcnow)

class Todo(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    date=db.Column(db.DateTime,default=datetime.utcnow)



@app.route('/',methods=["GET","POST"])
def home():
   return render_template("index.html") 

@app.route('/contact',methods=["GET","POST"])
def contact():
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        message=request.form["message"]

        entry=Contact(name=name,email=email,message=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('the massage from '+name,
                          sender=email,
                          recipients=['sayam.1999.sm@gmail.com'],
                          body=message
         
         
         )
    return render_template("contact.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if 'user' in session and session['user']==params["login-username"]:
        return render_template('dashboard.html')

    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username==params["login-username"] and password==params["login-password"]:
            session['user']=username
            return render_template('dashboard.html')
          
            

    return render_template("login.html",params=params)

   

@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    if request.method=='POST':
        title=request.form['todo-input']
        entry=Todo(title=title)
        db.session.add(entry)
        db.session.commit()
    todo=Todo.query.all()
    return render_template('dashboard.html',todos=todo)

@app.route('/delete/<int:sno>',methods=["GET","POST"])
def delete(sno):
    d=Todo.query.filter_by(sno=sno).first()
    db.session.delete(d)
    db.session.commit()
    return redirect('/dashboard')


@app.route('/update/<int:sno>',methods=["GET","POST"])
def update(sno):
    if request.method=='POST':
        u=request.form['todo-input']
        todo=Todo(title=u)
        todo=Todo.query.filter_by(sno=sno).first()

        todo.title=u
        db.session.add(todo)
        db.session.commit()
        return redirect('/dashboard')
    todo=Todo.query.filter_by(sno=sno).first()
    return render_template('update.html',todo=todo)










@app.route("/logout",methods=["GET","POST"])
def logout():
    if request.method=='POST':
        session.pop('user')
        return redirect('/login')


if __name__=="__main__":
  app.run(debug=True)
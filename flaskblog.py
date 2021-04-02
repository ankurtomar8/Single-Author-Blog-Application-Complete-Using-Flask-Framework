from flask import Flask,render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import os ,math
from werkzeug.utils import secure_filename






# Main Code Area Hai 



with open('Flask_Blog/config.json','r') as c:
   params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
   MAIL_SERVER = 'smtp.gmail.com',
   MAIL_PORT ='465',
   MAIL_USE_SSL = 'TRUE',
   MAIL_USERNAME = params['gmail-user'],
   MAIL_PASSWORD = params['gmail-password']

)

mail = Mail(app)

if(local_server):
   app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

else:   
   app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
   
  # sno, name , phone_num,msg,date,email

   
   sno = db.Column(db.Integer,primary_key=True)
   name = db.Column(db.String(80),unique = False , nullable=False)
   email = db.Column(db.String(120) , nullable=False)
   phone_num = db.Column(db.String(12) ,nullable=False)
   msg = db.Column(db.String(120) ,nullable=False)
   date = db.Column(db.String(12) ,nullable=True)




class Posts(db.Model):
   
  # sno, name ,date,email,line

   
   sno = db.Column(db.Integer,primary_key=True)
   title = db.Column(db.String(80),unique = False , nullable=False)
   slug = db.Column(db.String(25) , nullable=False)
   content = db.Column(db.String(200) ,nullable=False)
   tagline = db.Column(db.String(12) ,nullable=True)
   date = db.Column(db.String(12) ,nullable=True)
   img_file = db.Column(db.String(12) ,nullable=True)



# Routing Area

@app.route('/')
def home():
   posts = Posts.query.filter_by().all()
   last = math.ceil(len(posts)/int(params['no_of_post']))
   #[0:params['no_of_post']]
   page = ( request.args.get('page'))
   if(not str(page).isnumeric()):
      page = 1
   page = int ( page )   

   posts = posts[(page-1) * int (params['no_of_post']) : (page-1) * int (params['no_of_post']) + int(params['no_of_post'])]
   #Pagination Logic 
   #First 
   if (page==1):
      prev = "#"
      next = "/?page="+str(page+1)
   elif (page==last):
      prev = "/?page="+str(page-1)
      next = "#"
   else:
      prev = "/?page="+str(page-1)
      next = "/?page="+str(page+1)


   #previous =  #
   # next = page +1 
   
   #middle 
   # prev = page -1
   # next = page +1
   # Last 
   #prev = page -1
   # next = # 


   
   return render_template('index.html' , params=params , posts=posts,prev=prev ,next=next)


@app.route('/dashboard')
def dashboard():

   if ('user' in session and session ['user'] == params['admin_user']):
      posts = Posts.query.all()
      return render_template('dashboard.html',params=params,posts=posts )


@app.route('/login', methods = ['GET', 'POST'] )
def login():

   if ('user' in session and session ['user'] == params['admin_user']):
      posts = Posts.query.all()
      return render_template('dashboard.html',params=params,posts=posts )

   if request.method == 'POST':
      username = request.form.get('uname')
      userpass = request.form.get('pass')
      if (username == params['admin_user'] and userpass == params['admin_password'] ):
         #set the session variable
         session['user'] = username
         posts = Posts.query.all()
         return render_template('dashboard.html', params=params , posts=posts)

      #Redirect to Admin Panel
   else:
      return render_template('login.html' ,params=params )

#Post Request Handler

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
  post = Posts.query.filter_by(slug=post_slug).first() 
  return render_template('post.html' , params=params , post=post)   


@app.route('/about')
def about():

   return render_template('about.html' ,params=params )

@app.route('/post')
def post():

   return render_template('post.html', params=params  )

# Uploader Here 

@app.route('/uploader',methods = ['GET','POST'])
def uploader():
   if ('user' in session and session ['user'] == params['admin_user']):
      if (request.method == 'POST'):
         f = request.files['file1']
         f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))  
         return "Uploaded Successfully "

   




@app.route('/contact' , methods = ['GET', 'POST'])
def contact():
   if(request.method=='POST'):
     
      #  Add Entry To Database 
      
      
      name = request.form.get('name')
      email = request.form.get('email')
      phone= request.form.get('phone')
      message = request.form.get('message')

      
  #  sno, name , phone_num,msg,date,email    

      entry = Contacts(name=name , phone_num=phone , msg=message , date=datetime.now(), email=email)
      db.session.add(entry)
      db.session.commit()   
      mail.send_message('New Message From Blog ',
       sender=email,
       recipients =[ params['gmail-user']],
       body = message + "\n" + phone
    
      
      ) 

   return render_template('contact.html',params=params)


#Editing all posts here 

@app.route('/edit/<string:sno>' , methods = ['GET','POST'])
def edit(sno):
   if ('user' in session and session ['user'] == params['admin_user'] ):
      if (request.method == 'POST'):
         box_title = request.form.get('title')
         tline = request.form.get('tline')
         slug = request.form.get('slug')
         content = request.form.get('content')
         img_file = request.form.get('img_file')
         date = datetime.now()
         
         if (sno =='0'):
            post = Posts(title=box_title,slug=slug,content=content,tagline=tline,img_file=img_file,date=date)
            db.session.add(post)
            db.session.commit()
         else:
            post = Posts.query.filter_by(sno=sno).first()
            post.title = box_title
            post.slug = slug
            post.content = content
            post.tagline = tline
            post.img_file = img_file
            post.date = date
            db.session.commit()
            return redirect('/edit/'+sno)   
      post = Posts.query.filter_by(sno=sno).first()      
      return render_template('edit.html',params=params,post=post ,sno=sno)

   


@app.route('/delete/<string:sno>' , methods = ['GET','POST'])
def delete(sno):
   if ('user' in session and session ['user'] == params['admin_user'] ):
      post = Posts.query.filter_by(sno=sno).first()
      db.session.delete(post)
      db.session.commit()
   return redirect('/dashboard')   




@app.route('/logout')
def logout():
   session.pop('user')
   return redirect('/login')




app.run(debug=True)   







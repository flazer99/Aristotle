from flask import *
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'college'

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/admin/login")
def admin_login():
    return render_template('admin-login.html')

@app.route("/admin/home")
def admin_home():
    return render_template('admin_home.html')

@app.route("/admin/add-college")
def add_college():
    return render_template('add-college.html')

@app.route("/admin/add-college/details", methods = ['GET'])
def college_insert_values():
    cname = request.args.get('college-name')
    code = request.args.get('university-code')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO college_index(name, univ_code) VALUES (%s, %s)", (cname, code))
    mysql.connection.commit()
    cur.close()
    return "Success"

@app.route("/admin/add-cutoffs")
def add_cutoff():
    return render_template('add-cutoff.html')

@app.route("/admin/add-cutoffs/details", methods=["post"])
def cutoffs_insert_values():
    cname = request.form['name']
    branch = request.form['branch']
    cut_off = request.form['cut-off']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO add_cutoff(name, dept, cutoff) VALUES (%s, %s, %s)", (cname, branch, cut_off))
    mysql.connection.commit()
    cur.close()
    return "Recorded!"

@app.route("/admin/view-students")
def view_students():
    return render_template('view-students.html')
      
@app.route("/user/login")
def user_login():
    return render_template('user-login.html')

@app.route("/admin/register")
def admin_register():
    return render_template('admin-register.html')

@app.route("/admin/register/details", methods= ["POST"])
def admin_insert_values():
    name = request.form['name']
    password = request.form['pass']
    dob = request.form['dob']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO admin(name, password, dob) VALUES (%s, %s, %s)", (name, password, dob))
    mysql.connection.commit()
    cur.close()
    return render_template('home.html')


if(__name__=='__main__'):
    app.run(debug = True, port = 5000)
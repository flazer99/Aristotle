from flask import *
from scipy import stats
from math import pi
from math import exp
from math import sqrt

app = Flask(__name__)

def restructure(buff):
    data = [x.split(',') for x in buff.read().split('\n') if(len(x.split(',')) >= 2)]
    return data

def normal_dist(x, mean, stdev):
    exponent = exp(-((x-mean)**2 / (2 * stdev**2 )))
    return (1 / (sqrt(2 * pi) * stdev)) * exponent
    
def predict(x, probs, prob_ADMIT, prob_NOADMIT):
    pos = prob_ADMIT
    for i in range(5):
        pos *= normal_dist(x[i], probs[i][0], probs[i][1])
    if(x[-1] == 0):
        pos *= probs[5][1]
    else:
        pos *= probs[5][0]
        
    neg = prob_NOADMIT
    for i in range(5):
        neg *= normal_dist(x[i], probs[i][2], probs[i][3])
    if(x[-1] == 0):
        neg *= probs[5][3]
    else:
        neg *= probs[5][2]
    return float(pos) / (pos+neg)

def admission_prediction(cut_off_mark):
    f = open("probs","r")
    probs = restructure(f)
    probs = [list(map(float, i)) for i in probs]
    f.close()
    f = open("prob_(no)admits")
    admits_prob = restructure(f)
    f.close()
    ip = [340, max(92, cut_off_mark), 5, 5, 10, 1]
    return predict(ip, probs, float(admits_prob[0][1]), float(admits_prob[1][1]))
    # print('The probability of getting admission is', predict(ip, probs, float(admits_prob[0][1]), float(admits_prob[1][1])))

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/admin/login")
def admin_login():
    return render_template('admin-login.html')

@app.route("/admin/signup")
def signup():
    return render_template('admin-signup.html')

@app.route("/admin/signup/success", methods = ["post"])
def signup_register():
    usr = request.form['username']
    password = request.form['password']

    with open("admin-login", "a") as f:
        f.write(str(usr) + "," + str(password) + "\n")
    return render_template("admin-login.html")

@app.route("/admin/login/check", methods = ["post"])
def admin_login_check():
    usr = request.form['username']
    password = request.form['password']

    try:
        f = open("admin-login","r")
        res = restructure(f)
        for i in res:
            if(i[0] == usr and i[1] == password):
               return render_template('admin_home.html')
        return "Login Error!"
    except Exception as e:
        return "Admins haven't registered yet!" 


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
    rank = request.args.get('ranking')

    with open('college-details', "a") as f:
        f.write(str(cname)+","+str(code)+","+str(rank)+"\n")
        return "Success"
    return "Error"

@app.route("/admin/add-cutoffs")
def add_cutoff():
    try:
        f = open("college-details","r")
        res = restructure(f)
        college_list = list()
        for i in res:
            college_list.append(i[0])
        f.close()
    except Exception as e:
        return "Please add the details about the college!"
    return render_template('add-cutoff.html', college = college_list)

@app.route("/admin/add-cutoffs/details", methods=["post"])
def cutoffs_insert_values():
    cname = request.form['name']
    branch = request.form['branch']
    cut_off = request.form['cut-off']
    
    with open('previous-cutoff-details', "a") as f:
        f.write(str(cname)+","+str(branch)+","+str(cut_off)+"\n")
        return "Recorded!"
    return "Error"

@app.route("/admin/view-students")
def view_students():
    f = open("previous-cutoff-details","r")
    res = restructure(f)
    branch = list()
    for i in res:
        branch.append(i[1])
    branch = list(set(branch))
    f.close()
    return render_template('view-students.html', branch = branch, ctr = 0, students = [])
      
@app.route("/admin/view-students/details", methods = ["get"])
def view_students_details():
    branch_target = request.args.get('branch')
    f1 = open("previous-cutoff-details","r")
    res = restructure(f1)
    branch = list()
    for i in res:
        branch.append(i[1])
    branch = list(set(branch))
    f1.close()
    try:
        f = open("student-apply","r")
        res = restructure(f)
        students = list()
        for i in res:
            if(i[1] == branch_target):
                students.append(i)
        f.close()
        return render_template('view-students.html', branch = branch, ctr = 1, students = students)  
    except Exception as e:
        return "Error! Students haven't applied yet!"

@app.route("/admin/create-cutoff")
def create_cutoff():
    try:
        f = open("college-details","r")
        res = restructure(f)
        college_list = list()
        for i in res:
            college_list.append(i[0])
        f.close()
    except Exception as e:
        return "Please add the details about the college!"

    try:
        f = open("previous-cutoff-details","r")
        res = restructure(f)
        branch_list = list()
        for i in res:
            branch_list.append(i[1])
        f.close()
    except Exception as e:
        return "Please add previous cutoff details first to maintain branch integrity!"

    return render_template('create-cutoff.html', college = college_list, branch = branch_list, ctr = 0, buff = [] )


@app.route("/admin/create-cutoff/details", methods = ["get"])
def create_cutoff_details():
    cname = request.args.get('college')
    branch = request.args.get('branch')
    marks = request.args.get('marks')

    f = open("cutoff-details", "a")
    f.write(str(cname)+","+str(branch)+","+str(marks)+"\n")
    buff_write = [str(cname), str(branch), str(marks)]
    f.close()

    try:
        f = open("college-details","r")
        res = restructure(f)
        college_list = list()
        for i in res:
            college_list.append(i[0])
        f.close()
    except Exception as e:
        return "Please add the details about the college!"

    try:
        f = open("previous-cutoff-details","r")
        res = restructure(f)
        branch_list = list()
        for i in res:
            branch_list.append(i[1])
        f.close()
    except Exception as e:
        return "Please add previous cutoff details first to maintain branch integrity!"

    return render_template('create-cutoff.html', college = college_list, branch = branch_list, ctr = 1, buff = buff_write)

@app.route("/admin/register")
def register():
    try:
        f = open("student-apply","r")
        student = restructure(f)
        branch_list = list()
        f.close()
    except Exception as e:
        return "No Students have applied yet!"
    
    try:
        f = open("cutoff-details","r")
        cutoff = restructure(f)
        f.close()
    except Exception as e:
        return "Cutoffs haven't been set yet!"
    
    f = open("final-list","a")
    for i in student:
        college = i[0]
        branch = i[1]
        marks = i[2]
        name = i[3]

        for j in cutoff:
            if(j[0] == college and j[1] == branch and j[2]<=marks):
                f.write(str(college) + "," + str(branch) + "," + str(marks) + "," + str(name)+"\n")
                break
    f.close()
    REG = True
    return "Registration Process Completed!"

@app.route("/admin/final-list")
def final_list():
    try:
        f = open("final-list","r")
        students = restructure(f)
        f.close()
    except Exception as e:
        return "Final List of students haven't been computed yet! Please Register the students before trying this option."

    return render_template("final-list.html", students = students )

@app.route("/user/login")
def user_login():
    return render_template('user-login.html')

@app.route("/user/signup")
def user_signup():
    return render_template('user-signup.html')

@app.route("/user/signup/success", methods = ["post"])
def user_signup_register():
    usr = request.form['username']
    password = request.form['password']

    with open("user-login-details", "a") as f:
        f.write(str(usr) + "," + str(password) + "\n")
    return render_template("user-login.html")
    

@app.route("/user/login/check", methods = ["post"])
def user_login_check():
    usr = request.form['username']
    password = request.form['password']

    try:
        f = open("user-login-details","r")
        res = restructure(f)
        f.close()
        for i in res:
            if(i[0] == usr and i[1] == password):
                return render_template('user-home.html')
        return "Login Error!"
    except Exception as e:
        return "Users haven't registered yet!" 

@app.route("/user/view-college")
def view_college():
    f = open("previous-cutoff-details","r")
    res = restructure(f)
    college = list()
    for i in res:
        college.append(i[0])
    college = list(set(college))
    f.close()

    return render_template('view-college.html', college = college, ctr = 0, cutoff = [])

@app.route("/user/view-college/details", methods = ["get"])
def view_college_details():
    cname = request.args.get('college-name')
    f = open("previous-cutoff-details","r")
    res = restructure(f)
    cutoff = list()
    college = list()

    for i in res:
        college.append(i[0])
    college = list(set(college))

    for i in res:
        if(i[0] == cname):
            cutoff.append(i)
    
    f.close()
    return render_template('view-college.html', college = college , ctr = 1, cutoff = cutoff)

@app.route("/user/apply")
def apply_college():
    f = open("previous-cutoff-details","r")
    res = restructure(f)
    college = list()
    branch = list()
    for i in res:
        college.append(i[0])
    college = list(set(college))
    for i in res:
        branch.append(i[1])
    f.close()
    return render_template("apply-college.html", college = college, branch = branch)

@app.route("/user/apply/details", methods = ["get"])
def apply_college_details():
    cname = request.args.get('college-name')
    branch = request.args.get('branch')
    sname = request.args.get('sname')
    smarks = request.args.get('smarks')

    with open('student-apply', "a") as f:
        f.write(str(cname)+","+str(branch)+","+str(smarks)+","+str(sname)+"\n")
        return "Recorded!"
    return "Error"

@app.route("/user/view-cutoff")
def view_cutoff():
    try:
        f = open("cutoff-details","r")
        res = restructure(f)
        college = list()
        branch = list()
        f.close()
        
        for i in res:
            college.append(i[0])
            branch.append(i[1])
        
        college = list(set(college))
        branch = list(set(branch))  
        return render_template('view-current-cutoff.html', college = college, ctr = 0, branch = branch, result = [])
    except Exception as e:
        return "The Current Cut-Off list hasn't been released yet!" 


@app.route("/user/view-cutoff/details", methods = ["get"])
def view_cutoff_details():
    college = request.args.get('college')
    branch = request.args.get('branch')
    try:
        f = open("cutoff-details","r")
        res = restructure(f)
        college_list = list()
        branch_list = list()
        f.close()
        
        query_res = None
        for i in res:
            if(college == i[0] and branch == i[1]):
                query_res = i
            college_list.append(i[0])
            branch_list.append(i[1])
        
        college_list = list(set(college_list))
        branch_list = list(set(branch_list))

        return render_template('view-current-cutoff.html', college = college_list, ctr = 1, branch = branch_list, result = query_res)
    except Exception as e:
        return "The Current Cut-Off list hasn't been released yet!" 

# @app.route("/user/selection")
# def user_selection():
#     try:
#         f = open("final-list","r")
#         return render_template('user-selection.html')
#     except Exception as e:
#         return "The final list of students haven't been computed yet! Check back later!" 

@app.route("/user/selection")
def user_selection():
    try:
        return render_template('user-selection.html')
    except Exception as e:
        return "The final list of students haven't been computed yet! Check back later!" 

@app.route("/user/selection/details", methods = ["get"])
def user_selection_details():
    sname = request.args.get('sname')
    try:
        f = open("final-list","r")
        res = restructure(f)
        f.close()
        result = ["Sorry you didn't make the cutoff","Congratulations you're selected!"]

        f = 0
        for i in res:
            if(sname == i[3]):
                f = 1
                break
        return render_template('user-result.html', result = result[f])
    except Exception as e:
        f = open("student-apply","r")
        applys = restructure(f)
        f.close()
        print(applys)
        for i in applys:
            if(sname == i[3]):
                print(admission_prediction(float(i[2])))
                return "The cutoff isn't decided yet, but you have a probability of {} to get admission".format(admission_prediction(float(i[2])))
        return "The final list of students haven't been computed yet! Check back later!" 

if(__name__=='__main__'):
    # admission_prediction(90)
    app.run(debug = True, port = 5000)

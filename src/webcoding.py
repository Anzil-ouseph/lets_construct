from flask import *
from src.dbconnectionnew import *
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "1234564789"


# first route or first page of the webapplication
@app.route('/')
def login():
    return render_template("login_index.html")


@app.route('/login_code', methods=['post'])
def login_code():
    # getting entered username from html to server
    username = request.form['textfield']

    # getting entered password from html to server
    password = request.form['textfield2']

    # %s is used to represent string
    qry = "SELECT * FROM login WHERE `username`=%s AND `password`=%s"
    res = selectone(qry, (username, password))

    print(res)
    # res will be a dictionary

    if res is None:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''

    elif res['type'] == "admin":
        session['lid'] = res['id']
        return '''<script>alert("Welcome admin");window.location="/admin_home"</script>'''

    elif res['type'] == "user":
        session['lid'] = res['id']
        return '''<script>alert("Welcome user");window.location="/user_home"</script>'''

    elif res['type'] == "builder":
        session['lid'] = res['id']

        return '''<script>alert("Welcome builder");window.location="/builder_home"</script>'''

    else:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''


@app.route('/user_register')
def user_register():
    return render_template("user_register.html")


@app.route('/user_register_code', methods=['post'])
def user_register_code():
    fname = request.form['textfield']
    lname = request.form['textfield2']
    place = request.form['textfield3']
    post = request.form['textfield4']
    pin = request.form['textfield5']
    email = request.form['textfield6']
    phn = request.form['textfield7']
    uname = request.form['textfield8']
    pswd = request.form['textfield9']

    # insert username and password to database(login table)
    qry = "INSERT INTO `login` VALUES(NULL,%s,%s,'pending')"
    id = iud(qry, (uname, pswd))

    # insert remaining details to database(user table)
    qry = "INSERT INTO `user` VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s)"
    iud(qry, (id, fname, lname, place, post, pin, email, phn))

    return '''<script>alert("Registered successfully");window.location="/"</script>'''


@app.route('/builder_register')
def builder_register():
    return render_template("builder_register.html")


@app.route('/builder_register_code', methods=['post'])
def builder_register_code():
    name = request.form['textfield2']
    place = request.form['textfield3']
    post = request.form['textfield4']
    pin = request.form['textfield5']
    email = request.form['textfield6']
    phn = request.form['textfield7']

    lati = request.form['lati']
    longi = request.form['longi']

    uname = request.form['textfield8']
    pswd = request.form['textfield9']

    qry = "INSERT INTO `login` VALUES(NULL,%s,%s,'pending')"
    id = iud(qry, (uname, pswd))

    qry = "INSERT INTO `builders` VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    iud(qry, (id, name, place, post, pin, email, phn, lati, longi))

    return '''<script>alert("Registered successfully");window.location="/"</script>'''


@app.route('/admin_home')
def admin_home():
    return render_template("admin/admin_index.html")


@app.route('/verify_users')
def verify_users():
    qry = "SELECT * FROM `user` JOIN `login` ON `user`.lid=`login`.id WHERE `type`='pending'"
    res = selectall(qry)

    return render_template("admin/verify_users.html", val=res)


@app.route('/accept_user')
def accept_user():
    id = request.args.get('id')
    qry = "UPDATE `login` SET `type`='user' WHERE `id`=%s"
    iud(qry, id)
    return '''<script>alert("Accepted");window.location="/verify_users"</script>'''


@app.route('/reject_user')
def reject_user():
    id = request.args.get('id')
    qry = "UPDATE `login` SET `type`='rejected' WHERE `id`=%s"
    iud(qry, id)
    return '''<script>alert("Rejected");window.location="/verify_users"</script>'''


@app.route('/verify_builders')
def verify_builders():
    qry = "SELECT * FROM `builders` JOIN `login` ON `builders`.lid=`login`.id WHERE `type`='pending'"
    res = selectall(qry)

    return render_template("admin/verify_builders.html", val=res)


@app.route('/accept_builder')
def accept_builder():
    id = request.args.get('id')
    qry = "UPDATE `login` SET `type`='builder' WHERE `id`=%s"
    iud(qry, id)
    return '''<script>alert("Accepted");window.location="/verify_builders"</script>'''


@app.route('/reject_builder')
def reject_builder():
    id = request.args.get('id')
    qry = "UPDATE `login` SET `type`='rejected' WHERE `id`=%s"
    iud(qry, id)
    return '''<script>alert("Rejected");window.location="/verify_builders"</script>'''


@app.route('/view_complaint')
def view_complaint():
    qry = "SELECT `complaint`.*,`user`.`first_name`,`last_name` FROM `user` JOIN `complaint` ON `user`.`lid`=`complaint`.`uid` WHERE `complaint`.reply='pending'"
    res = selectall(qry)
    return render_template('admin/view_complaint.html', val=res)


@app.route('/send_reply')
def send_reply():
    id = request.args.get('id')
    session['cid'] = id
    return render_template('admin/send_reply.html')


@app.route('/insert_reply', methods=['post'])
def insert_reply():
    reply = request.form['textfield']
    qry = "UPDATE `complaint` SET reply=%s WHERE `id`=%s"
    iud(qry, (reply, session['cid']))

    return '''<script>alert("Reply send successfully");window.location="view_complaint"</script>'''


@app.route('/view_rating_review')
def view_rating_review():
    qry = "SELECT `builders`.* FROM `builders` JOIN `login` ON `builders`.lid=login.id"
    res = selectall(qry)
    return render_template('admin/view_rating_review.html', val=res)


@app.route('/load_review', methods=['post'])
def load_review():
    builder = request.form['select']
    print(builder)

    qry = "SELECT `builders`.* FROM `builders` JOIN `login` ON `builders`.lid=login.id"
    res = selectall(qry)

    qry = "SELECT `user`.`first_name`,`last_name`,`rating_and_review`.*,`builders`.`name` FROM `rating_and_review` JOIN `user` ON `rating_and_review`.`uid`=`user`.`lid` JOIN `builders` ON `rating_and_review`.`bid`=`builders`.`lid` WHERE `rating_and_review`.`bid`=%s"
    res2 = selectall2(qry, builder)
    return render_template('admin/view_rating_review.html', val=res, val2=res2)


@app.route('/view_work_details')
def view_work_details():
    qry = "SELECT `builders`.* FROM `builders` JOIN `login` ON `builders`.lid=login.id"
    res = selectall(qry)

    return render_template('admin/view_work_detials.html', val=res)


@app.route('/load_work_details', methods=['post'])
def load_work_details():
    builder = request.form['select']

    qry = "SELECT `builders`.* FROM `builders` JOIN `login` ON `builders`.lid=login.id"
    res = selectall(qry)

    qry = "SELECT `user`.`first_name`,`user`.`last_name`,`works`.`name` AS work_name,`builders`.`name`,`request`.* FROM `request` JOIN `works` ON `request`.`wid`=`works`.`id` JOIN `user` ON `request`.`uid`=`user`.`lid` JOIN `builders` ON `works`.`bid`=`builders`.`lid` WHERE `builders`.`lid`=%s"
    res2 = selectall2(qry, builder)

    return render_template('admin/view_work_detials.html', val=res, val2=res2)


@app.route('/builder_home')
def builder_home():
    return render_template("builders/builders_index.html")


@app.route('/manage_works')
def manage_works():
    qry = "select * from works where bid=%s"
    res = selectall2(qry, session['lid'])
    return render_template('builders/manage_work.html', val=res)


@app.route('/add_work', methods=['post'])
def add_work():
    return render_template('builders/add_new_work_details.html')


@app.route('/insert_works', methods=['post'])
def insert_works():
    name = request.form['textfield']
    place = request.form['textfield2']
    cost = request.form['textfield3']

    image = request.files['img']

    img_name = secure_filename(image.filename)
    image.save(os.path.join('static/uploads', img_name))

    qry = "INSERT INTO `works` VALUES(NULL,%s,%s,%s,%s,%s)"
    iud(qry, (session['lid'], name, place, cost, img_name))

    return '''<script>alert("Successfully added");window.location="/manage_works#about"</script>'''


@app.route('/delete_work')
def delete_work():
    id = request.args.get('id')
    qry = "delete from works where id=%s"
    iud(qry, id)

    return '''<script>alert("Deleted");window.location="/manage_works#about"</script>'''


@app.route('/edit_work')
def edit_work():
    id = request.args.get('id')
    session['wid'] = id

    qry = "SELECT * FROM `works` WHERE `id`=%s"
    res = selectone(qry, id)

    return render_template("builders/edit_works.html", val=res)


@app.route('/update_work', methods=['post'])
def update_work():
    try:
        name = request.form['textfield']
        place = request.form['textfield2']
        cost = request.form['textfield3']

        image = request.files['img']

        img_name = secure_filename(image.filename)
        image.save(os.path.join('static/uploads', img_name))

        qry = "UPDATE `works` SET `name`=%s,`place`=%s,`cost`=%s,`image`=%s WHERE `id`=%s"
        iud(qry, (name, place, cost, img_name, session['wid']))

        return '''<script>alert("Successfully Edited");window.location="/manage_works#about"</script>'''
    except Exception as e:
        name = request.form['textfield']
        place = request.form['textfield2']
        cost = request.form['textfield3']

        qry = "UPDATE `works` SET `name`=%s,`place`=%s,`cost`=%s WHERE `id`=%s"
        iud(qry, (name, place, cost, session['wid']))

        return '''<script>alert("Successfully Edited");window.location="/manage_works#about"</script>'''


@app.route('/view_works_request')
def view_works_request():
    qry = "SELECT `works`.`name`,`user`.*,`request`.request,request.date,request.id as reqid FROM `request` JOIN `works` ON `request`.`wid`=`works`.`id` JOIN `user` ON `request`.`uid`=`user`.`lid` WHERE `works`.`bid`=%s and status='pending'"
    res = selectall2(qry, session['lid'])
    return render_template("builders/view_works_request.html", val=res)


@app.route('/accept_work')
def accept_work():
    id = request.args.get('id')
    qry = "UPDATE `request` SET `status`='accepted' where id=%s"
    iud(qry,id)
    return '''<script>alert("Successfully Accepted");window.location="/view_works_request#about"</script>'''


@app.route('/reject_work')
def reject_work():
    id = request.args.get('id')
    qry = "UPDATE `request` SET `status`='rejected' where id=%s"
    iud(qry,id)
    return '''<script>alert("Successfully Accepted");window.location="/view_works_request#about"</script>'''


@app.route('/view_accepted_works')
def view_accepted_works():
    qry = "SELECT `works`.`name`,`user`.*,`request`.* FROM `request` JOIN `works` ON `request`.`wid`=`works`.`id` JOIN `user` ON `request`.`uid`=`user`.`lid` WHERE `works`.`bid`=%s and status!='pending' or 'rejected'"
    res = selectall2(qry, session['lid'])
    return render_template("builders/view_accepted_works.html", val=res)


@app.route('/update_work_status')
def update_work_status():
    id = request.args.get('id')
    session['awid'] = id
    return render_template("builders/update_work_status.html")


@app.route('/insert_work_status', methods=['post'])
def insert_work_status():
    status = request.form['textfield']
    qry = "UPDATE `request` SET `status`=%s WHERE id = %s"
    iud(qry, (status, session['awid']))

    return '''<script>alert("Updated");window.location="/view_accepted_works"</script>'''


@app.route('/view_rating_and_review')
def view_rating_and_review():
    qry = "SELECT `user`.`first_name`,`last_name`,`rating_and_review`.* FROM  `rating_and_review` JOIN `user` ON `rating_and_review`.uid=`user`.lid WHERE `rating_and_review`.bid=%s"
    res = selectall2(qry,session['lid'])
    print("=====", res)
    return render_template("builders/builders_view_rating_review.html", val=res)


@app.route('/user_home')
def user_home():
    return render_template("user/user_index.html")


@app.route('/view_works')
def view_works():
    qry = "SELECT `builders`.name AS bname,latitude,longitude,`works`.* FROM `works` JOIN `builders` ON `works`.`bid`=`builders`.`lid`"
    res = selectall(qry)
    return render_template("user/send_work_request.html", val=res)


@app.route('/send_request')
def send_request():
    id = request.args.get('id')
    session['work_id'] = id
    return render_template('user/send_request.html')


@app.route('/insert_request', methods=['post'])
def insert_request():
    req = request.form['textfield']
    qry = "INSERT INTO `request` VALUES(NULL,%s,%s,CURDATE(),%s,'pending')"
    iud(qry, (session['lid'], session['work_id'], req))
    return '''<script>alert("Request send successfully");window.location="/view_works"</script>'''


@app.route('/view_work_status')
def view_work_status():
    qry = "SELECT `builders`.`name` AS bname,`works`.`name`,`image`, request.status FROM `request` JOIN `works` ON `request`.`wid`=`works`.`id` JOIN `builders` ON `works`.`bid`=`builders`.`lid` WHERE `request`.`uid`=%s"
    res = selectall2(qry, session['lid'])
    return render_template('user/view_work_request_status.html' , val=res)


app.run(debug=True)

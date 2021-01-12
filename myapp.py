import os
import netCDF4
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
# %matplotlib inline
UPLOAD_FOLDER = '/tmp/scaas'
ALLOWED_EXTENSIONS = set(['txt', 'nc'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.isdir('/tmp/scaas'):
    os.mkdir('/tmp/scaas')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        f = os.listdir('./static')
        for i in f:
            os.remove('./static/' + i)
            print(i + ' removed')
        f = os.listdir('/tmp/scaas')
        for i in f:
            os.remove('/tmp/scaas/' + i)
            print(i + ' removed')

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            return '''
            <h1> Selected file is not valid... !!! </h1>
            <h1> Allowed Extensions are .txt or .nc </h1>
            <input type="button" value="Back" onclick="window.history.back()" />
            '''
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if os.path.isfile("/tmp/scaas/" + filename):
                msg = "Your file " + filename + " Successfully uploaded"
            else:
                msg = "Something went wrong...!!!"
        return redirect(url_for('show', fname = filename, msg = msg))

    return '''
        <!doctype html>
        <head>
        <link rel="shortcut icon" href="" type="image/x-icon">
        <link rel="icon" href="Dakirby309-Simply-Styled-VirtualBox.ico" type="image/x-icon">
        <title>Welcome to Scientific Computing as a Service Beta Version</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
            .right {
              background-color: lightblue;
              float: left;
              width: 100%;
              padding: 80px 15px;
              margin-top: 20px;
            }
            </style>
        </head>
        <body>
        <h1> Welcome to Scientific Computing as a Service Beta Version </h1>
        <h3>Please upload new netCDN file below</h3>
        <form method='post' enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>

        <div class="right">
            <p>
            One can find all the netCDF files on below links: <br>
            http://borealscicomp.com/metfiles/Irma-09-2017/wrfout/ <br>
            http://borealscicomp.com/metfiles/Alaska-08-2018/wrfout/ <br>
            </p>
            <h2> Direction Of Using ScaaS </h2>
            <h4>Step 1: Please upload only .txt or .nc file or else if will not proceed further.</h4> 
            <h4>Step 2: please click on "load variable" button </h4>
            <h4>Optional step: Press "show variable" button in the page to see variable list </h4>
            <h4>Step 3: Write a name of the variable in the text box and click on Draw Graph </h4>
            <h4>If your variable is 3D then it will ask for the level. Please provide intiger value there. </h4>
        </div>
        </body>
        '''
# /index?msg=Your+file+minion.jpegSuccessfully+uploaded&fname=minion.jpeg
@app.route('/index/<fname>,<msg>', methods=['POST', 'GET'])
def show(fname, msg):
    if request.method == 'POST':
        if os.path.isfile("/tmp/scaas/" + fname):
            print("we are in post method")
        return redirect(url_for('image', fname=fname))

    return render_template("var_load.html", msg=msg, fname=fname)

@app.route('/image/<fname>', methods=['POST', 'GET'])
def image(fname):
    try:
        dset = netCDF4.Dataset("/tmp/scaas/" + fname)
    except OSError:
        return '''<h1> Invalid txt tile uploaded </h1>
                  <input type="button" value="Back" onclick="window.history.back()" />
        '''
    l = []
    unit = []
    des = []
    c = []
    for i in dset.variables.keys():
        l.append(i)

    for i in l:
        try:
            sv = dset.variables[i]
            # print(str(sv.units))
            unit.append(str(sv.units))
        except AttributeError:
            unit.append(str("No Unit"))

    for i in l:
        try:
            sv = dset.variables[i]
            # print(str(sv.description))
            des.append(str(sv.description))
        except AttributeError:
            des.append("No description")

    for i in l:
        try:
            q = dset.variables[i]
            # print(str(q.dimensions))
            c.append(str(q.dimensions))
        except:
            c.append("No Dimensions")


    if request.method == 'POST':

        var_name = request.form['lname']
        print(var_name)
        if not var_name:
            return ''' <h1> Please give the variable name in the Text box <h1>
                    <input type="button" value="Back" onclick="window.history.back()" />
            '''

        dset = netCDF4.Dataset("/tmp/scaas/" + fname)
        try:
            q = dset.variables[var_name]
            print(type(q.dimensions))
            print(str(q.dimensions))
            print(len(q.dimensions))

            dy = len(q.dimensions)
        except KeyError:
            return ''' <h1> Give Correct Name of variable </h1>
            <input type="button" value="Back" onclick="window.history.back()" />'''
        if dy == 3:
            # dset = netCDF4.Dataset("./static/" + fname)
            t2 = dset.variables[var_name]
            T2 = t2[:]
            uni = t2.units
            plt.contourf(T2[0,:,:])
            plt.colorbar()
            plt.title("Graph of variable " + str(var_name))
            plt.savefig('./static/' + var_name + '.png')
            dset.close()
            return render_template("image.html", user_image='/static/' + var_name + '.png', var=var_name, unit=uni)
        elif dy == 4:
            # print(var_name + "in dy == 4")
            # t2 = dset.variables[var_name]
            # y = t2.dimensions[1]
            #
            # if request.method == 'POST':
            #     lvl = request.form['yname']
            #     T2 = t2[:]
            #     uni = t2.units
            #     plt.contourf(T2[0, lvl,:, :])
            #     plt.colorbar()
            #     plt.title("Graph of variable " + str(var_name))
            #     plt.savefig('./static/' + var_name + '.png')
            #     return render_template("image.html", user_image='/static/' + var_name + '.png', var=var_name, unit=uni)
            # dset.close()
            # return render_template("3Dimage.html", var= var_name , unit=uni, y=y)
            return redirect(url_for('tdimage', var_name=var_name, fname=fname))
    dset.close()
    return render_template("var_show.html", dset=l, unit=unit, des=des, dim=c, num=len(i), fname=fname)


@app.route('/tdimage/<var_name>,<fname>', methods=['POST', 'GET'])
def tdimage(var_name, fname):
    z = netCDF4.Dataset("/tmp/scaas/" + fname)
    t2 = z.variables[var_name]
    uni = t2.units
    y = t2.dimensions[1]

    if request.method == 'POST':
        lvl = int(request.form['yname'])
        T2 = t2[:]
        uni = t2.units
        plt.contourf(T2[0, lvl,:, :])
        plt.colorbar()
        plt.title("Graph of variable " + str(var_name) + " at " + '\n' + y + " = " + str(lvl) )
        plt.savefig('./static/' + var_name + '.png')
        return render_template("tdimage.html", user_image='/static/' + var_name + '.png', var=var_name, unit=uni)

    z.close()
    return render_template("3Dimage.html", var= var_name , unit=uni, y=y)
# from flask import Flask, render_template, redirect, abort, url_for

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return redirect(url_for('hello', name='worlds'))

# @app.route('/hello/<name>')
# def hello(name):
#     return render_template('page.html', name=name)
    
# @app.route('/error')
# def error():
#     abort(401)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')

from flask import Flask, render_template, send_from_directory, \
    redirect, abort, url_for, flash, request
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = "C:\\Users\\Mates\\Disk Google\\SW Projekty\\Python\\displux\\server\\uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')
    #return redirect(url_for('show'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file', filename=filename))
            flash('File uploaded')
            return redirect(request.url)                             
    
    return  render_template('file_upload.html')




@app.route('/show')
def show():
    directory = UPLOAD_FOLDER

    gifs = [('uploads' + '\\' + path) for path in os.listdir(directory)]
    return  render_template('show.html', pictures = gifs)



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

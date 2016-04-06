from compute import timeline
from flask import Flask, request, redirect, url_for, send_from_directory
from flask import render_template
from model import InputForm
from werkzeug import secure_filename
import os
import sys

app = Flask(__name__)

TEMPLATE_NAME = 'view_highcharts'

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['txt', 'out'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     print(filename)
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)


# @app.route('/uploads/<filename>')
def index(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    result = timeline(filepath)
    return render_template(TEMPLATE_NAME + '.html',
                           form=form, result=result)

if __name__ == '__main__':
    app.run(debug=True)
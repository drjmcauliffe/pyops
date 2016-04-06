from compute import datarate as compute_datarate
from compute import power as compute_power
from compute import timeline as compute_timeline
from flask import Flask, request, redirect, url_for, send_from_directory
from flask import render_template
from model import InputForm
from werkzeug import secure_filename
import os
import sys

app = Flask(__name__)

TEMPLATE_NAME = 'view_index'

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['txt', 'out'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():

    upload = {'active': 'active'}
    timeline = {'data': None, 'active': None}
    datarate = {'data': None, 'active': None}
    power = {'data': None, 'active': None}

    if request.method == 'POST':

        # file = request.files['file']
        uploaded_files = request.files.getlist("file[]")

        filenames = []

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'],
                                        filename)

                file.save(filepath)

                # timeline
                if filename.startswith('timeline'):
                    timeline['data'] = compute_timeline(filepath)
                    timeline['active'] = 'active'

                    datarate['active'] = None
                    power['active'] = None

                # datarate
                if filename.startswith('data_rate_avg'):
                    datarate['data'] = compute_datarate(filepath)
                    datarate['active'] = 'active'

                    power['active'] = None
                    timeline['active'] = None

                # datarate
                if filename.startswith('power_avg'):
                    power['data'] = compute_power(filepath)
                    power['active'] = 'active'

                    datarate['active'] = None
                    timeline['active'] = None


    return render_template(TEMPLATE_NAME + '.html', upload=upload,
        timeline=timeline, datarate=datarate, power=power)

if __name__ == '__main__':
    app.run(debug=True)
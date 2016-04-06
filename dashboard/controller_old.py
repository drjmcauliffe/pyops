from model import InputForm
from flask import Flask, render_template, request
from compute import timeline
import sys

app = Flask(__name__)

template_name = 'view_highcharts'

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
        for field in form:
            exec('{} = {}'.format(field.name, field.data))
        result = timeline()
    else:
        result = None

    return render_template(template_name + '.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
import os 
import uuid
import json
from flask import Flask, request, send_file, Response, send_from_directory
from flask import render_template
from flask_s3 import FlaskS3 

app = Flask(__name__, static_url_path=os.getenv('STATIC_PATH', None))
app.config['FLASKS3_BUCKET_NAME'] = 'dea-web-webtools-static'
s3 = FlaskS3(app)

@app.route('/')
def terria_au():
    return render_template('terria-au.html')


@app.route('/terria-africa')
def terria_afr():
    return render_template('terria-afr.html')

@app.route('/wps')
def terria_wps():
    return render_template('wps.html')

@app.route('/jsongenerator', methods=['POST'])
def json_generator():
    data = request.get_json()
    filename = str(uuid.uuid4())
    with open('/tmp/' + filename, 'w', encoding='utf8') as f:
        json.dump(data, f)
    return {'filename': filename}


@app.route('/download_catalog', methods=['GET', 'POST'])
def download_catalog():
    fname = request.form['filename']
    cname = request.form['catalogname']
    return send_from_directory('/tmp', fname, as_attachment=True, mimetype="application/json", attachment_filename=cname)


if __name__ == '__main__':
    app.run()

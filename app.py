from flask import Flask,make_response, render_template, request, redirect, url_for, Response
import pandas as pd
from werkzeug.utils import secure_filename
from flask_cors import CORS
from cnn import create_model
import json
app = Flask(__name__)
cors=CORS(app)

@app.route('/', methods = ['GET', 'PUT'])
def runner():
    print("runner")
    if request.method == 'PUT':
        f = request.files['file']
        f.save("./static/"+secure_filename("data.txt"))
        path = "./static/"+secure_filename("data.txt")
        print(request.headers["model"])
        result = create_model(path=path, model_name=request.headers["model"], leadtime=int(request.headers["leadtime"]), r_max_lag=int(request.headers["rmaxlag"]), q_max_lag=int(request.headers["qmaxlag"]) ,epochh=int(request.headers["epoch"]), optimizerr=request.headers["optimizer"], loss_func=request.headers["lossfunction"])
        result_parsed = json.loads(json.dumps(result))
        return result_parsed["model_results"]


@app.route('/test', methods = ['GET'])
def test():
    return "test"



if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5000,debug=True)
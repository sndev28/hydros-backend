from flask import Flask,make_response, render_template, request, redirect, url_for, Response
import pandas as pd
from pandas import DataFrame
from werkzeug.utils import secure_filename
from flask_cors import CORS
from cnn import create_model, plot_correlation, download_dataset
import base64
import json
app = Flask(__name__)
cors = CORS(app)


@app.route('/', methods = ['GET', 'PUT'])
def runner():
    print("runner")
    if request.method == 'PUT':
        f = request.files['file']
        f.save("./static/"+secure_filename("data.txt"))
        path = "./static/"+secure_filename("data.txt")
        result = create_model(path=path, model_name=request.headers["model"], leadtime=int(request.headers["leadtime"]), r_max_lag=int(request.headers["rmaxlag"]), q_max_lag=int(request.headers["qmaxlag"]) ,epochh=int(request.headers["epoch"]), optimizerr=request.headers["optimizer"], loss_func=request.headers["lossfunction"])
        result_parsed = json.loads(json.dumps(result))
        return result_parsed


@app.route("/processed_data",methods = ['GET','PUT'])
def processed_data_func():
    if request.method == 'PUT':
        f = request.files['file']
        f.save("./static/"+secure_filename("data.txt"))
        path = "./static/"+secure_filename("data.txt")
        resp_json = {}
        x_train_df, x_test_df, y_train_df, y_test_df, dis_cache_df = download_dataset(path=path, leadtime=int(request.headers["leadtime"]), r_max_lag=int(request.headers["rmaxlag"]), q_max_lag=int(request.headers["qmaxlag"]))
        files_list = [x_train_df, x_test_df, y_train_df, y_test_df, dis_cache_df]
        for file in files_list:
            file.to_csv(file+".csv",index=False)
            with open(file+".csv", "r") as f:
                data = f.read()
            encoded_string = base64.b64encode(bytes(data, 'utf-8'))
            resp_json[file] = encoded_string
        resp_final = json.loads(json.dumps(resp_json))
        return resp_final


@app.route('/corr_plot', methods = ['GET', 'PUT'])
def corr_plot():
    if request.method == 'PUT':
        f = request.files['file']
        f.save("./static/"+secure_filename("data.txt"))
        path = "./static/"+secure_filename("data.txt")
        result = plot_correlation(path)
        result_parsed = json.loads(json.dumps(result))
        return result_parsed
        

@app.route('/test', methods = ['GET'])
def test():
    return "test"


if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5000,debug=True)
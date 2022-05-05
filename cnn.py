# -*- coding: utf-8 -*-
"""CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pa88yFFOAPEZGxLhPzwO1RZQblEvefky
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPooling1D
from tensorflow.keras.layers import GlobalMaxPooling1D
from tensorflow.keras.layers import LSTM
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
import sklearn
from sklearn.metrics import r2_score
from tensorflow.keras.utils import plot_model
import matplotlib.pyplot as plt


def normalize(x):
    x = x+0.001
    x = np.log(x)
    x_mean = np.mean(x)
    x_std = np.std(x)
    x = (x - np.mean(x))/np.std(x)
    x_min = np.min(x)
    x_max = np.max(x)
    x = (x-np.min(x))/(np.max(x)-np.min(x))
    cache_normalized = [x_min,x_max,x_mean,x_std]
    return x,cache_normalized


def denormalize(x,cache):
    x_min = cache[0]
    x_max = cache[1]
    x_mean = cache[2]
    x_std = cache[3]
    x = (x*(x_max - x_min)) + x_min
    x = (x*x_std) + x_mean
    x = np.exp(x)
    x = x-0.001
    return x 


def create_dataset(path, leadtime, rmaxlag, qmaxlag):
    # rmaxlag=9
    # qmaxlag = 2
    a=rmaxlag
    main_data = np.loadtxt(path, usecols = range(3))
    rain = np.matrix(main_data[:,1])
    rain,cache_rain = normalize(rain)
    rain = rain.T
    discharge = np.matrix(main_data[:,2])
    discharge,cache_dis = normalize(discharge)
    dis = discharge.T
    Data1 = np.zeros((2175-leadtime,6))
    Data2 = np.zeros((2175-leadtime,6))
    Data3 = np.zeros((2175-leadtime,6))
    for t in range(rmaxlag,2184-leadtime):
        Data1[t-rmaxlag, :] = [rain[t-rmaxlag], rain[t-rmaxlag+1], rain[t-rmaxlag+1], dis[t-qmaxlag], dis[t-qmaxlag+1], dis[t+leadtime]]
    for t in range(2184+rmaxlag, 4368-leadtime):
        Data2[t-2184-rmaxlag, :] = [rain[t-rmaxlag], rain[t-rmaxlag+1], rain[t-rmaxlag+1], dis[t-qmaxlag], dis[t-qmaxlag+1], dis[t+leadtime]]
    for t in range(4368+rmaxlag, 6552-leadtime):
        Data3[t-4368-rmaxlag, :] = [rain[t-rmaxlag], rain[t-rmaxlag+1], rain[t-rmaxlag+1], dis[t-qmaxlag], dis[t-qmaxlag+1], dis[t+leadtime]]
    Data123 = np.vstack((Data1, Data2, Data3))
    return Data123, cache_rain, cache_dis


def create_dataset_custom(path, leadtime, r_num, q_num, rmaxlag, qmaxlag):
    # rmaxlag=9
    # qmaxlag = 2
    f_total = r_num+q_num
    a=rmaxlag
    main_data = np.loadtxt(path, usecols = range(3))
    rain = np.matrix(main_data[:,1])
    rain,cache_rain = normalize(rain)
    rain = rain.T
    discharge = np.matrix(main_data[:,2])
    discharge,cache_dis = normalize(discharge)
    dis = discharge.T
    Data1 = np.zeros((2175-leadtime, f_total+1))
    Data2 = np.zeros((2175-leadtime, f_total+1))
    Data3 = np.zeros((2175-leadtime, f_total+1))
    for t in range(rmaxlag,2184-leadtime):
        r_list = [rain[t-rmaxlag+ri] for ri in range(r_num)]
        q_list = [dis[t-qmaxlag+qi] for qi in range(q_num)]
        q_list.append(dis[t+leadtime])
        Data1[t-rmaxlag, :] = r_list + q_list
    for t in range(2184+rmaxlag,4368-leadtime):
        r_list = [rain[t-rmaxlag+ri] for ri in range(r_num)]
        q_list = [dis[t-qmaxlag+qi] for qi in range(q_num)]
        q_list.append(dis[t+leadtime])
        Data2[t-2184-rmaxlag, :] = r_list + q_list
    for t in range(4368+rmaxlag,6552-leadtime):
        r_list = [rain[t-rmaxlag+ri] for ri in range(r_num)]
        q_list = [dis[t-qmaxlag+qi] for qi in range(q_num)]
        q_list.append(dis[t+leadtime])
        Data3[t-4368-rmaxlag, :] = r_list + q_list
    Data123 = np.vstack((Data1, Data2, Data3))
    return Data123, cache_rain, cache_dis


def mean_squared_error(y_true, y_pred):
    return K.mean(K.square(y_pred - y_true))


def create_train_test_data(path, leadtime, r_num, q_num, r_max_lag, q_max_lag, custom=False):
    if custom:
        data, rain_cache, dis_cache = create_dataset_custom(path, leadtime, r_num, q_num, r_max_lag, q_max_lag)
        f_total = r_num + q_num
        x_train = data[0:5500, 0:f_total]
        y_train = data[0:5500, f_total:]
        x_test = data[5500:, 0:f_total]
        y_test = data[5500:, f_total:]
    else:
        data,rain_cache,dis_cache = create_dataset(path, leadtime, r_max_lag, q_max_lag)
        x_train = data[0:5500,0:5]
        y_train = data[0:5500,5:]
        x_test = data[5500:,0:5]
        y_test = data[5500:,5:]
    return x_train, y_train, x_test, y_test, dis_cache


def plot_correlation(path):
    df = pd.read_csv(path, delimiter="\t", header=None,
                     names=["index", "rain", "dis", "non"])
    x = plt.xcorr(df["rain"], df["dis"], normed=True, usevlines=True, maxlags=20)
    results_return = {}
    results_return["cross_lags"] = x[0].tolist()
    results_return["cross_lags"] = [str(i) for i in results_return["cross_lags"]]
    results_return["cross_values"] = x[1].tolist()
    results_return["cross_values"] = [str(i) for i in results_return["cross_values"]]
    return results_return


def download_dataset(path, leadtime, r_num, q_num, r_max_lag, q_max_lag):
    x_train, y_train, x_test, y_test, dis_cache = create_train_test_data(path, leadtime, r_num, q_num, r_max_lag, q_max_lag, True)
    r_cols = ["r"+str(ri) for ri in range(r_num)]
    q_cols = ["q"+str(qi) for qi in range(q_num)]
    t_cols = r_cols + q_cols
    x_train_df = pd.DataFrame(x_train,columns=t_cols)
    x_test_df = pd.DataFrame(x_test, columns=t_cols)
    y_train_df = pd.DataFrame(y_train, columns=["q"])
    y_test_df = pd.DataFrame(y_test, columns=["q"])
    dis_cache_df = pd.DataFrame([dis_cache], columns=["min", "max", "mean", "std"])
    return x_train_df, x_test_df, y_train_df, y_test_df, dis_cache_df


def get_data_from_local_path(paths):
    return_dfs = []
    for path in paths:
        return_dfs.append(pd.read_csv(path))
    return return_dfs


def create_model(path, model_name="ann", leadtime=0, r_num=3, q_num=2, r_max_lag=9, q_max_lag=2, epochh=100, optimizerr="rmsprop", loss_func="mean_squared_error", layers_list=[], activation_function='relu', dataset=False):

    if(dataset):
        x_train, y_train, x_test, y_test, dis_cache = get_data_from_local_path(path)
    else:
        x_train, y_train, x_test, y_test, dis_cache = create_train_test_data(path, leadtime, r_num, q_num, r_max_lag, q_max_lag)

    if model_name == "ann":
        if len(layers_list) == 0:
            model_1 = tf.keras.Sequential([tf.keras.layers.Dense(5,input_dim=5,activation=activation_function),
                                        tf.keras.layers.Dense(4,activation=activation_function),
                                        tf.keras.layers.Dense(2,activation=activation_function),
                                        tf.keras.layers.Dense(1,activation=activation_function)])
        else:
            f_total = r_num + q_num
            input_layer = tf.keras.layers.Dense(f_total, input_dim=f_total, activation=activation_function)
            tf_layers = [tf.keras.layers.Dense(neurons,activation=activation_function) for neurons in layers_list]
            model_1 = tf.keras.Sequential(tf_layers)

    elif model_name == "cnn":
        if len(layers_list) == 0:
            model_1 = Sequential()
            model_1.add(Conv1D(filters=256, kernel_size=3, activation=activation_function, input_shape=(5, 1)))
            model_1.add(Conv1D(filters=64, kernel_size=2, activation=activation_function))
            model_1.add(GlobalMaxPooling1D())
            model_1.add(Dense(30, activation=activation_function))
            model_1.add(Dense(20, activation=activation_function))
            model_1.add(Dense(10, activation=activation_function))
            model_1.add(Dense(1, activation=activation_function))
        else:
            f_total = r_num + q_num
            model_1 = Sequential()
            input_layer = model_1.add(Conv1D(filters=layers_list["conv1DL"][0][0], kernel_size=layers_list["conv1DL"][0][1], activation=activation_function, input_shape=(f_total, 1)))
            for filters,kernerl_size in layers_list["conv1DL"][1:]:
                model_1.add(Conv1D(filters=filters, kernel_size=kernerl_size, activation=activation_function))
            model_1.add(GlobalMaxPooling1D())
            for dense_layer in layers_list["Dense"]:
                model_1.add(Dense(dense_layer, activation=activation_function))

    elif model_name == "lstm":
        if len(layers_list) == 0:
            model1 = Sequential()
            model1.add(LSTM(256, activation=activation_function, input_shape=(8, 1)))
            model1.add(LSTM(128,activation=activation_function))
            model1.add(Dense(128, activation=activation_function))
            model1.add(Dense(65, activation=activation_function))
            model1.add(Dense(1, activation=activation_function))
        else:
            f_total = r_num + q_num
            model_1 = Sequential()
            model_1.add(Conv1D(filters=layers_list["lstm"][0][0], kernel_size=layers_list["lstm"][0][1], activation=activation_function, input_shape=(f_total, 1))) # input_layer
            for filters,kernerl_size in layers_list["lstm"][1:]:
                model_1.add(LSTM(filters=filters, kernel_size=kernerl_size, activation=activation_function))
            for dense_layer in layers_list["Dense"]:
                model_1.add(Dense(dense_layer, activation=activation_function))

    model_1.compile(loss=loss_func, optimizer=optimizerr)
    model_1.fit(x_train,y_train,validation_data = (x_test,y_test),batch_size=64,epochs=epochh)

    y_pred_train = model_1.predict(x_train)
    y_pred_test = model_1.predict(x_test)

    y_pred_train = denormalize(y_pred_train,dis_cache)
    y_pred_test = denormalize(y_pred_test,dis_cache)
    y_train_denor = denormalize(y_train,dis_cache)
    y_test_denor = denormalize(y_test,dis_cache)

    y_pred_train_list = [str(i[0]) for i in y_pred_train]
    y_pred_test_list = [str(i[0]) for i in y_pred_test]
    y_train_denor_list = [str(i[0]) for i in y_train_denor]
    y_test_denor_list = [str(i[0]) for i in y_test_denor]

    results_json = {}
    results_json["train_pred"] = y_pred_train_list
    results_json["train_true"] = y_train_denor_list
    results_json["test_true"] = y_test_denor_list
    results_json["test_pred"] = y_pred_test_list

    cc_train = np.corrcoef(y_pred_train.T,y_train_denor.T)[0][1]
    cc_test = np.corrcoef(y_pred_test.T,y_test_denor.T)[0][1]
    print("train cc:", cc_train)
    print("test cc:",cc_test)
    print("--------------------------------------")
    train_NS = r2_score(y_pred_train,y_train_denor, sample_weight=None, multioutput='uniform_average')
    test_NS = r2_score(y_pred_test,y_test_denor, sample_weight=None, multioutput='uniform_average')
    print("train NS:",train_NS)
    print("test NS:",test_NS)
    mse_train = sklearn.metrics.mean_squared_error(y_pred_train,y_train_denor, sample_weight=None, multioutput='uniform_average')
    mse_test = sklearn.metrics.mean_squared_error(y_pred_test,y_test_denor, sample_weight=None, multioutput='uniform_average')
    print("--------------------------------------")
    print("train mse: "+str(mse_train))
    print("test mse: "+str(mse_test))
    print("--------------------------------------")
    rmse_train = np.sqrt(mse_train)
    rmse_test = np.sqrt(mse_test)
    print("train rmse: "+str(np.sqrt(mse_train)))
    print("test rmse: "+str(np.sqrt(mse_test)))

    results = [['NS/R2',train_NS,test_NS],['Corr-coeff',cc_train,cc_test],['RMSE',rmse_train,rmse_test],['MSE',mse_train,mse_test]]
    df_results = pd.DataFrame(results,columns=['ERROR METRICS', 'Train', 'Test'])
    df_results.to_csv('static/results.csv', index = None, header=True)
    df_results.fillna('', inplace=True)
    result=df_results.to_dict()
    results_json["model_results"] = result
    return(results_json)
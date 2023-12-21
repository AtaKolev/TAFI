import numpy as np
from neural_networks import AnomalyDetector
from sklearn.metrics import mean_absolute_error
import pandas as pd


class HelperFunctions:
    
    @staticmethod
    def train_test_split(series, test_size, lag):
        for idx in range(len(series)):
            if (idx % lag) == 0:
                cut = series[idx:idx+lag].values    
                if idx == 0:
                    arr = cut
                else:
                    if len(cut) == lag:
                        arr = np.vstack((arr, cut))
                    else:
                        continue
            else:
                continue

        train = arr[:-test_size]
        test = arr[-test_size:]
        X_train = train[:-1]
        y_train = train[1:]
        X_test = test[:-1]
        y_test = test[-1]

        return X_train, X_test, y_train, y_test

    @staticmethod
    def autoencoder_optimize(X_train, X_test, y_train, y_test, model_params):

        losses = model_params['loss']
        optimizers = model_params['optimizer']
        activation_functions = model_params['activation_functions']
        epochs = model_params['epochs']
        error_structure_model = {}

        for activation_function in activation_functions:
            for loss in losses:
                for optimizer in optimizers:
                    for epoch in epochs:
                        print(f"Epoch: {epoch}")
                        print(f"optimizer: {optimizer}")
                        print(f"Loss: {loss}")
                        print(f"Activation: {activation_function}")
                        try:
                            model = AnomalyDetector(activation_function)
                            model.compile(loss = loss, optimizer = optimizer)
                            _ = model.fit(X_train, y_train, epochs = epoch)
                            prediction = model.predict(X_test)
                            error_structure_model.update({mean_absolute_error(y_test, prediction) : {(activation_function, loss, optimizer) : [model, prediction]}})
                        except:
                            print(f"Couldn't train with combination Epoch: {epoch} | Optimizer: {optimizer} | Loss: {loss} | Activation: {activation_function}")

        best_mae = sorted(list(error_structure_model.keys()))[0]

        return best_mae, error_structure_model     
    
    @staticmethod
    def train_test_split_AR(series, lag, test_size):
        X_cols = ['X'+str(i+1) for i in range(lag)]
        xy_df = pd.DataFrame(columns = X_cols + ['y'])

        for indx in range(len(series.shift(-lag).dropna())):
            xy_df.loc[indx, :] = np.hstack((series[indx:indx+lag].values, series[indx+lag]))
        
        #xy_df = xy_df.dropna()
        X = xy_df.loc[:, X_cols]
        y = xy_df.loc[:, 'y']

        X_train = X.loc[:len(X)-test_size].astype(np.float32)
        X_test = X.loc[len(X)-test_size:].astype(np.float32)
        y_train = y.loc[:len(y)-test_size].astype(np.float32)
        y_test = y.loc[len(y)-test_size:].astype(np.float32)

        return X_train, X_test, y_train, y_test
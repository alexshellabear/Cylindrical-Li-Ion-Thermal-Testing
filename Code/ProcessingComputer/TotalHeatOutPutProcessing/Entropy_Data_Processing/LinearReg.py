# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 17:09:15 2019

@author: Alexander
Note to self: For each row of the x array you will need the data (features) column and the weight (samples) column.
              each row on the y array has data (target) and frequency
              	
X : array-like or sparse matrix, shape (n_samples, n_features)
y : array_like, shape (n_samples, n_targets)
https://stackoverflow.com/questions/29462108/sklearn-linear-regression-x-and-y-input-format/29462216
"""

# linear regression

import numpy as np
from sklearn.linear_model import LinearRegression

class LinearRegClass:
    def __init__(self,XList,YList):
        if len(XList) == len(YList):
            # Convert to array and add dimension
            XArr = np.array(XList)[:,np.newaxis]
            YArr = np.array(YList)[:,np.newaxis]
            LinReg = LinearRegression()  # create object for the class
            LinReg.fit(XArr, YArr)  # perform linear regression
            self.Gradient = float(LinReg.coef_)
            #c = float(LinReg.intercept_)
        else:
            print('ERROR, LinearRegClass lengths are wrong')    
            self.Gradient = 0.0



















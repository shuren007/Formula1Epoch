#import tensorflow as tf
import numpy as np
import keras
#import matplotlib
#from matplotlib.pyplot import imshow
from keras.models import Model, load_model, Sequential
from keras.optimizers import Adam
from keras import optimizers
from keras.layers import Input, Convolution2D, MaxPooling2D, Activation, Dropout, Flatten, Dense
import cv2
import helperFunctions
from keras.utils import plot_model
from keras.callbacks import CSVLogger

csv = CSVLogger('SteerNetSimple.csv', separator='\n', append=True)

def model():
    #Model with 3 hidden layers
    #Input takes in image
    img = Input(shape = (376, 672, 3), name = 'img')
#    x = keras.layers.concatenate([img, lidarInput])

    # x = Dense(64, activation='relu')(x)
    # x = Dense(64, activation='relu')(x)
    # x = Dense(64, activation='relu')(x)

    #Convolution/Pooling Layer 1
    x = Convolution2D(4, 3, 3)(img)
    x = Activation('relu')(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    #Convolution/Pooling Layer 2
    x = Convolution2D(8, 3, 3)(x)
    x = Activation('relu')(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    #Convolution/Pooling Layer 3
    x = Convolution2D(16, 3, 3)(x)
    x = Activation('relu')(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    #Flattens into 1D array for Usage in final layer
    merged = Flatten()(x)
    #One final fully connected layer for figuring output values
    x = Dense(128)(merged)
    x = Activation('linear')(x)
    x = Dropout(.3)(x)

    # LIDAR LAYERS
    y = Input(shape=(1581, 3))
    y = Convolution2D(4, 3, 3)(img)
    x = Activation('relu')(y)
    y = MaxPooling2D(pool_size=(2, 2))(y)
    #Convolution/Pooling Layer 2
    y = Convolution2D(8, 3, 3)(y)
    y = Activation('relu')(y)
    y = MaxPooling2D(pool_size=(2, 2))(y)
    #Convolution/Pooling Layer 3
    y = Convolution2D(16, 3, 3)(y)
    y = Activation('relu')(y)
    y = MaxPooling2D(pool_size=(2, 2))(y)
    #Flattens into 1D array for Usage in final layer
    merged = Flatten()(y)
    #One final fully connected layer for figuring output values
    y = Dense(128)(merged)
    y = Activation('linear')(y)
    y = Dropout(.3)(y)

    #finalLayer = keras.layers.concatenate([x, y])

    #Final output
    jstk = Dense(1, name='jstk')(x)

    # We stack a densely-connected network on top
    # x = Dense(64, activation='relu')(x)
    # x = Dense(64, activation='relu')(x)
    # x = Dense(64, activation='relu')(x)
    #Compiled and initializes the model
    steerNet = Model(input=[img], output=[jstk])
    steerNet.compile(optimizer='adam', loss='mean_squared_error')
    #adamOptimizer = keras.optimizers.Adam(lr=0.000025, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
    print(steerNet.summary())
    return steerNet

def trainModel(model, imgIn, jstkOut):
    #Trains predefined model with verbose logging, input image data and output steering data
    csv = CSVLogger('SteerNetSimple.csv', separator='\n', append=True)
    model.fit(x= imgIn, y=jstkOut, batch_size=32, epochs=300, verbose=2, callbacks=[csv], validation_split=0.2, shuffle=True, initial_epoch=0)
    modelName = 'steerNetSimple'
    modelPng = modelName + ".png"
    modelName = modelName + ".h5"
    #Plots the trained model
    #plot_model(modelName, to_file=modelPng)
    model.save(modelName)
    print("Saved as %s" %(modelName) )
    return model

def testModel(model, testX, testY):
    # Test model and evauluate accuracy, prints it
    scores = model.evaluate(testX, testY)
    print("\nAccuracy: " + model.metrics_name[1], scores[1]*100)

def main():
    #Main Function, starts with path inputs
    #imagePath = raw_input("Please enter the filepath to your images folder")
    #labelPath = raw_input("Please enter the filepath to your labels folder")
    #Uses helper functions to get array of images and outputs
    imgAr = helperFunctions.getTrainingData('/media/ricky/ZED/images/')
    jstkAr = helperFunctions.mapImageToJoy('/media/ricky/ZED/joydata.txt', '/media/ricky/ZED/timestamp.txt')
    lidarData = helperFunctions.parseLidarData('/media/ricky/UBUNTU/scandata.txt', '/media/ricky/ZED/timestamp.txt')

    print(imgAr)
    #Runs model function to initialize model
    steerModel = model()
    #Trains model with the function
    trModel = trainModel(steerModel, imgAr, jstkAr, lidarData)

main()
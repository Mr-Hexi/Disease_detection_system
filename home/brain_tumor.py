import cv2
import numpy as np
from skimage import io
from PIL import Image 
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import ResNet50





        
def preprocess_img(img_path:str,mask:bool=False):
        img = io.imread(img_path)
        img = cv2.resize(img, (256,256))
        img = np.array(img, dtype=np.float64)
        if mask:
            img -= img.mean()
            img /= img.std()
        else:
            img = img *1./255.
        img = np.expand_dims(img,0)
        return img
    



def load_resnet(weights,train_params=True):
    clf_model = ResNet50(weights='imagenet', include_top=False, input_tensor=Input(shape=(256,256,3)))
    head = clf_model.output
    head = AveragePooling2D(pool_size=(4,4))(head)
    head = Flatten(name='Flatten')(head)
    head = Dense(256, activation='relu')(head)
    head = Dropout(0.3)(head)
    head = Dense(256, activation='relu')(head)
    head = Dropout(0.3)(head)
    head = Dense(2, activation='softmax')(head)
    model = Model(clf_model.input, head)
    model.load_weights(weights)

    if not train_params:
        for layer in model.layers:
            layer.trainable = False

    return model








def resblock(X, f):
    '''
    function for creating res block
    '''
    X_copy = X  #copy of input
    
    # main path
    X = Conv2D(f, kernel_size=(1,1), kernel_initializer='he_normal')(X)
    X = BatchNormalization()(X)
    X = Activation('relu')(X)
    
    X = Conv2D(f, kernel_size=(3,3), padding='same', kernel_initializer='he_normal')(X)
    X = BatchNormalization()(X)
    
    # shortcut path
    X_copy = Conv2D(f, kernel_size=(1,1), kernel_initializer='he_normal')(X_copy)
    X_copy = BatchNormalization()(X_copy)
    
    # Adding the output from main path and short path together
    X = Add()([X, X_copy])
    X = Activation('relu')(X)
    
    return X

def upsample_concat(x, skip):
    '''
    funtion for upsampling image
    '''
    X = UpSampling2D((2,2))(x)
    merge = Concatenate()([X, skip])
    
    return merge

def load_unet(weights ,train_params = True):
    input_shape = (256,256,3)
    X_input = Input(input_shape) #iniating tensor of input shape

    # Stage 1
    conv_1 = Conv2D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal')(X_input)
    conv_1 = BatchNormalization()(conv_1)
    conv_1 = Conv2D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv_1)
    conv_1 = BatchNormalization()(conv_1)
    pool_1 = MaxPool2D((2,2))(conv_1)

    # stage 2
    conv_2 = resblock(pool_1, 32)
    pool_2 = MaxPool2D((2,2))(conv_2)

    # Stage 3
    conv_3 = resblock(pool_2, 64)
    pool_3 = MaxPool2D((2,2))(conv_3)

    # Stage 4
    conv_4 = resblock(pool_3, 128)
    pool_4 = MaxPool2D((2,2))(conv_4)

    # Stage 5 (bottle neck)
    conv_5 = resblock(pool_4, 256)

    # Upsample Stage 1
    up_1 = upsample_concat(conv_5, conv_4)
    up_1 = resblock(up_1, 128)

    # Upsample Stage 2
    up_2 = upsample_concat(up_1, conv_3)
    up_2 = resblock(up_2, 64)

    # Upsample Stage 3
    up_3 = upsample_concat(up_2, conv_2)
    up_3 = resblock(up_3, 32)

    # Upsample Stage 4
    up_4 = upsample_concat(up_3, conv_1)
    up_4 = resblock(up_4, 16)

    # final output
    out = Conv2D(1, (1,1), kernel_initializer='he_normal', padding='same', activation='sigmoid')(up_4)
    seg_model = Model(X_input, out)
    seg_model.load_weights(weights)
    
    
    if not train_params:
        for layer in seg_model.layers:
            layer.trainable = False
    
    
    return seg_model



def prediction(img_path,model,seg_model=None):

    # First predicting if there is Tumor or not
    img = preprocess_img(img_path,mask=False)
    clf_pred = model.predict(img)
    print(clf_pred.argmax(),clf_pred)
    # Second Masking the Area Where Tumor is Present
    if clf_pred.argmax() ==1:
        img = preprocess_img(img_path,mask=True)
        seg_predict =  np.array(seg_model.predict(img)).squeeze().round()
        
        seg_img = io.imread(img_path)
        seg_img[seg_predict==1] = (0,255,150)
        im = Image.fromarray(seg_img)
        im.save("media/bt_seg.jpg")
        
        return 1
    else:
        im = Image.open(img_path)
        im.save("media/no_bt.jpg")  
        return 0 

    
    

    

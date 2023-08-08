import os
import cv2
import logging
import numpy as np
from PIL import Image 
from skimage import io
import tensorflow as tf
# logging.disable(logging.WARNING)
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"



def preprocess_img(img_path: str, mask: bool = False, resize_shape=(256, 256), normalize=True):
    img = io.imread(img_path)
    img = cv2.resize(img, resize_shape)
    img = np.array(img, dtype=np.float64)
    if normalize:
        img = img * 1.0 / 255.
    if mask:
        img -= img.mean()
        img /= img.std()
    img = np.expand_dims(img, 0)
    return img

def pneumonia_predict(img_path, model, scale=True,):
    class_names= ["NO PNEUMONIA DETECTED", "PNEUMONIA Detected"]
    # Read in the image
    img = tf.io.read_file(img_path)
    # Decode it into a tensor
    img = tf.io.decode_image(img, channels=3)
    # Resize the image
    img = tf.image.resize(img, [224,224])
    img = img/255.
    img = tf.expand_dims(img,axis=0)
    pred = model.predict(img)
    print("ppred",pred)
    pred_class = class_names[int(np.round(pred))]
    return pred_class

def bt_predict(img_path, model, seg_model=None):
    # First predicting if there is Tumor or not
    img = preprocess_img(img_path=img_path, mask=False)
    clf_pred = model.predict(img)
    if clf_pred.argmax() == 1:
        img = preprocess_img(img_path=img_path, mask=True)
        seg_predict = np.array(seg_model.predict(img)).squeeze().round()

        seg_img = io.imread(img_path)
        seg_img[seg_predict == 1] = (0, 255, 150)
        im = Image.fromarray(seg_img)
        im.save("media/bt_seg.jpg")

        return 1,clf_pred.max()
    else:
        im = Image.open(img_path)
        im.save("media/no_bt.jpg")
        return 0, clf_pred.max()


    
    



def ret_predict(img_path,model):
    class_names = ['No disease detected', 'CNV Detected', 'DME Detected', 'DRUSEN Detected']
    img = tf.io.read_file(img_path)
    # Decode it into a tensor
    img = tf.io.decode_image(img, channels=3)
    # Resize the image
    img = tf.image.resize(img, [150,150])
    img = img/255.
    img = tf.expand_dims(img,axis=0)
    pred = model.predict(img)
    pred_class = class_names[pred.argmax()]
    return pred_class
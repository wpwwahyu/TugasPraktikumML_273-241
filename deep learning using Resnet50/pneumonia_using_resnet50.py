# -*- coding: utf-8 -*-
"""Pneumonia Using Resnet50.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Y9RDwfAMpzFA37a_4HZMGWMGkzfTN6Lq

#Data
"""

# Tulis Program Anda Disini!
from google.colab import drive
drive.mount('/content/drive')

# Definisikan path kaggle json
# Sesuaikan dengan path anda
import os
os.environ['KAGGLE_CONFIG_DIR'] = "/content/drive/MyDrive/Kaggle"

# Commented out IPython magic to ensure Python compatibility.
# Ubah lokasi direktori kerja
# Sesuaikan dengan path anda
# %cd /content/drive/MyDrive/Colab Notebooks/Semester 7/Temu Kembali Citra/Tugas Besar CBIR
!ls

data_dir = "/content/drive/MyDrive/Colab Notebooks/Semester 7/Pembelajaran Mesin/Modul 4/chest_xray.zip"

# Cek isi direktori kerja untuk memastikan dataset telah berhasil diekstrak.
!ls

import os
base_dataset = "chest_xray"
class_dir = ['NORMAL', 'PNEUMONIA']
for class_item in class_dir:
  cur_dir = base_dataset+"/"+class_item
  dataset = os.listdir(cur_dir)
  for item in dataset:
    if not item.endswith(".jpeg"):
        os.remove(os.path.join(cur_dir, item))

"""##Splitting"""

!pip install split_folders
import splitfolders

#untuk menetapkan directory

input_folder = "/content/drive/MyDrive/Colab Notebooks/Semester 7/Temu Kembali Citra/Tugas Besar CBIR/chest_xray"
base_dir = "/content/drive/MyDrive/Colab Notebooks/Semester 7/Temu Kembali Citra/Tugas Besar CBIR/split_folder_pneumonia"

splitfolders.ratio(input_folder, output = base_dir, seed=1337, ratio=(0.80,0.19,0.01))

import os
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'val')
test_dir = os.path.join(base_dir, 'test')

train_normal_dir = os.path.join(train_dir, 'NORMAL')
train_pneumonia_dir = os.path.join(train_dir, 'PNEUMONIA')

validation_normal_dir = os.path.join(validation_dir, 'NORMAL')
validation_pneumonia_dir = os.path.join(validation_dir, 'PNEUMONIA')

test_normal_dir = os.path.join(test_dir, 'NORMAL')
test_pneumonia_dir = os.path.join(test_dir, 'PNEUMONIA')

print('Train NORMAL :', len(os.listdir(train_normal_dir)))
print('Train PNEUMONIA :', len(os.listdir(train_pneumonia_dir)))
print("\n")

print('Validation NORMAL :', len(os.listdir(validation_normal_dir)))
print('Validation PNEUMONIA :', len(os.listdir(validation_pneumonia_dir)))
print("\n")

print('Test NORMAL :', len(os.listdir(test_normal_dir)))
print('Test PNEUMONIA :', len(os.listdir(test_pneumonia_dir)))

"""#Preprocessing"""

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt 
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from keras.callbacks import ReduceLROnPlateau

# import library to build our model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dropout, Flatten, Dense, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import Model
#from tensorflow.keras.applications.vgg16 import preprocess_input

# plotting
# %matplotlib inline
import matplotlib.image as mpimg
import numpy as np

height = 150
width = 150
batch_size = 32

generator_datagen = ImageDataGenerator(
    rescale = 1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

val_gen = ImageDataGenerator(rescale = 1./255)

train_generator = generator_datagen.flow_from_directory(
    train_dir,
    target_size=(height, width),
    class_mode='binary',
    color_mode="rgb",
    shuffle=True,
    batch_size=batch_size
)

validation_generator = val_gen.flow_from_directory(
    validation_dir,
    target_size=(height,width),
    class_mode='binary',
    color_mode="rgb",
    shuffle=False,
    batch_size=batch_size
)

test_generator = val_gen.flow_from_directory(
    test_dir,
    target_size=(height,width),
    class_mode='binary',
    color_mode="rgb",
    shuffle=False,
    batch_size=batch_size
)

import cv2
import numpy as np

# Gather data train
train_data = []
train_label = []
for r, d, f in os.walk(train_dir):
    for file in f:
        if ".jpeg" in file:
            imagePath = os.path.join(r, file)
            image = cv2.imread(imagePath)
            image = cv2.resize(image, (150,150))
            train_data.append(image)
            label = imagePath.split(os.path.sep)[-2]
            train_label.append(label)

train_data = np.array(train_data)
train_label = np.array(train_label)

# Gather data validation
val_data = []
val_label = []
for r, d, f in os.walk(validation_dir):
    for file in f:
        if ".jpeg" in file:
            imagePath = os.path.join(r, file)
            image = cv2.imread(imagePath)
            image = cv2.resize(image, (150,150))
            val_data.append(image)
            label = imagePath.split(os.path.sep)[-2]
            val_label.append(label)

val_data = np.array(val_data)
val_label = np.array(val_label)

# Gather data test
test_data = []
test_label = []
for r, d, f in os.walk(test_dir):
    for file in f:
        if ".jpeg" in file:
            imagePath = os.path.join(r, file)
            image = cv2.imread(imagePath)
            image = cv2.resize(image, (150,150))
            test_data.append(image)
            label = imagePath.split(os.path.sep)[-2]
            test_label.append(label)

test_data = np.array(test_data)
test_label = np.array(test_label)

# Tampilkan shape dari data train dan data validation
print("Train Data = ", train_data.shape)
print("Train Label = ", train_label.shape)
print("Validation Data = ", val_data.shape)
print("Validation Label = ", val_label.shape)
print("Test Data = ", test_data.shape)
print("Test Label = ", test_label.shape)

# Normalisasi dataset
print("Data sebelum di-normalisasi ", train_data[0][0][0])

x_train = train_data.astype('float32') / 255.0
x_test = test_data.astype('float32') / 255.0
x_val = val_data.astype('float32') / 255.0
print("Data setelah di-normalisasi ", x_train[0][0][0])

# Transformasi label encoder
from sklearn.preprocessing import LabelEncoder

print("Label sebelum di-encoder ", train_label[3419:3422])
print("Label sebelum di-encoder ", train_label[800:803])

lb = LabelEncoder()
y_train = lb.fit_transform(train_label)
y_test = lb.fit_transform(test_label)
y_val = lb.fit_transform(val_label)

print("Label setelah di-encoder ", y_train[3419:3422])
print("Label setelah di-encoder ", y_train[800:803])

# #Performing over-sampling of the data, since the classes are imbalanced
# from imblearn.over_sampling import SMOTE

# smote = SMOTE(random_state=42)

# val_data, val_label = smote.fit_resample(val_data.reshape(-1, 150 * 150 * 3), val_label)

# val_data = val_data.reshape(-1, 150, 150, 3)

# print(val_data.shape, val_label.shape)

# from tensorflow.keras.preprocessing.image import ImageDataGenerator
# aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1,
#                         height_shift_range=0.1, shear_range=0.2, 
#                         zoom_range=0.8, horizontal_flip=True,
#                         fill_mode="nearest")

from tensorflow.keras.models import Sequential,load_model
from tensorflow.keras.layers import InputLayer, Dense, Conv2D, MaxPool2D, Flatten, BatchNormalization, Dropout,AveragePooling2D, GlobalAveragePooling2D
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from tensorflow.keras.optimizers import Adam
import time
from tensorflow.keras import layers

# Pertama, kita import dulu library yang dibutuhkan
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten, Dropout, Input
from tensorflow.keras.applications.vgg16 import VGG16

"""#Model 1"""

# Kita load model VGG16, kemudian kita potong bagian Top atau Fully Connected Layernya
baseModel = VGG16(include_top=False, input_tensor=Input(shape=(150, 150, 3)))

baseModel.summary()

x = layers.Flatten()(baseModel.output)
x = layers.Dense(64, activation='relu')(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.2)(x)                 
x = layers.Dense(3, activation='softmax')(x)

model = Model(baseModel.input, x)

for layer in baseModel.layers:
  layer.trainable = False

model.summary()

from tensorflow.keras.callbacks import EarlyStopping

class MyCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get('val_acc') > 0.9:
            print("\nReached accuracy threshold! Terminating training.")
            self.model.stop_training = True
            
my_callback = MyCallback()

#EarlyStopping callback to make sure model is always learning
early_stopping = EarlyStopping(monitor='val_loss', patience=2)

from tensorflow.keras.optimizers import Adam

CALLBACKS = [my_callback]

model.compile(optimizer=Adam(learning_rate=0.001, decay=0.001/32), # decay = learning_rate / batch_size 
              loss='categorical_crossentropy', 
              metrics=['acc'])

# history = model.fit(train_generator, batch_size=32, epochs=25, validation_data = validation_generator, callbacks=CALLBACKS)

# history = model.fit(train_generator, batch_size=32, epochs=150, validation_data = validation_generator)

history = model.fit(train_generator, batch_size=32, epochs=25, validation_data = validation_generator)

history2 = model.fit(train_generator, batch_size=32, epochs=10, validation_data = validation_generator, callbacks=CALLBACKS)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize = (30, 5))
ax = ax.ravel()

for i, metric in enumerate(["acc", "loss"]):
    ax[i].plot(history.history[metric])
    ax[i].plot(history.history["val_" + metric])
    ax[i].set_title("Model {}".format(metric))
    ax[i].set_xlabel("Epochs")
    ax[i].set_ylabel(metric)
    ax[i].legend(["train", "val"])

from sklearn.metrics import classification_report
import numpy as np

target_names = []

for key in train_generator.class_indices:
    target_names.append(key)

pred_labels = model.predict(test_generator)
y_pred = np.argmax(pred_labels, axis=1)

print('Classification Report')
print(classification_report(test_generator.classes, y_pred, target_names=target_names))

#Plot the confusion matrix. Set Normalize = True/False
from sklearn.metrics import confusion_matrix
import itertools

def plot_confusion_matrix(cm, classes, normalize=True, title='Confusion Matrix', cmap=plt.cm.Blues):

    plt.figure(figsize=(7,7))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm = np.around(cm, decimals=2)
        cm[np.isnan(cm)] = 0.0
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

pred = model.predict(test_generator)
labels = np.argmax(pred, axis=1)

print('Confusion Matrix')
cm = confusion_matrix(test_generator.classes, labels)
plot_confusion_matrix(cm, target_names, title='Confusion Matrix')

"""#Model 2"""

from tensorflow.keras.applications.resnet50 import ResNet50

resModel = ResNet50(include_top=False,weights='imagenet', input_tensor=Input(shape=(150, 150, 3)))

resModel.summary()

x = layers.Flatten()(resModel.output)
x = layers.Dense(64, activation='relu')(x)
x = layers.Dense(32, activation='relu')(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.2)(x)                 
x = layers.Dense(1, activation='sigmoid')(x)

model2 = Model(resModel.input, x)

for layer in resModel.layers:
  layer.trainable = False

model2.summary()

model2.compile(optimizer=Adam(learning_rate=0.001, decay=0.001/32), # decay = learning_rate / batch_size 
              loss='binary_crossentropy',
              metrics=['acc'])

history = model2.fit(train_generator, batch_size=32, epochs=5, validation_data = validation_generator)

"""#Save Model"""

model2.save('/content/drive/MyDrive/Colab Notebooks/Semester 7/Pembelajaran Mesin/Resnet50.h5')

# model.save('model.tflite')
model2.save('model2.tflite')

# loaded_model = tf.keras.models.load_model('model1.tflite')
# loaded_model.layers[0].input_shape #(None, 150, 150, 3)

loaded_model2 = tf.keras.models.load_model('model2.tflite')
loaded_model2.layers[0].input_shape #(None, 150, 150, 3)

from PIL import Image
import cv2
from tensorflow.keras.models import  load_model

img_upload = Image.open("/content/drive/MyDrive/Colab Notebooks/Semester 7/Temu Kembali Citra/Tugas Besar CBIR/chest_xray/NORMAL/IM-0001-0001.jpeg")
img_plt = plt.imshow(img_upload)
img = np.array(img_upload)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

model_list = ["/content/drive/MyDrive/Colab Notebooks/Semester 7/Temu Kembali Citra/Tugas Besar CBIR/model2.tflite"]
labels = ['NORMAL', 'PNEUMONIA']

for m in model_list:
    model = load_model(m)
    size_img = model.layers[0].output_shape[1:2]
    imgs = cv2.resize(img,(150, 150), interpolation = cv2.INTER_CUBIC)
    imgs = imgs.astype('float32') / 255
    pred = model.predict(np.expand_dims(imgs, axis=0))[0]
    print('Model :', m.split('/')[-1])
    print('Predicted Label :',labels[((pred > 0.5)+0).ravel()[0]])
    print('Probability :',[ round(elem, 4) for elem in pred ][0])
    print('===============\n')

from PIL import Image
import cv2
from tensorflow.keras.models import  load_model

img_upload = Image.open("/content/drive/MyDrive/Colab Notebooks/Semester 7/Temu Kembali Citra/Tugas Besar CBIR/chest_xray/PNEUMONIA/person1000_bacteria_2931.jpeg")
img_plt = plt.imshow(img_upload)
img = np.array(img_upload)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

model_list = ["/content/drive/MyDrive/Colab Notebooks/Semester 7/Temu Kembali Citra/Tugas Besar CBIR/model2.tflite"]
labels = ['NORMAL', 'PNEUMONIA']

for m in model_list:
    model = load_model(m)
    size_img = model.layers[0].output_shape[1:2]
    imgs = cv2.resize(img,(150, 150), interpolation = cv2.INTER_CUBIC)
    imgs = imgs.astype('float32') / 255
    pred = model.predict(np.expand_dims(imgs, axis=0))[0]
    print('Model :', m.split('/')[-1])
    print('Predicted Label :',labels[((pred > 0.5)+0).ravel()[0]])
    print('Probability :',[ round(elem, 4) for elem in pred ][0])
    print('===============\n')
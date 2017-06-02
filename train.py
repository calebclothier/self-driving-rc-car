import os
import numpy as np
import tensorflow as tf
import cv2
from sklearn.utils import shuffle
from keras.layers import Activation, Dense, Flatten, Lambda, Dropout
from keras.layers.convolutional import Conv2D
from keras.models import Sequential, model_from_json
from keras.optimizers import SGD
from keras.regularizers import l2
import matplotlib.pyplot as plt

def display_image(image):
    cv2.imshow('Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def label_histogram(labels):
    y = []
    for i in range(len(labels)):
        if np.argmax(labels[i]) == 0:
            y.append(0)
        if np.argmax(labels[i]) == 1:
            y.append(1)
        if np.argmax(labels[i]) == 2:
            y.append(2)
    plt.hist(y, bins='auto')
    plt.title('Histogram of steering labels')
    plt.show()

def crop(image):
    """Crop out the top part of the image"""
    image = image[130:220,:]
    return image

def blur(image):
    """Apply a slight blur to the image"""
    image = cv2.GaussianBlur(image, (3,3), 0)
    return image

def resize(image):
    """Resize the image in accordance with the nVidia paper model"""
    image = cv2.resize(image,(200, 66), interpolation=cv2.INTER_AREA)
    return image

def normalize(image):
    """Returns a normalized image with feature values from -1.0 to 1.0."""
    return image / 127.5 - 1.

def process(image):
    image = crop(image)
    image = blur(image)
    image = resize(image)
    return image

def random_distort(image):
    """Distorts input images to artificially augment the dataset"""
    # Randomly adjust brightness of the grayscale image
    value = np.random.randint(-28, 28)
    if value > 0:
        mask = (image + value) > 255 
    if value <= 0:
        mask = (image + value) < 0
    image += np.where(mask, 0, value) 
    return image

def flip(image, label):
    """Flips an image and changes the label accordingly"""
    image = cv2.flip(image, 1)
    if np.argmax(label) == 1:
        label = [0, 0, 1, 0]
    if np.argmax(label) == 2:
        label = [0, 1, 0, 0]
    return image, label

def generate_batch(train_images, train_labels, batch_size=64):
    """Generates a batch of 64 processed images and labels"""
    # From (240, 320, num_examples) --> (num_examples, 240, 320)
    train_images = np.rollaxis(train_images, 2, 0)
    train_images = np.expand_dims(train_images, axis=3)
    # Randomly shuffle the training data
    train_images, train_labels = shuffle(train_images, train_labels)
    # Generate batches continuously
    X, y = ([], [])
    while True:
        for i in range(len(train_labels)):
            image = process(train_images[i])
            image = random_distort(image)
            label = train_labels[i]
            X.append(image)
            y.append(label)
            # Add a flipped version of every image
            flipped_image, flipped_label = flip(image, label)
            X.append(flipped_image)
            y.append(flipped_label)
            # Once a full batch is created, the X and y arrays are reset
            if len(X) == batch_size:
                yield (np.expand_dims(np.array(X), axis=3), np.array(y))
                X, y = ([], [])
                train_images, train_labels = shuffle(train_images, train_labels)

def NVIDIA_model():
    """Creates a convolutional neural network as outlined in the nVidia paper"""
    model = Sequential()
    # Normalization layer
    model.add(Lambda(normalize, input_shape=(66, 200, 1)))
    # Block1
    model.add(Conv2D(24, (5, 5), strides=[2, 2], padding="valid", kernel_regularizer=l2(0.001)))
    model.add(Activation('relu'))
    # Block2
    model.add(Conv2D(36, (5, 5), strides=[2, 2], padding="valid", kernel_regularizer=l2(0.001)))
    model.add(Activation('relu'))
    # Block3
    model.add(Conv2D(48, (5, 5), strides=[2, 2], padding="valid", kernel_regularizer=l2(0.001)))
    model.add(Activation('relu'))
    # Block4
    model.add(Conv2D(64, (3, 3), strides=[1, 1], padding="valid", kernel_regularizer=l2(0.001)))
    model.add(Activation('relu'))
    # Block5
    model.add(Conv2D(64, (3, 3), strides=[1, 1], padding="valid", kernel_regularizer=l2(0.001)))
    model.add(Activation('relu'))
    # Flatten
    model.add(Flatten())
    # FC1
    model.add(Dense(100, activation='relu', kernel_regularizer=l2(0.001)))
    # FC3
    model.add(Dense(50, activation='relu', kernel_regularizer=l2(0.001)))
    # FC4
    model.add(Dense(10, activation='relu', kernel_regularizer=l2(0.001)))
    # Output
    #model.add(Dense(4))
    model.add(Dense(4, activation='softmax'))
    # Compile the model
    #model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def artificial_neural_network():
    """Creates a simple feedforward neural network with one hidden layer"""
    model = Sequential()
    model.add(Lambda(normalize, input_shape=(66, 200, 1)))
    # Flatten the image
    model.add(Flatten())
    # Hidden layer
    model.add(Dense(32, activation='tanh'))
    # Output layer
    model.add(Dense(4, activation='softmax'))
    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_NVIDIA_model(train_images, train_labels):
    # Initialize the neural network and train
    model = NVIDIA_model()
    model.summary()
    model.fit_generator(generate_batch(train_images, train_labels), 
        steps_per_epoch=60, epochs=30, verbose=2)
    print('Saving model weights and configuration file.')
    # Save model weights
    model_name = input('Enter model name: ')
    model.save_weights('NVIDIA_model/{}.h5'.format(model_name))
    # Save model architecture as json file
    json = model.to_json()
    with open('NVIDIA_model/{}.json'.format(model_name), 'w') as f:
        f.write(json)

def train_ANN(train_images, train_labels):
    model = artificial_neural_network()
    model.summary()
    model.fit_generator(generate_batch(train_images, train_labels), 
        steps_per_epoch=30, epochs=30, verbose=2)
    print('Saving model weights and configuration file.')
    # Save model weights
    model_name = input('Enter model name: ')
    model.save_weights('ANN/{}.h5'.format(model_name))
    # Save model architecture as json file
    json = model.to_json()
    with open('ANN/{}.json'.format(model_name), 'w') as f:
        f.write(json)

if __name__ == '__main__':
    # Load the training data
    data = np.load('training_data/data.npz')
    train_images = data['train_images']
    train_labels = data['train_labels']
    train_NVIDIA_model(train_images, train_labels)
    #train_ANN(train_images, train_labels)



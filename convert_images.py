import os
import numpy as np
import cv2
import re

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]"""
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """Sort the given list in the way that humans expect."""
    l.sort(key=alphanum_key)

def listdir(directory):
    """Removes '.DS_Store from list of folders/files"""
    return [f for f in os.listdir(directory) if f != '.DS_Store']

def convert_images():
    image_directory = 'training_images/'
    label_directory = 'training_labels/'
    # Initialize arrays that will hold training data
    train_images = np.zeros((240, 320))
    train_labels = np.zeros((1, 4))
    i = 1
    # Sort files in ascending order
    imdir = listdir(image_directory)
    sort_nicely(imdir)
    # Iterate through all the runs
    for folder_name in imdir:
        print(folder_name)
        label_array = np.load(label_directory+folder_name+'/labels.npy')
        # Create on big label array
        train_labels = np.vstack((train_labels, label_array[1:, :]))
        # Sort the filenames in ascending order
        filedir = listdir(image_directory+folder_name)
        sort_nicely(filedir)
        # Iterate through all files in a given run
        for file_name in filedir:
            image = cv2.imread(image_directory+folder_name+'/'+file_name, cv2.IMREAD_GRAYSCALE)
            # Convert image into numpy array
            image = image.astype(np.float32)
            # This stacks 2D images in the third dimension
            train_images = np.dstack((train_images, image))
        print(train_images.shape)
        print(train_labels.shape)
        print("Completed %d/%d folders" % (i, len(imdir)))
        i += 1
    # Remove the initial empty matrix
    train_images = train_images[:, :, 1:]
    train_labels = train_labels[1:, :]
    print(train_images.shape)
    print(train_labels.shape)
    np.savez('training_data/data.npz', train_images=train_images, train_labels=train_labels)

def add_more_images():
    """Load a preexisting image/label arrays and add new data"""
    image_directory = 'training_images/'
    label_directory = 'training_labels/'
    # Load arrays that hold training data
    data = np.load('training_data/data.npz')
    train_images = data['train_images']
    train_labels = data['train_labels']
    imdir = listdir(image_directory)
    # Sort files in order of runs
    sort_nicely(imdir)
    # Ask the user which run to start at
    start = int(input("Starting run: ")) - 1
    i = 1
    # Iterate through all the new runs
    for folder_name in imdir[start:]:
        print(folder_name)
        # Load label array and add to the existing train_labels array
        label_array = np.load(label_directory+folder_name+'/labels.npy')
        train_labels = np.vstack((train_labels, label_array))
        # Sort the filenames in ascending order
        filedir = listdir(image_directory+folder_name)
        sort_nicely(filedir)
        # Iterate through all files in a given run
        for file_name in filedir:
            image = cv2.imread(image_directory+folder_name+'/'+file_name, cv2.IMREAD_GRAYSCALE)
            # Convert image into numpy array
            image = image.astype(np.float32)
            # This stacks 2D images in the third dimension
            train_images = np.dstack((train_images, image))
        print(train_images.shape)
        print(train_labels.shape)
        print("Completed %d/%d folders" % (i, len(imdir[start:])))
        i += 1

convert_images()



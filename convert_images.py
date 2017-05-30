import os
import numpy as np
import cv2

def convert_images():
	image_directory = 'training_images/'
	label_directory = 'training_labels/'
	# Initialize arrays that will hold training data
	train_images = np.zeros((240, 320))
	train_labels = np.zeros((1, 4))
	i = 1
	# Iterate through all the runs
	for folder_name in os.listdir(image_directory):
		# There is a folder named .DS_Store, and it messes things up so skip over it
		if folder_name != '.DS_Store':
			print(folder_name)
			label_array = np.load(label_directory+folder_name+'/labels.npy')
			# Create on big label array
			train_labels = np.vstack((train_labels, label_array[1:, :]))
			# Iterate through all files in a given run
			for file_name in os.listdir(image_directory+folder_name):
				if file_name != '.DS_Store':
					image = cv2.imread(image_directory+folder_name+'/'+file_name, cv2.IMREAD_GRAYSCALE)
					# Convert image into numpy array
					image = image.astype(np.float32)
					# This stacks 2D images in the third dimension
					train_images = np.dstack((train_images, image))
			print("Completed %d/24 folders" % i)
			i += 1
	# Remove the initial empty matrix
	train_images = train_images[:, :, 1:]
	train_labels = train_labels[1:, :]
	print(train_images.shape)
	print(train_labels.shape)
	np.savez('training_data/data.npz', train_images=train_images, train_labels=train_labels)

convert_images()



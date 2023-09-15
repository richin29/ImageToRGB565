# Image To RGB565
Python script to convert JPG, JPEG, PNG ro GIF images to RGB565 header file to use with TFT displays.
The static images create a 1D array.
The GIF images create a 2D array.

# General Information
* Tested with python3.8
* Ensure the image name does not contain special characters other than underscore(_).
* The output header file is generated in the same folder as input and with same filename.

# HowTo
Execute the following command to convert the image to RGB565 array.
```
python ImageToRGB565.py <input file/folder>
```
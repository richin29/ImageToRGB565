# Image To RGB565
Python script to convert JPG, JPEG, PNG ro GIF images to RGB565 header file to use with TFT displays.
The static images create a 1D array.
The GIF images create a 2D array.

# General Information
* Tested with python3.8
* Ensure the image name does not contain special characters other than underscore(_).
* The output header file is generated in the same folder as input and with same filename.
* The script has the option to resize the images with -w for width in pixel and -t for height in pixel but its possible the image can be little distorted.

# HowTo
* Execute the following command to convert the image to RGB565 array.
```
python ImageToRGB565.py <input file/folder>
```

* Execute the following command to resize and convert the image to RGB565 array.
```
python ImageToRGB565.py <input file/folder> -w <width pixel> -t <height pixel>
```
import os
import argparse
from PIL import Image, ImageSequence

# Supported file formats
SUPPORTED_FILE_FORMATS = (".png", ".jpg", ".jpeg", ".gif")
OUTPUT_FILE_FORMAT = '.h'

def rgb_to_rgb565(red, green, blue):
    """
    Method to convert the RGB to RGB565.

    Parameters
    ----------
    red : int
        The red value of the pixel.
    green : int
        The green value of the pixel.
    blue : int
        The blue value of the pixel.

    Returns
    -------
    int
        16-bit data containing the RGB565 value.
    """
    # Ensure that the input values are in the range 0-255
    red = max(0, min(255, red))
    green = max(0, min(255, green))
    blue = max(0, min(255, blue))

    # Convert the RGB values to RGB565 format
    r5 = (red >> 3) & 0x1F  # 5 bits for red
    g6 = (green >> 2) & 0x3F  # 6 bits for green
    b5 = (blue >> 3) & 0x1F  # 5 bits for blue

    # Combine the bits to form the 16-bit RGB565 value
    rgb565 = (r5 << 11) | (g6 << 5) | b5

    return rgb565


def extract_frame_rgb565(img_frame):
    """
    Method to extract the RGB565 data array from an image frame.

    Parameters
    ----------
    img : 'PIL.Image.Image' object
        The image object returned by PIL open method.

    Returns
    -------
    list
        A list containing the RGB565 data of each pixel in the image.
    """
    rgb565_data = []

    # Get the dimensions of the image
    width, height = img_frame.size

    # Check if the image has an alpha channel (transparency)
    if img_frame.mode != "RGBA" and img_frame.mode != "RGB":
        img_frame = img_frame.convert("RGBA")
    elif img_frame.mode == "P":
        # Convert palette images to RGBA, as they may have transparency
        img_frame = img_frame.convert("RGBA")

    # Extract RGB565 values of each pixel
    rgb565_data = []
    for y in range(height):
        for x in range(width):
            # Get the RGBA values at the current pixel
            pixel = img_frame.getpixel((x, y))
            red, green, blue, alpha = pixel[0], pixel[1], pixel[2], pixel[3]

            # Convert RGB to RGB565
            rgb565 = rgb_to_rgb565(red, green, blue)

            # Store RGB565 value
            rgb565_data.append(rgb565)

    return rgb565_data

def process_image(input_path, output_path=None):
    # Check if the file is a supported image file
    if input_path.lower().endswith(SUPPORTED_FILE_FORMATS):
        # Extract the input filename without extension
        filename = os.path.splitext(os.path.basename(input_path))[0]
        # Open the image file
        img = Image.open(input_path)
        # Get the dimensions of the image
        width, height = img.size

        # Check if output path is not provided
        if output_path == None:
            # Output folder is the same as the input folder
            output_folder = os.path.dirname(os.path.abspath(input_path))
            # Create the output path
            output_path = os.path.join(output_folder, filename + OUTPUT_FILE_FORMAT)

        if input_path.lower().endswith('.gif'):
            frames_rgb565 = []
            frame_count = 0
            # Iterate through each frame and store its RGB565 data
            for frame in ImageSequence.Iterator(img):
                # Extract the RGB565 data of the extracted frame from the gif
                rgb565_data = extract_frame_rgb565(frame)
                # Add the RGB565 data of the frame into gif list
                frames_rgb565.append(rgb565_data)
                frame_count += 1
            # Create output header file
            with open(output_path, "w") as file:
                file.write("/**\n")
                file.write(f" * @file {filename}.h\n")
                file.write(" * @author Richin Abraham\n")
                file.write(f" * @arg Image frames: {frame_count} \n")
                file.write(f" * @arg Image Size: {width} * {height} pixels \n")
                file.write(f" * @arg Memory usage: {frame_count * width * height} bytes \n")
                file.write(" * @brief Generated file containing RGB565 array of an dynamic image.\n")
                file.write(" */\n\n")

                file.write(f"#ifndef {filename.upper()}_H\n")
                file.write(f"#define {filename.upper()}_H\n\n")

                file.write("// INCLUDES\n\n")
                file.write("#include <stdint.h>\n")
                file.write("#if defined(__AVR__)\n")
                file.write("#include <avr/pgmspace.h>\n")
                file.write("#elif defined(__PIC32MX__)\n")
                file.write("#define PROGMEM\n")
                file.write("#elif defined(__arm__)\n")
                file.write("#define PROGMEM\n")
                file.write("#endif\n\n")

                file.write("// DEFINES\n\n")
                # Define number of frames, image width and height
                file.write(f"/** @brief Number of frames. */\n")
                file.write(f"#define {filename.upper()}_NUM_FRAMES      {frame_count}\n")
                file.write(f"/** @brief Width of a single frame. */\n")
                file.write(f"#define {filename.upper()}_FRAME_WIDTH     {width}\n")
                file.write(f"/** @brief Height of a single frame. */\n")
                file.write(f"#define {filename.upper()}_FRAME_HEIGHT    {height}\n\n")

                file.write("// GLOBAL VARIABLES\n\n")
                file.write("/** @brief Array with image information. */\n")
                file.write(f"const uint16_t {filename.lower()}[{filename.upper()}_NUM_FRAMES][{width * height}] PROGMEM = {{\n")

                for frame_index, frame_rgb565 in enumerate(frames_rgb565):
                    file.write(f"    {{ // Frame {frame_index + 1}\n")
                    pixel_count = 0
                    for rgb565 in frame_rgb565:
                        if pixel_count % 16 == 0:
                            file.write("        ")
                        # Write the RGB565 value to the file
                        file.write(f"0x{rgb565:04X}, ")  # Format as a 4-digit hexadecimal number
                        pixel_count += 1

                        # Add a C++ comment at the end of every line with 16 elements
                        if pixel_count % 16 == 0:
                            file.write(f"// 0x{pixel_count:04X} ({pixel_count}) pixels\n")
                    # Close the 1D array
                    file.write("    }%s\n"%(',' if (frame_index + 1) < frame_count else ''))
                # Close the 2D array
                file.write("};\n\n")
                file.write(f"#endif // {filename.upper()}_H\n\n")
        else:
            # Extract the RGB565 data of the static image, i.e single frame
            rgb565_data = extract_frame_rgb565(img)

            # Create output header file
            with open(output_path, "w") as file:
                file.write("/**\n")
                file.write(f" * @file {filename}.h\n")
                file.write(" * @author Richin Abraham\n")
                file.write(f" * @arg Image Size: {width} * {height} pixels \n")
                file.write(f" * @arg Memory usage: {width * height} bytes \n")
                file.write(" * @brief Generated file containing RGB565 array of an image.\n")
                file.write(" */\n\n")

                file.write(f"#ifndef {filename.upper()}_H\n")
                file.write(f"#define {filename.upper()}_H\n\n")

                file.write("// INCLUDES\n\n")
                file.write("#include <stdint.h>\n")
                file.write("#if defined(__AVR__)\n")
                file.write("#include <avr/pgmspace.h>\n")
                file.write("#elif defined(__PIC32MX__)\n")
                file.write("#define PROGMEM\n")
                file.write("#elif defined(__arm__)\n")
                file.write("#define PROGMEM\n")
                file.write("#endif\n\n")

                file.write("// DEFINES\n\n")
                # Define image width and height
                file.write(f"/** @brief Width of the image. */\n")
                file.write(f"#define {filename.upper()}_IMAGE_WIDTH    {width}\n")
                file.write(f"/** @brief Height of the image. */\n")
                file.write(f"#define {filename.upper()}_IMAGE_HEIGHT   {height}\n\n")

                file.write("// GLOBAL VARIABLES\n\n")
                file.write("/** @brief Array with image information. */\n")
                file.write(f"const uint16_t {filename.lower()}[{width * height}] PROGMEM = {{\n")

                count = 0
                for rgb565 in rgb565_data:
                    if count % 16 == 0:
                        file.write("    ")
                    # Write the RGB565 value to the file
                    file.write(f"0x{rgb565:04X}, ")  # Format as a 4-digit hexadecimal number
                    count += 1

                    # Add a C++ comment at the end of every line with 16 elements
                    if count % 16 == 0:
                        file.write(f"// 0x{count:04X} ({count}) pixels\n")

                file.write("};\n\n")
                file.write(f"#endif // {filename.upper()}_H\n\n")

        print(f"Created header file: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert PNG image(s) to RGB565 format and create C header file(s).")
    parser.add_argument("input", help="Input PNG image file or folder path")
    parser.add_argument("-o", "--output", help="Output C header file (optional)")

    args = parser.parse_args()
    input_path = args.input
    output_path = args.output

    if os.path.isfile(input_path):
        process_image(input_path, output_path)
    elif os.path.isdir(input_path):
        # Process all PNG files in the folder
        for filename in os.listdir(input_path):
                file_path = os.path.join(input_path, filename)
                if output_path:
                    # If an output path is specified, use it for all files
                    process_image(file_path, output_path)
                else:
                    # Otherwise, create individual header files
                    process_image(file_path)
    else:
        print("Input path does not exist or is not valid.")

if __name__ == "__main__":
    main()

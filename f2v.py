import os
import math
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import io
import numpy as np
from moviepy.editor import ImageSequenceClip

def file_to_binary():
    # Create a Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the window

    # Get file path from user using file dialog
    file_path = filedialog.askopenfilename(title="Select a file")

    # Check if the file was selected
    if not file_path:
        print("No file selected!")
        return None

    # Get file size
    file_size = os.path.getsize(file_path)

    # Read file as binary and convert to string of 0's and 1's
    binary_string = ""
    try:
        with open(file_path, "rb") as f:
            for chunk in tqdm(iterable=iter(lambda: f.read(1024), b""), total=math.ceil(file_size/1024), unit="KB"):
                binary_string += "".join(f"{byte:08b}" for byte in chunk)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    return binary_string

def binary_to_video(bin_string, output_file='video.mp4', width=1920, height=1080, pixel_size=4, fps=24):
    # Calculate the total number of pixels needed to represent the binary string
    num_pixels = len(bin_string)

    # Calculate the number of pixels that can fit in one image
    pixels_per_image = (width // pixel_size) * (height // pixel_size)

    # Calculate the number of images needed to represent the binary string
    num_images = math.ceil(num_pixels / pixels_per_image)

    # Create an array to store the frames
    frames = []

    # Loop through each image
    for i in tqdm(range(num_images)):
        # Calculate the range of binary digits needed for this image
        start_index = i * pixels_per_image
        end_index = min(start_index + pixels_per_image, num_pixels)
        binary_digits = bin_string[start_index:end_index]

        # Create a new image object with the given size
        img = Image.new('RGB', (width, height), color='white')

        # Loop through each row of binary digits
        for row_index in range(height // pixel_size):
            # Get the binary digits for the current row
            start_index = row_index * (width // pixel_size)
            end_index = start_index + (width // pixel_size)
            row = binary_digits[start_index:end_index]

            # Loop through each column of binary digits
            for col_index, digit in enumerate(row):
                # Determine the color of the pixel based on the binary digit
                color = (0, 0, 0) if digit == '1' else (255, 255, 255)  # Black for 1, White for 0

                # Calculate the coordinates of the pixel
                x1 = col_index * pixel_size
                y1 = row_index * pixel_size
                x2 = x1 + pixel_size
                y2 = y1 + pixel_size

                # Draw the pixel on the image
                img.paste(color, (x1, y1, x2, y2))

        # Convert image to numpy array and add the frame to the list of frames
        with io.BytesIO() as f:
            img.save(f, format='PNG')
            frame = np.array(Image.open(f))
        frames.append(frame)

    # Create a video from the frames using MoviePy
    clip = ImageSequenceClip(frames, fps=fps)

    # Write the video to a file
    try:
        clip.write_videofile(output_file, fps=fps)
        print(f"Video saved as '{output_file}'")
    except Exception as e:
        print(f"Error saving video: {e}")

if __name__ == "__main__":
    binary_string = file_to_binary()
    if binary_string is not None:
        binary_to_video(binary_string)

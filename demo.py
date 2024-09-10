import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import io
import numpy as np
from tqdm import tqdm
from moviepy.editor import ImageSequenceClip, VideoFileClip

# Converts a file to binary string representation
def file_to_binary():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select a file")
    if not file_path:
        print("No file selected!")
        return None
    file_size = os.path.getsize(file_path)
    binary_string = ""
    try:
        with open(file_path, "rb") as f:
            for chunk in tqdm(iterable=iter(lambda: f.read(1024), b""), total=math.ceil(file_size / 1024), unit="KB"):
                binary_string += "".join(f"{byte:08b}" for byte in chunk)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    return binary_string

# Converts binary string back to a video
def binary_to_video(bin_string, output_file='video.mp4', width=1920, height=1080, pixel_size=4, fps=24):
    num_pixels = len(bin_string)
    pixels_per_image = (width // pixel_size) * (height // pixel_size)
    num_images = math.ceil(num_pixels / pixels_per_image)
    frames = []
    for i in tqdm(range(num_images)):
        start_index = i * pixels_per_image
        end_index = min(start_index + pixels_per_image, num_pixels)
        binary_digits = bin_string[start_index:end_index]
        img = Image.new('RGB', (width, height), color='white')
        for row_index in range(height // pixel_size):
            start = row_index * (width // pixel_size)
            end = start + (width // pixel_size)
            row = binary_digits[start:end]
            for col_index, digit in enumerate(row):
                color = (0, 0, 0) if digit == '1' else (255, 255, 255)
                x1, y1 = col_index * pixel_size, row_index * pixel_size
                x2, y2 = x1 + pixel_size, y1 + pixel_size
                img.paste(color, (x1, y1, x2, y2))
        with io.BytesIO() as f:
            img.save(f, format='PNG')
            frame = np.array(Image.open(f))
        frames.append(frame)
    clip = ImageSequenceClip(frames, fps=fps)
    try:
        clip.write_videofile(output_file, fps=fps)
        print(f"Video saved as '{output_file}'")
    except Exception as e:
        print(f"Error saving video: {e}")

# Convert video to binary
def video_to_binary(video_file, width=1920, height=1080, pixel_size=4):
    clip = VideoFileClip(video_file)
    binary_string = ""
    for frame in clip.iter_frames():
        img = Image.fromarray(frame)
        img = img.resize((width, height))
        binary_string += image_to_binary(img, width, height, pixel_size)
    clip.close()
    return binary_string

# Convert image to binary string
def image_to_binary(img, width, height, pixel_size):
    binary_string = ""
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            region = img.crop((x, y, x + pixel_size, y + pixel_size))
            color = np.array(region).mean(axis=(0, 1))
            binary_string += '1' if color[0] < 128 else '0'
    return binary_string

# Convert binary string back to original file
def binary_to_file(binary_string, output_file):
    num_pixels = len(binary_string)
    pixel_size = 4
    width = 1920
    height = 1080
    pixels_per_image = (width // pixel_size) * (height // pixel_size)
    binary_data = bytearray()
    for i in range(0, num_pixels, 8):
        byte = binary_string[i:i + 8]
        if len(byte) < 8:
            byte = byte.ljust(8, '0')
        binary_data.append(int(byte, 2))
    with open(output_file, 'wb') as f:
        f.write(binary_data)

# Restore original file from binary file
def bin_to_original_file(bin_file, output_file):
    try:
        with open(bin_file, 'rb') as f:
            binary_data = f.read()
        with open(output_file, 'wb') as f:
            f.write(binary_data)
        messagebox.showinfo("Success", "File reconstruction complete.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# File selection UI
def select_video_file():
    file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    if file_path:
        video_file_var.set(file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Save Reconstructed File As", defaultextension=".bin", filetypes=[("Binary Files", "*.bin")])
    if file_path:
        output_file_var.set(file_path)

def select_bin_file():
    file_path = filedialog.askopenfilename(title="Select Binary File", filetypes=[("Binary Files", "*.bin")])
    if file_path:
        bin_file_var.set(file_path)

def select_original_file():
    file_path = filedialog.asksaveasfilename(title="Save Original File As", defaultextension=".dat", filetypes=[("Data Files", "*.dat")])
    if file_path:
        original_file_var.set(file_path)

def process_files():
    video_file = video_file_var.get()
    output_file = output_file_var.get()
    if not video_file or not output_file:
        messagebox.showerror("Error", "Please select both video file and output file.")
        return
    try:
        binary_string = video_to_binary(video_file)
        binary_to_file(binary_string, output_file)
        messagebox.showinfo("Success", "Binary file created successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def process_bin_to_original():
    bin_file = bin_file_var.get()
    original_file = original_file_var.get()
    if not bin_file or not original_file:
        messagebox.showerror("Error", "Please select both binary file and original file destination.")
        return
    try:
        bin_to_original_file(bin_file, original_file)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Main UI window
root = tk.Tk()
root.title("File Conversion Tool")

# Widgets for video to binary
tk.Label(root, text="Video File:").grid(row=0, column=0, padx=10, pady=10)
video_file_var = tk.StringVar()
tk.Entry(root, textvariable=video_file_var, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_video_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Output Binary File:").grid(row=1, column=0, padx=10, pady=10)
output_file_var = tk.StringVar()
tk.Entry(root, textvariable=output_file_var, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_output_file).grid(row=1, column=2, padx=10, pady=10)

tk.Button(root, text="Convert Video to Binary", command=process_files).grid(row=2, column=1, padx=10, pady=20)

# Widgets for binary to original file
tk.Label(root, text="Binary File:").grid(row=3, column=0, padx=10, pady=10)
bin_file_var = tk.StringVar()
tk.Entry(root, textvariable=bin_file_var, width=50).grid(row=3, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_bin_file).grid(row=3, column=2, padx=10, pady=10)

tk.Label(root, text="Original File Destination:").grid(row=4, column=0, padx=10, pady=10)
original_file_var = tk.StringVar()
tk.Entry(root, textvariable=original_file_var, width=50).grid(row=4, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_original_file).grid(row=4, column=2, padx=10, pady=10)

tk.Button(root, text="Convert Binary to Original File", command=process_bin_to_original).grid(row=5, column=1, padx=10, pady=20)

root.mainloop()

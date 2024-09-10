import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip
import tkinter as tk
from tkinter import filedialog, messagebox
import io

def video_to_binary(video_file, width=1920, height=1080, pixel_size=4):
    clip = VideoFileClip(video_file)
    
    binary_string = ""
    
    for frame in clip.iter_frames():
        img = Image.fromarray(frame)
        img = img.resize((width, height))
        binary_string += image_to_binary(img, width, height, pixel_size)

    clip.close()
    return binary_string

def image_to_binary(img, width, height, pixel_size):
    binary_string = ""
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            region = img.crop((x, y, x + pixel_size, y + pixel_size))
            color = np.array(region).mean(axis=(0, 1))
            
            if color[0] < 128:
                binary_string += '1'
            else:
                binary_string += '0'
    
    return binary_string

def binary_to_file(binary_string, output_file):
    num_pixels = len(binary_string)
    pixel_size = 4
    width = 1920
    height = 1080
    pixels_per_image = (width // pixel_size) * (height // pixel_size)
    
    binary_data = bytearray()
    
    for i in range(0, num_pixels, 8):
        byte = binary_string[i:i+8]
        if len(byte) < 8:
            byte = byte.ljust(8, '0')
        binary_data.append(int(byte, 2))
    
    with open(output_file, 'wb') as f:
        f.write(binary_data)

def bin_to_original_file(bin_file, output_file):
    try:
        with open(bin_file, 'rb') as f:
            binary_data = f.read()
        
        with open(output_file, 'wb') as f:
            f.write(binary_data)
        
        messagebox.showinfo("Success", "File reconstruction complete.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

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

# Create the main Tkinter window
root = tk.Tk()
root.title("File Conversion Tool")

# Create and place widgets for video to binary
tk.Label(root, text="Video File:").grid(row=0, column=0, padx=10, pady=10)
video_file_var = tk.StringVar()
tk.Entry(root, textvariable=video_file_var, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_video_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Output Binary File:").grid(row=1, column=0, padx=10, pady=10)
output_file_var = tk.StringVar()
tk.Entry(root, textvariable=output_file_var, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_output_file).grid(row=1, column=2, padx=10, pady=10)

tk.Button(root, text="Convert Video to Binary", command=process_files).grid(row=2, column=1, padx=10, pady=20)

# Create and place widgets for binary to original file
tk.Label(root, text="Binary File:").grid(row=3, column=0, padx=10, pady=10)
bin_file_var = tk.StringVar()
tk.Entry(root, textvariable=bin_file_var, width=50).grid(row=3, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_bin_file).grid(row=3, column=2, padx=10, pady=10)

tk.Label(root, text="Original File Destination:").grid(row=4, column=0, padx=10, pady=10)
original_file_var = tk.StringVar()
tk.Entry(root, textvariable=original_file_var, width=50).grid(row=4, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_original_file).grid(row=4, column=2, padx=10, pady=10)

tk.Button(root, text="Convert Binary to Original File", command=process_bin_to_original).grid(row=5, column=1, padx=10, pady=20)

# Run the Tkinter event loop
root.mainloop()

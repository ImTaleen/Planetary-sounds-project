import numpy as np
import pandas as pd
import os
from scipy.integrate import solve_ivp
from scipy.io.wavfile import write
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pygame
import glob


df = pd.read_csv("planetary_frequencies_cleaned.csv")


sampling_rate = 44100  # Hz
duration = 3  # seconds
t = np.linspace(0, duration, int(sampling_rate * duration))

def wave_equation(t, y, omega):
    return [y[1], -omega**2 * y[0]]


output_dir = "planet_sounds"
os.makedirs(output_dir, exist_ok=True)


planet_sounds = {}


for i, row in df.iterrows():
    planet = row['Planet'].replace(" ", "_")
    freq = row['Frequency_Hz']

    if freq > 20000 or freq <= 0:
        print(f"Skipping {planet} (invalid frequency: {freq} Hz)")
        continue

    omega = 2 * np.pi * freq
    sol = solve_ivp(wave_equation, [0, duration], [0, 1], t_eval=t, args=(omega,))
    wave = sol.y[0]
    wave = wave / np.max(np.abs(wave))
    wave_int16 = np.int16(wave * 32767)


    if planet not in planet_sounds:
        planet_sounds[planet] = []

    sound_index = len(planet_sounds[planet]) + 1
    filename = os.path.join(output_dir, f"{planet}_{sound_index}.wav")
    write(filename, sampling_rate, wave_int16)
    planet_sounds[planet].append(filename)

    print(f"Saved sound: {filename}")


pygame.mixer.init()


image_folder = "planet_images"
planet_images = {}
for planet in planet_sounds.keys():
    img_path_png = os.path.join(image_folder, planet + ".png")
    img_path_jpg = os.path.join(image_folder, planet + ".jpg")
    if os.path.exists(img_path_png):
        planet_images[planet] = img_path_png
    elif os.path.exists(img_path_jpg):
        planet_images[planet] = img_path_jpg
    else:
        planet_images[planet] = None


root = tk.Tk()
root.title("Planet Sounds 🎵🪐")
root.geometry("1000x800")
root.configure(bg="black")

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def stop_sound():
    try:
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"Error stopping sound: {e}")

canvas = tk.Canvas(root, bg="black")
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

row = 0
col = 0
for planet, sound_list in planet_sounds.items():
    frame = ttk.Frame(scrollable_frame, padding=10)
    frame.grid(row=row, column=col, padx=20, pady=20)

    #
    if planet_images[planet]:
        img = Image.open(planet_images[Jupiter_Fuhr])
        img = img.resize((120, 120))
        img = ImageTk.PhotoImage(img)
        label_img = tk.Label(frame, image=img)
        label_img.image = img
        label_img.pack()
    else:
        label_img = tk.Label(frame, text="No Image", bg="gray", width=12, height=6)
        label_img.pack()

    label_name = tk.Label(frame, text=planet.replace("_", " "), font=("Arial", 12, "bold"), bg="black", fg="white")
    label_name.pack(pady=5)


    for idx, sound_path in enumerate(sound_list):
        btn_play = ttk.Button(frame, text=f"Play Sound {idx+1}", command=lambda path=sound_path: play_sound(path))
        btn_play.pack(pady=2)


    btn_stop = ttk.Button(frame, text="⏹️ Stop Sound", command=stop_sound)
    btn_stop.pack(pady=5)

    col += 1
    if col >= 3:
        col = 0
        row += 1

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

root.mainloop()

import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
import cv2

# TEST IMAGE
f = 'images/test.png'

img = cv2.imread('images/test.png') # reads image 'opencv-logo.png' as grayscale
# cv2.imshow("Test img", img)
# cv2.waitKey(0)

# 2======= try with pysimplegui
imgbytes = cv2.imencode('.png', img)[1].tobytes()
image_elem = sg.Image(data=imgbytes)
col = [[image_elem]]
col_buttons = [[sg.Button('Next', size=(4,2)),sg.Button('Prev', size=(4,2))]]
layout = [
    [sg.Column(col), sg.Column(col), sg.Column(col_buttons), ],
    [sg.Column(col), sg.Column(col)]
    ]
window = sg.Window('Image Browser', layout, return_keyboard_events=True,
                   location=(0, 0), use_default_focus=False)
window.read()

window.close()

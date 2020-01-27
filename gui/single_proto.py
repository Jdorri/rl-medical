import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
# sg.theme('DarkAmber')

# TEST IMAGE
f = 'images/test.png'
fnames = [os.path.join('images', p) for p in os.listdir('images')]

# ------------------------------------------------------------------------------
# use PIL to read data of one image
# ------------------------------------------------------------------------------

def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)
# ------------------------------------------------------------------------------

# Display first image
image_elem = sg.Image(data=get_img_data(f, first=True))
col = [[image_elem]]
# col_files = [[sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')],
#              [sg.Button('Next', size=(8, 2)), sg.Button('Prev', size=(8, 2))]]
col_buttons = [[sg.Button('Next', size=(8,2)),sg.Button('Prev', size=(8, 2))]]
layout = [[sg.Column(col_buttons), sg.Column(col)]]

window = sg.Window('Image Browser', layout, return_keyboard_events=True,
                   location=(0, 0), use_default_focus=False)
# user_input('asdicasdcin')
# loop reading the user input and displaying image, filename
i = 1
while True:
    # read the form
    event, values = window.read()
    print(event, values)
    # perform button and keyboard operations
    if event is None:
        break
    elif event is 'Next':
        f = fnames[i]
    elif event is 'Prev':
        if i >= 0:
            i -= 2
            f = fnames[i]

    # Update the window with new image
    image_elem.update(data=get_img_data(f, first=True))

    i += 1
window.close()

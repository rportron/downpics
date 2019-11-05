# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 12:03:43 2019

@author: rportron
"""

import tkinter
import tkinter.filedialog
import recup_img

def file_select():
    app.find_the_location = tkinter.filedialog.askdirectory()
    app.folder_bool = True
    app.destroy() #redraw windows

def go_downpics():
    app.url_str = app.url_entry.get()
    if app.folder_bool and app.url_str != '':
        url = app.url_str
        #print("DEBUG: this is the url: ", url)
        folder = app.find_the_location
        prefixe_nom_image = app.prefix_entry.get()
        #print("DEBUG: this is the : ", prefixe_nom_image)
        #app.status_message = 'Downloading "linked pics" from ' + app.url_str + ' to ' + app.find_the_location #ajout du 09/10/2019 : ne fonctionne toujours pas
        app.destroy()
        app.downloading()
        recup_img.image_downloader_linked(url, folder, prefixe_nom_image)
        app.status_message = 'Download completed'
        app.url_str = ''
        app.destroy()

class Recup_img_Frame(tkinter.Tk):
    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)
        self.parent = parent #keep reference of the parent
        self.url_str = ''
        self.folder_bool = False
        self.prefix_entry_text = ''
        self.status_message = ''
        self.initialize()

    def initialize(self):
        #logo
        self.canva = tkinter.Canvas(self, width = 666, height = 200, bg = 'pink')
        self.canva.create_text(333, 60, font=("Arial", 18), text=recup_img.FANCY_BANNER)
        self.canva.create_text(333, 150, text=self.status_message)
        self.canva.create_text(630, 190, text='version ' + recup_img.VERSION)
        #Text
        #destination
        var_destination_text = tkinter.StringVar()
        self.destination_text = tkinter.Label(self, textvariable=var_destination_text)
        if self.folder_bool:
            var_destination_text.set('Download "linked pics" to this location: ' + self.find_the_location)
        else:
            var_destination_text.set('Download "linked pics" to this location:')
        self.browse_button = tkinter.Button(self, text='Browse', command=file_select)

        #url
        var_url_text = tkinter.StringVar()
        self.url_entry = tkinter.Entry(self, bg='pink')
        var_url_text.set('from this url: ' + self.url_str)
        self.url_text = tkinter.Label(self, textvariable=var_url_text)

        #prefix
        self.prefix_text = tkinter.Label(self, text='with this optional pics name prefix:')
        self.prefix_entry = tkinter.Entry(self, bg='pink')
        self.empty_line_text = tkinter.Label(self, text='')
        #buttons
        self.button_go = tkinter.Button(self, text='Go!', command=go_downpics)
        self.button_quit = tkinter.Button(self, text='Quit', command=self.quit)
        #kepp all things together
        self.canva.grid(row = 1, columnspan = 2)

        self.destination_text.grid(row = 2, column = 0)
        self.browse_button.grid(row=2, column=1)

        self.url_text.grid(row = 3, column = 0, sticky = 'EW')
        self.url_entry.grid(row = 3, column = 1, sticky = 'EW')

        self.prefix_text.grid(row = 5, column = 0)
        self.prefix_entry.grid(row = 5, column = 1)
        self.empty_line_text.grid(row=6, columnspan=2)
        self.button_go.grid(row = 7, column = 0)
        self.button_quit.grid(row = 7, column = 1)

    def downloading(self):
        #logo
        self.canva = tkinter.Canvas(self, width = 333, height = 100, bg = 'red')
        self.canva.create_text(117, 60, text=recup_img.FANCY_BANNER)
        #Text
        downloading_text = 'Downloading "linked pics" from ' + self.url_str + ' to ' + self.find_the_location
        self.downloading_text = tkinter.Label(self, text=downloading_text)
        self.empty_line_text = tkinter.Label(self, text='')
        #buttons
        self.button_stop = tkinter.Button(self, text='Go!', command=self.quit)
        self.button_quit = tkinter.Button(self, text='Quit', command=self.quit)
        #kepp all things together
        self.canva.grid(row = 1, columnspan = 2)
        self.downloading_text.grid(row = 2, column = 0, sticky = 'EW')
        self.empty_line_text.grid(row=3, columnspan=2)
        self.button_stop.grid(row = 4, column = 0)
        self.button_quit.grid(row = 4, column = 1)

    def destroy(self):
        for c in self.winfo_children():
            c.destroy()
        self.initialize()

if __name__ == "__main__":
    app = Recup_img_Frame(None)
    app.title('DownPics')
    app.mainloop()
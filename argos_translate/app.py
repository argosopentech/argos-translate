#!/usr/bin/env python3

from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import *
import subprocess

class GUI:
    output_scrolledtext = None
    input_scrolledtext = None

    def switch_button_clicked():
        print('switch_button clicked')

    def translate_button_clicked():
        print('translate_button clicked')
        input_text = GUI.input_scrolledtext.get("1.0",END)
        print('input:')
        print(input_text)
        result = subprocess.check_output('echo "' + input_text + '" | apertium en-es', shell=True)
        print(result)
        print('-----------------------------------------------------------')
        GUI.output_scrolledtext.delete(1.0,END)
        GUI.output_scrolledtext.insert(INSERT,result)

    def main_loop():
        ## Gui ##
        window = Tk()
        window.title("Argos Translate")

        GUI.output_scrolledtext = scrolledtext.ScrolledText(window,width=40,height=10)

        output_combo = Combobox(window)
        output_combo['values']= ('English')
        output_combo.current(0) 
        output_combo.grid(column=0, row=1)

        input_combo = Combobox(window)
        input_combo['values']= ('Spanish')
        input_combo.current(0) 
        input_combo.grid(column=2, row=1)

        GUI.input_scrolledtext = scrolledtext.ScrolledText(window,width=40,height=10)

        GUI.input_scrolledtext.grid(column=0, row=2)
        GUI.input_scrolledtext.insert(INSERT, 'Text to translate from')

        switch_button = Button(window, text='⟷', command=GUI.switch_button_clicked)
        switch_button.grid(column=1, row=2)

        GUI.output_scrolledtext.grid(column=2, row=2)
        GUI.output_scrolledtext.insert(INSERT, 'Text to translate to')

        translate_button = Button(window, text='Translate', command=GUI.translate_button_clicked)
        translate_button.grid(column=1, row=3)

        window.mainloop()

def main():
    GUI.main_loop()

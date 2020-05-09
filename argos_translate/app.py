#!/usr/bin/env python3

from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import *
import os

from argos_translate import translate

class GUI:
    def __init__(self):
        self.output_scrolledtext = None
        self.input_scrolledtext = None
        
        window = Tk()
        window.title("Argos Translate")

        language_names = tuple([language.name for language in translate.languages])

        self.input_combo = Combobox(window)
        self.input_combo['values'] = language_names
        self.input_combo.current(0) 
        self.input_combo.grid(column=0, row=1)

        self.output_combo = Combobox(window)
        self.output_combo['values'] = language_names
        self.output_combo.current(1) 
        self.output_combo.grid(column=1, row=1)

        self.input_scrolledtext = scrolledtext.ScrolledText(window,width=80,height=50)
        self.input_scrolledtext.grid(column=0, row=2)
        self.input_scrolledtext.insert(INSERT, 'Text to translate from')

        self.output_scrolledtext = scrolledtext.ScrolledText(window,width=80,height=50)
        self.output_scrolledtext.grid(column=1, row=2)
        self.output_scrolledtext.insert(INSERT, 'Text to translate to')

        translate_button = Button(window, text='→', command=self.translate_button_clicked)
        translate_button.grid(column=0, row=3)

        window.mainloop()

    def translate_button_clicked(self):
        input_text = self.input_scrolledtext.get("1.0",END)
        input_combo_value = self.input_combo.current()
        input_language = translate.languages[input_combo_value]
        output_combo_value = self.output_combo.current()
        output_language = translate.languages[output_combo_value]
        translation = input_language.get_translation(output_language)
        result = translation.translate_function(input_text)
        self.output_scrolledtext.delete(1.0,END)
        self.output_scrolledtext.insert(INSERT,result)

def main():
    gui = GUI()

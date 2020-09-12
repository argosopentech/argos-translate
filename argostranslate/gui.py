#!/usr/bin/env python3

from tkinter import *
from tkinter import scrolledtext, filedialog, messagebox
from tkinter.ttk import *

from argostranslate import translate, package, settings

class GUIWindow:
    def __init__(self):
        self.output_scrolledtext = None
        self.input_scrolledtext = None
        
        self.window = Tk()
        self.window.title("Argos Translate")

        # Manage window resizing
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=0)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=0)

        # Menu Bar
        self.menubar = Menu(self.window)
        self.window.config(menu=self.menubar)
        self.menubar.add_command(label='Install model', command=self.open_model_filedialog)

        # Left combo
        self.left_combo = Combobox(self.window)
        self.left_combo.grid(column=0, row=0, sticky=N)

        # Right combo
        self.right_combo = Combobox(self.window)
        self.right_combo.grid(column=1, row=0, sticky=N)

        # Left Scrolled Text
        self.left_scrolledtext = scrolledtext.ScrolledText(self.window,width=80,height=50)
        self.left_scrolledtext.grid(column=0, row=1, sticky='NSEW')
        self.left_scrolledtext.insert(INSERT, 'Text to translate from')

        # Right Scrolled Text
        self.right_scrolledtext = scrolledtext.ScrolledText(self.window,width=80,height=50)
        self.right_scrolledtext.grid(column=1, row=1, sticky='NSEW')
        self.right_scrolledtext.insert(INSERT, 'Text to translate to')

        # Translate buttons
        translate_button = Button(self.window, text='→',
                command=self.translate)
        translate_button.grid(column=0, row=2)
        translate_button_back = Button(self.window, text='←',
                command=self.translate_backward)
        translate_button_back.grid(column=1, row=2)

        # Enable Ctrl-a and Ctrl-v (Tkinter is goofy)
        def handle_select_all_event(event):
            event.widget.tag_add(SEL, "1.0", END) 
            event.widget.mark_set(INSERT, "1.0")
            return "break"
        def handle_paste_event(event):
            try:
                event.widget.delete('sel.first', 'sel.last')
            except:
                pass
            event.widget.insert(INSERT, event.widget.clipboard_get())
            return 'break'
        self.left_scrolledtext.bind("<Control-Key-a>", handle_select_all_event)
        self.right_scrolledtext.bind("<Control-Key-a>", handle_select_all_event)
        self.left_scrolledtext.bind('<Control-Key-v>', handle_paste_event)
        self.right_scrolledtext.bind('<Control-Key-v>', handle_paste_event)

        # Enable <Enter> to translate
        def handle_enter_clicked(event):
            self.translate()
        def handle_enter_clicked_back(event):
            self.translate_backward()
        self.left_scrolledtext.bind('<Return>', handle_enter_clicked)
        self.right_scrolledtext.bind('<Return>', handle_enter_clicked_back)

        # Final setup for window
        self.load_languages()
        self.translate()
        self.window.mainloop()

    def load_languages(self):
        self.languages = translate.load_installed_languages()
        language_names = tuple([language.name for language in self.languages])
        self.left_combo['values'] = language_names
        if len(language_names) > 0: self.left_combo.current(0) 
        self.right_combo['values'] = language_names
        if len(language_names) > 0: self.right_combo.current(1) 

    def translate(self, translate_backwards=False):
        if len(self.languages) < 1: return
        if not translate_backwards:
            from_scrolledtext = self.left_scrolledtext
            to_scrolledtext = self.right_scrolledtext
            from_combo = self.left_combo
            to_combo = self.right_combo
        else:
            from_scrolledtext = self.right_scrolledtext
            to_scrolledtext = self.left_scrolledtext
            from_combo = self.right_combo
            to_combo = self.left_combo
        input_text = from_scrolledtext.get("1.0", END)
        input_combo_value = from_combo.current()
        input_language = self.languages[input_combo_value]
        output_combo_value = to_combo.current()
        output_language = self.languages[output_combo_value]
        translation = input_language.get_translation(output_language)
        if translation:
            result = translation.translate(input_text)
            to_scrolledtext.delete("1.0", END)
            to_scrolledtext.insert("1.0", result)
        else:
            messagebox.showerror('Error', 'No translation between these languages installed')

    def translate_backward(self):
        self.translate(True)

    def open_model_filedialog(self):
        filepaths = filedialog.askopenfilenames(
                filetypes=[('Argos Models', '.argosmodel')])
        for file_path in filepaths:
            package.install_from_path(file_path)
        self.load_languages()

def main():
    gui = GUIWindow()

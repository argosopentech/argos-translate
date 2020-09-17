#!/usr/bin/env python3

from pathlib import Path
import os

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

        # Add icon
        image_path = Path(os.path.dirname(__file__)) / 'img' / 'icon.png'
        icon_photo = PhotoImage(file=image_path)
        self.window.iconphoto(False, icon_photo)

        # Manage window resizing
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=0)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=0)

        # Menu Bar
        self.menubar = Menu(self.window)
        self.window.config(menu=self.menubar)
        self.menubar.add_command(label='About', command=self.open_about)
        self.menubar.add_command(label='Manage Packages', command=self.open_package_manager)

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
        self.translate(showError=False)
        self.window.mainloop()

    def load_languages(self):
        self.languages = translate.load_installed_languages()
        language_names = tuple([language.name for language in self.languages])
        self.left_combo['values'] = language_names
        if len(language_names) > 0: self.left_combo.current(0) 
        self.right_combo['values'] = language_names
        if len(language_names) > 0: self.right_combo.current(1) 

    def translate(self, translate_backwards=False, showError=True):
        """Try to translate based on languages selected.

        Args:
            translate_backwards (bool): If True translate from the right 
                ScrolledText to the left one.
            showError (bool): If True show an error messagebox if the
                currently selected translation isn't installed
        """
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
            if showError:
                messagebox.showerror('Error', 'No translation between these languages installed')

    def translate_backward(self):
        self.translate(True)

    TABLE_CELL_PADDING = 10

    def make_table_cell(parent, row, column, text, isUnderlined=False):
        if isUnderlined:
            table_cell = Label(parent, text=text, font=('Arial', 12, 'bold', 'underline'))
        else:
            table_cell = Label(parent, text=text)
        table_cell.grid(row=row, column=column,
                padx=GUIWindow.TABLE_CELL_PADDING,
                pady=GUIWindow.TABLE_CELL_PADDING)

    def reload_package_manager_window(self):
        self.clear_package_manager_window()
        self.populate_package_manager_window()
        self.package_manager_window.lift()

    def uninstall_package(self, pkg):
        package.uninstall(pkg)
        self.reload_package_manager_window()

    def install_packages(self):
        self.open_model_filedialog()
        self.reload_package_manager_window()

    def clear_package_manager_window(self):
        window = self.package_manager_window
        for widget in window.winfo_children():
            widget.destroy()

    def open_package_readme(self, pkg):
        readme_window = Tk()
        readme_window.title(str(pkg))
        text = Label(readme_window, text=pkg.get_readme(),
                wraplength=750)
        text.pack(padx=15, pady=15)

    def populate_package_manager_window(self):
        window = self.package_manager_window
        packages = package.get_installed_packages()
        row = 0
        install_pkg_button = Button(window, text='Install Package', 
                command=self.install_packages)
        install_pkg_button.grid(row=row, column=0, padx=5, pady=5)
        row += 1
        GUIWindow.make_table_cell(window, row, 1, 'package_version', True)
        GUIWindow.make_table_cell(window, row, 2, 'argos_version', True)
        GUIWindow.make_table_cell(window, row, 3, 'from_code', True)
        GUIWindow.make_table_cell(window, row, 4, 'from_name', True)
        GUIWindow.make_table_cell(window, row, 5, 'to_code', True)
        GUIWindow.make_table_cell(window, row, 6, 'to_name', True)
        GUIWindow.make_table_cell(window, row, 7, 'Delete', True)
        row += 1
        row_offset = row
        for pkg in packages:
            view_readme_button = Button(window, text='README', command=(
                lambda pkg=pkg: self.open_package_readme(pkg)))
            view_readme_button.grid(row=row, column=0,
                    padx=GUIWindow.TABLE_CELL_PADDING,
                    pady=GUIWindow.TABLE_CELL_PADDING)
            GUIWindow.make_table_cell(window, row, 1, pkg.package_version)
            GUIWindow.make_table_cell(window, row, 2, pkg.argos_version)
            GUIWindow.make_table_cell(window, row, 3, pkg.from_code)
            GUIWindow.make_table_cell(window, row, 4, pkg.from_name)
            GUIWindow.make_table_cell(window, row, 5, pkg.to_code)
            GUIWindow.make_table_cell(window, row, 6, pkg.to_name)
            delete_button = Button(window, text='x', command=(
                lambda pkg=pkg: self.uninstall_package(pkg)))
            delete_button.grid(row=row, column=7,
                    padx=GUIWindow.TABLE_CELL_PADDING,
                    pady=GUIWindow.TABLE_CELL_PADDING)
            row += 1

    def open_package_manager(self):
        self.package_manager_window = Tk()
        self.package_manager_window.title("Package Manager")
        self.populate_package_manager_window()

    def open_model_filedialog(self):
        filepaths = filedialog.askopenfilenames(
                filetypes=[('Argos Models', '.argosmodel')])
        for file_path in filepaths:
            package.install_from_path(file_path)
        self.load_languages()

    def open_about(self):
        readme_window = Tk()
        readme_window.title('About')
        text = Label(readme_window, text=settings.about_text,
                wraplength=750)
        text.pack(padx=15, pady=15)

def main():
    try:
        gui = GUIWindow()
    except Exception as e:
        messagebox.showerror("Error", str(e))

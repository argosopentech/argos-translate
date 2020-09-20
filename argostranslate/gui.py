#!/usr/bin/env python3

from pathlib import Path
import os
import threading
import functools
from tkinter import *
from tkinter import scrolledtext, filedialog, messagebox
from tkinter.ttk import *

from argostranslate import translate, package, settings

# Based on Stack Overflow answer
# https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
class EventText(Text):
    """Tkinter Text widget that has a <<TextModified>> event"""
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.original = self._w + '_original'
        self.tk.call('rename', self._w, self.original)
        self.tk.createcommand(self._w, self.proxy)

    def proxy(self, command, *args):
        cmd = (self.original, command) + args
        result = self.tk.call(cmd)

        if command in ['insert', 'delete', 'replace']:
            self.event_generate('<<TextModified>>')

        return result

class GUIWindow:

    # Time delay between refreshes of self.right_text
    REFRESH_TIME = 100

    # Above this number of characters in the input text will show a 
    # message in the output text while the translation
    # is happening
    SHOW_LOADING_THRESHOLD = 300

    def __init__(self):
        # Threading variables
        # self.right_text is the text that
        # the right text field should be set to by
        # the main thread. None if it should be left as is.
        # self.work_to_do is a bound function for the worker
        # thread to run.
        # *** These variables are shared between threads ***
        # and self.lock needs to be used to access them.
        self.lock = threading.Lock()
        with self.lock:
            self.right_text = 'Text to translate to'
            self.work_to_do = None

        # self.work_semaphore represents if there is work to be done.
        # The worker thread blocks on self.work_semaphore when
        # there is no work and to add work the main thread sets
        # self.work_to_do to a bound function for the worker thread
        # to execute and increments self.work_semaphore. 
        # The worker thread should set self.work_to_do
        # to None after copying it so that the main thread can 
        # overwrite self.work_to_do without incrementing work_semaphore
        # if there is existing work. Since you always want the most
        # recent translation the main thread will want to overwrite
        # work that hasn't been done yet.
        self.work_semaphore = threading.Semaphore(value=0)

        self.output_scrolledtext = None
        self.input_scrolledtext = None
        
        self.window = Tk()
        self.window.title('Argos Translate')

        # Add icon
        image_path = Path(os.path.dirname(__file__)) / 'img' / 'icon.png'
        icon_photo = PhotoImage(file=image_path)
        self.window.iconphoto(False, icon_photo)

        # Menu Bar
        self.menubar = Menu(self.window)
        self.window.config(menu=self.menubar)
        self.menubar.add_command(label='Manage Packages', command=self.open_package_manager)
        self.menubar.add_command(label='About', command=self.open_about)

        # Row frames
        self.language_bar_frame = Frame(self.window)
        self.language_bar_frame.pack(fill=X)
        self.text_frame = Frame(self.window)
        self.text_frame.pack(fill=BOTH, expand=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.columnconfigure(1, weight=1)
        self.text_frame.rowconfigure(0, weight=1)

        # Left combo
        self.left_language_bar_frame = Frame(self.language_bar_frame)
        self.left_language_bar_frame.pack(fill=X, side=LEFT, expand=1)
        self.left_combo = Combobox(self.left_language_bar_frame)
        self.left_combo.pack()

        # Languages swap button
        self.center_language_bar_frame = Frame(self.language_bar_frame)
        self.center_language_bar_frame.pack(fill=X, side=LEFT)
        self.language_swap_button = Button(self.center_language_bar_frame,
                text='↔', width=2, command=self.swap_languages)
        self.language_swap_button.pack()

        # Right combo
        self.right_language_bar_frame = Frame(self.language_bar_frame)
        self.right_language_bar_frame.pack(fill=X, side=LEFT, expand=1)
        self.right_combo = Combobox(self.right_language_bar_frame)
        self.right_combo.pack()

        # Left Scrolled Text
        self.left_scrolledtext = EventText(self.text_frame, width=80,height=50)
        self.left_scrolledtext.grid(row=0, column=0, sticky='NSEW')
        self.left_scrolledtext.insert(INSERT, 'Text to translate from')

        # Right Scrolled Text
        self.right_scrolledtext = Text(self.text_frame, width=80,height=50)
        self.right_scrolledtext.grid(row=0, column=1, sticky='NSEW')

        # Enable Ctrl-a and Ctrl-v (Tkinter is goofy)
        def handle_select_all_event(event):
            event.widget.tag_add(SEL, '1.0', END) 
            event.widget.mark_set(INSERT, '1.0')
            return 'break'
        self.left_scrolledtext.bind('<Control-Key-a>', handle_select_all_event)
        self.right_scrolledtext.bind('<Control-Key-a>', handle_select_all_event)

        # Final setup for window
        self.load_languages()
        self.translate(showError=False)

        # Translate automatically on left text edited
        self.left_scrolledtext.bind('<<TextModified>>', lambda x: self.translate())

        # Run text update loop
        self.window.after(self.REFRESH_TIME, self.refresh_data)

        # Setup a protocol handler on window close to join with worker_thread
        self.continue_worker_thread = True # Only written to by main thread
        self.window.protocol('WM_DELETE_WINDOW', self.main_window_close_event)

        # Run worker thread
        self.worker_thread = threading.Thread(
                target=self.worker_thread_function)
        self.worker_thread.start()

        self.window.mainloop()

    def refresh_data(self):
        with self.lock:
            if self.right_text != None:
                self.right_scrolledtext.delete('1.0', END)
                self.right_scrolledtext.insert('1.0', self.right_text)
                self.right_text = None
        self.window.after(self.REFRESH_TIME, self.refresh_data)

    def worker_thread_function(self):
        while self.continue_worker_thread:
            self.work_semaphore.acquire()
            with self.lock:
                work_to_do = self.work_to_do
                self.work_to_do = None
            work_to_do()

    def main_window_close_event(self):
        with self.lock:
            if self.work_to_do == None:
                self.work_semaphore.release()
            self.work_to_do = lambda: None
            self.continue_worker_thread = False
        self.worker_thread.join()
        self.window.destroy()

    def swap_languages(self):
        old_left_value = self.left_combo.current()
        self.left_combo.current(self.right_combo.current())
        self.right_combo.current(old_left_value)

    def load_languages(self):
        self.languages = translate.load_installed_languages()
        language_names = tuple([language.name for language in self.languages])
        self.left_combo['values'] = language_names
        if len(language_names) > 0: self.left_combo.current(0) 
        self.right_combo['values'] = language_names
        if len(language_names) > 1: self.right_combo.current(1) 

    def translation_work(self, translation, show_loading_message):
        if show_loading_message:
            with self.lock:
                self.right_text = 'Translating...'
        result = translation()
        with self.lock:
            self.right_text = result

    def translate(self, showError=True):
        """Try to translate based on languages selected.

        Args:
            showError (bool): If True show an error messagebox if the
                currently selected translation isn't installed
        """
        if len(self.languages) < 1: return
        from_scrolledtext = self.left_scrolledtext
        from_combo = self.left_combo
        to_combo = self.right_combo
        input_text = from_scrolledtext.get("1.0", END)
        input_combo_value = from_combo.current()
        input_language = self.languages[input_combo_value]
        output_combo_value = to_combo.current()
        output_language = self.languages[output_combo_value]
        translation = input_language.get_translation(output_language)
        if translation:
            bound_translation_function = functools.partial(translation.translate,
                    input_text)
            show_loading_message = len(input_text) > self.SHOW_LOADING_THRESHOLD
            translation_work = functools.partial(self.translation_work,
                    bound_translation_function, show_loading_message)
            with self.lock:
                if self.work_to_do == None:
                    self.work_semaphore.release()
                self.work_to_do = translation_work

        else:
            if showError:
                messagebox.showerror('Error', 'No translation between these languages installed')

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
        self.package_manager_window.title('Package Manager')
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
        messagebox.showerror('Error', str(e))

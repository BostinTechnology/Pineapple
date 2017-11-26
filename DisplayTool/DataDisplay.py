#!/usr/bin/env python3
"""
    This program preovides a user interface that allows the CognIot data to be
    displayed using the api

    
"""



from tkinter import *
from tkinter.ttk import *
import logging
import logging.config
import dict_Logging

import os
import sys
import os.path

import SystemSettings as SS

class DataDisplay(Frame):
    def __init__(self, master=None):
        Frame.__init__(self,master)

        gbl_log.info("Starting Main Frame")
        # These are the tuples of what is selected in the listbox
        self.current_device = StringVar()
        self.current_sensor = StringVar()
        self.user = StringVar()
        self.password = StringVar()
        self.sensor_info_text = StringVar()
        self.data_window_text = StringVar()
        self.refresh_rate = IntVar()


        #These are the check boxes
        self.label_text = StringVar()
        self.label_text.set("Enter Book info")

        # Build the Selection row
        selection_frame = Frame(self, relief='ridge')
        self.device = Combobox(selection_frame, height=10, textvariable=self.current_device, width=20)
#        self.user.bind("<<ComboboxSelected>>", self.reset_find)
        self.device.grid(row=0, column=0)#, padx=30)
        self.sensor = Combobox(selection_frame, height=10, textvariable=self.current_sensor, width=10)
#        self.press.bind("<<ComboboxSelected>>", self.reset_find)
        self.sensor.grid(row=0, column=1)#, padx=10)
        self.sensor_info = Label(selection_frame, relief='sunken', text="Log In", textvariable=self.sensor_info_text, width=30, wraplength=50)
        self.sensor_info.grid(row=0, column=2)
        self.login_button = Button(selection_frame, text='Login', command=self.login).grid(row=0, column=3)#, padx=20)
        selection_frame.grid(row=0, column=0, columnspan=2, pady=10)

        # Build the data display frame and the selection part
        data_frame = Frame(self, relief='ridge')
        self.data_info = Label(data_frame, relief='sunken', text="Data Info", textvariable=self.data_window_text, width=30, wraplength=200)
        self.data_info.grid(row=0, column=0)
        data_frame.grid(row=1, column=0, pady=10)
        
        # Build the book canvas picture
        graph_frame = Frame(self, relief='ridge')
        graph_canvas = Canvas(graph_frame, width=450, height=300, background='#ffffff')
        graph_canvas.create_polygon(140,60,290,75,280,240,130,225, outline="blue", fill="")
        graph_canvas.create_line(140,60,130,45,120,210,130,225, fill="blue")          # spine line
        graph_canvas.create_line(128,78,138,93, fill="lightblue")          # across spine line upper
        graph_canvas.create_line(126,111,136,126, fill="green")          # across spine line upper middle
        graph_canvas.create_line(124,144,134,159, fill="brown")          # across spine linelower middle
        graph_canvas.create_line(122,177,132,192, fill="lightgreen")          # across spine line lower
        graph_canvas.create_line(130,45,280,60,290,75, fill="blue")                   # top line
        graph_canvas.create_arc(220,185,360,275,outline="red",style="arc")

        graph_canvas.pack()

        graph_frame.grid(row=1, column=1)

        close_frame = Frame(self,relief='ridge')
        self.refresh = Combobox(close_frame, height=10, textvariable=self.refresh_rate, width=20)
        self.refresh.grid(row=2, column=0)#, padx=30)
        exit_program = Button(close_frame, text="Exit", command=self.exit_program).grid(row=2, column=3, padx=40)
        close_frame.grid(row=2, column=0, columnspan=2)

        # Put it all together on the screen
        self.pack(fill=BOTH, expand=NO)
                    

    def check_data_entered(self):
        """
        Check the necessary fields have been entered
        """
        if len(self.user.get()) < 1:
            self.UpdateBookText("Please Select a User")
            return False
            
        if len(self.day.get()) < 1 or len(self.month.get()) < 1 or len(self.year.get()) < 1:
            self.UpdateBookText("Please Select a Date")
            return False
            
        if len(self.press.get()) < 1 or len(self.shelf.get()) < 1 or len(self.position.get()) < 1:
            self.UpdateBookText("Please select a press, shelf and row first")
            return False

        return True

    def login(self):
        # called from teh login button
        return
        
    def exit_program(self):
        # called form the capture button
        logging.debug("Exiting Program")
        exit()
        return
        
def SetupLogging():
    """
    Setup the logging defaults
    Using the logger function to span multiple files.
    """
    global gbl_log
    # Create a logger with the name of the function
    logging.config.dictConfig(dict_Logging.log_cfg)
    gbl_log = logging.getLogger()

    gbl_log.info("\n\n")
    gbl_log.info("[CTRL] Logging Started, current level is %s" % gbl_log.getEffectiveLevel())

    return

        
def main():

    SetupLogging()

    root = Tk()
    text_font = ('TkDefault', '20')
    root.option_add('*TCombobox*Listbox.font', text_font)
    #root.option_add('*TCombobox*Height', 20)
    app = DataDisplay(master=root)
    root.geometry("800x410")
    app.master.title("Data Display Tool")
    app.mainloop()
    return

if __name__ == '__main__':
	main()


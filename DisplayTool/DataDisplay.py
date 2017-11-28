#!/usr/bin/env python3
"""
    This program preovides a user interface that allows the CognIot data to be
    displayed using the api

    
"""



from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import logging
import logging.config
import dict_Logging

import os
import sys
import os.path
import requests

import SystemSettings as SS

class Login(Toplevel):
    """"""
 
    def __init__(self, original):
        """Constructor"""
        self.original_frame = original
        self.user = StringVar()
        self.password = StringVar()
        self.db = StringVar()
        self.login_status = False

        Toplevel.__init__(self)
        self.geometry("350x200")
        self.title("Login")
        self.frame = Frame(self, relief='ridge')
        Label(self.frame, text="     Username:").grid(row=0,column=0, padx=20, sticky=W)
        user = Entry(self.frame, textvariable=self.user).grid(row=0,column=1, padx=10, pady=10, sticky=E)
        Label(self.frame, text="     Password:").grid(row=1,column=0, padx=20, sticky=W)
        password = Entry(self.frame, textvariable=self.password, show='*').grid(row=1,column=1, padx=10, pady=10, sticky=E)
        Radiobutton(self.frame, text="File", value="FILE", variable=self.db).grid(row=2,column=0, sticky=W, padx=10)
        Radiobutton(self.frame, text="DBLocal", value="DBLocal", variable=self.db).grid(row=2,column=1, sticky=W, padx=10)
        Radiobutton(self.frame, text="DBRemote", value="DBRemote", variable=self.db).grid(row=3,column=0, sticky=W, padx=10)
        Radiobutton(self.frame, text="AWS", value="AWS", variable=self.db).grid(row=3,column=1, sticky=W, padx=10)
        self.db.set("DBLocal")
        btn = Button(self.frame, text="Login", command=self.onLogin).grid(row=4,column=0, pady=10, columnspan=2)

        self.frame.pack(fill=BOTH, expand=NO)#, anchor="center")
 
    def onLogin(self):
        """"""
        # Validate the input
        if self.check_credentials():
            self.destroy()
            self.original_frame.show(True, self.user.get(), self.password.get())
        else:
            messagebox.showinfo("Unsuccessful", "Username / password not authenticated" )
        return

    def check_credentials(self):
        """"""
        print("Checking Credentials")
        fulldata = {'id':self.user.get(), 'auth':self.password.get(), 'dest':self.db.get()}
        #print("Payload Being Sent:\n%s" % fulldata)
        try:
            r = requests.get('http://RPi_3B:8080/authenticateuser', data=fulldata)
            #print("response:%s" % r)
            if r.status_code ==200:
                self.status = True
            else:
                self.status = False
        except:
            self.status = False
        return self.status

class DataDisplay(Frame):
    def __init__(self, master=None):
        Frame.__init__(self,master)
        self.master = master

        gbl_log.info("Starting Main Frame")
        # These are the tuples of what is selected in the listbox
        self.current_device = StringVar()
        self.current_sensor = StringVar()
        self.user = StringVar()
        self.password = StringVar()
        self.sensor_info_text = StringVar()
        self.data_window_text = StringVar()
        self.refresh_rate = IntVar()

        # Build the Selection row
        selection_frame = Frame(self, relief='ridge')
        self.device = Combobox(selection_frame, height=10, textvariable=self.current_device, width=20)
#        self.user.bind("<<ComboboxSelected>>", self.reset_find)
        self.device.grid(row=0, column=0, padx=30)
        self.sensor = Combobox(selection_frame, height=10, textvariable=self.current_sensor, width=10)
#        self.press.bind("<<ComboboxSelected>>", self.reset_find)
        self.sensor.grid(row=0, column=1, padx=10)
        self.sensor_info = Label(selection_frame, relief='sunken', text="Log In", textvariable=self.sensor_info_text, width=30, wraplength=50)
        self.sensor_info.grid(row=0, column=2)
        self.login_button = Button(selection_frame, text='Login', command=self.login).grid(row=0, column=3, padx=20)
        selection_frame.grid(row=0, column=0, columnspan=2, pady=10)

        # Build the data display frame and the selection part
        data_frame = Frame(self, relief='ridge',width=20,height=20)
        self.data_info = Label(data_frame, relief='sunken', text="Data Info", textvariable=self.data_window_text, width=30, wraplength=200)
        self.data_info.grid(row=0, column=0)
        data_frame.grid(row=1, column=0, pady=10)
        
        # Build the book canvas picture
        graph_frame = Frame(self, relief='ridge')
        graph_canvas = Canvas(graph_frame, width=450, height=300, background='#ffffff')
        graph_canvas.create_polygon(20,20,430,20,430,280,20,280, outline="green", fill="")
        for r in range(40,280,20):
            graph_canvas.create_line(20,r,430,r, fill="lightblue")
        for c in range(40,430,20):
            graph_canvas.create_line(c,20,c,280, fill="lightblue")
        
        graph_canvas.pack()

        graph_frame.grid(row=1, column=1)

        close_frame = Frame(self,relief='ridge')
        self.refresh = Combobox(close_frame, height=10, textvariable=self.refresh_rate, width=20)
        self.refresh.grid(row=2, column=0, padx=30)
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
        # called from the login button
        self.hide()
        subFrame = Login(self)
        
    def hide(self):
        """"""
        self.master.withdraw()
        return

    def show(self,status, uid, pwd):
        """"""
        self.status = status        # The value passed back from the pop up window
        self.user = uid
        self.password = pwd
        self.master.update()
        self.master.deiconify()
        print("Details Back - status:%s, username:%s, password:%s" % (self.status, self.user, self.password))
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
    app = DataDisplay(root)
    root.geometry("800x410")
    app.master.title("Data Display Tool")
    app.mainloop()
    return

if __name__ == '__main__':
	main()


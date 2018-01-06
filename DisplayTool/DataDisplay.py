#!/usr/bin/env python3
"""
    This program preovides a user interface that allows the CognIot data to be
    displayed using the api

    
"""

#TODO: Force Login at the beginning
#TODO: Populate Device / Sensor selection
#TODO: 



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
import random
import json

import SystemSettings as SS

MAX_LENGTH = 100        # The maximum number of values to be displayed


# Graph coordinates
#   50,10   _____________________
#           |..|..|..|..|..|..|..|
#           |..|..|..|..|..|..|..|      Each '|' is 20 pixels across
#           |..|..|..|..|..|..|..|      there are 20 vertical segments
#           |..|..|..|..|..|..|..|
#           |..|..|..|..|..|..|..|      Each '.' is 20 pixels down
#           |..|..|..|..|..|..|..|      there are 14 horizontal segments
#           |..|..|..|..|..|..|..|
#           |__|__|__|__|__|__|__| 430, 270
#
START_X = 50
START_Y = 10
END_X = 430
END_Y = 270
GRAPH_STEP = 20
START_LEGEND_Y = 5                 # Where the legent starts for the Y axis


class Login(Toplevel):
    """"""
 
    def __init__(self, original):
        """Constructor"""
        self.log = logging.getLogger()
        self.log.debug("[Disp] cls_Login initialised")
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
        Radiobutton(self.frame, text="Amazon Web Services", value="AWS", variable=self.db).grid(row=3,column=1, sticky=W, padx=10)
        self.db.set("DBLocal")
        btn = Button(self.frame, text="Login", command=self.onLogin).grid(row=4,column=0, pady=10, columnspan=2)

        self.frame.pack(fill=BOTH, expand=NO)#, anchor="center")
 
    def onLogin(self):
        """"""
        # Validate the input
        if self.check_credentials():
            self.destroy()
            self.original_frame.after_login_show(True, self.user.get(), self.password.get(), self.db.get())
        else:
            messagebox.showinfo("Unsuccessful", "Username / password not authenticated" )
        return

    def check_credentials(self):
        """"""
        print("Checking Credentials")
        fulldata = {'id':self.user.get(), 'auth':self.password.get(), 'dest':self.db.get()}
        #print("Payload Being Sent:\n%s" % fulldata)
        try:
            r = requests.get(SS.API_ADDRESS+'/authenticateuser', data=fulldata)
            #print("response:%s" % r)
            if r.status_code ==200:
                self.login_status = True
            else:
                self.login_status = False
        except:
            self.login_status = False
        return self.login_status


class LoginDDown(Toplevel):
    """"""
 
    def __init__(self, original):
        """Constructor"""
        self.log = logging.getLogger()
        self.log.debug("[Disp] cls_LoginDDown (Login Drop Downs) initialised")
        self.original_frame = original
        self.user = StringVar()
        self.db = StringVar()
        self.password = StringVar()
        self.login_status = False

        Toplevel.__init__(self)
        self.geometry("350x200")
        self.title("Login")
        self.frame = Frame(self, relief='ridge')
        Label(self.frame, text="     Username:").grid(row=0,column=0, padx=20, sticky=W)
        user = Combobox(self.frame, height=10, textvariable=self.user, width=20, values=SS.USERS)
        user.bind("<<ComboboxSelected>>", self.select_password)
        user.grid(row=0,column=1, padx=10, pady=10, sticky=E)
        Radiobutton(self.frame, text="File", value="FILE", variable=self.db).grid(row=2,column=0, sticky=W, padx=10)
        Radiobutton(self.frame, text="DBLocal", value="DBLocal", variable=self.db).grid(row=2,column=1, sticky=W, padx=10)
        Radiobutton(self.frame, text="DBRemote", value="DBRemote", variable=self.db).grid(row=3,column=0, sticky=W, padx=10)
        Radiobutton(self.frame, text="Amazon Web Services", value="AWS", variable=self.db).grid(row=3,column=1, sticky=W, padx=10)
        self.db.set("DBLocal")
        btn = Button(self.frame, text="Login", command=self.onLogin).grid(row=4,column=0, pady=10, columnspan=2)

        self.frame.pack(fill=BOTH, expand=NO)#, anchor="center")

    def select_password(self, event):
        """
        Auto populate the password from the list
        """
        self.log.debug("[Disp] User selected:%s" % self.user.get())
        if self.user.get() in SS.USERS:
            self.password.set(SS.PASSWORDS[SS.USERS.index(self.user.get())])
            self.log.debug("[Disp] Password selected from the list:%s" % self.password.get())
        else:
            self.password.set("")
            self.log.debug("[Disp] User not in the prescribed list, password set to <emply string>")
        return
        
    def onLogin(self):
        """"""
        # Validate the input
        if self.check_credentials():
            self.destroy()
            self.original_frame.after_login_show(True, self.user.get(), self.password.get(), self.db.get())
        else:
            messagebox.showinfo("Unsuccessful", "Username / password not authenticated" )
        return

    def check_credentials(self):
        """"""
        print("Checking Credentials")
        fulldata = {'id':self.user.get(), 'auth':self.password.get(), 'dest':self.db.get()}
        print("Payload Being Sent:\n%s" % fulldata)
        try:
            r = requests.get(SS.API_ADDRESS+'/authenticateuser', data=fulldata)
            print("response:%s" % r)
            if r.status_code ==200:
                self.login_status = True
            else:
                self.login_status = False
        except:
            self.login_status = False
        return self.login_status



class DataDisplay(Frame):
    def __init__(self, master=None):
        self.log = logging.getLogger()
        self.log.debug("[Disp] cls_DataDisplay initialised")
        Frame.__init__(self,master)
        self.master = master
        self.login_status = False

        self.log.info("Starting Main Frame")
        # These are the tuples of what is selected in the listbox
        self.current_device = StringVar()
        self.current_sensor_acroyn = StringVar()
        self.current_sensor_desc = StringVar()
        self.user = ""
        self.password = ""
        self.db = ""
        self.device_dict = {}
        self.data_window_text = StringVar()
        self.refresh_rate = IntVar()
        self.y_max_scale_value = IntVar()
        self.y_min_scale_value = IntVar()
        
        self.running = False       # When true, data is being captured.
        self.data_in = [[]]           # The data after it has been passed into the 
        self.dataset = [[]]           # The dataset being displayed and graphed
        self.starttime = "2000-01-01 00:00:00"         # The date of the oldest record
        self.limit = 10
        self.y_max_scale_value.set(0)
        self.y_min_scale_value.set(0)

        # Build the Selection row
        selection_frame = Frame(self, relief='ridge')
        self.device = Combobox(selection_frame, height=10, textvariable=self.current_sensor_acroyn, width=20)
        self.device.bind("<<ComboboxSelected>>", self.populate_sensor_info)
        self.device.grid(row=0, column=0, padx=30)
        self.sensor = Label(selection_frame, relief='sunken', textvariable=self.current_device, width=15)
        self.sensor.grid(row=0, column=1, padx=10)
        self.sensor_info = Label(selection_frame, relief='sunken', textvariable=self.current_sensor_desc, width=30)#, wraplength=50)
        self.sensor_info.grid(row=0, column=2)
        self.login_button = Button(selection_frame, text='Login', command=self.call_login_popup).grid(row=0, column=3, padx=20)
        selection_frame.grid(row=0, column=0, columnspan=2, pady=10)

        # Build the data display frame and the selection part
        data_frame = LabelFrame(self, relief='ridge',width=20, text="Data Received")
        #self.data_info = Listbox(data_frame, relief='sunken', listvariable=self.data_window_text, width=30)#, textvariable=self.data_window_text, text="Data Info", wraplength=200)
        # Changed to Label so that only the new values are displayed
        self.data_info = Label(data_frame, relief='sunken', textvariable=self.data_window_text, width=30, wraplength=200)
        self.data_info.grid(row=0, column=0)
        data_frame.grid(row=1, column=0, pady=10)
        
        # Build the graph canvas picture
        graph_frame = Frame(self, relief='ridge')
        self.graph_canvas = Canvas(graph_frame, width=440, height=300, background='#ffffff')
        self.graph_canvas.create_polygon(START_X,START_Y,END_X,START_Y,END_X,END_Y,START_X,END_Y, outline="green", fill="")
        for r in range(START_Y + GRAPH_STEP,END_Y,GRAPH_STEP):
            self.graph_canvas.create_line(START_X,r,END_X,r, fill="lightblue")
        for c in range(START_X + GRAPH_STEP,END_X,GRAPH_STEP):
            self.graph_canvas.create_line(c,START_Y,c,END_Y, fill="lightblue")

        # Graph axis labels
        x_max_label = Label(self.graph_canvas, relief='sunken', text='Now')
        x_max_label_window = self.graph_canvas.create_window(END_X-15, END_Y, anchor=NW, window=x_max_label)
        x_min_label = Label(self.graph_canvas, relief='sunken', text='Oldest')
        x_min_label_window = self.graph_canvas.create_window(START_X, END_Y, anchor=NW, window=x_min_label)
        y_max_label = Label(self.graph_canvas, relief='sunken', textvariable=self.y_max_scale_value, width=5)
        y_max_label_window = self.graph_canvas.create_window(START_LEGEND_Y, START_Y, anchor=NW, window=y_max_label)
        y_min_label = Label(self.graph_canvas, relief='sunken', textvariable=self.y_min_scale_value, width=5)
        y_min_label_window = self.graph_canvas.create_window(START_LEGEND_Y, END_Y-10, anchor=NW, window=y_min_label)
        
        self.graph_canvas.pack()

        graph_frame.grid(row=1, column=1)

        close_frame = Frame(self,relief='ridge')
        self.refresh = Combobox(close_frame, height=10, textvariable=self.refresh_rate, width=20)
        self.refresh.grid(row=2, column=0, padx=30)
        exit_program = Button(close_frame, text="Exit", command=self.exit_program).grid(row=2, column=3, padx=40)
        close_frame.grid(row=2, column=0, columnspan=2)

        # Put it all together on the screen
        self.pack(fill=BOTH, expand=NO)
        self.after(100, self.main)      # was root.
        return

    def reset(self):
        """
        Reset the valus back to the start for another dataset
        """
        self.data_in = [[]]
        self.dataset = [[]]
        self.starttime = "2000-01-01 00:00:00"
        self.limit = 10
        self.y_max_scale_value.set(0)
        self.y_min_scale_value.set(0)
        self.graph_canvas.delete('graphline')
        return

    def populate_sensor_info(self, event):
        """
        Populate the sensor info following selection of the device id.
        """
        print("populate sensor values reached")
        selection = self.device.get()
        for i in range(0, len(self.device_dict)):
            entry = self.device_dict[i]
            if entry[0]['DeviceAcroynm'] == selection:
                self.current_device.set(entry[0]['DeviceID'])
                self.current_sensor_desc.set(entry[0]['DeviceDescription'])
        self.reset()
        self.running = True
        
    def populate_dropdowns(self):
        """
        Populate the variables used by the main display from data from the db

        Data Returned:[{
        "0":{"DeviceAcroynm":"RPi_3B","DeviceDescription":"RPi on workbench","DeviceID":"3355054600"},
        "1":{"DeviceAcroynm":"RPi_Zero","DeviceDescription":"RPi by Cosy Sensor","DeviceID":"165456298"},
        "2":{"DeviceAcroynm":"RPi_Sens","DeviceDescription":"Rpi on windowsil","DeviceID":"135080095"}
        }]

        """
        # Initially can only populate the device list
        print("Getting Device List")
        fulldata = {'id':self.user, 'auth':self.password, 'dest':self.db}
        #print("Payload Being Sent:\n%s" % fulldata)
        try:
            r = requests.get(SS.API_ADDRESS+'/retrievedevicelist', data=fulldata)
            if r.status_code ==200:
                # r.text contains the dictionary of data
                device_list = []
                self.device_dict = json.loads(r.text)
                self.log.debug("[Disp] Device Dictionary: %s" % self.device_dict)
                for entry in self.device_dict:
                    # r.text could contain multiple dictionaries in the response
                    for element in entry:
                        #device_list.append(element['DeviceID'])
                        device_list.append(element['DeviceAcroynm'])
                self.device['values'] = device_list

            else:
                self.device['values'] = ["No Devices"]
        except:
            self.device['values'] = ["Error Finding devices"]
            
        #print("Device List:%s <-> %s" % (self.device['values'], device_list))
        return

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

    def update_data(self, data):
        """
        Takes the new values in from outside the class
        data is a list of values, the newest reading is last
        """
        self.log.debug("[Disp] Incoming data to be added to feed:%s" % data)
        self.data_in = data
        for i in range(0, len(self.data_in)):
            if len(self.dataset) > i-1:
                # Dataset doesn't contain the right number of elements, so need to add one
                self.dataset.append([])
            if len(self.data_in[i]) > 0:
                self.dataset[i] = self.dataset[i] + data[i]
                self.dataset[i] = self.dataset[i][-MAX_LENGTH:]        # Trim the data to the last 100 readings max
            self.log.info("[Disp] Dataset %s after update and trim:%s" % (i, self.dataset[i]))
        self.update_idletasks() #was root.
        return
        
    def update_data_old(self, data):
        """
        Takes the new values in from outside the class
        data is a list of values, the newest reading is last
        """
        self.log.debug("[Disp] Incoming data to be added to feed:%s" % data)
        self.data_in = data
        if len(self.data_in) > 0:
            self.dataset = self.dataset + data
            self.dataset = self.dataset[-MAX_LENGTH:]        # Trim the data to the last 100 readings max
        self.log.info("[Disp] Dataset after update and trim:%s" % self.dataset)
        self.update_idletasks() #was root.
        return
        
    def _is_number(check):
        """
        Check if the string passed into check is a number or a string
        """
        try:
            float(check)
            return True
        except:
            return False

    def get_data(self):
        # Function to retrieve the data from the database
        # Just an example at the moment
        # This is self running and will send new data every 1000mS
        text_to_add = []

        if self.running:
            fulldata = {'id':self.user, 'auth':self.password, 'dest': self.db, 'device_id' : self.current_device.get(),
                        'limit':self.limit, 'starttime':self.starttime}
            print("Payload Being Sent:\n%s" % fulldata)
            r = requests.get(SS.API_ADDRESS+'/retrievesensorvalues', data=fulldata)

            if r.status_code ==200:
                self.log.info("[Disp] Data of length %s received from the RestFul API:%s" % (len(r.text), r.text))
                dataset = json.loads(r.text)
                self.log.debug("[Disp] JSON converted data of length %s received from the RestFul API:%s" % (len(dataset), dataset))
                if len(dataset['values']) >0:        #TODO: This will be required to check if there is any new data
                    self.log.debug("[Disp] length of values are greater than zero")
                    data = dataset['values']     # Extact the first dataset returned
                    self.log.debug("[Disp] Dataset selected to be used:%s" % data)
                    # Need to convert each sub dataset to a number from a string now
                    for j in range(0, len(data)):
                        for i in range(0,len(data[j])):
                            self.log.debug("[Disp] Item being converted:%s" % i)
                            if _is_number(data[j][i]):
                                #text_to_add.append(float(i))
                                data[j][i] = float(format(float(data[j][i]), '.2f'))          # Take the floating point number, reduce it to 2 decimal places and return a number, not a a string
                                self.log.debug("[Disp] record added:%s" % float(data[j][i]))
                    self.update_data(data)#text_to_add)
                self.starttime = dataset['last_key']
            else:
                print('Failed to Read')
                print('Status Code:%s' % r.status_code)
        return

    def get_data_old(self):
        # Function to retrieve the data from the database
        # Just an example at the moment
        # This is self running and will send new data every 1000mS
        text_to_add = []

        if self.running:
            fulldata = {'id':self.user, 'auth':self.password, 'dest': self.db, 'device_id' : self.current_device.get(),
                        'limit':self.limit, 'starttime':self.starttime}
            print("Payload Being Sent:\n%s" % fulldata)
            r = requests.get(SS.API_ADDRESS+'/retrievesensorvalues', data=fulldata)

            if r.status_code ==200:
                self.log.info("[Disp] Data of length %s received from the RestFul API:%s" % (len(r.text), r.text))
                dataset = json.loads(r.text)
                self.log.debug("[Disp] JSON converted data of length %s received from the RestFul API:%s" % (len(dataset), dataset))
                if len(dataset['values']) >0:        #TODO: This will be required to check if there is any new data
                    self.log.debug("[Disp] length of values are greater than zero")
                    data = dataset['values'][0]     # Extact the first dataset returned
                    self.log.debug("[Disp] Dataset selected to be used:%s" % data)
                    for i in data:
                        self.log.debug("[Disp] Item being converted:%s" % i)
                        if _is_number(i):
                            #text_to_add.append(float(i))
                            text_to_add.append(float(format(float(i), '.2f')))          # Take the floating point number, reduce it to 2 decimal places and return a number, not a a string
                            self.log.debug("[Disp] record added:%s" % float(i))
                self.update_data(text_to_add)
                self.starttime = dataset['last_key']
            else:
                print('Failed to Read')
                print('Status Code:%s' % r.status_code)
        return

    def draw_graph(self,data_to_draw, line_no):
        """
        Draw the graph on the graph area
        Graph area is 0 - 20 sections wide, 0 - 13 high
        coord ranges 20 - END_X across, 20 - 280 up.
        """
        # If the line has been drawn before, delete it.
        #try:
        #    self.graph_canvas.delete('graphline')
        #except:
        colours = ["red", "green", "blue", "cyan", "yellow", "magenta", "black", 'white']

        if line_no == 0:
            if len(self.graph_canvas.find_withtag('graphline'))> 0:
                self.graph_canvas.delete('graphline')
        #data_to_draw = self.dataset     # Take a copy so it is not updated as I draw the graph
        x_spacing = (END_X - START_X) / len(data_to_draw)       # Add 1 as
        if self.y_max_scale_value.get() < max(data_to_draw):
            self.y_max_scale_value.set(max(data_to_draw))
        if self.y_min_scale_value.get() > min(data_to_draw):
            self.y_min_scale_value.set(min(data_to_draw))

        if (self.y_max_scale_value.get() - self.y_min_scale_value.get()) > 0:
            y_spacing = (END_Y - START_Y) / (self.y_max_scale_value.get() - self.y_min_scale_value.get())
        else:
            y_spacing = (END_Y - START_Y)
        #print("y_spacing:%s" % y_spacing)
        start_line_x = START_X        # Set the starting point for the X axis
        start_line_y = END_Y - ((data_to_draw[0] - self.y_min_scale_value.get()) * y_spacing)
        for reading in data_to_draw[1:]:        # Start at the second reading as first one is starting point
            end_line_x = start_line_x + x_spacing
            end_line_y = END_Y - ((reading - self.y_min_scale_value.get()) * y_spacing)
            #print("END_Y:%s, reading:%s, end_line_y:%s" % (END_Y, reading, end_line_y))
            self.graph_line = self.graph_canvas.create_line(start_line_x,start_line_y,end_line_x,end_line_y, fill=colours[line_no], tags=('graphline'))
            start_line_x = end_line_x
            start_line_y = end_line_y
        #print(data_to_draw)
        return

    def update_stream(self):
        """
        If there is any data in the incoming stream, add it to the listbox,
        but then clear the incoming stream to stop it being re-added!
        """
        if len(self.data_in) >0:
            self.log.debug("Length of the data to be added:%d" % len(self.data_in))
            #self.data_info.insert(0,self.data_in)
            self.data_window_text.set(self.data_in)
            self.data_in = []
        else:
            self.data_window_text.set("")
        self.update_idletasks()     #was root.
        return
        
    def main_old(self):
        """
        Called regularly to update values etc.
        """
        if self.running:
            # Call this when running
            self.get_data()
            self.update_stream()
            if len(self.dataset) > 0:
                # Only draw the graph if there is data to draw
                self.draw_graph(self.dataset)
        self.after(1000, self.main)      #was root.

    def main(self):
        """
        Called regularly to update values etc.
        """
        if self.running:
            # Call this when running
            self.get_data()
            self.update_stream()
            for i in range(0,len(self.dataset)):
                self.log.debug("[Disp] Drawing graph for dataset %s" % i)
                if len(self.dataset[i]) > 0:
                    # Only draw the graph if there is data to draw
                    self.draw_graph(self.dataset[i], i)
        self.after(1000, self.main)      #was root.

    def call_login_popup(self):
        # called from the login button
        self.hide()
        # subFrame = Login(self)        # removed to allow user to be selected from dropdown for demo
        subFrame = LoginDDown(self)
        
    def hide(self):
        """"""
        self.master.withdraw()
        return

    def after_login_show(self,status, uid, pwd, db):
        """This is called after the pop up window has completed"""
        self.status = status        # The value passed back from the pop up window
        self.user = uid
        self.password = pwd
        self.db = db
        self.master.update()
        self.master.deiconify()
        print("Details Back - status:%s, username:%s, password:%s, db:%s" % (self.status, self.user, self.password, self.db))
        self.populate_dropdowns()
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

def GetData_random():
    # Function to retrieve the data from the database
    # Just an example at the moment
    # This is self running and will send new data every 1000mS
    text_to_add = []
    #TODO: Convert the function below to get real data
    text_to_add.append(random.randint(0,100))
    gbl_log.debug("Data to be added:%s" % text_to_add)
    if len(text_to_add) >0:        #TODO: This will be required to check if there is any new data
        app.update_data(text_to_add)
    root.after(100, GetData)
    return

def _is_number(check):
    """
    Check if the string passed into check is a number or a string
    """
    try:
        float(check)
        return True
    except:
        return False
        
def GetData():
    # Function to retrieve the data from the database
    # Just an example at the moment
    # This is self running and will send new data every 1000mS
    text_to_add = []

    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal', 'device_id' : '165456298'}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(SS.API_ADDRESS+'/retrievesensorvalues', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    #TODO: Convert the function below to get real data
#    text_to_add.append(random.randint(0,100))
    gbl_log.debug("Data to be added:%s" % text_to_add)
    if len(r.text[0]) >0:        #TODO: This will be required to check if there is any new data
        for i in r.text[0]:
            if _is_number(i):
                text_to_add.append(float(i))
    app.update_data(text_to_add)
    #root.after(100, GetData)
    return
        
def main():

    SetupLogging()

    global root
    global app
    root = Tk()
    text_font = ('TkDefault', '20')
    root.option_add('*TCombobox*Listbox.font', text_font)
    #root.option_add('*TCombobox*Height', 20)
    app = DataDisplay(root)
    root.geometry("800x410")
    app.master.title("Data Display Tool")
    #GetData()
    app.mainloop()
    return

if __name__ == '__main__':
	main()


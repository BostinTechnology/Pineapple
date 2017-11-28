"""

"""


import tkinter as Tk
from tkinter import messagebox
 
########################################################################
class OtherFrame(Tk.Toplevel):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, original):
        """Constructor"""
        self.original_frame = original
        Tk.Toplevel.__init__(self)
        self.geometry("400x300")
        self.title("otherFrame")
 
        btn = Tk.Button(self, text="Close", command=self.onClose)
        btn.pack()
 
    #----------------------------------------------------------------------
    def onClose(self):
        """"""
        self.destroy()
        self.original_frame.show("suceeded")
 
########################################################################
class MyApp(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        self.root = parent
        self.root.title("Main frame")
        self.frame = Tk.Frame(parent)
        self.frame.pack()
 
        btn = Tk.Button(self.frame, text="Open Frame", command=self.openFrame)
        btn.pack()
        msg = Tk.Button(self.frame, text="Message", command=self.message_box)
        msg.pack()
 
    #----------------------------------------------------------------------
    def hide(self):
        """"""
        self.root.withdraw()
 
    #----------------------------------------------------------------------
    def openFrame(self):
        """"""
        self.hide()
        subFrame = OtherFrame(self)
        
 
    #----------------------------------------------------------------------
    def show(self,status):
        """"""
        self.root.update()
        self.root.deiconify()
        print(status)

    def message_box(self):
        """"""
        messagebox.showinfo("Greetings", "This is a message box" )
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    root = Tk.Tk()
    root.geometry("800x600")
    app = MyApp(root)
    root.mainloop()

from os import name
from sqlite3.dbapi2 import Time
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import multiprocessing as mp
from tkinter.font import families
import backend
from main3 import textRecognition
from datetime import datetime as dt
from tkinter.filedialog import asksaveasfile


global windowsize
global prevDone
prevDone = 0
global currentPatdbId
global isp2Started
isp2Started = False


def get_selected_row(event):
    try:
        global selected_tuple, item_id
        item_id = event.widget.focus()
        item = event.widget.item(item_id)
        selected_tuple=item['values']
        e1.delete(0,END)
        e1.insert(END,selected_tuple[0])
        e2.delete(0,END)
        e2.insert(END,selected_tuple[1])
    except IndexError:
        pass   


def show():
    listBox.delete(*listBox.get_children())
    for row in backend.view():
        temp = row[3]
        try:
            if str(temp).split("-")[2] == "Finished":
                temp = "Finished"
        except:
            pass
        listBox.insert("","end",id=row[0], values=(row[1], row[2], temp))
    
def start_command():
    global currentPatdbId
    raiseFrame2()
    global isp2Started
    isp2Started = True
    mp.freeze_support()

    currentPatdbId = backend.getCurrentPatID(selected_tuple[0], selected_tuple[1], selected_tuple[2])
    #length of 'awaiting start' and 'hrs-mins-Finished' is more than 10 always
    #checking for unfinished PAT to extract list of people who bought gifts already
    if len(selected_tuple[2]) < 10: 
        global sharedPatDoneList
        try:
            del sharedPatDoneList[:]
        except:
            pass
        patDoneList = backend.getPatDoneList(currentPatdbId)
        for name, temptime in patDoneList:
            sharedPatDoneList.append(name)
            
    global p2, sharedPatAmountDict
    sharedPatAmountDict['patamt'] = str(selected_tuple[1])
    p2 = mp.Process(target=m.startPat, args=(q,currentPatdbId,sharedPatDoneList,sharedPatAmountDict))
    
    if selected_tuple[2] != "Finished":
        changeWindowPos()
        p2.start()
        
        print("starting...")


def create_command():
    name = name_text.get()
    amt = amount_int.get()
    if name != "" and amt != "" :
        try:
            if int(amt) >= 1000:
                amt = str(int(amt) / 1000) + "K"
        except:
            pass 
        backend.insert(name,amt)
    else:
        print("add something...")

    show()

def delete_command():
    backend.deleteSelected(selected_tuple[0], selected_tuple[1], selected_tuple[2])
    show()

def finished_delete():
    for row in backend.view():
        if row[3] == "Finished":
            backend.delete(row[0])
    show()

def waiting_delete():
    for row in backend.view():
        if row[3] == "awaiting start":
            backend.delete(row[0])

    show()
    
def details_command():
    global currentPatdbId, selected_tuple
    currentPatdbId = backend.getCurrentPatID(selected_tuple[0], selected_tuple[1], selected_tuple[2])
    textFileList = []
    global Write2TxtCurrentTime
    Write2TxtCurrentTime = ""
    def writeToTxt():
        try:
            # Getting a filename to save the file.
            f = asksaveasfile(initialfile='Untitled.txt',defaultextension=".txt",filetypes=[("Text Documents","*.txt")])
            print(f)
            open(f.name, 'w')
            f.write(Write2TxtCurrentTime+"\n")              
            for item in textFileList:
                f.write(item+"\n")
            
            f.close()
        except:
            pass
    
    def refreshDetailsList():
        tree.delete(*tree.get_children())
        textFileList.clear()
        patDoneList = backend.getPatDoneList(currentPatdbId)
        #once pat finish status gets implemented then replace time_now with pat_finish_time
        dindex = 0
        RunOnceToSaveCurrentTime = False
        for item1, time1 in patDoneList:
            dindex = dindex+1
            t_hr_diff = 0
            t_hr = str(time1).split(":")[0]
            t_min = str(time1).split(":")[1]
            t_hr = int(t_hr)
            t_min = int(t_min)
            t_min_now = dt.now().minute
            t_hr_now = dt.now().hour
            try:
                if str(selected_tuple[2]).split("-")[2] == "Finished":
                    t_min_now = int(str(selected_tuple[2]).split("-")[1])
                    t_hr_now = int(str(selected_tuple[2]).split("-")[0])
            except:
                pass 

            t_hr_diff = t_hr_now - t_hr
            t_min_diff = t_min_now - t_min

            if t_min_diff < 0:
                t_hr_diff = (t_hr_now - t_hr) - 1
                t_min_diff = 60 - abs(t_min_diff)

            finalTime = str(t_hr_diff) + "hr " + str(t_min_diff) + "mins ago"
            tree.insert('', 'end',text=dindex, values=(dindex, item1, finalTime))
            temp = str(dindex) + "   " + str(item1) + "   " + finalTime
            textFileList.append(temp)

            #Run Once
            if RunOnceToSaveCurrentTime == False:
                RunOnceToSaveCurrentTime = True
                global Write2TxtCurrentTime
                Write2TxtCurrentTime = "Current Time: " + str(t_hr_now)+"hrs "+str(t_min_now)+"mins "

        

    dWindow = Toplevel(window)

    #dWindow.geometry("600x600")
    tree = ttk.Treeview(dWindow, column=("c1", "c2", "c3"), show='headings')

    # define headings
    tree.column("#1", anchor=CENTER)
    tree.heading("#1", text="INDEX")
    tree.column("#2", anchor=CENTER)
    tree.heading("#2", text="NAME")
    tree.column("#3", anchor=CENTER)
    tree.heading("#3", text="TIME")

    tree.grid(row=0, column=0, sticky='nsew')
    # add a scrollbar
    dButton = Button(dWindow,text="Save As Text File",style='s1.TButton',command=writeToTxt)
    dButton.grid(row=1,column=0, sticky='es')

    dButton2=Button(dWindow,text="Refresh", style='s2.TButton',command=refreshDetailsList)
    dButton2.grid(row=1,column=0, sticky='w')

    scrollbar = ttk.Scrollbar(dWindow, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='e')

    dWindow.grab_set()

def raiseFrame2():
    global windowsize
    windowsize = window.wm_geometry(None)

    f2.tkraise()
    window.geometry("125x500")
    changeWindowPos()
    print("Queue Frame raised.")

def changeWindowPos():
    window.geometry("+10+250")
    #print("changed pos")

def raiseFrame1():
    #try to add Finished state in database 
    try: 
        patDoneList = backend.getPatDoneList(currentPatdbId)
        done = len(patDoneList)
        if done >= 100:
            t_min_now = dt.now().minute
            t_hr_now = dt.now().hour
            finished = str(t_hr_now)+"-"+str(t_min_now)+"-Finished"
            backend.update(currentPatdbId, finished)
    except:
        pass

    window.wm_geometry(windowsize)
    f1.tkraise()
    global p2
    if p2.is_alive() == True:
        p2.terminate()
        print("PAT stopped.")

    clearPatdonedb()


def clearPatdonedb():
    patdbList = backend.getAllRowIDFromPatdb()
    patdoneList = backend.getAllpatdbIDFromPatdone()
    newPatdoneList = []
    for i in patdoneList:
        if i not in newPatdoneList:
            newPatdoneList.append(i)

    delItemList = []
    for id in newPatdoneList:
        if id not in patdbList:
            if id not in delItemList:
                delItemList.append(id)

    for item in delItemList:
        item = int(item[0])
        print("item delete ", item)
        backend.deleteFromPatdone(item)



def updateQueue():
    temp = []
    #print("UPDAtED QUEUEEEEEEEe")
    lb1.delete(0,END)
    while(q.empty() == False):
        temp2 = q.get()
        lb1.insert(END, temp2)
        print(temp2)
        temp.append(temp2)
        
    for item in temp:
        q.put(item)
    f2.after(1000,updateQueue)

def updateDone():
    try:
        global prevDone, isp2Started
        global tempid
        
        if isp2Started == False:
            tempid = backend.getCurrentPatID(selected_tuple[0], selected_tuple[1], selected_tuple[2])
        patDoneList = backend.getPatDoneList(tempid)
        done = len(patDoneList)
        if done > prevDone:
            prevDone = done
            temp = str(done)+"/100"
            entryDone.delete(0,END)
            entryDone.insert(END, temp)
            backend.update(temp,currentPatdbId)
    except:
        pass 
    f2.after(1000,updateDone)

def windowDestroy():
    clearPatdonedb()
    window.destroy()

window=Tk()   
#window.wm_attributes("-topmost", 1)
window.wm_title("Patronage Manager")
window.iconbitmap(default='icon.ico')
window.resizable(width=False, height=False)

f1 = Frame(window)
f2 = Frame(window)

f1.grid(row=0, column=0, sticky="news") #north-east-west-south
f2.grid(row=0, column=0,sticky="news")


#frame2 begin
style = Style()
style.configure('stop.TButton', font =('Times New Roman', 10, 'bold'))
style.map('stop.TButton', foreground = [('pressed', 'blue'),('active', 'red')], background = [('pressed','!disabled', 'black'),('active', 'blue')])

bb1 = Button(f2,text="STOP",style='stop.TButton', command=raiseFrame1)
bb1.grid(row=4,column=0)

ll1=Label(f2,text="QUEUE",font=("Times New Roman", 10, "bold"))
ll1.grid(row=2,column=0)

lb1 = Listbox(f2,height = 15, width = 10, bg = "grey",activestyle = 'dotbox', font = "Helvetica",fg = "yellow")
lb1.grid(row=3,column=0)
lb1.anchor('center')

ll2=Label(f2,text="DONE",font=("Times New Roman", 10, "bold"))
ll2.grid(row=0,column=0)

patDoneEntry = StringVar()
entryDone = Entry(f2,textvariable=patDoneEntry)
entryDone.grid(row=1,column=0)
#frame2 end

l1=Label(f1,text="Patronage Name",font=("Times New Roman", 12, "bold"))
l1.grid(row=0,column=0)

l2=Label(f1,text="Patronage Amount",font=("Times New Roman", 12, "bold"))
l2.grid(row=1,column=0)

name_text=StringVar()
e1=Entry(f1,textvariable=name_text, width=40)
e1.grid(row=0,column=1)

amount_int=StringVar()
e2=Entry(f1,textvariable=amount_int, width=40)
e2.grid(row=1,column=1)

listBox = Treeview(f1, column=("c1", "c2", "c3"), show='headings')

# define headings
listBox.column("#1", anchor=CENTER)
listBox.heading("#1", text="Name")
listBox.column("#2", anchor=CENTER)
listBox.heading("#2", text="Amount")
listBox.column("#3", anchor=CENTER)
listBox.heading("#3", text="Status")
    
listBox.grid(row=3, column=0, rowspan=7, columnspan=3)

listBox.tag_configure('focus', background='yellow')
listBox.bind("<Button-1>", get_selected_row)

style = Style()
style.configure('s1.TButton', font =('Times New Roman', 12, 'bold' ),borderwidth = '4', width=20, height= 2)
style.configure('s2.TButton', font =('Times New Roman', 10, 'bold'), width=20)
style.configure('s3.TButton', font =('Times New Roman', 10, 'bold'), width=20)
style.map('s1.TButton', foreground = [('pressed', 'green'),('active', 'blue')], background = [('pressed','!disabled', 'black'),('active', 'green')])
style.map('s2.TButton', foreground = [('pressed', 'blue'),('active', 'green')], background = [('pressed','!disabled', 'black'),('active', 'blue')])
style.map('s3.TButton', foreground = [('pressed', 'red'),('active', 'blue')], background = [('pressed','!disabled', 'black'),('active', 'red')])

b2=Button(f1,text="Start", style='s1.TButton',command=start_command)
b2.grid(row=0,column=3, rowspan=2)

b3=Button(f1,text="Create", style='s1.TButton',command=create_command)
b3.grid(row=0,column=2,rowspan=2)

b1=Button(f1,text="Refresh", style='s2.TButton',command=show)
b1.grid(row=3,column=3)

b4=Button(f1,text="Details", style='s2.TButton',command=details_command)
b4.grid(row=4,column=3)

b5=Button(f1,text="Delete Selected", style='s3.TButton',command=delete_command)
b5.grid(row=5,column=3)

b5=Button(f1,text="Delete All Finished", style='s3.TButton',command=finished_delete)
b5.grid(row=6,column=3)

b5=Button(f1,text="Delete All Waiting", style='s3.TButton',command=waiting_delete)
b5.grid(row=7,column=3)

b6=Button(f1,text="Close", style='s3.TButton',command=windowDestroy)
b6.grid(row=8,column=3)

if __name__ == "__main__":
    mp.freeze_support()
    q = mp.Queue()
    currentPatdbId = mp.Value('i')
    global sharedPatDoneList, sharedPatAmountDict
    sharedPatDoneList = mp.Manager().list()
    sharedPatAmountDict = mp.Manager().dict()

    m = textRecognition()
    f1.tkraise()
    window.geometry("773x273")
    updateQueue()
    updateDone()
    window.mainloop()


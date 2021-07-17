from ctypes import sizeof
import re
from time import sleep
from numpy import empty, true_divide
import pyautogui
from pyscreeze import locateOnScreen
from win32gui import IsWindow
from windowcapture import WindowCapture


class my_dictionary(): 

    global chat
    # __init__ function 
    def __init__(self): 
        self.chat = {}
          
    # Function to add key:value 
    #If new chat value is different than old chat then add it to chat.
    #keeping only last 100 character of chat for every person
    def add(self, key, value):
        prevChat = ""
        key = re.sub('[^A-Za-z0-9]+', '', key) #removes all symbols from names
        if key in self.chat.keys():
            prevChat = str(self.chat[key])+" "
        
        if prevChat.lower() != str(value).lower():
            self.chat[key] = prevChat + value
    
        if len(self.chat[key]) > 100 :
            self.chat[key] = self.chat[key][-100:]  

    def delchat(self,key):
        #self.chat[key] = ""
        return True   


class searchAndQueue():

    mydictionary = my_dictionary()

    def __init__(self) -> None:
        pass

    def isName(self, chatlist, index):
        isname = False

        if ("[" and "]" in chatlist[index]) or ("@" and "]" in chatlist[index]) or ("@" and "[" in chatlist[index]):
            isname = True
        
        return isname

    def isReady2Buy(self, str):
        isready2buy = False
        temp = str.lower()
        #print(str.lower())
        queuepls = ['q pls','q pis' , 'q me', 'qme ', 'qme pis', 'me in q', 'queue me']
        for qpls in queuepls:
            if re.search(qpls, temp, re.IGNORECASE):
                isready2buy = True
                break

        return isready2buy

    def haveYouBoughtGift(self, index, chatbook):
        boughtGift = False
        #print(index)
        if index == None:
            return boughtGift

        #print(chatbook)
        for key in chatbook:
            if index == key:
                value = str(chatbook[key]).lower().replace("#isdone", "")
                isDone = ['done', 'bought']
                for isdone in isDone:
                    if isdone in value:
                        boughtGift = True
                        break
        
        
        return boughtGift


    def areWeOnAllianceChat(self):
        onChat = False
        imgList = ["chatWin.png","allianceChatActiveWin.png","chat.png","allianceChatActive.png",]

        if locateOnScreen(imgList[0]) != None and locateOnScreen(imgList[1]) != None:
            onChat = True
        elif locateOnScreen(imgList[2]) != None and locateOnScreen(imgList[3]) != None:
            onChat = True

        return onChat

    def write2Chat(self,text="Wellcome to PAT. Lets start."):
        wincap = WindowCapture('March of Empires: War of Lords')
        print("write2chat called...")
        if self.areWeOnAllianceChat() == True: 
            img = pyautogui.screenshot(region=(1340,915,500,35))
            img.save(r'tempChatError.png')
            sleep(0.5)
            pyautogui.click(150,985) #clicked on chatbox
            pyautogui.typewrite(text)
            pyautogui.press('enter')
            sleep(0.5)
            pyautogui.click(150,985) #clicked on chatbox
            sleep(2.5)
            onceWriteTemp = False
            chk = wincap.isChatError()
            while(chk == True):
                pyautogui.click(150,985)
                sleep(0.5)
                if onceWriteTemp == False:
                    pyautogui.typewrite("Chat error.")
                    onceWriteTemp = True
                pyautogui.press('enter')
                sleep(1)
                pyautogui.click(150,985)
                chk = wincap.isChatError()


            sleep(0.5)
            wincap.setPatManagerWindowForeground()
            
        else:
            obj = wincap.getChatbox()
            #print(obj)
            if  obj == True:
                img = pyautogui.screenshot(region=(1340,915,500,35))
                img.save(r'tempChatError.png')
                sleep(0.5)
                pyautogui.click(150,985) #clicked on chatbox
                pyautogui.typewrite(text)
                pyautogui.press('enter')
                sleep(0.5)
                pyautogui.click(150,985) #clicked on chatbox
                sleep(2.5)
                onceWriteTemp = False
                chk = wincap.isChatError()
                while(chk == True):
                    pyautogui.click(150,985)
                    sleep(0.5)
                    if onceWriteTemp == False:
                        pyautogui.typewrite("Chat error.")
                        onceWriteTemp = True
                    pyautogui.press('enter')
                    sleep(1)
                    pyautogui.click(150,985)
                    chk = wincap.isChatError()

                sleep(0.5)
                wincap.setPatManagerWindowForeground()
                #print("entered")

        


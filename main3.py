import multiprocessing
from multiprocessing.queues import Queue
from os import remove, replace
import queue
from typing import Counter
import cv2
from pyautogui import sleep
import pytesseract
import time
from windowcapture import WindowCapture
from manager import my_dictionary
from manager import searchAndQueue
import collections
import copy
from difflib import SequenceMatcher
import backend
from datetime import datetime as dt


class textRecognition():

    chatbook = my_dictionary()
    snq = searchAndQueue() 
    queue = queue.Queue(maxsize=15)
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    patDone = None
    prevImg = None
    prevCmd = ""

    def __init__(self):
        self.queue = []
        self.patDone = []
        
        

    def textOcr(self):
        wincap = WindowCapture('March of Empires: War of Lords')
        adaptive_threshold = wincap.getImage()
        
        ocr_result_roi = pytesseract.image_to_string(adaptive_threshold)

        ocrtemp = ocr_result_roi.split("\n")
        #print(ocrtemp)
        #print("\n\n")
        txts = []
        for ocr in ocrtemp:
            temp = ocr.strip()
            if temp != "":
                txts.append(temp)

        #print(txts)
        #print("\n\n")

        

        for i in range(0,len(txts)):
            temp2 =""
            if len(txts[i]) < 23 and len(txts[i]) > 5 and str(txts[i]).lower() != 'ago':   
                if self.snq.isName(txts, i):
                    temp2 = txts[i].split(" ")[-1]
                    if len(temp2) > 3:
                        if i+1 < len(txts):
                            if str(txts[i+1]).lower() != 'ago':
                                self.chatbook.add(temp2, txts[i+1])
                
                else:
                    prev = i - 2
                    next = i + 2
                    if prev >= 0 and self.snq.isName(txts, prev):
                        temp2 = txts[i].split(" ")[-1]
                        if len(temp2) > 3:
                            #print(temp2 + "\n")
                            if i+1 < len(txts):
                                if str(txts[i+1]).lower() != 'ago':
                                    self.chatbook.add(temp2, txts[i+1])
                    
                    elif next < len(txts) and self.snq.isName(txts, next):
                        temp2 = txts[i].split(" ")[-1]
                        if len(temp2) > 2:
                            #print(temp2 + "\n")
                            if i+1 < len(txts):
                                if str(txts[i+1]).lower() != 'ago':
                                    self.chatbook.add(temp2, txts[i+1])


    def cmdCheck(self,sharedPatAmountDict):
        currentCmd = ""
        isdoneWho = ""
        for key, value in self.chatbook.chat.items():
            if "#" in value:
                #print("# detected", key, "  ", value)
                value = str(value).strip().split()
                for i in range(0,len(value)):
                    if 'status' in str(value[i]).lower():
                        currentCmd = currentCmd + key + "status-"

                    if 'amount' in str(value[i]).lower():
                        currentCmd = currentCmd + key + "amount-"

                    if 'isdone' in str(value[i]).lower():
                        currentCmd = currentCmd + key + "isdone-"
                        isdoneWho=str(value[i+1])

            
        if currentCmd.lower() not in self.prevCmd.lower():
            tempCurrentCmd = currentCmd
            #print("currentCMD ", currentCmd)
            #print("preveousCmd", self.prevCmd)
            prevCmdList = self.prevCmd.split("-")
            newPrevCmdList = []
            for i in prevCmdList:
                if i not in newPrevCmdList:
                    newPrevCmdList.append(i)

            #print("splited List", newPrevCmdList)
            for cCmd in newPrevCmdList:
                currentCmd = currentCmd.lower().replace(cCmd.lower(),"",1) #replacing one instance of duplicate command
            #print("commandNEW ", currentCmd)
            self.prevCmd = tempCurrentCmd
            if "status" in currentCmd.lower():
                text = "Status: " +  str(len(self.patDone))+ "/100"
                self.snq.write2Chat(text)
            if "amount" in currentCmd.lower():
                text = "Pat Amount: " + str(sharedPatAmountDict['patamt']) + " gold coins."
                self.snq.write2Chat(text)
            if "isdone" in currentCmd.lower():
                if isdoneWho.lower() in str(self.patDone).lower():
                    text = "YES "+ isdoneWho + " has bought patronage gift."
                    self.snq.write2Chat(text)
                else:
                    text = isdoneWho+" haven't bought patronage gift yet."
                    self.snq.write2Chat(text)



    def getQueue(self,q):
        for key in self.chatbook.chat.keys():
            if (self.snq.isReady2Buy(self.chatbook.chat[key])):
                if key not in self.queue:
                    if key not in self.patDone:
                        temp = True
                        for wordi in self.queue:
                            score = SequenceMatcher(None, key, wordi).ratio()
                            if score > 0.8:
                                temp = False

                        for wordj in self.patDone:
                            score = SequenceMatcher(None, key, wordj).ratio()
                            if score > 0.8:
                                temp = False

                        if temp == True:
                            self.queue.append(key)
                            q.put(key)
                            
        tempDelList = []
        for key in self.chatbook.chat.keys():
            if key not in self.queue:
                tempDelList.append(key)
        for key in tempDelList:
            del self.chatbook.chat[key]
        del tempDelList[:]


    def startPat(self,q,currentPatdbId,sharedPatDoneList,sharedPatAmountDict):
        
        self.patDone.clear()
        if len(sharedPatDoneList) > 0:
            for item in sharedPatDoneList:
                self.patDone.append(item)

        c = 1
        myTurn2BuyGift = None
        previousQueue = []
        self.snq.write2Chat()

        while(True):

            time.sleep(1)
            print("startPat...", c)
            c= c+ 1

            self.textOcr()
            self.cmdCheck(sharedPatAmountDict)

            if len(self.queue) == 15:
                #print("Queue is full. Please be patients.")
                tempText = "Queue is full. Please be patients."
                self.snq.write2Chat(tempText)
            else:
                self.getQueue(q)

            
            if len(self.queue) > 0:
                if collections.Counter(self.queue) != collections.Counter(previousQueue):
                    #print("Queue : ", self.queue)
                    tempText =" ,".join(map(str,self.queue))
                    tempText = " QUEUE: " + tempText
                    #self.snq.write2Chat(tempText)
                    previousQueue = copy.deepcopy(self.queue)
                    
                    if myTurn2BuyGift == None:
                        myTurn2BuyGift = self.queue[0]
                        #print("Current turn : " + self.queue[0] + " pls buy patronage gifts now.")
                        tempText1 = "Current turn : " + self.queue[0] + " pls buy now. "
                        tempText1 = tempText1 + tempText
                        self.snq.write2Chat(tempText1)

                if self.snq.haveYouBoughtGift(myTurn2BuyGift, self.chatbook.chat) == True:
                    tempText = "done : " + self.queue[0]
                    self.patDone.append(self.queue[0])
                    self.queue.pop(0)
                    q.get() #multiprocess queue
                    temptime = dt.now().time()
                    temptime = str(temptime)
                    
                    print("From Main3: currentPatdbId: ", currentPatdbId)
                    backend.addPatDone(currentPatdbId,str(self.patDone[-1]), temptime)
                    print("ADDED TO PATDONE LIST")
                    myTurn2BuyGift = None
                    print(tempText)
                    self.snq.write2Chat(tempText)
                    



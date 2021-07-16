import numpy as np
import win32gui, win32ui, win32con
import pyautogui
from time import sleep
import cv2

class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    moeWindowHandle = [0,1]

    # constructor
    def __init__(self, window_name=None):

        top_windows = []
        win32gui.EnumWindows(self.windowEnumerationHandler, top_windows)
        #print(top_windows)
        
        for window in top_windows:
            moe = False
            pat = False
            if moe == False and 'march of empires' in window[1].lower():
                #print(window)
                #win32gui.ShowWindow(window[0],5)
                self.moeWindowHandle[0] = window[0]
                moe = True

            elif pat == False and 'patronage' in window[1].lower():
                self.moeWindowHandle[1] = window[0]
                pat = True
            
            elif moe == True and pat == True:
                break

        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)

    
    def windowEnumerationHandler(self, hwnd, top_windows):
        top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    


    def getChatbox(self):
        win32gui.SetForegroundWindow(self.moeWindowHandle[0])
        sleep(0.5)
        Chat = False
        chatLoc = None
        isSteam = False
        while(Chat==False):
            pyautogui.click(360,900)
            sleep(1)
            for img in ["chat.png","chatWin.png"]:
                if chatLoc != None:
                    isSteam = True
                    break
                chatLoc = pyautogui.locateOnScreen(img, region=(850,30,1080,100))
                

            if chatLoc != None:
                Chat = True
                allianceChatLoc = None
                while(allianceChatLoc==None):
                    for img in ["allianceChatInActive.png","allianceChatInActiveWin.png","allianceChatActive.png","allianceChatActiveWin.png"]:
                        allianceChatLoc = pyautogui.locateOnScreen(img, region=(5,100,1900,200))
                        if allianceChatLoc != None:
                            break

                pyautogui.click(allianceChatLoc)
                sleep(0.5)
                if isSteam == False:
                    pyautogui.click(150,985) #clicked on chatbox
                
                return True


            else:
                pyautogui.press('esc')
                sleep(0.5)
        
    def setPatManagerWindowForeground(self):
        win32gui.SetForegroundWindow(self.moeWindowHandle[1])

    def getImage(self):
        #screenshot = self.get_screenshot()
        #cv2.imwrite("temp/screenshot.png", screenshot)
        img = self.get_screenshot()
        #img = cv2.imread('temp/screenshot.png')
        #base_image = img.copy()
        height = img.shape[0]
        width = img.shape[1]

        height = height - 280
        width = width - 810
        image = img[200:200+height, 80:80+width] #y:y+h, x:x+w

        #cv2.imwrite("temp/screenshot2.png", image)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        adaptive_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50) #151 50
        #cv2.imwrite("temp/chat_adaptive_threshold.png", adaptive_threshold)
        return adaptive_threshold

    def isChatError(self):
        img2 = pyautogui.screenshot(region=(1340,915,500,35))
        img2.save(r'tempChatError2.png')
        image1 = cv2.imread('tempChatError.png')
        image2 = cv2.imread('tempChatError2.png')
        gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50) #151 50

        gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        image2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50) #151 50

        difference = cv2.subtract(image1,image2)
        aa = cv2.countNonZero(difference)
    
        if aa > 0:
            return False  #no chat error
        else:
            return True
import cv2
import mediapipe as mp
import time
import pickle
import numpy as np
import pyautogui
from tensorflow import keras



def main():
    left_click_flag = False
    right_click_flag = False
    left_dbl_click_flag = False
    left_arrow_flag = False
    right_arrow_flag = False
    scroll_down_count = 2
    scroll_up_count =2
    cod_x = ""
    cod_y = ""
    action = ""

    classes = {0:'pointer',1:'left_click',2:'right_click',3:'hold_drag',4:'left_dbl_click',5:'scrolldown',6:'scrollup',7:"right_arrow",8:"left_arrow"}

    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 90)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False,
                        max_num_hands=1,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5)

    mpDraw = mp.solutions.drawing_utils
    landmarks = ["WRIST","THUMB_CMC","THUMB_MCP","THUMB_IP","THUMB_TIP","INDEX_FINGER_MCP","INDEX_FINGER_PIP","INDEX_FINGER_DIP","INDEX_FINGER_TIP","MIDDLE_FINGER_MCP","MIDDLE_FINGER_PIP","MIDDLE_FINGER_DIP","MIDDLE_FINGER_TIP","RING_FINGER_MCP","RING_FINGER_PIP","RING_FINGER_DIP","RING_FINGER_TIP","PINKY_MCP","PINKY_PIP","PINKY_DIP","PINKY_TIP"]
    loaded_model = keras.models.load_model('./../models/DL_model_3.h5')
    screenWidth, screenHeight = pyautogui.size()
    #from tensorflow import keras
    #loaded_model = keras.models.load_model('./../models/DL_model.h5')

    while True:
        success, img = cap.read()
        width = cap.get(3)
        height = cap.get(4)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #cv2.rectangle(imgRGB, (int(width*0.1),int( height*0.1)), (int(width*0.9),int( height*0.9)),(0, 255, 0), 3)
        results = hands.process(imgRGB)
        lmlist = []

        row = []

        if not results.multi_hand_landmarks:
            #print(1)
            continue
                
        for hand_landmarks in results.multi_hand_landmarks:
            #print("\n")
            #print('hand_landmarks:', hand_landmarks)
            for land_mark in landmarks:
                row.append(hand_landmarks.landmark[mpHands.HandLandmark[land_mark]].x)
                row.append(hand_landmarks.landmark[mpHands.HandLandmark[land_mark]].y)
                row.append(hand_landmarks.landmark[mpHands.HandLandmark[land_mark]].z)
                #print(land_mark,hand_landmarks.landmark[mp_hands.HandLandmark[land_mark]].x,hand_landmarks.landmark[mp_hands.HandLandmark[land_mark]].y)
        inp_row = []
        inp_row.append(row)
        pred_action = loaded_model.predict(inp_row)
        predict_action = classes[np.argmax(pred_action)]
        #predict_action = pred_action
        print(predict_action)

        img = cv2.flip(img, 1)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                x_cod = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x
                x_cod *= 100000
                x_cod = int(x_cod)
                x_cod = float(x_cod/100000.0)
                y_cod = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y
                y_cod *= 100000
                y_cod = int(y_cod)
                y_cod = float(y_cod/100000.0)
                cod = "x: " + str(x_cod)
                cod += " y: " + str(y_cod)
                
                cv2.putText(img,cod, (10,100), cv2.FONT_HERSHEY_PLAIN, 2, (255,0,255), 3)
                cv2.putText(img,predict_action, (10,200), cv2.FONT_HERSHEY_PLAIN, 2, (255,0,255), 3)
                
                img = cv2.flip(img, 1)

                for id, lm in enumerate(handLms.landmark):
                    #print(id,lm)
                    h, w, c = img.shape
                    cx, cy = int(lm.x *w), int(lm.y*h)
                    lmlist.append([id, cx, cy])
                    #if id ==0:
                    cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)

                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                img = cv2.flip(img, 1)

        if (predict_action == 'hold_drag') :
            pyautogui.dragTo((1-x_cod)*screenWidth, y_cod*screenHeight, button='left')
            left_click_flag = False
            right_click_flag = False
            left_dbl_click_flag = False
            left_arrow_flag = False
            right_arrow_flag = False
            scroll_down_count = 2
            scroll_up_count =2

        elif (predict_action == 'left_click'):
            if(left_click_flag == False):
                pyautogui.click(button="left")
                left_click_flag = True
                right_click_flag = False
                left_dbl_click_flag = False
                left_arrow_flag = False
                right_arrow_flag = False
                scroll_down_count = 2
                scroll_up_count =2

        elif (predict_action == 'right_click'):
            if(right_click_flag == False):
                pyautogui.click(button= 'right')
                left_click_flag = False
                right_click_flag = True
                left_dbl_click_flag = False
                left_arrow_flag = False
                right_arrow_flag = False
                scroll_down_count = 2
                scroll_up_count =2

        elif predict_action == 'left_dbl_click':
            if(left_dbl_click_flag == False):
                pyautogui.doubleClick(button = "left")
                left_click_flag = False
                right_click_flag = False
                left_dbl_click_flag = True
                left_arrow_flag = False
                right_arrow_flag = False
                scroll_down_count = 2
                scroll_up_count =2

        elif predict_action == 'scrollup':
            scroll_up_count+=1
            pyautogui.scroll(100*int(scroll_up_count/2))
            left_click_flag = False
            right_click_flag = False
            left_dbl_click_flag = False
            left_arrow_flag = False
            right_arrow_flag = False
            scroll_down_count =2

        elif predict_action == 'scrolldown':
            scroll_down_count+=1
            pyautogui.scroll(-100*int(scroll_down_count/2))
            left_click_flag = False
            right_click_flag = False
            left_dbl_click_flag = False
            left_arrow_flag = False
            right_arrow_flag = False
            scroll_up_count=2

        elif predict_action == 'left_arrow':
            if(left_arrow_flag == False):
                pyautogui.press('right')
                left_click_flag = False
                right_click_flag = False
                left_dbl_click_flag = False
                left_arrow_flag = True
                right_arrow_flag = False
                scroll_down_count = 2
                scroll_up_count =2
    
        elif predict_action == 'right_arrow':
            if(right_arrow_flag == False):
                pyautogui.press('left')
                left_click_flag = False
                right_click_flag = False
                left_dbl_click_flag = False
                left_arrow_flag = False
                right_arrow_flag = True
                scroll_down_count = 2
                scroll_up_count =2

            #pyautogui.dragTo((1-x_cod)*screenWidth, y_cod*screenHeight, button='left')
        else :
            sizew = (1-x_cod)*screenWidth*1.1
            sizeh =  y_cod*screenHeight*1.1
            if(sizew >= screenWidth):
                sizew = (1-x_cod)*screenWidth
            if(sizeh>= screenHeight):
                sizeh = y_cod*screenHeight
            pyautogui.moveTo(sizew, sizeh)
            left_click_flag = False
            right_click_flag = False
            left_dbl_click_flag = False
            left_arrow_flag = False
            right_arrow_flag = False
            scroll_down_count = 2
            scroll_up_count =2

        
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime


        cv2.putText(img,str(int(cap.get(cv2.CAP_PROP_FPS))), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
        #flipped = cv2.flip(img, 1)
        cv2.imshow("Image",img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
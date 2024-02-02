import numpy as np
import cv2
import Cars
import time
#mendefinisikan input dan output
cnt_up   = 0
cnt_down = 0#Membuka video
cap = cv2.VideoCapture('highway.mp4')#Dimensi (properti) video
##cap.set(3,160) #Width
##cap.set(4,120) #Height#Meletakkan properti video ke setiap frame di video
for i in range(19):
    print(i), cap.get(i)
w = cap.get(3)
h = cap.get(4)
frameArea = h*w
areaTH = frameArea/500
print ('Area Threshold'), areaTH#Garis masuk dan keluar
line_up = int(1.85*(h/3))
line_down   = int(3*(h/4))
up_limit =   int(2.65*(h/5))
down_limit = int(3.5*(h/4))
print ("Red line y:"),str(line_down)
print ("Blue line y:"), str(line_up)
line_down_color = (255,0,0)
line_up_color = (0,0,255)
pt1 =  [0, line_down];
pt2 =  [w, line_down];
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_up];
pt4 =  [w, line_up];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))
pt5 =  [0, up_limit];
pt6 =  [w, up_limit];
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, down_limit];
pt8 =  [w, down_limit];
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))#Background subtractor
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = True)#Elemen struktural untuk filter morfologi
kernelOp = np.ones((3,3),np.uint8)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)#Variabel-variabel
font = cv2.FONT_HERSHEY_SIMPLEX
cars = []
max_p_age = 5
pid = 1
while(cap.isOpened()):#Membaca gambar dari aliran video
    ret, frame = cap.read()
    for i in cars:
        i.age_one() #tandai setiap mobil sebagai satu object#Tahap Pra-pengolahan    
    #Penerapan background subtractor
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)#Menggunakan metode binarisasi untuk menghilangkan bayangan (color ke grey)
    try:
        ret,imBin= cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
        ret,imBin2 = cv2.threshold(fgmask2,200,255,cv2.THRESH_BINARY)
  
        #Proses Opening (erosi->dilasi) untuk menghilangkan noise
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kernelOp)
  
        #Proses Closing (dilasi -> erosi) untuk menghilangkan pixel ke putih
        mask =  cv2.morphologyEx(mask , cv2.MORPH_CLOSE, kernelCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernelCl)
    except:
        print('EOF')
        print ('UP:'),cnt_up
        print ('DOWN:'),cnt_down
        break
    
#Pembuatan Kontur    
     
    contours, hierarchy = cv2.findContours(mask2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > areaTH:
    
            #   TRACKING 
            #Pengaturan untuk kondisi mobil yang jamak
   
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv2.boundingRect(cnt)
            new = True
            if cy in range(up_limit,down_limit):
                for i in cars:
                    if abs(cx-i.getX()) <= w and abs(cy-i.getY()) <= h:
                        
      #object dekat dengan object yang telah terdeteksi sebelumnya
                        new = False
                        i.updateCoords(cx,cy)   
      #perbaharui koordinat dalam object dalam atur ulang usia (awal penandaan)
                        if i.going_UP(line_down,line_up) == True:
                            cnt_up += 1;
                            print ("ID:"),i.getId(),'crossed going up at',time.strftime("%c")
                        elif i.going_DOWN(line_down,line_up) == True:
                            cnt_down += 1;
                            print ("ID:"),i.getId(),'crossed going down at',time.strftime("%c")
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
      #hapus object (mobil) dari daftar
                        index = cars.index(i)
                        cars.pop(index)
                        del i     #hapus dari memori
                if new == True:
                    p = Cars.MyCars(pid,cx,cy, max_p_age)
                    cars.append(p)
                    pid += 1     
            
            #Gambar
            
            cv2.circle(frame,(cx,cy), 5, (0,0,255), -1)
            img = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            
            #cv2.drawContours(frame, cnt, -1, (0,255,0), 3)
            
    #Akhir cnt dalam kontur
 
    
    # Trayektori Gambar 
    
    for i in cars:
        cv2.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv2.LINE_AA)
        str_up = 'Keluar: '+ str(cnt_up)
        str_down = 'Masuk: '+ str(cnt_down)
        frame = cv2.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
        frame = cv2.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
        frame = cv2.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
        frame = cv2.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
        cv2.putText(frame, str_up ,(15,40),font,0.5,(200,200,200),2,cv2.LINE_AA)
        cv2.putText(frame, str_up ,(15,40),font,0.5,(0,200,0),1,cv2.LINE_AA)
        cv2.putText(frame, str_down ,(15,60),font,0.5,(200,200,200),2,cv2.LINE_AA)
        cv2.putText(frame, str_down ,(15,60),font,0.5,(0,0,200),1,cv2.LINE_AA)
        cv2.imshow('Frame',frame)
        #cv2.imshow('Mask',mask)    
    
    #klik ESC untuk keluar
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
#Akhir untuk while(cap.isOpened())
    
#bersihkan layar
cap.release()
cv2.destroyAllWindows()
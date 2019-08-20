import cv2
import numpy as np
import sys

img = cv2.imread(sys.argv[1])
imgOriginalCopy = img.copy()
xCoord = []
yCoord = []
count = 0 #number of points
w,h = 0,0
startX, startY = 0,0

Coord = [] #four-coordinates of polygon

# mouse callback function
def draw_circle(event,x,y,flags,param):
    global count
    if event == cv2.EVENT_LBUTTONDOWN:
        if(count!=4):
            #cv2.circle(img,(x,y),2,(255,0,0),-1)
            xCoord.append(x)
            yCoord.append(y)
            Coord.append([x,y])
            count+=1
            print(count)
        elif(count==4):
            xCoord.clear()
            yCoord.clear()
            Coord.clear()
            print("Inside")
            print(Coord)
            count = 1
            xCoord.append(x)
            yCoord.append(y)
            Coord.append([x,y])
'''
        #Drawing reference lines
        if(count>1 and count<6):
            x1 = xCoord[count-2]
            y1 = yCoord[count-2]
            x2 = xCoord[count-1]
            y2 = yCoord[count-1]
            cv2.line(img,(x1,y1),(x2,y2),(255,0,0),2)
'''

def doCrop():
    global startX,startY
    coordArray = np.array(Coord)
    print(coordArray)

    #Find cropped image
    rect = cv2.boundingRect(coordArray)
    x,y,w,h = rect
    startX,startY = x,y
    cropped = imgOriginalCopy[y:y+h, x:x+w].copy()

    #Bringing cropped image co-ordainates back to the origin
    coordArray1 = coordArray
    for i in range(4):
        coordArray1[i][0]-=x
        coordArray1[i][1]-=y

    #Create mask
    croppedCopy = cropped.copy()
    croppedCopy[:] = (255)
    cv2.fillPoly(croppedCopy,[coordArray1],(0,0,0))

    #Apply mask
    global toPaint
    toPaint = cv2.add(cropped,croppedCopy)

    #Display
    #cv2.imshow('cropped',cropped)
    #cv2.imshow('croppedCopy',croppedCopy)
    #cv2.imshow('final',toPaint)

    doInpaint()

def doInpaint():
    global w,h, startX, startY
    original = toPaint.copy()

    gray = cv2.cvtColor(toPaint, cv2.COLOR_BGR2GRAY)
    imgCopy = gray.copy()
    imgCopy[:] = (0)

    #Invert colours
    inv = cv2.bitwise_not(gray)

    # create a CLAHE object (Arguments are optional).
    clahe = cv2.createCLAHE(clipLimit=30, tileGridSize=(6,6))
    cl1 = clahe.apply(inv)

    #Mask colour range
    #mask = cv2.inRange(cl1, 200, 255)

    #Median Blur
    blur = cv2.medianBlur(cl1, 15)

    #Bilateral Filter
    #blur = cv2.bilateralFilter(cl1,15,100,100)

    #Find circles
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 5, param1=30, param2=13, minRadius=5, maxRadius=10)

    j=0
    #Draw circles
    if circles is None:
        print("No circles found")
        #exit()
    else:
        for i in circles[0,:]:
            x = int(i[0])
            y = int(i[1])
            pixelValue = cl1[y,x]
            if pixelValue in range(160, 256, 1):
                #Inpaint
                cv2.circle(imgCopy,(i[0],i[1]),i[2],(255,255,255),-1)
                j+=1
                #cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),1)
                #cv2.putText(img,str(j), (i[0], i[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                #print(j,"  ",i[2],pixelValue)
        kernel = np.ones((5,5), np.uint8)
        dilation = cv2.dilate(imgCopy,kernel,iterations = 2)
        inpainted = cv2.inpaint(original, dilation, inpaintRadius=8, flags=cv2.INPAINT_TELEA)
        print("Number of circles: ",j)

        #cv2.imshow('Inpainted', inpainted)

        foreground = inpainted.copy()
        background = img.copy()
        mask = background.copy()
        mask2 = mask.copy()
        background2 = background.copy()

        h,w,c = foreground.shape
        h1,w1,c1 = background.shape

        coordArray = np.array(Coord)

        print("Inpaint coordinates",startX,startY)
        print("Foreground Shape",h,w)
        print("Background Shape",h1,w1)

        for i in range(h):
            for j in range(w):
                mask[startY+i,startX+j] = foreground[i,j]


        maskCopy = mask.copy()   
        maskCopy[:] = (255)
        cv2.fillPoly(maskCopy,[coordArray],(0,0,0))

        final = cv2.add(mask,maskCopy)

        mask2[:] = (0)
        cv2.fillPoly(mask2,[coordArray],(255,255,255))

        img[np.where(mask2 == 255)] = final[np.where(mask2 == 255)]

        #cv2.imshow('outImg', final)
        #cv2.imshow('outImg1', mask2)
        cv2.imshow('image', img)

        #doReplace()

'''
def doReplace():
    foreground = inpainted.copy()
    background = img.copy()
    mask = background.copy()
    mask2 = mask.copy()
    background2 = background.copy()

    h,w,c = foreground.shape

    for i in range(h):
        for j in range(w):
            mask[338+i,477+j] = foreground[i,j]


    Coord = [[477,338],[720,364],[723,480],[484,570]]
    coordArray = np.array(Coord)

    maskCopy = mask.copy()
    maskCopy[:] = (255)
    cv2.fillPoly(maskCopy,[coordArray],(0,0,0))

    final = cv2.add(mask,maskCopy)

    mask2[:] = (0)
    cv2.fillPoly(mask2,[coordArray],(255,255,255))

    background2[np.where(mask2 == 255)] = final[np.where(mask2 == 255)]

    cv2.imshow('outImg2', background2)
'''

#START
cv2.namedWindow('image')
cv2.setMouseCallback('image',draw_circle)

while(1):
    cv2.imshow('image',img)
    k = cv2.waitKey(20) & 0xFF
    if k == ord('q'):
        break
    elif k == ord('a'):
        #cv2.line(img,(xCoord[count-1],yCoord[count-1]),(xCoord[0],yCoord[0]),(255,0,0),2)
        doCrop()
cv2.destroyAllWindows()
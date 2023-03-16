import cv2
import numpy as np

def boxing(img):
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    median = cv2.medianBlur(thresh, 3)

    # Creating kernel
    kernel = np.ones((3, 3), np.uint8)
    
    # Using cv2.erode() method 
    erode = cv2.erode(median, kernel) 

    # Find contours and draw rectangle
    cnts = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    return cnts



def draw(img, cnts):

    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(img, (x-2, y-2), (x + w + 2, y + h + 2), (0, 255, 0), 2)
    cv2.imshow('image', img)
    cv2.waitKey()

# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
from interruptingcow import timeout

def welcome_msg(lcd):
    lcd.lcd_clear()
    lcd.lcd_display_string("Welcome to Demo", 1)

def verify_qrcode(lcd):
    # construct the argument parser and parse the arguments
    #ap = argparse.ArgumentParser()
    #ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
        #help="path to output CSV file containing barcodes")
    #args = vars(ap.parse_args())
    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    # vs = VideoStream(src=0).start()
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    # open the output CSV file for writing and initialize the set of
    # barcodes found thus far
    data = open("barcodes.csv", "r")
    found = set(data.read().split())
    barcode_found = False;
    welcome_msg(lcd)
    lcd.lcd_display_string("Show QR code", 2)
    counter = 0;
    #frame = vs.read()
    #frame = imutils.resize(frame, width=400)
    #cv2.imshow("Barcode Scanner", frame)
    
    #key = cv2.waitKey(1) & 0xFF
    # loop over the frames from the video stream
    while (counter < 5):
        try:
            with timeout(10, exception=RuntimeError):
                while (barcode_found == False):
                # grab the frame from the threaded video stream and resize it to
                # have a maximum width of 400 pixels
                    frame = vs.read()
                    frame = imutils.resize(frame, width=400)
    #                cv2.imshow("Barcode Scanner", frame)
                    # find the barcodes in the frame and decode each of the barcodes
                    barcodes = pyzbar.decode(frame)
                    
                # loop over the detected barcodes
                    for barcode in barcodes:
                        # extract the bounding box location of the barcode and draw
                        # the bounding box surrounding the barcode on the image
                        (x, y, w, h) = barcode.rect
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        # the barcode data is a bytes object so if we want to draw it
                        # on our output image we need to convert it to a string first
                        barcodeData = barcode.data.decode("utf-8")
                        barcodeType = barcode.type
                        # draw the barcode data and barcode type on the image
                        text = "{} ({})".format(barcodeData, barcodeType)
                        cv2.putText(frame, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        # if the barcode text is currently not in our CSV file, write
                        # the timestamp + barcode to disk and update the set
                        if barcodeData in found:
                            barcode_found = True;
                            break
                    cv2.imshow("Barcode Scanner", frame)
                    key = cv2.waitKey(1) & 0xFF
                break
        except RuntimeError:
            counter = counter + 1
            welcome_msg(lcd)
            lcd.lcd_display_string("Show QR code", 2)
            lcd.lcd_display_string("QR Match Fail", 3)
            lcd.lcd_display_string("Attempt" + str(counter), 4)
            pass
     
    # close the output CSV file do a bit of cleanup
    print("[INFO] cleaning up...")
    data.close()
    cv2.imshow("Barcode Scanner", frame)
    welcome_msg(lcd)
    lcd.lcd_display_string("Show QR code", 2)
    lcd.lcd_display_string("QR code Matched", 3)
    time.sleep(3)
    cv2.destroyAllWindows()
    vs.stop()
    return (barcode_found)
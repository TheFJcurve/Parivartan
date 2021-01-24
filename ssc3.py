import lcddriver
import motor
import hashlib
import gsm
from pyfingerprint.pyfingerprint import PyFingerprint
from smartcard.Exceptions import CardConnectionException, NoCardException
from smartcard.System import *
from smartcard import util
from cardstate import *
from time import *
from barcode import *
import RPi.GPIO as GPIO
from gpiozero import MotionSensor
from interruptingcow import timeout

COUNTER_FOR_SMS = 3

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Black
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Red
    lcd = lcddriver.lcd()
    return(lcd)
    
def welcome_msg(lcd):
    lcd.lcd_clear()
    lcd.lcd_display_string("Welcome to Demo", 1)
    
def warning_msg(lcd, e):
    lcd.lcd_clear()
    lcd.lcd_display_string("Welcome to Demo", 1)
    lcd.lcd_display_string(str(e), 2)
    lcd.lcd_display_string("Wait: Retrying", 3)
    
def error_msg(lcd, e):
    print('Operation failed!')
    print(str)
    lcd.lcd_clear()
    lcd.lcd_display_string("Welcome to Demo", 1)
    lcd.lcd_display_string(str(e), 2)
    lcd.lcd_display_string("Error:Reset System", 3)
    
def init_smart_card_reader(lcd):
    try:
        ret, context = get_reader_context()
        ret, readers = get_readers(context)
        while (ret == 0):
            welcome_msg(lcd)
            lcd.lcd_display_string("CardReader NotFound", 2)
            sleep(1)
            ret, readers = get_readers(context)
            if (ret == 1):
                lcd.lcd_clear()
                lcd.lcd_display_string("Welcome to Demo", 1)
                lcd.lcd_display_string("CardReader Found", 2)
                break;
        return(context, readers)
    except Exception as e:
        error_msg(lcd, e)
    exit(1)
    
def init_smart_card(lcd, context, readers):
    try:
        ret, state = get_card_state(context, readers)
        while True:
            if(ret == 5):
                welcome_msg(lcd)
                lcd.lcd_display_string("CardReader Found", 2)
                lcd.lcd_display_string("Insert your DL", 3)
                ret, state = wait_card_state_change(context, readers, state)
            elif(ret == 6):
                welcome_msg(lcd)
                lcd.lcd_display_string("CardReader Found", 2)
                lcd.lcd_display_string("DL Found", 3)
                sleep(3)
                break
        return(state)
    except Exception as e:
        error_msg(lcd, e)
        pass
def wait_new_smart_card(lcd, context, readers, state):
    try:
        ret, state = wait_card_state_change(context, readers, state)
        while True:
            if(ret == 5):
                welcome_msg(lcd)
                lcd.lcd_display_string("CardReader Found", 2)
                lcd.lcd_display_string("Insert your DL", 3)
                ret, state = wait_card_state_change(context, readers, state)
            elif(ret == 6):
                welcome_msg(lcd)
                lcd.lcd_display_string("CardReader Found", 2)
                lcd.lcd_display_string("DL Found", 3)
                sleep(2)
                break
        return(state)
    except Exception as e:
        error_msg(lcd, e)
        pass

def init_fp(lcd):
    while True:
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
            if ( f.verifyPassword() == False ):
                print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
                raise Exception('FP password wrong!')
                break
            else:
                break
        except Exception as e:
            print("Some issue with FP sendor, trying again")
            warning_msg(lcd, e)
            pass
    return(f)

def read_fp_sensor(lcd, f):
    while ( f.readImage() == False ):
        pass
    f.convertImage(0x01)
    ## Searchs template
    result = f.searchTemplate()

    positionNumber = result[0]
    accuracyScore = result[1]
    return(positionNumber, accuracyScore)
        
def verify_fp_from_sensor(lcd, f):
    counter = 0
    while True:
        positionNumber, accuracyScore = read_fp_sensor(lcd, f)
        if ( positionNumber == -1 ):
                counter = counter + 1
                print('fp fail count is:' + str(counter))
                welcome_msg(lcd)
                lcd.lcd_display_string("Pls dont remove DL", 2)
                lcd.lcd_display_string('No match ' + str(counter), 3)
                lcd.lcd_display_string('Try again',4)
                sleep(3)
                global COUNTER_FOR_SMS
                if (counter > COUNTER_FOR_SMS):
                    print("sending sms")
                    gsm.sendsms('ALERT: THEFT THREAT FOR CAR HR26 CP 1234')
                    counter = 0
                #for i in range(1,5):
                 #   sleep (1)
                  #  welcome_msg(lcd)
                   # lcd.lcd_display_string("Pls dont remove DL", 2)
                    #lcd.lcd_display_string('No match ' + str(counter), 3)
                    #lcd.lcd_display_string('Try after 5 secs' + str(i+1), 4)
        else:
            break
    return(positionNumber, accuracyScore)

def read_verify_dl(lcd, f, positionNumber):
    while True:
        try:
            fp_card = read_fp_from_card()
        except Exception as e:
            lcd.lcd_clear()
            lcd.lcd_display_string("Welcome to Demo", 1)
            lcd.lcd_display_string("FP Matched-1", 2)
            lcd.lcd_display_string('DL Not found', 3)
            lcd.lcd_display_string('Pls insert DL', 4)
            pass            
                #f.uploadCharacteristics(0x01, fp_card)
        f.loadTemplate(positionNumber, 0x01)
        characterics = f.downloadCharacteristics(0x01)
        print(positionNumber)
        print(characterics)
        print('--------')
        print(fp_card)
        f.uploadCharacteristics(0x02, fp_card)
        result = f.compareCharacteristics()
        break
    return(result)

def drive(lcd):
    try:
        f = init_fp(lcd)
        welcome_msg(lcd)
        lcd.lcd_display_string("Smart DL: Push Black", 2)
        lcd.lcd_display_string("QRCode: Push Red", 3)
        drive_enable = False
        while True:
           button_state_dl = GPIO.input(17)
           button_state_qr = GPIO.input(27)
           
           if button_state_dl == GPIO.HIGH:
                context, readers = init_smart_card_reader(lcd)
                state = init_smart_card(lcd, context, readers)
                lcd.lcd_display_string("Pls dont remove DL", 2)
                lcd.lcd_display_string('Place your finger..', 3)
                positionNumber, accuracyScore = verify_fp_from_sensor(lcd, f)
                welcome_msg(lcd)
                lcd.lcd_display_string("Pls dont remove DL", 2)
                lcd.lcd_display_string('FingerPrint Matched-1', 3)
                lcd.lcd_display_string('Verifying DL', 4)
                sleep(3)
                result = read_verify_dl(lcd, f, positionNumber)
                if ( result == 0 ):
                    welcome_msg(lcd)
                    lcd.lcd_display_string("FP Matched-1", 2)
                    lcd.lcd_display_string('DL check Fail', 3)
                    lcd.lcd_display_string('Pls insert valid DL', 4)
                    print("No match for DL")
                    state = wait_new_smart_card(lcd, context, readers, state)
                    #sleep(5)
                    execfile("ssc3.py")
                else:
                    print('Found template at position #' + str(positionNumber))
                    print('The accuracy score is: ' + str(accuracyScore))
                    drive_enable = True
                    break;
           elif button_state_qr == GPIO.HIGH:
              welcome_msg(lcd)
              lcd.lcd_display_string('Place your finger..', 2)
              positionNumber, accuracyScore = verify_fp_from_sensor(lcd, f)
              welcome_msg(lcd)
              lcd.lcd_display_string("FP - Matched", 2)
              sleep(2)                
              #lcd.lcd_display_string("Show QR code", 2)
              #sleep(1)
              result = verify_qrcode(lcd)
              if (result == False):
                  welcome_msg(lcd)
                  lcd.lcd_display_string("QR Code Match Fail", 2)
                  lcd.lcd_display_string("QR Code Attempts Over", 3)
                  sleep(10)
                  execfile(ssc3.py)
              else:
                  print('QR code match')
                  drive_enable = True
                  break;
        if drive_enable == True:
            welcome_msg(lcd)
            lcd.lcd_display_string("Wishing Safe Driving", 2)
            lcd.lcd_display_string("push red to stop", 3)
            sleep(1)
            motor.init()
            pir = MotionSensor(23)
            while True:
                motor.right(1)
                button_state_stop = GPIO.input(27)
                if button_state_stop == GPIO.HIGH:
                    #motor.cleanup()
                    welcome_msg(lcd)
                    lcd.lcd_display_string("Car Stopped", 2)
                    lcd.lcd_display_string("Motion: Push Red", 3)
                    lcd.lcd_display_string("Exit: Push black", 4)
                    break
            counter = 0
            motion_detect = False;
            while True:
                button_state_exit = GPIO.input(17)
                button_state_pir = GPIO.input(27)
                if button_state_exit == GPIO.HIGH:
                    welcome_msg(lcd)
                    lcd.lcd_display_string("Demo Over", 2)
                    exit(1)
                elif button_state_pir == GPIO.HIGH or motion_detect:
                    if motion_detect == False:
                        welcome_msg(lcd)
                        lcd.lcd_display_string("Motion Detect Started",2)
                        motion_detect = True
                    try: 
                        with timeout(1, exception=RuntimeError):
                            pir.wait_for_motion()
                            counter = counter + 1
                            if counter > 2000:
                                lcd.lcd_display_string("SMS sent", 3)
                                gsm.sendsms('ALERT: Someone Locked in Car No: 1234');
                                pass
                    except RuntimeError:
                        counter = 0
                        pass
                    print("Motion detected!")
                    #sleep(2)
    except Exception as e:
            GPIO.setmode(GPIO.BCM)
            print(e)
            #motor.cleanup()
            GPIO.cleanup()
            error_msg(lcd, e)
def enroll_car(lcd):
    try:
        counter = 0
        f = init_fp(lcd)
        while True:
            welcome_msg(lcd)
            lcd.lcd_display_string("Owner verification", 2)
            lcd.lcd_display_string("Place Finger", 3)
            positionNumber, accuracyScore = read_fp_sensor(lcd, f)
            if(positionNumber == -1):
                counter = counter + 1
                lcd.lcd_display_string("Verification fail", 4)
                sleep(4)
                global COUNTER_FOR_SMS
                if(counter > COUNTER_FOR_SMS):
                    gsm.sendsms('ALERT: THEFT THREAT FOR CAR HR26 CP 1234');
                    return
            else:
                break
        welcome_msg(lcd)
        lcd.lcd_display_string("Owner verification", 2)
        lcd.lcd_display_string("Verify Success", 3)
        sleep(4)
        while True:
            welcome_msg(lcd)
            lcd.lcd_display_string("Place FP to enroll", 2)
            positionNumber, accuracyScore = read_fp_sensor(lcd, f)
            if ( positionNumber >= 0 ):
                print('Template already exists at position #' + str(positionNumber))
                welcome_msg(lcd)
                lcd.lcd_display_string("Already Enrolled ", 2)
                sleep(3)
                welcome_msg(lcd)
                lcd.lcd_display_string("Enroll DL:Push Black", 2)
                lcd.lcd_display_string("Main Menu: Push Red", 3)
                sleep(5)
                while True:    
                    button_state_dl_enroll = GPIO.input(17) #car
                    button_state_menu = GPIO.input(27) #dl
                    if button_state_dl_enroll == GPIO.HIGH:
                        enroll_dl(lcd, f, positionNumber)
                        break
                    elif button_state_menu == GPIO.HIGH:
                        break
                break
            else:
                welcome_msg(lcd)
                lcd.lcd_display_string("Remove Finger", 2)
                sleep(4)
                welcome_msg(lcd)
                lcd.lcd_display_string("Waiting same finger", 2)
                print('Waiting for same finger again...')
                ## Wait that finger is read again
                while ( f.readImage() == False ):
                    pass
                ## Converts read image to characteristics and stores it in charbuffer 2
                f.convertImage(0x02)
                sleep(1)
                ## Compares the charbuffers
                if ( f.compareCharacteristics() == 0 ):
                    lcd.lcd_display_string("Mismatch", 3)
                    lcd.lcd_display_string("Try Again", 4)
                    sleep(4)
                else:
                    ## Creates a template
                    f.createTemplate()
                    ## Saves template at new position number
                    positionNumber = f.storeTemplate()
                    print('Finger enrolled successfully!')
                    lcd.lcd_display_string("Enrolled", 3)
                    print('New template position #' + str(positionNumber))
                    sleep(5)
                    welcome_msg(lcd)
                    lcd.lcd_display_string("Enroll DL:Push Black", 2)
                    lcd.lcd_display_string("Main Menu: Push Red", 3)
                    while True:    
                        button_state_dl_enroll = GPIO.input(17) #car
                        button_state_menu = GPIO.input(27) #dl
                        if button_state_dl_enroll == GPIO.HIGH:
                            enroll_dl(lcd, f, positionNumber)
                            break
                        elif button_state_menu == GPIO.HIGH:
                            break
                    break
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        pass
    
def enroll_dl(lcd, f, positionNumber):
    try:
        welcome_msg(lcd)
        lcd.lcd_display_string("Wait, Enrolling", 2)
        f.loadTemplate(positionNumber, 0x01)
        #characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
        characterics = f.downloadCharacteristics(0x01)
        print(characterics)
        write_fp_to_card(characterics)
        welcome_msg(lcd)
        lcd.lcd_display_string("Enrolled", 2)
        sleep(3)
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        pass

def main():
    try:
        lcd = init()
        while True:
            welcome_msg(lcd)
            lcd.lcd_display_string("Enroll: Push Black", 2)
            lcd.lcd_display_string("Drive: Push Red", 3)
            while True:
                button_state_enroll = GPIO.input(17)
                button_state_drive = GPIO.input(27)
                if button_state_drive == GPIO.HIGH:
                    drive(lcd)
                    break
                elif button_state_enroll == GPIO.HIGH:
                    enroll_car(lcd)
                    sleep(1)
                    break
                    
    except Exception as e:
            print(e)
            GPIO.cleanup()
            error_msg(lcd, e)
    
if __name__== "__main__":
  main()

from __future__ import print_function
from smartcard.scard import *
import smartcard.util
from time import *
from smartcard.Exceptions import CardConnectionException, NoCardException
from smartcard.System import *
from smartcard import util

srTreeATR = \
    [0x3B, 0x77, 0x94, 0x00, 0x00, 0x82, 0x30, 0x00, 0x13, 0x6C, 0x9F, 0x22]
srTreeMask = \
    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
CLA = 0x90
INS = 0xB8
P1 = 0x00
P2 = 0x00
LE = 0x07
# apdu chip info apdu
CHIP_INFO = [CLA, INS, P1, P2, LE]

def printstate(state):
    reader, eventstate, atr = state
    print(reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX))
    if eventstate & SCARD_STATE_ATRMATCH:
        print('\tCard found')
        return(1)
    if eventstate & SCARD_STATE_UNAWARE:
        print('\tState unware')
        return(2)
    if eventstate & SCARD_STATE_IGNORE:
        print('\tIgnore reader')
        return(3)
    if eventstate & SCARD_STATE_UNAVAILABLE:
        print('\tReader unavailable')
        return(4)
    if eventstate & SCARD_STATE_EMPTY:
        print('\tReader empty')
        return(5)
    if eventstate & SCARD_STATE_PRESENT:
        print('\tCard present in reader')
        return(6)
    if eventstate & SCARD_STATE_EXCLUSIVE:
        print('\tCard allocated for exclusive use by another application')
        return(7)
    if eventstate & SCARD_STATE_INUSE:
        print('\tCard in used by another application but can be shared')
        return(8)
    if eventstate & SCARD_STATE_MUTE:
        print('\tCard is mute')
        return(9)
    if eventstate & SCARD_STATE_CHANGED:
        print('\tState changed')
        return(10)
    if eventstate & SCARD_STATE_UNKNOWN:
        print('\tState unknowned')
        return(11)
        
def get_reader_context():
    hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
    if hresult != SCARD_S_SUCCESS:
        print('Failed to establish context: ' + \
              SCardGetErrorMessage(hresult))
        return (0, 0)
    print('Context established!')
    
    return (1, hcontext)

def get_readers(hcontext):
    hresult, readers = SCardListReaders(hcontext, [])
    if hresult != SCARD_S_SUCCESS:
        print ('Failed to list readers: ' + \
                    SCardGetErrorMessage(hresult))
        return (0, 0)
    print('PCSC Readers:', readers)
    return (1, readers)

def get_card_state(hcontext, readers):
    readerstates = []
    for i in range(len(readers)):
        readerstates += [(readers[i], SCARD_STATE_UNAWARE)]
    hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
    for i in newstates:
        ret = printstate(i)
    return (ret, newstates)

def wait_card_state_change(hcontext, readers, newstates):
    print('----- Please insert or remove a card ------------')
    hresult, newstates = SCardGetStatusChange(
                              hcontext,
                              INFINITE,
                              newstates)

    print('----- New reader and card states are: -----------')
    for i in newstates:
        ret = printstate(i)
        return(ret, newstates)
    
def release_context(hcontext):
    hresult = SCardReleaseContext(hcontext)
    if hresult != SCARD_S_SUCCESS:
        print(
                'Failed to release context: ' + \
                SCardGetErrorMessage(hresult))
        return(0)
    print('Released context.')
    return(1)

def read_fp_from_card():
    sc_readers = readers()
    print(sc_readers)
    # create a connection to the first reader
    first_reader = sc_readers[0]
    connection = first_reader.createConnection()

    # get ready for a command
    get_uid = util.toBytes("FF 20 00 00 02 FF FF")
    
    try:
        # send the command and capture the response data and status
        connection.connect()
        data, sw1, sw2 = connection.transmit(get_uid)

        # print the response
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))
        
        read_payload = []
        
        for i in range (0, 512, 64):
            
            read_command = [0xFF, 0xB0, i/64, 0x00, 0x40]
            #get_uid = util.toBytes("FF B0 00 00 40")
            data, sw1, sw2 = connection.transmit(read_command)
            read_payload = read_payload + data
            print("UID = {}\tstatus = {}".format(util.toHexString(data), util.toHexString([sw1, sw2])))
        print (read_payload)
        return read_payload
    except NoCardException:
        print("ERROR: Card not present")
        raise Exception("ERROR: Card not present")
    
def erase_card(connection):
    try:
        write_command = [0xFF, 0x0E, 0x80, 0x00]
        payload = write_command 
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

            
        write_command = [0xFF, 0x0E, 0x81, 0x00]
        payload = write_command 
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))


        write_command = [0xFF, 0x0E, 0x82, 0x00]
        payload = write_command 
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0x0E, 0x83, 0x00]
        payload = write_command 
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0x0E, 0x84, 0x00]
        payload = write_command 
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0x0E, 0x85, 0x00]
        payload = write_command 
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

            
        write_command = [0xFF, 0x0E, 0x86, 0x00]
        payload = write_command 
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0x0E, 0x87, 0x00]
        payload = write_command 
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))
    except NoCardException:
        print("ERROR: Card not present")

def write_card(connection, characterics):
    try:
        write_command = [0xFF, 0xD0, 0x80, 0x00, 0x40]
        payload = write_command + characterics[0:64]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

            
        write_command = [0xFF, 0xD0, 0x81, 0x00, 0x40]
        payload = write_command + characterics[64:128]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))


        write_command = [0xFF, 0xD0, 0x82, 0x00, 0x40]
        payload = write_command + characterics[128:192]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0xD0, 0x83, 0x00, 0x40]
        payload = write_command + characterics[192:256]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0xD0, 0x84, 0x00, 0x40]
        payload = write_command + characterics[256:320]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0xD0, 0x85, 0x00, 0x40]
        payload = write_command + characterics[320:384]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

            
        write_command = [0xFF, 0xD0, 0x86, 0x00, 0x40]
        payload = write_command + characterics[384:448]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))

        write_command = [0xFF, 0xD0, 0x87, 0x00, 0x40]
        payload = write_command + characterics[448:512]
        print(payload)
        data, sw1, sw2 = connection.transmit(payload)
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status)) 
            
            
        read_payload = []
            
        read_command = [0xFF, 0xB0, 0x80, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
            
        read_command = [0xFF, 0xB0, 0x81, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
            
        read_command = [0xFF, 0xB0, 0x82, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
          
        read_command = [0xFF, 0xB0, 0x83, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
            
        read_command = [0xFF, 0xB0, 0x84, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
            
        read_command = [0xFF, 0xB0, 0x85, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
            
        read_command = [0xFF, 0xB0, 0x86, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
            
        read_command = [0xFF, 0xB0, 0x87, 0x00, 0x40]
        data, sw1, sw2 = connection.transmit(read_command)
        read_payload = read_payload + data
            
                # print the response
        print(read_payload)        

    except NoCardException:
        print("ERROR: Card not present")

def write_fp_to_card(write_payload):
    sc_readers = readers()
    print(sc_readers)
    # create a connection to the first reader
    first_reader = sc_readers[0]
    connection = first_reader.createConnection()

    # get ready for a command
    get_uid = util.toBytes("FF 20 00 00 02 FF FF")
    
    try:
        # send the command and capture the response data and status
        connection.connect()
        data, sw1, sw2 = connection.transmit(get_uid)

        # print the response
        uid = util.toHexString(data)
        status = util.toHexString([sw1, sw2])
        print("UID = {}\tstatus = {}".format(uid, status))
        erase_card(connection)
        write_card(connection, write_payload)
    except Exception as e:
        print(e)
        print("Operation Failed")
    

class MustBeEvenException(Exception):
    pass

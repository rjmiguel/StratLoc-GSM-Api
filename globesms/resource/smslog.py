"""
SMS Data Collector 1.0
(c) Roland Jay Miguel
StratLoc Corporation
Brief Description:
This program logs SMS Messages to a CSV file
Operator messages are automatically ignored
"""
from __future__ import with_statement
import time
import re
import serial
import os
import ConfigParser

offline = False
gsm_wait = 5
modem_port = 0
sleeptime = 10
deletemsg = True
debug = True
directory = "./SMSLog"


def modem_read():
    """
    Waits for complete response from GSM modem.
    Usage: str = gsmreply()
    """
    a = modem.read(modem.inWaiting())
    now = time.time()
    while a.find('\r\nOK\r\n')<0 and a.find('\r\nERROR\r\n')<0 and \
            a.find('\r\n+CMS ERROR: 500\r\n')<0 and time.time() < now+10:
        a = a + modem.read(modem.inWaiting())
        time.sleep(0.5)
        if time.time()>now+10:
            a='ERROR'
    return a

def modem_write(command):
     """
     sends a command to the modem
     """
     modem.write(command)
     a = modem_read()
     return a

def modem_close():
     """
     closes the serial port where the modem is attached
     """
     modem.close()

def modem_setup():
     """
     initialization routine for the modem
     """
     reply = ''
     trial = 0

     while trial < 3:
         modem.write("ATE0\r")
         reply = modem_read()
         print reply
         if reply.find("OK") >= 0:
              print "Turned echo off"
              trial = 3
         else:
              print "Turn echo off Failed"
              print '\a'
              trial = trial + 1
              time.sleep(1)
     trial = 0
     while trial < 3:
         modem.write("AT+CMGF=1\r")
         print "AT+CMGF=1\r"
         reply = modem_read()
         print reply
         if reply.find("OK") >= 0:
              print "Turned to text mode"
              trial = 3
         else:
              print "Text mode on Failed"
              print '\a'
              trial = trial + 1
              time.sleep(1)
     #modem.read(modem.inWaiting())

def modem_readmsg():
    modem.write('AT+CMGL="ALL"\r')
    time.sleep(3)
    allmsgs = modem_read()
    print allmsgs
    allmsgs = allmsgs.rsplit("+CMGL")[1].split("\r\n",1)
    # remove the "OK" at the end of the modem's reply"
    allmsgs[1] = allmsgs[1].rsplit("\r\n", 3)[0]
    #sender = re.search(r'"(\+?\d+)"',allmsgs[0]).group(1)
    sender = allmsgs[0].split(",")[2]
    #date_sent = allmsgs[0].split(",")[4].strip('"')
    #time_sent = allmsgs[0].split(",")[5].strip('"')
    date_sent = time.strftime("%Y%m%d")
    time_sent = time.strftime("T%H:%M:%S")
    
    if allmsgs[1][0]=='\x82':  # is it a multipart message?
        time.sleep(5)  # wait for all the parts to come in
        modem_write('AT+CMGL="ALL"\r')
        allmsgs = modem_read()
        # remove preamble and tail
        allmsgs = allmsgs.splitlines()[1:-2]
        msg = ''
        # string together all multipart messages from the same sender
        #  - assume parts of a message are in proper order already
        while len(allmsgs)>0:
            #thisnum = re.search(r'"(\+?\d+)"',allmsgs[0]).group(1)
            if  thisnum==sender and allmsgs[1][0]=='\x82':
                msg += allmsgs[1][7:]
                if deletemsg:
                    #delete the message after reading it
                    d = 'at+cmgd=' + re.search(r'\d+',allmsgs[0]).group(0) + '\r'
                    #print d
                    modem.write(d)
                    print 'Deleting recieved message... ', modem_read().strip()                
            del allmsgs[0:2]
    else:
        msg = allmsgs[1]
        if deletemsg:
            a = modem_read()
            d = 'at+cmgd=' + re.search(r'\d+',allmsgs[0]).group() + '\r'
            #print d
            modem.write(d)
            print 'Deleting recieved message... ', modem_read().strip()                
    print 'Sender:',sender
    print 'Msg:',msg
    return (sender, date_sent, time_sent, msg)
     
def modem_sendmsg(celnum,txt):
    while True:
        modem.write('AT+CMGS="' + celnum + '"\r')
        time.sleep(1)
        reply = modem.read(modem.inWaiting())
        if reply.find('>') < 0:
            print 'Error sending sms'
        else:
            modem_write(txt + '\x1a')
            sendstatus = modem_read()
            if sendstatus.find('ERROR')<0:
                print 'Message sent : ',celnum, " , ", sendstatus
                time.sleep(2)
                return 0
            else:
                print 'Error sending..retrying..'
                time.sleep(5)
                print modem_read()
    return 0

def modem_delmsg(index):
     """
     deletes the message identified by index
     """
     reply = ''
     modem.write("AT+CMGD=" + repr(index) + "\r")
     reply = modem_read()
     return reply

def get_sender_num(msg):
     """
     Get the number of the sender given the actual reply of the gsm modem
     """
     return msg.split(",")[2]

def get_msg_index(msg):
     """
     returns the index number of the message read
     """
     return msg[0][0]

def modem_procmsg():
     """
     Process only the message with the lowest index
     msgs[0] : headers for the message
     msgs[1] : actual message
     """
     #read the messages
     msgs = modem_readmsg()
     if msgs == '' : #in case the modem timed out
          return ''
     
     msgs = msgs.strip("\r\n+CMGL: ").strip('\r\nOK').split('\r\n')
     print "Sender : " , get_sender_num(msgs[0]) #message with the lowest index
     print "Index: ", get_msg_index(msgs[0])

     if deletemsg:
          modem_delmsg( get_msg_index(msgs[0]) )
     return msgs[:2]
     #check for multiparts
     #assemble multiparts

def modem_msgcount():
     """
     counts the number of messages in the sim
     """
     reply = ''
     modem.write('AT+CPMS?\r')
     reply = modem_read()
     try:
          reply = int(reply.strip('\r\n+CPMS: ').split(",")[1])
          return reply
     except:
          return 0

def writelog(logfile, sender, time, data, comments):
    if not os.path.isdir(directory + "/"):
    	os.mkdir(directory)    
    FILE = open(directory + "/" + logfile + ".csv", "a+")
    FILE.writelines(sender + "," + time + "," + data + "," + comments + "\n")
    FILE.close()

def getdir():
    i = 0
    dir_name = list()
    directory = os.getcwd()
    try :
        with open(directory + "/SMS/smsdirectory.txt") as f:
            for line in f:            
                if len(line.strip()) > 0:
                    dir_name.insert(i,line.strip())
                i = i + 1
        f.close()
        return dir_name
    except :
        return list()

def getmsg():
    try:
        msg = ""
        directory = os.getcwd()
        with open(directory +  "/SMS/smsque.txt") as f:
            for line in f:
                msg = msg + line
        print "Message pending found : ", msg
        f.close()
        return msg
    except:
        #print "There is no message on que"
        return False

def delqueue():
    try:
        directory = os.getcwd()
        os.remove(directory +  "/SMS/smsque.txt")
        print "Message queue deleted. Alert message sent."
    except:
        print "Delete queue failed"

def sendalert():
    msg = getmsg()
    recipient = getdir()
    if (msg != False) and (len(recipient) > 0):
        for celnum in recipient:
            modem_sendmsg(celnum, msg)
            time.sleep(3)
        delqueue()
    
def modem_poweron():
    power = 0
    counter = 0

    modem.setDTR(1)
    time.sleep(0.2)
    modem.setDTR(0)
    time.sleep(0.2)
    modem.setDTR(1)
    print modem.read(modem.inWaiting())    
    while ((power == 0) and (counter < 5)):
        
        time.sleep(2)
        modem.write("AT\r")
        time.sleep(1)
        reply = modem_read()
        print reply
        if reply.find("OK") >= 0:
            print "Power on ok"
            power = 1
            return 1
        else:
            print "Power on error"
            counter = counter + 1
            print '\a'
    print "modem error."
    return 0

def modem_signal():
    modem.write("AT+CSQ\r")
    signal = modem_read()
    signal = signal.strip("\r\n+CSQ: ").split("\r\n")
    return int(signal[0].split(',')[0])

"""
some startup routines
"""
if offline == False :
    #try:
    #modem = serial.Serial(modem_port,baudrate=57600,timeout=5)
    modem = serial.Serial('/dev/ttyS0',baudrate=38400,timeout=5)
    modem.open()
    time.sleep(1)
    power = modem_poweron()
    if (power == 0):
        print "Could not find modem"
        print "\a\a\a"
        time.sleep(5)
    else:
        print "Initializing ... "
        print "\a"
        time.sleep(1)
        modem_setup()          
        #sms_main()
    #except:
        #print "serial port error"
        #print "\a\a\a"
        #time.sleep(5)

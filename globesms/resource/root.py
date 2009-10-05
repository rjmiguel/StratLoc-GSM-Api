import logging
from restish import http, resource
import wsgiref.handlers

import time, subprocess, random
from threading import Thread
from smslog import modem_readmsg, modem_sendmsg


callback = http://127.0.0.1:8080
log = logging.getLogger(__name__)
gsmlock = False

class Root(resource.Resource):
    @resource.GET()
    def html(self, request):
        return http.ok([('Content-Type', 'text/html')],
            "<p>StratLoc SMS Gateway</p>")

    @resource.child()
    def gsms(self, request, segments):
        return gsms()

class gsms(resource.Resource):
    global gsmlock

    @resource.GET()
    def html(self, request):
        return http.ok([('Content-Type', 'text/html')],
            "<p>StratLoc SMS Gateway</p>")

    @resource.POST()
    def post(self, request):
	data = request.POST
	try:
		print "uname:" , data['uName']
		print "uPin:" , data['uPin']
		print "MSISDN:" , data['MSISDN']
		print "messageString:" , data['messageString']
		#print "Display:", data['Display']
		#print "udh:", data['udh']
		#print "mwi:", data['mwi']
		#print "coding:", data['coding']
		if str.isdigit(data['MSISDN']) == False:
			print "Bad MSISDN : " , data['MSISDN']
			callback(data['uName'], "STRATLOC")
			return http.ok([('Content-Type', 'text/html')], "<return>501</return>")
		print "----------------------------------------"
		#wait until modem becomes available
		print "Lock : " , gsmlock		
		if (gsmlock == True):
			print "waiting for modem to become available"
			while (gsmlock == True):
				pass
		modem_sendmsg(data['MSISDN'] , data['messageString'])
        	return http.ok([('Content-Type', 'text/html')], "<return>201</return>")
	except:
		return http.ok([('Content-Type', 'text/html')], "<return>506</return>")

#Thread that checks for SMS
def SMSChecker():
    global gsmlock
    while 1:
	print "now checking for new sms..."
	gsmlock = True
    	time.sleep(20)
        while (modem_msgcount() > 0):
            try:
                sender, date_sent, time_sent, msg = modem_readmsg()
            except:
                pass    
            if len(sender) < 11:
                print "operator message detected ... deleting"
	    else:
                writelog('others', sender, time_sent, "0", msg)
		ReportSMS(sender, msg)
            print "wrote to file.."
        time.sleep(sleeptime)
	gsmlock = False

#Send reply to the callback handler
def SMSCallBack(source, target):
    reply = '<?xml version="1.0" encoding="utf-8"?><message><param><name>messageType</name><value>SMS-NOTIFICATION</value>\
</param><param><name>source</name><value>'+source+"</value></param><param><name>type</name><value>1</value>\
</param><param><name>msg</name><value>Message for "+target+", has been delivered on "+time.strftime("%D - %H:%M")+"</value>\
</param><param><name>target</name><value> "+target+"</value></param></message>"

    #return reply
    post = subprocess.Popen(["curl", "-X", "POST", "-d" , reply , callback],stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    out, error = post.communicate()
    print out

def ReportSMS(source, msg):
    reply = '<?xml version="1.0" encoding="utf-8"?><message><param><name>messageType</name><value>SMS</value>\
</param><param><name>id</name><value>none</value></param><param><name>source</name><value>'& source &'</value>\
</param><param><name>target</name><value>STRATLOC</value></param><param><name>msg</name><value>'& msg &'</value>\
</param><param><name>udh</name><value></value></param></message>'
    post = subprocess.Popen(["curl", "-X", "POST", "-d" , reply , callback],stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    out, error = post.communicate()
    print out

#This will start the sms checker thread
t = Thread(target=SMSChecker)
t.start()


import time
import pyb
import gc

show_debug=False

def setDebug(on):
	global show_debug
	show_debug=on

#File i/o Helper
def isFile(filename):
	try:
		if(len(filename)>0):
			d=open(filename,'r')
			d.close()
			return True
		return False
	except:
		return False

#Socket Helper
def writeHeader(csocket,status,Contenttype):
	csocket.send(status)
	csocket.send('\n')
	csocket.send('Server: pyboard\n')
	csocket.send('Content-Type: ')
	csocket.send(Contenttype)
	csocket.send('\n')
	csocket.send('CacheControl: no-cache\n')
	csocket.send('Connection: close\n') #close   Keep-Alive
	csocket.send('\n')

def WriteHTMLHead(csocket,data,stitel):
	csocket.send('<!DOCTYPE html>\n')
	csocket.send('<head>\n')
	csocket.send(' <title>')
	csocket.send(stitel)
	csocket.send('</title>\n')
	csocket.send(' <meta http-equiv="content-type" content="text/html; charset=UTF-8">\n')
	csocket.send('<style>p{margin:0;}</style>\n')
	csocket.send('</head>\n')

def WriteDefaultPage(csocket,data):
	import pyb
	WriteHTMLHead(csocket,data,'pyboardserver')
	csocket.send('<body>\n')
	csocket.send('<h1>Hello</h1>\n')
	csocket.send('<p>Server running on the pyboard.</p>\n')
	
	for x in data:
		csocket.send('<p>')
		csocket.send(x)
		csocket.send('</p>\n')
	
	t = pyb.millis()
	csocket.send('<p>')
	csocket.send(str(t))
	csocket.send('</p>\n')
	
	dt = pyb.RTC().datetime()
	csocket.send('<p>')
	csocket.send(str(dt[2]))
	csocket.send('.')
	csocket.send(str(dt[1]))
	csocket.send('.')
	csocket.send(str(dt[0]))
	csocket.send(' ')
	csocket.send(str(dt[4]))
	csocket.send(':')
	csocket.send(str(dt[5]))
	csocket.send(':')
	csocket.send(str(dt[6]))
	csocket.send('.')
	csocket.send(str(dt[7]))
	csocket.send(' ')
	csocket.send('</p>\n')
	
	csocket.send('</body>\n')
	csocket.send('</html>\n')

#Basics-Helper
def getTimeStr():
	#t=time.localtime()  #(year, month, mday, hour, minute, second, weekday, yearday)
	t=pyb.RTC().datetime()  #(year, month, mday, tayofweack, hour, minute, second, ms)
	re=''
	if(t[2]<10):re=re+'0'
	re=re+str(t[2])+'.'
	if(t[1]<10):re=re+'0'
	re=re+str(t[1])+'.'+str(t[0])+'-'	
	if(t[4]<10):re=re+'0'
	re=re+str(t[4])+':'
	if(t[5]<10):re=re+'0'
	re=re+str(t[5])+':'
	if(t[6]<10):re=re+'0'
	re=re+str(t[6])+'.'
	if(t[7]<100):re=re+'0'
	if(t[7]<10):re=re+'0'
	re=re+str(t[7])
	return re #tt.mm.yyyy-hh:mm:ss.mmm

def getFileNameAndOp(a_data):
	global show_debug
	s_datei=''
	s_dateiOp=''
	t=0
	while t<len(a_data):
		s_get=a_data[t]
		if(show_debug):print(t,s_get)
		if (s_get.find('GET')==0):
			#print(s_get)
			s_get=s_get.split(' ')
			s_datei=s_get[1]
			if (s_datei.find('?')>0):
				s_dateiOp=s_datei.split('?')[1]
				s_datei=s_datei.split('?')[0]
			
			s_datei=s_datei[1:]  #copy ohne erstes Zeichen
			break
		t+=1
	return (s_datei,s_dateiOp)

#http://de.selfhtml.org/diverses/mimetypen.htm
#http://tools.ietf.org/html/rfc2616
def getMimeType(s_dateiname): 
	s_contenttype='application/octet-stream' #If the media type remains unknown
	
	if(s_dateiname.count('.htm')==1):
		s_contenttype='text/html'
	if(s_dateiname.count('.css')==1):
		s_contenttype='text/css'
	if(s_dateiname.count('.txt')==1):
		s_contenttype='text/plain'
	if(s_dateiname.count('.js')==1):
		s_contenttype='text/javascript'
		
	if(s_dateiname.count('.xml')==1):
		s_contenttype='text/xml'
		
	if(		s_dateiname.count('.mpeg')==1 or
			s_dateiname.count('.mpg')==1 or
			s_contenttype.count('.mpe')):
		s_contenttype='video/mpeg'
		
	if(		s_dateiname.count('.jpe')==1 or
			s_dateiname.count('.jpeg')==1 or
			s_contenttype.count('.jpg')):
		s_contenttype='image/jpeg'
	if(s_dateiname.count('.png')==1):
		s_contenttype='image/png'
	if(s_dateiname.count('.gif')==1):
		s_contenttype='image/gif'
	if(s_dateiname.count('.ico')==1):
		s_contenttype='image/x-icon'
		
	if(s_dateiname.count('.zip')==1):
		s_contenttype='application/zip'
		
	if(s_dateiname.count('.wav')==1):
		s_contenttype='audio/x-wav'
		
	return s_contenttype

#ini Server and Start
def ini(s_host,i_port):
	import sys
	import socket
	import pyb
	
	global show_debug
	
	errorcounter=0
	
	my_socket="";
	try:
		my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('Failed to create socket')
		sys.exit()
		
	my_socket.bind((s_host, i_port))  #exept: OSError: no available NIC

	#my_socket.setblocking(1)
	my_socket.listen(1)     #1=the maximum value is system-dependent; queue up to 1 requests
	
	print("Server is listen")
	pyb.LED(1).off() #red
	pyb.LED(2).on() #green
	pyb.LED(3).off() #yellow
	pyb.LED(4).off() #blue
	
	# Loop forever, listening for requests: telnet 192.168.0.46 8080
	while True:
		try:
			print('>>')
			csock, caddr = my_socket.accept()  #!!!!!!!!!!!!!!!!! macht errors?
			
			
			print('>1',csock)
			pyb.LED(3).on() #yellow
			print('>2',caddr)
			#print(getTimeStr(), caddr)
			
			#empfangene Daten
			data=csock.recv(512) 		#array of byte
			
			print('>3')
			#print('',data)
			
			data=data.decode('utf-8')	# 
			data=data.split("\r\n")
			
			print('>4 data ',len(data))
			#print(data)
			
			#b'GET / HTTP/1.1\r\nHost: 192.168.0.46\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/2'
			#b'GET /index.htm HTTP/1.1\r\nHost: 192.168.0.46\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0'
			
			#GET /index.htm?tut=6&lo=6 HTTP/1.1
			#Host: 192.168.0.46
			#User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0
			#Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
			#Accept-Language: de,en-US;q=0.7,en;q=0.3
			#Accept-Encoding: gzip, deflate
			#Connection: keep-alive
			
			#suche GET (=1. zeile)
			a_FO=getFileNameAndOp(data)
			s_datei=a_FO[0]
			s_dateiOp=a_FO[1]
			
			print(getTimeStr(), caddr,s_datei,s_dateiOp)
			
			if(show_debug):print('s_dateiOp='+s_dateiOp)
			
			#Datei angefordert?
			if(s_datei!=''):
				if isFile(s_datei): #Datei vorhanden
					#open File an recive
					if(show_debug):print('open File '+s_datei)
					
					writeHeader(csock,'HTTP/1.1 200 OK',getMimeType(s_datei)+'; charset=utf-8')
					
					datei=open(s_datei,'r')
					csock.send(datei.read())
					datei.close()
				
				else:
					print('404 Not Found',s_datei)
					#404
					writeHeader(csock,'HTTP/1.1 404 Not Found','text/html; charset=utf-8')
					WriteHTMLHead(csock,data,'404 Not Found')
					csock.send('<body>');
					csock.send('<h1>404 Not Found ');
					csock.send(s_datei);
					csock.send('</h1>');
					csock.send('</body>');
			else:
				#Standartserverantwort, evtl auf Standard-Datei umleiten (index.htm)
				writeHeader(csock,'HTTP/1.1 200 OK','text/html; charset=utf-8')
				WriteDefaultPage(csock,data)
				print('defpage')
			
			#csock.send('HTTP/1.1 200 OK\n')
			#csock.send('Server: pyboard\n')
			#csock.send('Content-Type: text/html; charset=utf-8\n')
			#csock.send('CacheControl: no-cache\n')
			#csock.send('Connection: close\n') #close   Keep-Alive
			#csock.send('\n')
			
			csock.close()
			if(show_debug):print('sock.close()')
			pyb.LED(3).off() #yellow
			
			pyb.delay(10)
			gc.collect()
			
			if(s_dateiOp.count('QUIT')>0):
				print(getTimeStr()," Quit Server")
				break
			#break #nach einer Verbindung Funktion beenden, todo: loop oder als timer-loop?
		
		except MemoryError:
			print ("	MemoryError")
			pyb.LED(4).on()
			pyb.delay(1000)
			break
		except OSError as er:
			#kein int, kein str !
			
			print ("	OSError",er) 
			#print (er.args) 
			#print (er.args[0]) 
			#57    wiederholt sich
			#32 ^=404
			#-57   einmal
			# 1
			
			if(er.args[0]==1):
				print ("Error 1")
			if(er.args[0]==32):
				print ("Error 32")
			if(er.args[0]==-57):
				print ("Error -57")
			if(er.args[0]==57):
				print ("Error 57")
			
			pyb.LED(1).on()
			pyb.delay(500)	
			#print('',data)	
			pyb.LED(1).off()
			pyb.delay(250)
			
			errorcounter+=1
			if(errorcounter>10):break
			
			#pass #platzhalter nop
	
	print ("by")
	pyb.LED(2).off() #green

	#my_socket.close()

# import inic3k
# inic3k.ini()

#import httpserver
#httpserver.ini('',80)

#http://192.168.0.46/
#http://192.168.0.46/index.htm
#http://192.168.0.46/index.htm?fu=fu
#http://192.168.0.46/?QUIT

#pyb.RTC().datetime((2014,11,30,7, 21,11,0,0))


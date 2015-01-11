def ini():
	import pyb
	import time
	import network
	cc3k = network.CC3K(pyb.SPI(2), pyb.Pin('Y5'), pyb.Pin('Y4'), pyb.Pin('Y3'))
	cc3k.connect('42','***') #WLAN: (Ap , Password)

	while(cc3k.isconnected()==0):
		time.sleep(0.5)

	print( "network:",cc3k.isconnected() )
	print( cc3k.ifconfig() )

import socket
import sys

TIMEOUT = 10

#
# Recebe um ip e porta e conecta via telnet e retorna 0 (Sucesso), -1 (Falha)
#
def telnet(ip,port):	

	result = -1
	result_msg = ''
	
	try:
		skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		skt.settimeout(TIMEOUT)
	except socket.error, e:
		result_msg = 'failed: Error creating socket: %s' % e
	else:
		try:
			skt.connect((ip,port))
			result = 0
			result_msg = 'success'
		except socket.error, e:
			result_msg = 'failed: Error connecting to socket: %s' % e
	
	print str(result) + ';' + result_msg 
		
# Main
arg = sys.argv[1:]
ip = ''
port = 0

try:
	ip = arg[0]
except:
	ip = '0.0.0.0'
	
try:
	port = int(arg[1])
except:
	port = 0

telnet(ip,port)
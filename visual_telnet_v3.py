#!/usr/bin/python
import socket
import sys
#import os
import math
import time
from pygraphviz import *
from time import gmtime, strftime
import threading, Queue
import paramiko
import base64

TIMEOUT=10
TIMESTAMP = str(math.trunc(time.time())) # Generate a sequence for file name

telnet_queue = Queue.Queue()
client = paramiko.SSHClient()

class ConnectionTestRemote(threading.Thread):

	def __init__(self, ip_, port_, seq, fo, ip_from):

		threading.Thread.__init__(self)
		self.fo = fo
		
		self.ip_from = ip_from
		self.ip = ip_
		self.port = int(port_)
		self.result = -1
		self.result_msg = ''
		self.seq = seq	


	def run(self):
		try:
			stdin, stdout, stderr = client.exec_command('python telnet.py ' + self.ip + ' ' + str(self.port))
			stdin.close()
			for line in stdout.read().splitlines():
				print line
				self.result, self.result_msg = line.split(';')
		except:
			print stderr
			self.result_msg = 'Error executing program...'
			
		print '(' + str(self.seq) + ') ' + str(self.result)
		print '(' + str(self.seq) + ') ' + self.result_msg
		
		self.fo.write(self.ip_from + '\t' + self.ip + '\t' + str(self.port) + '\t' + str(self.result) + "\t" + self.result_msg + '\n')

		telnet_queue.task_done() #signals to queue job is done

#
# Desenha o grafico
#
def graph_generator(grapf_file_name, test_out_file, short_desc):
	#nodeA = origin_
	#nodeB = destination_
	#connector = connector_
	file_name = grapf_file_name + '-' + TIMESTAMP # Generate a sequence for file name

	A=AGraph()

	# set some default node attributes
	A.node_attr['style']='filled'
	A.node_attr['shape']='component'
	A.node_attr['fixedsize']='false'
	A.node_attr['fontcolor']='#000000'

	i = 0
	#A -(C)-> B
	for line in test_out_file:
		
		i += 1
		
		l = line.strip()
		print l
		
		# Trata comentarios
		if l.startswith('#'):
			print line
		else:
			# Termina quando encontra o identificador de fim de linha <EOF>
			if l.startswith('<'):
				return
			else:
				if  (not l.startswith('-')) and (not l == ''):
					try:
						ip_from, ip_to, port_to, result, result_msg = l.split('\t')
					except ValueError, e:
						print 'Ignoring line: ' + str(i)
						print e 
						print line
					else:
						print '(' + str(i) + ') Connecting... ' + ip_from + '->' + ip_to + ':' + port_to + ' - ' + str(result) + ' ' + result_msg
						A.add_edge(ip_from, ip_to + ':' + port_to)
						n=A.get_node(ip_to + ':' + port_to)
						if result == "0":
							n.attr['fillcolor']='green'
						else:
							n.attr['fillcolor']='tomato'


	# make timestamp
	A.node_attr['shape']='none'
	A.node_attr['fillcolor']='none'
	A.node_attr['style']='dotted'
	A.add_node(strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime()))

	# write files (dot and png)
	print A.string() # print to screen
	A.write(file_name + '.dot') # write to <file_name>.dot
	print 'Wrote ' + file_name + '.dot'
	A.draw(file_name + '.png',prog='circo') # draw to png using circo
	print 'Wrote ' + file_name + '.png'
	return 

#
# Coordena as threads de testes
#
def coordinator(fi, fo, fh, hostname):

	# Interact on from_hosts.txt file
	j = 0
	for line_fh in fh:
		j += 1
		
		lfh = line_fh.strip()
		#print lfh
		
		# Trata comentarios
		if lfh.startswith('#'):
			print line_fh
		else:
			# Termina quando encontra o identificador de fim de linha <EOF>
			if lfh.startswith('<'):
				return
			else:
				if  (not lfh.startswith('-')) and (not lfh == ''):
					try:
						ip_from, user, passwd = lfh.split('\t')
					except ValueError, e:
						print 'Sintaxe error in line: ' + str(j)
						print e 
						print line_fh
					else:
						# Login remote host
						client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
						client.connect(ip_from,username=user,password=base64.b64decode(passwd))
						# Interact on hosts file (hosts to test)
						i = 0
						fi.seek(0) # Go to first line of file
						for line in fi:
						
							while threading.activeCount() > 20:
								time.sleep(10) # wait 5 seconds some threads finish
								
							i += 1
							
							l = line.strip()
							print l
							
							# Trata comentarios
							if l.startswith('#'):
								print '\n\n'
								print line
							else:
								# Termina quando encontra o identificador de fim de linha <EOF>
								if l.startswith('<'):
									#return
									print 'End of File encountered...'
								else:
									if  not l.startswith('-') and not l == '':
										try:
											#ip_port = line.split('\n')
											ip_to, port_to = l.split('\t')
											#port_to, ret_ = port_.split('\r')
										except ValueError, e:
											print 'Sintaxe error in line: ' + str(i)
											print e 
											print line
										else:
											print '\n'
											print '(' + str(i) + ') Testing from ' + ip_from + ' to ' + ip_to + ':' + port_to
											
											t = ConnectionTestRemote(ip_to, port_to, i, fo, ip_from)
											t.setDaemon(True)
											t.start()
											telnet_queue.put(i)
	
						# Wait all threads before close ssh connection
						telnet_queue.join()
						client.close()

# Main program
def main(): 
	start = time.time()

	# Command line parameters. TODO: Improve input parameters and generate help output
	print '\nInput parameters: from_hosts_file input_file output_file(without extension) generate_graph_out(yes/no)'
	try:
		arg = sys.argv[1:]
		from_hosts = arg[0]
	except:
		from_hosts = 'from_hosts.txt'

	try:
		input_file = arg[1]
	except:
		input_file = 'hosts.txt'

	try:
		output_file = arg[2]
	except:
		output_file = 'hosts-tests-results'
		
	try:
		graph_out = arg[3] # yes / [no]
	except:
		graph_out = 'no'
	
	print '\nExecution with parameters: visual_telnet_v3.py ' + from_hosts + ' ' + input_file + ' ' + output_file + ' ' + graph_out 

	# Open files

	in_file = open(input_file, 'r')
	out_file = open(output_file + '-' + TIMESTAMP + '.txt', 'a')
	from_host_file = open(from_hosts, 'r')

	# Valores padrao para o cabecalho
	hostname = socket.gethostname()
	hostIP = socket.gethostbyname(hostname)
	description = 'From: ' + hostname + ' (' + hostIP + ')' + '\n' + 'With TIMEOUT set to ' + str(TIMEOUT) + ' seconds' + '\nFrom: ' + from_hosts + '\nTo: ' + input_file + '\nResult: ' + output_file +'-'+ str(TIMESTAMP) + '.txt|dot|png\n'

	if hostname == '':
		hostname = hostIP

	# screen feedback
	print '\n' + description

	# Write output header
	out_file.write(description)
	out_file.write(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
	out_file.write('\n\n\n')
	out_file.write('ip_from' + '\t' + 'ip_to' + '\t' + 'port' + '\t' + 'result' + "\t" + 'result_msg' + '\n')


	# Coordinate test execution
	coordinator(in_file, out_file, from_host_file, hostname)
	
	print 'Wait on the queue until everything has been processed...'     
	telnet_queue.join()
	
	if graph_out == 'yes':
	
		out_file.close()
		out_file = open(output_file + '-' + TIMESTAMP + '.txt', 'r')
	
		# Generate graph
		# grapf_file_name, host_description, test_out_file, host_description
		graph_generator(output_file + '-graph', out_file, hostname)
	else:
		print 'No graph output will be generated.'
	
	in_file.close()
	out_file.close()
	
	print 'Elapsed Time: %s.' % (time.time() - start)
	print 'Main program waited until background was done.'
	
# Execute program
main()
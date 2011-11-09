import base64
import cmd
import sys

class RunCommand(cmd.Cmd):
	#Simple shell to run a command on the host
	prompt = 'from_host > '

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.hosts = []
		self.connections = []
		self.host_file = ''
		self.filename = ''

	def do_add_host(self, args):
		#add_host <hostip,user,password>. Add the host to the host list
		if self.host_file == '':
			print 'Open file first!!! Command: open_file <file_name>'
		if args:
			ip, user, passwd = args.split(',')
			passwd_encoded = base64.b64encode(passwd)
			print passwd_encoded
			self.host_file.write(ip + '\t' + user + '\t' + passwd_encoded + '\n')
		#decoded = base64.b64decode(encoded)
		#print decoded
		else:
			print "usage: add_host <hostip,user,password>"

	def do_add_comment(self, args):
		#add_comment <some text>. Add comment to host_file
		if self.host_file == '':
			print 'Open file first!!! Command: open_file <file_name>'
			
		if args:
			self.host_file.write('#' + args + '\n')
		else:
			print 'usage: add_comment <some text>'

	def do_open_file(self, args):
		#open_file <filename>. Open filename to add new entries
		if args:
			self.host_file = open(args, 'ar')
		else:
			print 'usage: open_file <filename> (optional path)'

	def do_close_file(self, args):
		#close_file. Close filename
		try:
			self.host_file.close()
			print 'File closed...'
		except:
			print 'File already closed...'

	def do_view_content(self,args):
		#view_content. View content of file
		print '\n'
		for line in self.host_file:
			print line,
		print '\n'

	def do_help(self, args):
		print '\n## Help ##'
		print 'make_from_hosts_file v1.0'
		print 'Use this utility to make from_hosts_file to use with visual_telnet_v3.py'
		print '\nCommand list:'
		print 'help \t\t\t\t\tShow this help.'
		print 'add_host <hostip,user,password> \tAdd the host to the host list.'
		print 'add_comment <some text> \t\tAdd comment to host_file.'
		print 'open_file <filename> \t\t\tOpen filename to add new entries.'
		print 'close_file \t\t\t\tClose filename.'
		print 'view_content \t\t\t\tView content of file.'
		print 'quit \t\t\t\t\tClose file and quit interactive command line.'
		print '## end ##\n'

	def do_quit(self, args):
		#quit. Quit app
		print "Closing file..."
		self.do_close_file(args)
		sys.exit("Goodbye!")
		
if __name__ == '__main__':
	RunCommand().cmdloop()
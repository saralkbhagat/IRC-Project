# client.py to connect server
import select, socket, sys
from helper import Rooms, CH, Members
import util_chat




server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_connection.connect(('127.0.0.1', 8000)) #trying to connect to server

print("Connected to server\n")
msg_prefix = ''

socket_list = [sys.stdin, server_connection]


def prompt():
	sys.stdout.write('-->  :')
	sys.stdout.flush()
try:
	while True:
	
		read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
		
		
		
		for s in read_sockets:
		#
			if s is server_connection: # incoming message
				msg = s.recv(2048)
				if not msg:
					print(" Sorry the server is down!")
					sys.exit(2)
				else:
					if msg == util_chat.QUIT_STRING.encode():
						#MSG COMING FROM SERVER
						sys.stdout.write('Bye\n')
						sys.exit(2)
					else:
						sys.stdout.write(msg.decode())
						if 'Please tell us your name' in msg.decode():
							msg_prefix = 'name: ' # identifier for name
						else:
							msg_prefix = ''
						prompt()
			else:
				msg = msg_prefix + sys.stdin.readline()
				server_connection.sendall(msg.encode())
finally:
    sys.exit(2)

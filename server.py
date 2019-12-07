# server_chat.py  supports multiple clients.
import select, socket, sys, pdb
from helper import CH, Rooms, Members
import util_chat



listensocket = util_chat.create_socket(('127.0.0.1', 8000))
#return object
serversocket=listensocket
chat_hall_list = CH()
connection_list = []
connection_list.append(listensocket)
# all sockets, server socket,
# appending client socket

while True:

	read_players, write_players, error_sockets = select.select(connection_list, [], [])
	
	for member in read_players:
		# if there are multiple items, add 10 clients, listen sockets, if
		if member is listensocket:
			new_socket, add = member.accept()
			# accept client's who is trying to connect, store socket connection of the new client, add client's PORT
			new_member = Members(new_socket)
			# create Members object and initialize all the values, set socket as new socket
			connection_list.append(new_member)
			# append chat member object to the  connection_list
			chat_hall_list.welcome_new(new_member)
			# call the function welcome_new in the class CH()

		else: # new message
			msg = member.socket.recv(2048)
			# particular clients socket message
			if not msg:
				chat_hall_list.remove_member(member)
			if msg:
				msg = msg.decode().lower()
				chat_hall_list.msg_handler(member, msg)
			else:
				member.socket.close()
				connection_list.remove(member)

	for sock in error_sockets:  # close error sockets
		sock.close()
		connection_list.remove(sock)


			

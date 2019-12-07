# Supports Join , Leave , Switch Rooms , sending personal message.
import socket, pdb, sys

MAX_CLIENTS = 10

QUIT_STRING = '<$quit$>'


def create_socket(address):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.setblocking(0)
	s.bind(address)
	s.listen(MAX_CLIENTS)
	print("Now listening at ", address)
	return s
    
class Rooms:
	def __init__(self, name):
		self.members = [] # a list of sockets
		self.name = name

	def welcome_new(self, from_member):
		msg = self.name + " welcomes: " + from_member.name + '\n'
		for member in self.members:
			member.socket.sendall(msg.encode())

	def broadcast(self, from_member, msg):
		msg = from_member.name.encode() + b":" + msg
		for member in self.members:
			member.socket.sendall(msg)

	def remove_member(self, member):
		self.members.remove(member)
		leave_msg = member.name.encode() + b"has left the Rooms\n"
		self.broadcast(member, leave_msg)

class Members:
	def __init__(self, socket, name = "new" , currentRoomsname="new"):
		socket.setblocking(0)
		self.socket = socket
		self.name = name
		self.currentRoomsname=currentRoomsname

	def fileno(self):
		return self.socket.fileno()


class CH:
	def __init__(self):
		self.Roomss = {} # {Rooms_name: Rooms}
		self.Rooms_member_map = {} # {membername-Roomsname: RoomsName}
		self.members_map = {} # {membername : member}

	def welcome_new(self, new_member):
		new_member.socket.sendall(b'Welcome to pychat.\nPlease tell us your name:\n')
		#send message to scket of client with the message

	def list_Roomss(self, member):

		if len(self.Roomss) == 0:
			msg = 'Oops, no active Roomss currently. Create your own!\n' \
				+ 'Use [join Rooms_name] to create a Rooms.\n'
			member.socket.sendall(msg.encode())
		else:
			msg = 'Listing current Roomss and members...\n'
			for Rooms in self.Roomss:
				if 'personal' not in Rooms:
					print (self.Roomss[Rooms].members)
					
					msg += Rooms + ": " + str(len(self.Roomss[Rooms].members)) + " member(s)\n"
					for member1 in self.Roomss[Rooms].members:
						msg += member1.name +"\n"
		member.socket.sendall(msg.encode())

	def msg_handler(self, member, msg):
        
		instructions = b'Instructions:\n'\
		+ b'1. list   --> To list all Rooms\n'\
		+ b'2. join  -->  Room name to join or create or switch to a Rooms\n' \
		+ b'3. personal -->  Member name to chat personally\n'\
		+ b'4. switch  --> To switch Room\n' \
		+ b'5. leave -->  To leave Room\n'\
		+ b'6. quit -->  To quit\n' \
		+ b'Otherwise start typing and enjoy!' \
		+ b'\n'

		print(member.name + " ::: " + msg)
		if "name:" in msg:
			name = msg.split()[1]
			member.name = name
			print("New connection from:", member.name)
			self.members_map[member.name]=member
			member.socket.sendall(instructions)

		elif "join" in msg:
			same_Rooms = False
			if len(msg.split()) >= 2: # error check
				Rooms_name = msg.split()[1]
				member.currentRoomsname = Rooms_name
				if member.name+"-"+Rooms_name in self.Rooms_member_map: # switching?
					if self.Rooms_member_map[member.name+"-"+Rooms_name] == Rooms_name:
						member.socket.sendall(b'You are already in Rooms: ' + Rooms_name.encode())
						same_Rooms = True
					else: # switch
						old_Rooms = self.Rooms_member_map[member.name+"-"+Rooms_name]
						# self.Roomss[old_Rooms].remove_member(member)
				if not same_Rooms:
					if not Rooms_name in self.Roomss: # new Rooms:
						new_Rooms = Rooms(Rooms_name)
						self.Roomss[Rooms_name] = new_Rooms
					self.Roomss[Rooms_name].members.append(member)
					self.Roomss[Rooms_name].welcome_new(member)
					self.Rooms_member_map[member.name+"-"+Rooms_name] = Rooms_name
					#if member.name+"-"+member.currentRoomsname in self.Rooms_member_map:
						#print (member.currentRoomsname)
						#sys.stdout.write(member.currentRoomsname)
						#sys.stdout.flush()
						#print (Rooms_name)
						#sys.stdout.write(Rooms_name)
						#sys.stdout.flush()
						#self.Rooms_member_map.pop(member.name+"-"+member.currentRoomsname)
					#member.currentRoomsname = Rooms_name
			else:
				member.socket.sendall(instructions)

		elif "list" in msg:
			print(self.Roomss)
			print(self.Rooms_member_map)
			self.list_Roomss(member) 

		elif "manual" in msg:
			member.socket.sendall(instructions)

		elif "leave" in msg:

			if len(msg.split()) >= 2: # error check
				leaveRoomsname=msg.split()[1]

				if member.name+"-"+leaveRoomsname in self.Rooms_member_map:
					del self.Rooms_member_map[member.name+"-"+member.currentRoomsname]
					self.Roomss[leaveRoomsname].remove_member(member)
					print("Members: " + member.name + " has left"+leaveRoomsname+"\n")
					if len(self.Roomss[leaveRoomsname].members)==0:
						del self.Roomss[leaveRoomsname]
				else :
					msg = "you entered wrong Rooms name please try again\n"
					member.socket.sendall(msg.encode())
			else:
				member.socket.sendall(instructions)

		elif "quit" in msg:
			member.socket.sendall(QUIT_STRING.encode())
			self.remove_member(member)

		elif "switch" in msg:
			if len(msg.split()) >= 2:
				switchRoomsname=msg.split()[1]
				#   isRooms = self.Rooms_member_map[member.name+"-"+switchRoomsname]
				#   if isRooms == switchRoomsname :
				if member.name+"-"+switchRoomsname in self.Rooms_member_map:

					member.currentRoomsname = switchRoomsname

				else:
					msg = "you are not in entered Rooms please join"
					member.socket.sendall(msg.encode())
			else:
				member.socket.sendall(instructions)

		elif "personal" in msg:
			if len(msg.split()) >= 2:
				membername = msg.split()[1]
				if membername in self.members_map:
					newmember = self.members_map[membername]
					personal_Rooms = Rooms("personal-"+member.name+"-"+membername)
					self.Roomss["personal-"+member.name+"-"+membername] = personal_Rooms
					self.Roomss["personal-"+member.name+"-"+membername].members.append(member)
					self.Roomss["personal-"+member.name+"-"+membername].members.append(newmember)
					self.Rooms_member_map[member.name+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
					#self.Roomss[Rooms_name].welcome_new(member)
					self.Rooms_member_map[membername+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
					member.currentRoomsname = "personal-"+member.name+"-"+membername
					newmember.currentRoomsname = "personal-"+member.name+"-"+membername
				else:
					msg = "Entered member does not exsist!!"
					member.socket.sendall(msg.encode())
			else:
				member.socket.sendall(instructions)

		elif not msg:
			self.remove_member(member)

		else:
			# check if in a Rooms or not first
			if member.name+"-"+member.currentRoomsname in self.Rooms_member_map:
				self.Roomss[self.Rooms_member_map[member.name+"-"+member.currentRoomsname]].broadcast(member, msg.encode())
			else:
				msg = 'You are currently not in any Rooms! \n' \
				+ 'Use [list] to see available Roomss! \n' \
				+ 'Use [join Rooms_name] to join a Rooms! \n'
				member.socket.sendall(msg.encode())

	def remove_member(self, member):
		if member.name +"-"+member.currentRoomsname in self.Rooms_member_map:
			self.Roomss[self.Rooms_member_map[member.name+"-"+member.currentRoomsname]].remove_member(member)
			del self.Rooms_member_map[member.name+"-"+member.currentRoomsname]
		print("Members: " + member.name + " has left\n")


    

			
			

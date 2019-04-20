import socket
from threading import Thread
import time
import os as os
import hashlib
import sys

succ= 0
pred= 0
topology= []
filesList= []

def initialize(port):
	s= socket.socket()
	print ("Socket successfully created")
	s.bind(('', port))
	return s

def listen(socket):
	global succ
	global pred
	global filesList
	myself= socket.getsockname()[1]
	socket.listen()
	print("socket is listening")
	while True:
		c, addr = socket.accept()
		message= c.recv(1024)
		message= message.decode("utf-8")
		message= message.split(":")
		flag= message[0]
		if(flag=="-a"):
			send= str(succ)+"-"+str(pred)
			send= send.encode()
			c.send(send)
			# printStatus()
		elif(flag=="-o"):
			addingThis= int(message[1])
			succ= addingThis
			pred= addingThis
			send= "done"
			send= send.encode()
			c.send(send)
			printStatus()
		elif(flag=="-u"):
			recvPort= int(message[1])
			recvPortSucc= int(message[2])
			recvPortPred= int(message[3])
			send= "done"
			send= send.encode()
			c.send(send)
			if(recvPortSucc==myself):
				pred= recvPort
				printStatus()
				continue
			if(recvPortPred==myself):
				succ= recvPort
				printStatus()
				continue
		elif(flag=="-f"):
			filename= message[1]
			fileHashValue= int(message[2])
			print("getting {} with hash {} from {}".format(filename,fileHashValue,addr))
			send= "done"
			send= send.encode()
			c.send(send)
			time.sleep(0.2)
			f= open(filename,'wb')
			sprite= ''
			i= 1
			while(i):
				l= c.recv(1024)
				f.write(l)
				if((i%100)==0):
					sprite= sprite+"."
					print(sprite)
				if not l:
					break
				i=i+1
			f.close()
			print("copied")
			fileInfo= str(fileHashValue)+":"+filename
			filesList.append(fileInfo)
		elif(flag=="-l"):
			if(len(filesList)==0):
				send= "-1"
			else:
				send= ""
				for i in range(0,len(filesList)):
					pushStr= filesList[i]+"::"
					send= send+pushStr
			send= send.encode()
			c.send(send)
		elif(flag=="-r"):
			nameVal= message[1]
			print("got a: ",nameVal)
			f= open(nameVal, "rb")
			l= f.read(1024)
			while(l):
				c.send(l)
				l= f.read(1024)
		c.close()

def giveAdjacentNodes(port):
	soc = socket.socket()                        
	try:
		soc.connect(('127.0.0.1', port))
		sendMsg= "-a"
		sendMsg= sendMsg.encode()
		soc.send(sendMsg)
		time.sleep(0.2) 
		msg= soc.recv(1024)
		msg= msg.decode("utf-8")
		msg=msg.split("-")
		return (int(msg[0]),int(msg[1]))
	except ConnectionRefusedError:
		pass
	except ConnectionResetError:
		pass
	finally:
		soc.close()

def addMe(port, me):
	soc = socket.socket()
	try:                     
		soc.connect(('127.0.0.1', port))
		sendMsg= "-o"+":"+str(me)
		sendMsg= sendMsg.encode()
		soc.send(sendMsg)
		time.sleep(0.2) 
		msg= soc.recv(1024)
		msg= msg.decode("utf-8")
		soc.close()
		if(msg=="done"):
			return 1
		return 0
	except ConnectionRefusedError:
		pass
	except ConnectionResetError:
		pass
	finally:
		soc.close()

def isLastNode(port):
	succ, pred= giveAdjacentNodes(port)
	if(succ<port):
		return 1
	return 0

def updateYourself(port,infoList):
	infoStr= str(infoList[0])+":"+str(infoList[1])+":"+str(infoList[2])
	soc= socket.socket()
	try:                      
		soc.connect(('127.0.0.1', port))
		sendMsg= "-u:"+infoStr
		sendMsg= sendMsg.encode()
		soc.send(sendMsg)
		time.sleep(0.2) 
		msg= soc.recv(1024)
		msg= msg.decode("utf-8")
	except ConnectionRefusedError:
		pass
	except ConnectionResetError:
		pass
	finally:
		soc.close()

def updateAdjacentNodes(newNode, thisNode):
	global succ
	global pred
	if(newNode==thisNode):
		succ= newNode
		pred= newNode
		printStatus()
	else:
		knows= newNode
		while(True):
			ks, kp= giveAdjacentNodes(knows)
			if((ks==knows) and (kp==knows)):
				succ= newNode
				pred= newNode
				printStatus()
				addMe(newNode, thisNode)
				break
			else:
				if(isLastNode(knows)):
					if((thisNode>knows) or (thisNode<ks)):
						succ= ks
						pred= knows
						printStatus()
						updateYourself(succ,[thisNode,succ,pred])
						updateYourself(pred,[thisNode,succ,pred])
						break
					else:
						knows= ks
						continue
				else:
					if((knows<=thisNode) and (thisNode<=ks)):
						succ= ks
						pred= knows
						printStatus()
						updateYourself(succ,[thisNode,succ,pred])
						updateYourself(pred,[thisNode,succ,pred])
						break
					else:
						knows= ks
						continue

def printStatus():
	print("")
	print("Node: {} Successor: {} Predecessor: {}".format(identity,succ,pred))

def isNodeUp(node):
	if(identity==node):
		return True
	else:
		soc= socket.socket()
		try:
			soc.connect(('127.0.0.1',node))
			return True
		except socket.error:
			return False
		finally:
			soc.close()

def consistentTopology():
	global topology
	delList= []
	for i in range(0,len(topology)):
		entry= topology[i]
		if(entry>0):
			if(isNodeUp(entry)==False):
				delList.append(entry)
		else:
			delList.append(entry)
	for i in range(0,len(delList)):
		topology.remove(delList[i])

def checkTopology():
	global topology
	global succ
	global pred
	while(True):
		giveList(succ)
		checkFlag= False
		adjacentStatus= checkAdjacentNodes()
		if(adjacentStatus):
			checkFlag= True
			print("Successor is down")
			newSuccessor= findNewSuccessor()
			print("New successor is: {}".format(newSuccessor))
			if(newSuccessor==identity):
				succ= newSuccessor
				pred= newSuccessor
			else:
				succ= newSuccessor
				updateYourself(succ,[identity,succ,pred])
			print("done!")
			printStatus()
		consistentTopology()
		if(checkFlag):
			print(topology)
		time.sleep(1)

def findNewSuccessor():
	global topology
	global succ
	topology.remove(-1*succ)
	upList= []
	for i in range(0,len(topology)):
		entry= topology[i]
		if(isNodeUp(entry)):
			upList.append(entry)
	upList.sort()
	if(len(upList)==1):
		return identity
	if(succ<identity):
		return upList[0]
	else:
		for j in range(0,len(upList)):
			entry= upList[j]
			if(entry>identity):
				return entry
		return upList[0]

def checkAdjacentNodes():
	global topology
	global succ
	toLookFor= -1*succ
	if(toLookFor in topology):
		return 1
	return 0

def giveList(port):
	global topology
	if(port==identity):
		if(port not in topology):
			topology.append(port)
		return topology
	else:
		if(isNodeUp(port)):
			if(port not in topology):
				topology.append(port)
			portSucc, portPred= giveAdjacentNodes(port)
			giveList(portSucc)
		else:
			if((-1*port) not in topology):
				topology.append(-1*port)
			return topology

def giveHash(filename):
	hash_object = hashlib.md5(filename.encode())
	hexHash= hash_object.hexdigest()
	value= int(hexHash, 16)
	value= value%9000
	return value

def findNodeForHash(hashValue):
	portList= sorted(topology)
	for i in range(0,len(portList)):
		if(portList[i]>hashValue):
			return portList[i]
	if(hashValue>portList[len(portList)-1]):
		return portList[len(portList)-1]

def sendFile(filename, hashValue, port):
	global filesList
	if(port==identity):
		fileInfo= str(hashValue)+":"+filename
		filesList.append(fileInfo)
	else:
		infoStr= filename+":"+str(hashValue)
		soc= socket.socket()                        
		try:
			soc.connect(('127.0.0.1', port))
			sendMsg= "-f:"+infoStr
			sendMsg= sendMsg.encode()
			soc.send(sendMsg)
			time.sleep(0.2) 
			msg= soc.recv(1024)
			msg= msg.decode("utf-8")
			if(msg=="done"):
				print("got confirmation")
				f= open(filename, "rb")
				l= f.read(1024)
				while(l):
					soc.send(l)
					l= f.read(1024)
		except ConnectionRefusedError:
			pass
		except ConnectionResetError:
			pass
		finally:
			soc.close()

def getFiles(port):
	soc = socket.socket()
	try:                      
		soc.connect(('127.0.0.1', port))
		sendMsg= "-l"
		sendMsg= sendMsg.encode()
		soc.send(sendMsg)
		time.sleep(0.2) 
		msg= soc.recv(1024)
		msg= msg.decode("utf-8")
		if(msg=="-1"):
			return -1
		else:
			msg=msg.split("::")
			msg.remove("")
			return msg
	except ConnectionRefusedError:
		pass
	except ConnectionResetError:
		pass
	finally:
		soc.close()

def showAvailableFiles():
	global topology
	allFiles= []
	for i in range(0, len(filesList)):
		allFiles.append(filesList[i])
	for i in range(0, len(topology)):
		if(topology[i]==identity):
			continue
		else:
			fromPort= getFiles(topology[i])
			if(fromPort==-1):
				continue
			else:
				for j in range(0, len(fromPort)):
					allFiles.append(fromPort[j])
	return allFiles

def requestFile(port, filename):
	global filesList
	soc = socket.socket()
	try:                       
		soc.connect(('127.0.0.1', port))
		sendMsg= "-r:"+filename
		sendMsg= sendMsg.encode()
		soc.send(sendMsg)
		time.sleep(0.2)
		f= open(filename,'wb')
		i=0
		while(i):
			l= soc.recv(1024)
			f.write(l)
			if((i%100)==0):
				sprite= sprite+"."
				print(sprite)
			if not l:
				break
			i=i+1
		f.close()
		print("downloaded")
	except ConnectionRefusedError:
		pass
	except ConnectionResetError:
		pass
	finally:
		soc.close()

def showOptions():
	while(True):
		print("What do you want to do?")
		print("1) Upload a file")
		print("2) Download a file")
		print("3) Leave the Chord")
		try:
			choice= int(input("Enter option number: "))
			pass
		except EOFError:
			os._exit(1)
		if(choice==1):
			os.system("DIR")
			try:
				filename= str(input("Out of these files, which one do you want to upload? "))
				pass
			except EOFError:
				os._exit(1)
			hashValue= giveHash(filename)
			storageNode= findNodeForHash(hashValue)
			print("Uploading: {} belongs to: {} hashed: {}".format(filename,storageNode,hashValue))
			sendFile(filename,hashValue,storageNode)
		elif(choice==2):
			print("I'll fetch the list of files on the DHT")
			filesOnNetwork= showAvailableFiles()
			print(filesOnNetwork)
			if(len(filesOnNetwork)==0):
				continue
			indexOfFile= 0
			while(True):
				try:
					indexOfFile= int(input("Enter the list index of the file you want to download: "))
					pass
				except EOFError:
					os._exit(1)
				if((0<=indexOfFile) and (indexOfFile<=(len(filesOnNetwork)-1))):
					break
				print("Invalid index!")
			fileToDownload= filesOnNetwork[indexOfFile]
			print("Will download this {}".format(fileToDownload))
			fileInfo= fileToDownload.split(":")
			fileHash= int(fileInfo[0])
			fileName= fileInfo[1]
			targetNode= findNodeForHash(fileHash)
			requestFile(targetNode,fileName)
		elif(choice==3):
			print("Okay. Transferring your files to others")
			if(len(filesList)!=0):
				for i in range(0,len(filesList)):
					entry= filesList[i]
					entry= entry.split(":")
					fileHash= entry[0]
					fileName= entry[1]
					sendFile(fileName,fileHash,succ)
			os._exit(1)
		else:
			print("Invalid choice")

def checkMyFiles():
	global filesList
	while(True):
		if(len(filesList)!=0):
			delList= []
			for i in range(0,len(filesList)):
				entry= filesList[i]
				originalEntry= entry
				entry= entry.split(":")
				fileHash= int(entry[0])
				fileName= entry[1]
				correctNode= findNodeForHash(fileHash)
				if(correctNode!=identity):
					print("someone New came in and now Transferring the files that belongs to them")
					sendFile(fileName,fileHash,correctNode)
					delList.append(originalEntry)
			for i in range(0,len(delList)):
				filesList.remove(delList[i])
		time.sleep(1.5)
				
try:
	identity= int(input("Enter your port: "))
	pass
except EOFError:
	os._exit(1)
s= initialize(identity)
listenThread= Thread(target=listen, args=[s])
listenThread.start()
try:
	port= int(input("Who do you know: "))
	pass
except EOFError:
	os._exit(1)
except KeyboardInterrupt:
	os._exit(1)
updateAdjacentNodes(port,identity)
checkThread= Thread(target=checkTopology, args=[])
checkThread.start()
optionThread= Thread(target=showOptions, args=[])
optionThread.start()
filesCheckThread= Thread(target=checkMyFiles, args=[])
filesCheckThread.start()
print("")
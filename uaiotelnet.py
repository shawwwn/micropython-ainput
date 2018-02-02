import socket
import uos
import errno
import uasyncio

last_client_socket = None
loop = None

# Provide necessary functions for dupterm and replace telnet control characters that come in.
class TelnetWrapper():
	def __init__(self, socket):
		self.socket = socket
		self.discard_count = 0

	def readinto(self, b):
		global last_client_socket
		readbytes = 0
		for i in range(len(b)):
			try:
				byte = 0
				# discard telnet control  characters and
				# null bytes 
				while(byte == 0):
					byte = self.socket.recv(1)[0]
					if byte == 0xFF:
						self.discard_count = 2
						byte = 0
					elif self.discard_count > 0:
						self.discard_count -= 1
						byte = 0

				b[i] = byte

				readbytes += 1
			except (IndexError, OSError) as e:
				if type(e) == IndexError or len(e.args) > 0 and e.args[0] == errno.EAGAIN:
					if readbytes == 0:
						return None
					else:
						return readbytes
				else:
					self.close()
					raise
		return readbytes

	def write(self, data):
		global last_client_socket
		# we need to write all the data but it's a non-blocking socket
		# so loop until it's all written eating EAGAIN exceptions
		while len(data) > 0:
			try:
				written_bytes = self.socket.write(data)
				data = data[written_bytes:]
			except OSError as e:
				if len(e.args) > 0 and e.args[0] == errno.EAGAIN:
					# can't write yet, try again
					pass
				else:
					# something else...propagate the exception
					self.close()
					raise

	def close(self):
		self.socket.close()

# On accepting client connection
async def server(reader, writer):
	global last_client_socket

	if last_client_socket:
		# close any previous clients
		yield uasyncio.IOReadDone(last_client_socket)
		last_client_socket.close()
		uos.dupterm(None)

	last_client_socket = writer.s
	last_client_socket.setblocking(False)
	remote_addr = writer.extra["peername"]
	print("Telnet connection from: ", remote_addr)
	last_client_socket.sendall(bytes([255, 252, 34])) # dont allow line mode
	last_client_socket.sendall(bytes([255, 251, 1])) # turn off local echo
	uos.dupterm(TelnetWrapper(last_client_socket))

# On receiving client data
async def client_rx():
	global last_client_socket

	while True:
		if last_client_socket!=None:
			try:
				# dirty hack for checking if socket is still connected
				s=str(last_client_socket)
				i=s.index('state=')+6
				if int(s[i:s.index(' ', i)]) != 2:
					raise

				yield uasyncio.IORead(last_client_socket)
				uos.dupterm_notify(last_client_socket)
			except:
				# clean up
				print("Telnet client disconnected ...")
				yield uasyncio.IOReadDone(last_client_socket)
				last_client_socket = None
				uos.dupterm(None)
		else:
			await uasyncio.sleep(1)
		await uasyncio.sleep_ms(1)

# Add server tasks to asyncio event loop
# Server will run after loop has been started
async def start(ip="0.0.0.0", port=23):
	global loop

	loop = uasyncio.get_event_loop()
	loop.create_task(uasyncio.start_server(server, ip, port))
	loop.create_task(client_rx())

	print("Telnet server started on {}:{}".format(ip, port))

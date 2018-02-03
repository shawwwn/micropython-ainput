import errno

# Provide necessary functions for dupterm and replace telnet control characters that come in.
class TelnetWrapper():
	def __init__(self, socket):
		self.socket = socket
		self.discard_count = 0

	def readinto(self, b):
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
#
# Simple Telnet server runing in uasyncio
#
# Adapted from
# https://github.com/cpopp/MicroTelnetServer
#
import socket
import uos
import errno
import uasyncio

last_client_socket = None
loop = None

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

	from .wrapper import TelnetWrapper
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

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

sw_client = None
loop = None

# On accepting client connection
async def server(reader, writer):
	global sw_client

	remote_addr = writer.extra["peername"]
	print("Telnet connection from: ", remote_addr)

	if sw_client:
		print("Close previous connection ...")
		stop()

	from .sw import TelnetWrapper
	sw_client = TelnetWrapper(writer.s)
	sw_client.socket.setblocking(False)
	sw_client.socket.sendall(bytes([255, 252, 34])) # dont allow line mode
	sw_client.socket.sendall(bytes([255, 251, 1])) # turn off local echo
	uos.dupterm(sw_client)

# On receiving client data
async def client_rx():
	global sw_client

	while True:
		if sw_client != None:
			try:
				# dirty hack to check if socket is still connected
				s=str(sw_client.socket)
				i=s.index('state=')+6
				if int(s[i:s.index(' ', i)]) != 2:
					raise

				yield uasyncio.IORead(sw_client.socket)
				uos.dupterm_notify(sw_client.socket) # dupterm_notify will somehow make a copy of sw_client
			except:
				# clean up
				print("Telnet client disconnected ...")
				yield uasyncio.IOReadDone(sw_client.socket)
				stop()
		else:
			await uasyncio.sleep(1)
		await uasyncio.sleep_ms(1)

def stop():
	global sw_client
	if sw_client:
		sw_client.close()
		uos.dupterm_notify(sw_client) # deactivate dupterm
		sw_client = None
		uos.dupterm(None)

# Add server tasks to asyncio event loop
# Server will run after loop has been started
async def start(ip="0.0.0.0", port=23):
	global loop

	loop = uasyncio.get_event_loop()
	loop.create_task(uasyncio.start_server(server, ip, port))
	loop.create_task(client_rx())

	print("Telnet server started on {}:{}".format(ip, port))

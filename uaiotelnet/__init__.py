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
is_esp8266 = True if uos.uname()[0]=='esp8266' else False
rx_handler_coro = None

# On accepting client connection
async def server(reader, writer):
	global sw_client, rx_handler_coro

	remote_addr = writer.extra["peername"]
	print("Telnet connection from: ", remote_addr)

	if sw_client:
		# close previous socket
		if rx_handler_coro:
			uasyncio.cancel(rx_handler_coro)
		await uasyncio.sleep(1) # wait some time for error to trigger in previous socket handler
		sw_client = None
		rx_handler_coro = client_rx()
		loop = uasyncio.get_event_loop()
		loop.create_task(rx_handler_coro)
		uos.dupterm(None)
		await uasyncio.sleep_ms(500)

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
				# dirty hack for checking if socket is still connected
				# only for esp8266 with NONOS SDK
				if is_esp8266:
					s=str(sw_client.socket)
					i=s.index('state=')+6
					if int(s[i:s.index(' ', i)]) != 2:
						raise

				yield uasyncio.IORead(sw_client.socket)

				# works on my MicroPython fork (https://github.com/shawwwn/micropython)
				# dupterm_notify() will return -2 or -3 upon stream error
				# check: micropython/extmod/uos_dupterm.c
				if uos.dupterm_notify(sw_client.socket) < -1:
					raise
			except:
				# clean up
				print("Telnet client disconnected ...")
				yield uasyncio.IOReadDone(sw_client.socket)
				stop()
		else:
			await uasyncio.sleep(2)
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
	loop = uasyncio.get_event_loop()
	loop.create_task(uasyncio.start_server(server, ip, port))
	rx_handler_coro = client_rx()
	loop.create_task(rx_handler_coro)

	print("Telnet server started on {}:{}".format(ip, port))

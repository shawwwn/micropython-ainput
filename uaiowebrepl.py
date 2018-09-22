#
# WebREPL server runing in uasyncio
#
# NOTE:
# This module has to be run with uaiorepl for non-blocking input
#
# Adapted from
# https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/webrepl_setup.py
#
import uos
import websocket
import _webrepl
import uasyncio

client_s = None
is_esp8266 = True if uos.uname()[0]=='esp8266' else False
rx_handler_coro = None

# On accepting client connection
async def server(reader, writer):
	global client_s, rx_handler_coro

	remote_addr = writer.extra["peername"]
	print("WebREPL connection from: ", remote_addr)

	if client_s:
		# close previous socket
		if rx_handler_coro:
			uasyncio.cancel(rx_handler_coro)
		await uasyncio.sleep(1) # wait some time for error to trigger in previous socket handler
		rx_handler_coro = client_rx()
		loop = uasyncio.get_event_loop()
		loop.create_task(rx_handler_coro)
		uos.dupterm(None)
		await uasyncio.sleep_ms(500)

	client_s = writer.s
	# Blocking is needed for websocket_helper.server_handshake()
	# TODO: rewrite async server_handshake
	client_s.setblocking(True)
	import websocket_helper
	websocket_helper.server_handshake(client_s)
	ws = websocket.websocket(client_s)
	ws = _webrepl._webrepl(ws)
	client_s.setblocking(False)
	uos.dupterm(ws)

# On receiving client data
async def client_rx():
	global client_s

	while True:
		if client_s != None:
			try:
				# dirty hack for checking if socket is still connected
				# only for esp8266 with NONOS SDK
				if is_esp8266:
					s=str(client_s)
					i=s.index('state=')+6
					if int(s[i:s.index(' ', i)]) != 2:
						raise

				yield uasyncio.IORead(client_s);

				# works on my MicroPython fork (https://github.com/shawwwn/micropython)
				# dupterm_notify() will return -2 or -3 upon stream error
				# check: micropython/extmod/uos_dupterm.c
				if uos.dupterm_notify(client_s) < -1:
					raise
			except:
				# clean up
				print("WebREPL client disconnected ...")
				yield uasyncio.IOReadDone(client_s)
				stop()
		else:
			await uasyncio.sleep(2)
		await uasyncio.sleep_ms(1)

def stop():
	global client_s
	uos.dupterm(None)
	if client_s:
		client_s.close()
		client_s = None


# Add server tasks to asyncio event loop
# Server will run after loop has been started
async def start(ip="0.0.0.0", port=8266, password=None):
	global rx_handler_coro

	stop()
	if password is None:
		try:
			import webrepl_cfg
			_webrepl.password(webrepl_cfg.PASS)
			print("Started webrepl in normal mode")
		except:
			print("WebREPL is not configured, run 'import webrepl_setup'")
	else:
		_webrepl.password(password)
		print("Started webrepl in manual override mode")

	loop = uasyncio.get_event_loop()
	loop.create_task(uasyncio.start_server(server, ip, port))
	rx_handler_coro = client_rx()
	loop.create_task(rx_handler_coro)

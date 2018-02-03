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
uterm_id = 0 # duplicated uterm id this module has attached to

# On accepting client connection
async def server(reader, writer):
	global client_s

	if client_s:
		# close any previous clients
		client_s.close()
		uos.dupterm(None, uterm_id)

	client_s = writer.s
	# Blocking is needed for websocket_helper.server_handshake()
	# TODO: rewrite async server_handshake
	client_s.setblocking(True)
	import websocket_helper
	websocket_helper.server_handshake(client_s)
	ws = websocket.websocket(client_s)
	ws = _webrepl._webrepl(ws)
	client_s.setblocking(False)
	remote_addr = writer.extra["peername"]
	print("WebREPL connection from: ", remote_addr)
	uos.dupterm(ws, uterm_id)

# On receiving client data
async def client_rx():
	global client_s

	while True:
		if client_s!=None:
			try:
				# dirty hack for checking if socket is still connected
				s=str(client_s)
				i=s.index('state=')+6
				if int(s[i:s.index(' ', i)]) != 2:
					raise

				yield uasyncio.IORead(client_s)
				uos.dupterm_notify(client_s)
			except:
				# clean up
				print("WebREPL client disconnected ...")
				yield uasyncio.IOReadDone(client_s)
				stop()
		else:
			await uasyncio.sleep(1)
		await uasyncio.sleep_ms(1)

def stop():
	global client_s, uterm_id
	uos.dupterm(None, uterm_id)
	if client_s:
		client_s.close()
		client_s = None


# Add server tasks to asyncio event loop
# Server will run after loop has been started
# TODO: dupterm(,index) isn't really working in MicroPython as of v1.9.3
#       uterm must set to 0 unless some upstream works have been done
async def start(ip="0.0.0.0", port=8266, password=None, uterm=0):
	global loop, uterm_id
	uterm_id = uterm

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
	loop.create_task(client_rx())

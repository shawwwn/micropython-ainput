#
# MIT License
#
# Copyright (c) 2018 Shawwwn <shawwwn1@gmai.com>
#
import machine
import uio
import sys
import uasyncio
from uasyncio.synchro import Lock
try:
    import esp32
    from esp32 import UART0 as UART
except ImportError:
    from machine import UART

input_lock = Lock() # global lock
ua = UART(0)
ua.init()

async def ainput(prompt=None, password=False):
	await input_lock.acquire() # two ainput() cant read at the same time

	def stdout_write(buf):
		if not password:
			sys.stdout.write(buf)

	if prompt!="" or prompt!=None:
		sys.stdout.write(prompt)

	ss = uio.StringIO()
	ss.seek(0)
	ss_cur = 0

	while True:
		if ua.any():
			ch = ua.read(1)
			asc2 = ord(ch)

			if 31<asc2<127: # ASCII printable characters
				ss.seek(ss_cur)
				ss.write(ch)
				ss_cur += 1
				stdout_write(ch)
			elif asc2==127: # DEL
				ss_cur -= 1 if ss_cur>0 else 0
				stdout_write(ch)
			elif asc2==13 or asc2==10: # CR|LF
				sys.stdout.write(b'\n')
				break
		await uasyncio.sleep_ms(1)

	await uasyncio.sleep_ms(1)
	input_lock.release()
	ss.seek(0)
	return ss.read(ss_cur)

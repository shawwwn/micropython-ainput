#
# MIT License
#
# Copyright (c) 2018 Shawwwn <shawwwn1@gmai.com>
#
# NOTE:
# For this script to work correctly on ESP32
# You need to use my fork of MicroPython:
# https://github.com/shawwwn/micropython
#
import machine
import uio
import sys
import uasyncio
import gc
try:
    import esp32
    from esp32 import UART0 as UART
except ImportError:
    from machine import UART

ua = UART(0)
ua.init()

async def start(prompt=b">>>> ", cont_prompt=b".... "):
	ss = uio.StringIO()

	# get user input
	while True:
		# reset internal & external stream cursor
		ss.seek(0)
		ss_cur = 0

		sys.stdout.write(prompt)

		# one character at a time
		while True:
			if ua.any():
				ch = ua.read(1)
				asc2 = ord(ch)

				if 31<asc2<127: # ASCII printable characters
					ss.seek(ss_cur)
					ss.write(ch)
					ss_cur += 1
					sys.stdout.write(ch)
				elif asc2==127: # DEL(backspace)
					ss_cur -= 1 if ss_cur>0 else 0
					sys.stdout.write(ch)
				elif asc2==13: # CR(return)
					sys.stdout.write(b'\n')
					break
				elif asc2==2 or asc2==10: # STX(ctrl+b) | LF(newline)
					sys.stdout.write(b'\n')
					sys.stdout.write(cont_prompt)
					ss.write(b'\n')
					ss_cur += 1
			await uasyncio.sleep_ms(1)

		# read to a string
		ss.seek(0)
		src_code = ss.read(ss_cur)

		# Trying to simulate mp_compile() with flag isrepl=true
		try:
			ret = eval(src_code)
			if ret!=None:
				print(ret)
		except: # if eval() fail, then exec()
			try:
				exec(src_code)
			except Exception as e:
				print(e) # display syntax error, etc.

		gc.collect()
		await uasyncio.sleep_ms(10)


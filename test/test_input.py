import sys
import uasyncio
import uaioinput

async def test_input():
	while True:
		print("-- normal input --")
		s = await uaioinput.ainput(">>>>>> ")
		print(s)

		await uasyncio.sleep_ms(10)

		print("-- password input --")
		pw = await uaioinput.ainput(prompt=">>>>>> ", password=True)
		print(pw)

		await uasyncio.sleep_ms(10)

loop = uasyncio.get_event_loop()
loop.call_soon(test_input())
loop.run_forever()
loop.close()

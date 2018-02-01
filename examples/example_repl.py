import uasyncio
import uaiorepl

print("== Testing repl module ...")
loop = uasyncio.get_event_loop()
loop.call_soon(uaiorepl.start())
loop.run_forever()
loop.close()
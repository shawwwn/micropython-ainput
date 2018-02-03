import uasyncio
import uaiowebrepl
import uaiorepl

print("== Testing webrepl module ...")
loop = uasyncio.get_event_loop()
loop.call_soon(uaiowebrepl.start())
loop.call_soon(uaiorepl.start()) # uasyncio repl takes webrepl input
loop.run_forever()
loop.close()

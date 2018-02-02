import uasyncio
import uaiotelnet
import uaiorepl

print("== Testing telnet module ...")
loop = uasyncio.get_event_loop()
loop.call_soon(uaiotelnet.start())
loop.call_soon(uaiorepl.start()) # uasyncio repl will process telnet input
loop.run_forever()
loop.close()

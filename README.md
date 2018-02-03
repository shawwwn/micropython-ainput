# micropython-ainput
Asynchronous user input libraries using MicroPython [uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio) library



## uaioinput
Library for for getting user input inside uasyncio event-loop

#### Usage
```python
import uasyncio
from uaioinput import ainput
s = await ainput(prompt="User Input: ", password=False)
print(s)
```

To prevent two `ainput()` being called at the same time, a global **lock** is 
implemented at the module level.\
To check **lock** status,
```python
import uaioinput
print(uaioinput.input_lock.locked)
```

#### Dependencies
 * [micropython-uasyncio.synchro](https://github.com/micropython/micropython-lib/tree/master/uasyncio.synchro)



## uaiorepl
A simple(dumb) REPL console that runs inside uasyncio event-loop.\
Features are severely limited comparing to the standard MicroPython REPL, 
only basic repl operations are supported.

NOTE:\
`ctrl+b` for manual linebreak

#### Usage
```python
import uasyncio
import uaiorepl
loop = uasyncio.get_event_loop()
loop.call_soon(uaiorepl.start())
loop.run_forever()
```



## uaiotelnet
Modified telnet server that runs inside uasyncio event-loop.\
Adapted from **cpopp**'s [MicroTelnetServer](https://github.com/cpopp/MicroTelnetServer)

NOTE:\
Must run concurrently with a `uaiorepl` or `uaioinput` otherwise user input will still be blocked.

#### Usage
```python
import uasyncio, uaiotelnet, uaiorepl
loop = uasyncio.get_event_loop()
loop.call_soon(uaiotelnet.start(ip="0.0.0.0", port=23))
loop.call_soon(uaiorepl.start()) # uasyncio repl will process telnet input
loop.run_forever()
```



## uaiowebrepl
Modified WebREPL server that runs inside uasyncio event-loop.\
Adapted from [the offical WebREPL for ESP8266](https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/webrepl.py)

NOTE:\
Must run concurrently with a `uaiorepl` or `uaioinput` otherwise user input will still be blocked.
May have some conflicts with `uaiotelnet` due to `uos.dupterm(,index)` not working properly as of Micropython v1.9.3

#### Usage
```python
import uasyncio, uaiowebrepl, uaiorepl
loop = uasyncio.get_event_loop()
loop.call_soon(uaiowebrepl.start(ip="0.0.0.0", port=8266, password=123))
loop.call_soon(uaiorepl.start()) # uasyncio repl will process webrepl input
loop.run_forever()
```


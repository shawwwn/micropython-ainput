# micropython-ainput
Asynchronous user input libraries using the MicroPython uasyncio library



## uaioinput
Library for for getting user input inside an uasyncio event-loop

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
 * [micropython-uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio)
 * [micropython-uasyncio.synchro](https://github.com/micropython/micropython-lib/tree/master/uasyncio.synchro)



## uaiorepl
A simple(or rather dump) REPL console that runs inside an uasyncio event-loop.\
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

#### Dependencies
 * [micropython-uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio)



## uaiotelnet
A simple telnet server that runs inside an uasyncio event-loop.\
Adapted from **cpopp**'s [MicroTelnetServer](https://github.com/cpopp/MicroTelnetServer)

NOTE:\
Must run concurrently with a `uaiorepl` or `uaioinput` otherwise user input will still be blocked.

#### Usage
```python
import uasyncio, uaiotelnet, uaiorepl
loop = uasyncio.get_event_loop()
loop.call_soon(uaiotelnet.start())
loop.call_soon(uaiorepl.start()) # uasyncio repl will process telnet input
loop.run_forever()
```

#### Dependencies
 * [micropython-uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio)

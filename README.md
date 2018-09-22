# micropython-ainput
Asynchronous user input libraries using MicroPython [uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio) library



## uaioinput <esp32(**\***), esp8266>
Library for for getting user input inside uasyncio event-loop

NOTE(**\***):\
For this to work on esp32, you need to use [my fork of micropython](https://github.com/shawwwn/micropython) which incorperates a hack on the UART console.

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



## uaiorepl <esp32(**\***), esp8266>
A simple(dumb) REPL console that runs inside uasyncio event-loop.\
Features are severely limited comparing to the standard REPL, 
only basic operations are supported.

NOTE(**\***):\
`ctrl+b` for manual linebreak\
For this to work on esp32, you need to use [my fork of micropython](https://github.com/shawwwn/micropython) which incorperates a hack on the UART console.

#### Usage
```python
import uasyncio
import uaiorepl
loop = uasyncio.get_event_loop()
loop.call_soon(uaiorepl.start())
loop.run_forever()
```



## uaiotelnet <esp32(**\***), esp8266>
Modified telnet server that runs inside uasyncio event-loop.\
Adapted from **cpopp**'s [MicroTelnetServer](https://github.com/cpopp/MicroTelnetServer)

NOTE(**\***):\
Must run concurrently with a `uaiorepl` or `uaioinput` otherwise user input will still be blocked.

NOTE:\
If you are using Putty in windows as your telnet client, then you must set the following parameters:\
* Terminal - Local echo - force off
* Terminal - Local line editing - force off
* Connection - Telnet - [UNCHECK] Return key sends Telnet New Line instead of ^M

#### Usage
```python
import uasyncio, uaiotelnet, uaiorepl
loop = uasyncio.get_event_loop()
loop.call_soon(uaiotelnet.start(ip="0.0.0.0", port=23))
loop.call_soon(uaiorepl.start()) # uasyncio repl will process telnet input
loop.run_forever()
```



## uaiowebrepl <esp32(**\***), esp8266>
The offical implementation of WebREPL relies on socket interrupt and can be horribly slow.
This modified WebREPL runs inside uasyncio event-loop and is way faster than the official one.\
Adapted from [the offical WebREPL for ESP8266](https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/webrepl.py)

NOTE:\
Must run concurrently with `uaiorepl` or `uaioinput` otherwise user input will still be blocked.

#### Usage
```python
import uasyncio, uaiowebrepl, uaiorepl
loop = uasyncio.get_event_loop()
loop.call_soon(uaiowebrepl.start(ip="0.0.0.0", port=8266, password=123))
loop.call_soon(uaiorepl.start()) # uasyncio repl will process webrepl input
loop.run_forever()
```


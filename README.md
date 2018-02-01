# micropython-ainput
Asynchronous user input libraries using the MicroPython uasyncio library

## uaioinput
Library for for getting user input inside an uasyncio event-loop

### Usage
```python
import uasyncio
from uaioinput import ainput
s = await ainput(prompt="User Input: ", password=False)
print(s)
```

To prevent two `ainput()` being called at the same time, a global **lock** is 
implemented at the module level.
To check **lock** status,
```python
import uaioinput
print(uaioinput.input_lock.locked)
```

### Dependencies
 * [micropython-uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio)
 * [micropython-uasyncio.synchro](https://github.com/micropython/micropython-lib/tree/master/uasyncio.synchro)
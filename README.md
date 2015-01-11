# HTTPServer
HTTP Server wit Micro Phython

wiering
-------

```
C3K pin | board pin
-----------+----------
    GND     |    GND
    Vin     |    Vin
    IRG     |    Y3
    V3EN    |    Y4
    CS      |    Y5
    CLK     |    Y6
    MISO    |    Y7
    MOSI    |    Y8
```


using
-----
add the password in inic3k.py

per PnTTY (Win7)
```
import inic3k
inic3k.ini()

import httpserver86
httpserver86.ini('',80)
```

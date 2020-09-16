# Divar post discover

https://divar.ir/ post discover and save to microsoft excel file
use the onion router for bypass blocking the IP

Dependencies:

Python3 libraries:
  requests
  bs4
  stem
  openpyxl

/etc/tor/torrc:

**...
ControlPort: 9051
**

If you have trouble connecting to the tor please check bridges ( https://bridges.torproject.org/bridges )
and add this lines to /etc/tor/torrc:

**...
UseBridges 1
Bridge [1st bridge]
Bridge [2st bridge]
Bridge [3st bridge]
**




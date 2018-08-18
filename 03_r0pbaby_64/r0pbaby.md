# r0pbaby

## checksec 

```
checksec --file r0pbaby
```

```
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
No RELRO        No canary found   NX enabled    PIE enabled     No RPATH   No RUNPATH   r0pbaby
```

NX有効でカナリーも有効。
問題名からしてROPを使うのだろう。

## 実行

```bash
socat TCP-LISTEN:1234,reuseaddr,fork exec:./r0pbaby,stderr
```

してホスト側から以下のコメンドで実行

```
nc 192.168.33.12 1234
```

親切にlibcのアドレスなどを教えてくれる模様

```
Welcome to an easy Return Oriented Programming challenge...
Menu:
1) Get libc address
2) Get address of a libc function
3) Nom nom r0p buffer to stack
4) Exit
: 
```

## libc.so.6の場所を確認

```
ldd r0pbaby
```

`/lib/x86_64-linux-gnu/libc.so.6`にあるとわかる。

```
	linux-vdso.so.1 =>  (0x00007fff4b1b6000)
	libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f43bddaf000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f43bd9e5000)
	/lib64/ld-linux-x86-64.so.2 (0x0000564f68f7f000)
```

---

libc.so.6のパスがわかったので、そのままsystem関数へのオフセットも調べる。

```
nm -D /lib/x86_64-linux-gnu/libc.so.6| grep system
```

`0000000000045390`らしい。

```
0000000000045390 T __libc_system
0000000000138810 T svcerr_systemerr
0000000000045390 W system
```

---

`"bin/sh"`のオフセットも調べる。

```
strings -a -tx /lib/x86_64-linux-gnu/libc.so.6 | grep sh$
```

`18cd57`らしい。

```
  11e62 inet6_opt_finish
  12d5b _IO_wdefault_finish
  12f86 bdflush
  13302 _IO_fflush
  13379 _IO_file_finish
  159c3 tcflush
  15c53 _IO_default_finish
 18a145 Trailing backslash
 18acf8 sys/net/ash
 18cd57 /bin/sh
 18e8e2 /bin/csh
 1c6e11 .gnu.hash
 1c711b .gnu.warning.__compat_bdflush
```


## rop gadegetの位置を調べる

```
rp -f /lib/x86_64-linux-gnu/libc.so.6 -r 1 | grep 'pop rdi'
```


`0x00021102`あたりを使えば良い。

```
0x0010741a: pop rdi ; call rax ;  (1 found)
0x000f9901: pop rdi ; jmp qword [rbp+rax*2-0x77] ;  (1 found)
0x000f994a: pop rdi ; jmp qword [rbp+rax*2-0x77] ;  (1 found)
0x00104052: pop rdi ; jmp rax ;  (1 found)
0x00037861: pop rdi ; rep ret  ;  (1 found)
0x0007926e: pop rdi ; rep ret  ;  (1 found)
0x0007f35b: pop rdi ; rep ret  ;  (1 found)
0x00116170: pop rdi ; rep ret  ;  (1 found)
0x00138d7d: pop rdi ; rep ret  ;  (1 found)
0x00021102: pop rdi ; ret  ;  (1 found)
0x0002111a: pop rdi ; ret  ;  (1 found)
0x00021142: pop rdi ; ret  ;  (1 found)
.
.
.

```


```
rp -f r0pbaby -r 1 | grep pop
```

`pop rdi` となっている`0x00000f23`を使えば良さそうである。

```
0x00000bf4: pop r14 ; ret  ;  (1 found)
0x00000f22: pop r15 ; ret  ;  (1 found)
0x00000ab8: pop rbp ; jmp rax ;  (1 found)
0x00000ab9: pop rbp ; jmp rax ;  (1 found)
0x00000aab: pop rbp ; ret  ;  (1 found)
0x00000ae8: pop rbp ; ret  ;  (1 found)
0x00000eb2: pop rbp ; ret  ;  (1 found)
0x00000f23: pop rdi ; ret  ;  (1 found)
0x00000bf5: pop rsi ; ret  ;  (1 found)
```
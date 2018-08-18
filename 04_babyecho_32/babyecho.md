# babyecho

## fileコマンド
32bitのELF
strippedなので関数を読み解く必要あり。辛い。

```
babyecho: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, for GNU/Linux 2.6.24, BuildID[sha1]=c9a66685159ad72bd157b521f05a85e2e427f5ee, stripped
```

## とりあえず実行
13バイト読み込んで表示するプログラムの用。
FSK（Format String Attack）が使えることを確認。
入力した文字列は7バイト目に格納される模様。

```
Reading 13 bytes
hoge
hoge
Reading 13 bytes
hogefjaoudsfdf
hogefjaoudsf
Reading 13 bytes
f
Reading 13 bytes
1234568790123
123456879012
Reading 13 bytes

Reading 13 bytes
123456789012
123456789012
Reading 13 bytes
%x%x%x%x%x]
da0dbfc62ccc]
Reading 13 bytes
aaaa%x
aaaad
Reading 13 bytes
AAAA%2$x
AAAAa
Reading 13 bytes
AAAA%3$x
AAAA0
Reading 13 bytes
AAAA%4$x
AAAAd
Reading 13 bytes
AAAA%5$x
AAAAbfc62ccc
Reading 13 bytes
AAAA%6$x
AAAA0
Reading 13 bytes
AAAA%7$x
AAAA41414141
```

## checksec

```
checksec --file babyecho
```

全ての脆弱性がある。
Partial RELROなので、GOT overwrite っぽい。
と思ったが、strippedなのでNXがdisableなのを利用してシェルコード。


```
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   babyecho
```

## gdb-pedaで解析

メイン関数がないので、`start`後、`x`コマンドで命令を見ていく。

```
x/20i  0x8048d0a
```

`0x8049050`だけ呼ばれているから、ここが主な関数かな。

```
=> 0x8048d0a:	xor    ebp,ebp
   0x8048d0c:	pop    esi
   0x8048d0d:	mov    ecx,esp
   0x8048d0f:	and    esp,0xfffffff0
   0x8048d12:	push   eax
   0x8048d13:	push   esp
   0x8048d14:	push   edx
   0x8048d15:	push   0x80497d0
   0x8048d1a:	push   0x8049730
   0x8048d1f:	push   ecx
   0x8048d20:	push   esi
   0x8048d21:	push   0x8048f3c
   0x8048d26:	call   0x8049050
   0x8048d2b:	hlt
   0x8048d2c:	xchg   ax,ax
   0x8048d2e:	xchg   ax,ax
   0x8048d30:	mov    ebx,DWORD PTR [esp]
   0x8048d33:	ret
```

`0x8049050`は200行以上ある、、。

ひたすら`ni`で進めて、fget関数が呼ばれているっぽいところは
`0x8049216: call DWORD PTR [esp+0x60]`だった。
`esp+0x60`を調べると、`0x08048f3c`である。

```
gdb-peda$ x $esp+0x60
0xbffffbd0:	0x08048f3c
```

`0x08048f3c`では、`0x8048ff7:	call   0x8048e24`が怪しい。

`0x8048e24`を調べてみると、`0x8048e24`関数内部の`0x806d4b0`関数が１文字ずつ受け付けるっぽい。
この関数では、第二引数（`ebp+0xc`）の回数だけループしている。

ここまでの情報から、`0x8048e24`がfgets関数っぽい。



```
# スタック配置(引数)
ebp+0x8	: 0xbffff740 --> 0xbffff75c --> 0x0
ebp+0xc	: 0xbffff744 --> 0xd ('\r')
ebp+0x10	: 0xbffff748 --> 0xa ('\n')
```

```
# 関数 0x8048e24

0x8048e24:	push   ebp
0x8048e25:	mov    ebp,esp
0x8048e27:	sub    esp,0x28
0x8048e2a:	mov    eax,DWORD PTR [ebp+0x10]
0x8048e2d:	mov    BYTE PTR [ebp-0x1c],al
0x8048e30:	mov    DWORD PTR [ebp-0xc],0x0
0x8048e37:	jmp    0x8048e93

.
.
.

0x8048e93:	mov    eax,DWORD PTR [ebp-0xc]
0x8048e96:	cmp    eax,DWORD PTR [ebp+0xc]
0x8048e99:	jl     0x8048e39

.
.
.


0x8048eaf:	leave
0x8048eb0:	ret
```

`0x8048e24`関数を呼び出しているところを見てみる。

espの値は`0xbffff740`なので、+10の`0xbffff750`を大きな数字に書き換えれば良いのでは。

```
# 関数 0x8048f3c

   0x8048f3c:	push   ebp
   0x8048f3d:	mov    ebp,esp
   0x8048f3f:	and    esp,0xfffffff0
   0x8048f42:	sub    esp,0x420
   0x8048f48:	mov    eax,gs:0x14
   0x8048f4e:	mov    DWORD PTR [esp+0x41c],eax
   0x8048f55:	xor    eax,eax
   0x8048f57:	lea    eax,[esp+0x1c]
   0x8048f5b:	mov    DWORD PTR [esp+0x14],eax
   0x8048f5f:	mov    DWORD PTR [esp+0x18],0x0
   0x8048f67:	mov    DWORD PTR [esp+0x10],0xd
   0x8048f6f:	mov    eax,ds:0x80ea4c0
   0x8048f74:	mov    DWORD PTR [esp+0xc],0x0
   0x8048f7c:	mov    DWORD PTR [esp+0x8],0x2
   0x8048f84:	mov    DWORD PTR [esp+0x4],0x0
   0x8048f8c:	mov    DWORD PTR [esp],eax
   0x8048f8f:	call   0x804fc40
   0x8048f94:	mov    DWORD PTR [esp+0x4],0x8048eb1
   0x8048f9c:	mov    DWORD PTR [esp],0xe
   0x8048fa3:	call   0x804de70
   0x8048fa8:	mov    DWORD PTR [esp],0x14
   0x8048faf:	call   0x806cb50
   0x8048fb4:	jmp    0x804902c
   0x8048fb6:	mov    eax,0x3ff
   0x8048fbb:	cmp    DWORD PTR [esp+0x10],0x3ff
   0x8048fc3:	cmovle eax,DWORD PTR [esp+0x10]
   0x8048fc8:	mov    DWORD PTR [esp+0x10],eax
   0x8048fcc:	mov    eax,DWORD PTR [esp+0x10]
   0x8048fd0:	mov    DWORD PTR [esp+0x4],eax
   0x8048fd4:	mov    DWORD PTR [esp],0x80be5f1
   0x8048fdb:	call   0x804f560
   0x8048fe0:	mov    DWORD PTR [esp+0x8],0xa
   0x8048fe8:	mov    eax,DWORD PTR [esp+0x10]
   0x8048fec:	mov    DWORD PTR [esp+0x4],eax
   0x8048ff0:	lea    eax,[esp+0x1c]
   0x8048ff4:	mov    DWORD PTR [esp],eax
   0x8048ff7:	call   0x8048e24
   0x8048ffc:	lea    eax,[esp+0x1c]
   0x8049000:	mov    DWORD PTR [esp],eax
   0x8049003:	call   0x8048ecf
   0x8049008:	lea    eax,[esp+0x1c]
   0x804900c:	mov    DWORD PTR [esp],eax
   0x804900f:	call   0x804f560
   0x8049014:	mov    DWORD PTR [esp],0xa
   0x804901b:	call   0x804fde0
   0x8049020:	mov    DWORD PTR [esp],0x14
   0x8049027:	call   0x806cb50
   0x804902c:	cmp    DWORD PTR [esp+0x18],0x0
   0x8049031:	je     0x8048fb6
   0x8049033:	mov    eax,0x0
   0x8049038:	mov    edx,DWORD PTR [esp+0x41c]
   0x804903f:	xor    edx,DWORD PTR gs:0x14
   0x8049046:	je     0x804904d
   0x8049048:	call   0x806f1f0
   0x804904d:	leave
   0x804904e:	ret
```


入力が`esp + 1ch`

入力文字数を決めているのが`esp + 10h` 

リターンアドレスは`esp + 42ch`

無限ループを回しているのが、`esp + 0x18`


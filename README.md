# pangu.py

将饱负盛名的 [`pangu.vim`][1] Vim 插件移植到 Python3 以便用在其它地方。

---

Port the wellknown [`pangu.vim`][1] Vim plugin to Python3 so that it can be used everywhere!
Usage: `pangu.py FILE` or `cat <SOMETHING> | pangu.py -`.
Options are the same as `pangu.vim`'s `g:pangu_rule_*` variables.
See `pangu.py --help` for detailed help.

I'll sync the functionality with my fork of [`pangu.vim`][2].
However, there's currently no support of range operation in `pangu.py`.

## Configure as [`vim-autoformat`][3] formatter

```bash
# make it executable if not yet
chmod u+x pangu.py

# cp or symlink pangu.py to somewhere under PATH;
# here I cp it to ~/bin
cp pangu.py ~/bin
```

Then in `~/.vimrc`,

```vim
" the trailing `-' is important
let g:formatdef_pangupy = '"pangu.py --no-fullwidth-punctuation --date=1 -"'
let g:formatters_markdown = ['pangupy']
```

Execute `:Autoformat` in a markdown file will launch `pangu.py` on that file.


[1]: https://github.com/hotoo/pangu.vim
[2]: https://github.com/kkew3/pangu.vim
[3]: https://github.com/vim-autoformat/vim-autoformat

# Match-Bracket-And-Pangu-Format

A little tool to check markdown file's bracket match and use `Pangu.js` to add space, which makes your markdown more elegently.

一个小工具，检查 Markdown 文件的括号匹配，并使用 `Pangu.js` 添加空格，让您的 Markdown 更优雅。

## Feature

### Match Bracket

1. 忽略中英文差别，逐行检查括号是否匹配，如果不匹配，提示。
2. 如果括号匹配，按照左括号的类型对应调整右括号的语言类型。
3. 检查所有英文左括号，如果有其左右任一为中文字符，则将其与其配对的括号替换为中文括号



### Pangu Format

1. 使用 `Pangu.js` 来对文件格式化
2. 忽略可以被正则表达式 `r'(<img src)|!\[.*?\]\(.*?\)|^\n$'` 匹配到的行。这是为了避免图片的文件路径被不正确的格式化。
3. 去除 `Pangu.js` 错误地在加粗语法中添加的空格
4. 修复因 `Pangu.js` 最后调用 `.strip ()` 而被移除的行首空格和行末回车



### Other

该脚本接收 0 或 1 个参数：

* 0 参数：默认对当前路径下所有 markdown 文件执行操作
* 1 参数：如果为 markdown 文件，则仅对该文件执行操作；如果为路径，则对给定路径下所有 markdown 文件执行操作



### For Typora

**请注意：Typora 默认使用终端为 Bash 而不是 zsh**，所以如果你和我一样使用了 `pyenv` 来控制 Python 版本，你可能需要按照 [pyenv 指引](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)，来调整你的 `~/.bash_profile` （而不是 `~/.bashrc`）！！

> [Why doesn't .bashrc run automatically?](https://apple.stackexchange.com/questions/12993/why-doesnt-bashrc-run-automatically)

按照自定义导出，调整命令为

```bash
python3 ~/path/to/BracketMatch\&PanguSpace.py ${currentPath}
```

或者

```bash
python3 ~/path/to/BracketMatch\&PanguSpace.py ${currentFolder}
```



当然，你可以在去 `系统设置 - 键盘 - 键盘快捷键 - App 快捷键` 内为这个命令设定快捷键。

如果你不希望有输出，你可以使用快捷指令来通过 shell 运行此脚本。


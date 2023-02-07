# Match-Bracket-And-Pangu-Format

A little tool to check markdown file's bracket match and use `Pangu.js` to add space, which makes your markdown more elegently.

一个小工具，检查 Markdown 文件的括号匹配，并使用 `Pangu.js` 添加空格，让您的 Markdown 更优雅。

## Feature

### Match Bracket

1. 忽略代码块和 LaTeX 公式块（包括行内代码和行内LaTeX公式）内的内容。
2. 忽略中英文差别，逐行检查括号是否匹配，如果不匹配，提示。
3. 如果括号匹配，按照左括号的类型对应调整右括号的语言类型。
4. 检查所有英文左括号，如果有其左右任一为中文字符，则将其与其配对的括号替换为中文括号。



### Pangu Format

1. 忽略代码块和 LaTeX 公式块（包括行内代码和行内LaTeX公式）内的内容。
2. 使用 `Pangu.js` 来对文件格式化。
3. 忽略可以被正则表达式 `r'(<img src)|!\[.*?\]\(.*?\)|^\n$'` 匹配到的行。这是为了避免图片的文件路径被不正确的格式化。
4. 去除 `Pangu.js` 错误地在加粗语法中添加的空格。
5. 修复因 `Pangu.js` 最后调用 `.strip ()` 而被移除的行首空格和行末回车。



## Usage

```bash
usage: BracketMatchAndPanguSpace.py [-h] [-r] [--no-bracket] [--no-pangu] [path]

Format markdown file, including pangu format and bracket match.

positional arguments:
  path             file or directory to format

options:
  -h, --help       show this help message and exit
  -r, --recursive  recursive format directory
  --no-bracket     disable bracket match
  --no-pangu       disable pangu format
```

参数说明：

`path`：文件 / 文件夹路径，如果为 markdown 文件，则仅对该文件执行操作；如果为路径，则对给定路径下所有 markdown 文件执行操作。

`-r`：指定此参数时，对给定的 `path` 文件夹下递归查找所有 `.md` 文件并执行操作。

`--no-bracket`：不进行括号匹配操作。

`--no-pangu`：不进行 `Pangu.js` 格式化的操作。



### For Typora

**请注意：Typora 默认使用终端为 Bash 而不是 zsh**，所以如果你和我一样使用了 `pyenv` 来控制 Python 版本，你可能需要按照 [pyenv 指引](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)，来调整你的 `~/.bash_profile` （而不是 `~/.bashrc`）！！

> [Why doesn't .bashrc run automatically?](https://apple.stackexchange.com/questions/12993/why-doesnt-bashrc-run-automatically)

按照自定义导出，调整命令为

```bash
python3 ~/path/to/BracketMatchAndPanguSpace.py ${currentPath}
```

或者

```bash
python3 ~/path/to/BracketMatchAndPanguSpace.py ${currentFolder}
```



当然，你可以在去 `系统设置 - 键盘 - 键盘快捷键 - App 快捷键` 内为这个命令设定快捷键。



### For Shortcuts

如果你不希望有输出，你可以使用 `快捷指令` 来通过 shell 运行此脚本。

以下是一个例子：

```bash
source ~/.zshrc && python3 /path/to/BracketMatchAndPanguSpace.py /targetPath
```

![Cleanshot-2023-02-06-at-01.07.53](./README.assets/Cleanshot-2023-02-06-at-01.07.53.png)




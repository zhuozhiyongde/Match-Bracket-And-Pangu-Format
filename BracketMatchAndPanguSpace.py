# -*- encoding: utf-8 -*-
#@Author  :   Arthals
#@File    :   BracketMatchAndPanguSpace.py
#@Time    :   2023/02/02 20:35:56
#@Contact :   zhuozhiyongde@126.com
#@Software:   Visual Studio Code

import re
import os
import pangu
import argparse


def match_brackets(origin_text: str):
    # 忽略图片行、空行
    pattern = re.compile(r'(<img src)|!\[.*?\]\(.*?\)|^\n$')
    if pattern.search(origin_text):
        return origin_text
    # 将所有中文圆括号替换为英文圆括号
    text = origin_text.replace('（', '(').replace('）', ')')

    # 使用栈检查括号匹配
    stack = []
    for i in range(len(text)):
        if text[i] == '(':
            stack.append(text[i])
        elif text[i] == ')':
            if not stack or stack[-1] != '(':
                return False
            stack.pop()

    if stack:
        return False

    # 已知忽略中英文差别下括号匹配，递归从左到右按照左括号类型进行匹配
    new_text = origin_text
    left_brackets_stack = []
    for i in range(len(origin_text)):
        if re.match(r'\(|（', origin_text[i]):
            left_brackets_stack.append(origin_text[i])
        elif re.match(r'\)|）', origin_text[i]):
            right_bracket = ')' if left_brackets_stack[-1] == '(' else '）'
            left_brackets_stack.pop()
            new_text = new_text[:i] + right_bracket + new_text[i + 1:]

    # 以下为自定义的其他替换规则
    # 目的：只要左括号左右字符任一为中文，就将左右括号替换为中文括号
    # 将所有形如`中文()`的类型递归替换为`中文（）`
    pattern = re.compile(r'(?<=[\u4e00-\u9fff])\(([^(]*?)\)')
    while True:
        text = new_text
        new_text = re.sub(pattern, '（\\1）', new_text)
        if text == new_text:
            break

    # 将所有形如`(第一个字符为中文)`的类型递归替换为`（文本）`
    pattern = re.compile(r'\(([\u4e00-\u9fff][^\(]*?)\)')
    while True:
        text = new_text
        new_text = re.sub(pattern, '（\\1）', new_text)
        if text == new_text:
            break

    return new_text


def find_inline_latex(text: str):
    latex_blocks = re.compile(
        r'(?s)(?<!\\)\$\$(.*?)(?<!\\)\$\$|(?<!\\)\$(.*?)(?<!\\)\$')
    return [(m.start(), m.end()) for m in latex_blocks.finditer(text)]


def pangu_format_line(line: str) -> str:
    # 忽略图片行、空行
    pattern = re.compile(r'(<img src)|!\[.*?\]\(.*?\)|^\n$')
    if pattern.search(line):
        return line

    latex_blocks = find_inline_latex(line)
    result = []
    start = 0
    for start_inx, end_inx in latex_blocks:
        result.append(pangu.spacing_text(line[start:start_inx]))
        result.append(line[start_inx:end_inx])
        start = end_inx
    result.append(pangu.spacing_text(line[start:]))
    new_line = ''.join(result)

    # 去除 Pangu.js 错误的在加粗语法**text**中添加的空格
    pattern = re.compile(r'(?<=\*\*)[^\*]*?(?=\*\*)')
    new_line = pattern.sub(lambda x: x.group().strip(), new_line)

    # Pangu.js 最后调用了 .strip() 方法，导致最后一行的换行符被去除，这里补上
    if not new_line.endswith('\n'):
        new_line += '\n'

    # 同上原因，还会移除行首空格，这里补上
    if re.match(r' +', line):
        new_line = re.match(r' +', line).group() + new_line.lstrip()

    return new_line


def format_file(file: str,
                show_info: bool = True,
                do_bracket_format: bool = True,
                do_pangu_format: bool = True):
    if not file.endswith('.md'):
        return False

    if not do_bracket_format and not do_pangu_format:
        return False

    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 匹配括号
    bracket_flag = False
    code_block_flag = False
    latex_block_flag = False
    code_block_index = []
    latex_block_index = []
    match_flag = False
    for i in range(len(lines)):
        line = lines[i]

        # 忽略代码块和行内公式
        if re.match(r'```', line):
            if code_block_flag is True:
                code_block_index[-1].append(i)
            else:
                code_block_index.append([i])

            code_block_flag = not code_block_flag
            continue

        elif re.match(r'\$\$', line):
            if not code_block_flag:
                if latex_block_flag is True:
                    latex_block_index[-1].append(i)
                else:
                    latex_block_index.append([i])

                latex_block_flag = not latex_block_flag
                continue

        if not do_bracket_format:
            continue

        if re.search(r'[\(\)（）]', line):
            new_line = match_brackets(line)
            if new_line is False:
                print('Error in file: %s, line: %d' % (file, i + 1))
                print('Error line: %s' % line)
                match_flag = True
                continue

            if new_line == line:
                continue

            lines[i] = new_line
            bracket_flag = True
            print('File: %s, line: %d bracket formatted' % (file, i + 1))

    if not do_bracket_format:
        if not bracket_flag and not match_flag:
            print('File: %s, no bracket error' % file)

        if match_flag:
            print('File: %s, bracket match error' % file)

    # pangu format lines
    pangu_flag = False
    new_lines = []
    ignore_lines = [item for sublist in code_block_index for item in sublist] + \
        [item for sublist in latex_block_index for item in sublist]
    # 去重（其实不必要）
    ignore_lines = list(set(ignore_lines))

    for i in range(len(lines)):
        # 忽略代码块、公式块
        if i in ignore_lines:
            new_lines.append(lines[i])
            continue

        if not do_pangu_format:
            new_lines.append(lines[i])
            continue

        new_line = pangu_format_line(lines[i])

        new_lines.append(new_line)
        if new_line != lines[i]:
            print('File: %s, line: %d pangu formatted' % (file, i + 1))
            if show_info:
                print([lines[i]], [new_line], '', sep='\n')
            pangu_flag = True

    if not do_pangu_format:
        if not pangu_flag:
            print('File: %s, no pangu format' % file)

    # pangu format lines and write to file
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


parser = argparse.ArgumentParser(
    description=
    'Format markdown file, including pangu format and bracket match.')

parser.add_argument('path',
                    type=str,
                    nargs='?',
                    default='.',
                    help='file or directory to format')
parser.add_argument('-r',
                    '--recursive',
                    action='store_true',
                    default=False,
                    help='recursive format directory')
parser.add_argument('--no-bracket',
                    action='store_true',
                    default=False,
                    help='disable bracket match')
parser.add_argument('--no-pangu',
                    action='store_true',
                    default=False,
                    help='disable pangu format')

if __name__ == '__main__':
    args = parser.parse_args()
    path = args.path
    recursive = args.recursive
    do_bracket = not args.no_bracket
    do_pangu = not args.no_pangu

    if path.endswith('.md'):
        format_file(path,
                    do_bracket_format=do_bracket,
                    do_pangu_format=do_pangu)

    elif os.path.isdir(path):
        if recursive:
            md_files = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.md'):
                        md_files.append(os.path.join(root, file))
            print('Detect %d markdown files' % len(md_files))
            for file in md_files:
                format_file(file,
                            show_info=False,
                            do_bracket_format=do_bracket,
                            do_pangu_format=do_pangu)
        else:
            md_files = [
                file for file in os.listdir(path) if file.endswith('.md')
            ]
            for file in md_files:
                format_file(os.path.join(path, file),
                            show_info=False,
                            do_bracket_format=do_bracket,
                            do_pangu_format=do_pangu)
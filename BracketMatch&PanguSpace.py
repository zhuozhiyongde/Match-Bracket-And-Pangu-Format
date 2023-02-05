# -*- encoding: utf-8 -*-
#@Author  :   Arthals
#@File    :   BracketMatch&PanguSpace.py
#@Time    :   2023/02/02 20:35:56
#@Contact :   zhuozhiyongde@126.com
#@Software:   Visual Studio Code

import re
import os
import sys
import pangu


def match_brackets(origin_text: str):
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


def format_file(file: str):
    if not file.endswith('.md'):
        return False

    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    flag = False
    match_flag = False
    for i in range(len(lines)):
        line = lines[i]

        # 忽略图片行
        pattern = re.compile(r'(<img src)|!\[.*?\]\(.*?\)')
        if pattern.search(line):
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
            flag = True
            print('File: %s, line: %d bracket formatted' % (file, i + 1))

    if not flag and not match_flag:
        print('File: %s, no bracket error' % file)

    if match_flag:
        print('File: %s, bracket match error' % file)

    # pangu format lines
    flag = False
    new_lines = []
    for i in range(len(lines)):
        # 忽略图片行、空行
        pattern = re.compile(r'(<img src)|!\[.*?\]\(.*?\)|^\n$')
        if pattern.search(lines[i]):
            new_lines.append(lines[i])
            continue

        new_line = pangu.spacing_text(lines[i])

        # 去除 Pangu.js 错误的在加粗语法中添加的空格
        pattern = re.compile(r'(?<=\*\*)[^\*]*?(?=\*\*)')
        new_line = pattern.sub(lambda x: x.group().strip(), new_line)

        # Pangu.js 最后调用了 .strip() 方法，导致最后一行的换行符被去除，这里补上
        if not new_line.endswith('\n'):
            new_line = new_line + '\n'

        # 同上原因，还会移除行首空格，这里补上
        if re.match(r' +', lines[i]):
            # print(lines[i])
            new_line = re.match(r' +', lines[i]).group() + new_line.lstrip()

        new_lines.append(new_line)
        if new_line != lines[i]:
            print('File: %s, line: %d pangu formatted:' % (file, i + 1))
            print([lines[i]], [new_line], sep='\n')
            flag = True

    if not flag:
        print('File: %s, no pangu format' % file)

    # pangu format lines and write to file
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


if __name__ == '__main__':

    print(sys.argv[0])
    print(os.listdir('.'))
    # exit()

    # 检查参数，如果参数指定为文件，则只对该文件进行括号匹配和空格格式化，如果为目录，则对目录下所有md文件进行括号匹配和空格格式化。如果未指定参数，则对当前目录下所有md文件进行括号匹配和空格格式化。
    if len(sys.argv) == 2:
        if sys.argv[1].endswith('.md'):
            format_file(sys.argv[1])
        elif os.path.isdir(sys.argv[1]):
            md_files = [
                file for file in os.listdir(sys.argv[1])
                if file.endswith('.md')
            ]
            for file in md_files:
                format_file(f'{sys.argv[1]}/{file}')

    elif len(sys.argv) == 1:
        md_files = [file for file in os.listdir('.') if file.endswith('.md')]
        for file in md_files:
            format_file(file)
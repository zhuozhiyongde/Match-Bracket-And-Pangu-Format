# -*- encoding: utf-8 -*-
# @Author  :   Arthals
# @File    :   BracketMatchAndPanguSpace.py
# @Time    :   2023/02/07 19:36:35
# @Contact :   zhuozhiyongde@126.com
# @Software:   Visual Studio Code

import re
import os
import pangu
import argparse


def process_text(
    origin_text: str, do_match_brackets: bool, do_pangu_format: bool
) -> list:
    """
    处理文本，返回处理后结果列表

    Parameters
    ----------
    origin_text : str
        原始文本
    do_match_brackets : bool
        是否进行括号匹配
    do_pangu_format : bool
        是否进行格式化

    Returns
    -------
    list
        处理后结果列表
        list[0] : int, -1:括号匹配失败, 0:未操作, 1:括号匹配成功
        list[1] : int, -1:格式化失败, 0:未操作, 1:格式化成功
        list[2] : str, 处理后文本
    """

    def remove_space_between_chinese(origin_text: str) -> str:
        # 去除中文之间的空格
        pattern = re.compile(r"(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])")
        return pattern.sub("", origin_text)

    def match_brackets(origin_text: str) -> str:
        # 将所有中文圆括号替换为英文圆括号
        text = origin_text.replace("（", "(").replace("）", ")")

        # 使用栈检查括号匹配
        stack = []
        for i in range(len(text)):
            if text[i] == "(":
                stack.append(text[i])
            elif text[i] == ")":
                if not stack or stack[-1] != "(":
                    return False
                stack.pop()

        if stack:
            return False

        # 已知忽略中英文差别下括号匹配，递归从左到右按照左括号类型进行匹配
        new_text = origin_text
        left_brackets_stack = []
        for i in range(len(origin_text)):
            if re.match(r"\(|（", origin_text[i]):
                left_brackets_stack.append(origin_text[i])
            elif re.match(r"\)|）", origin_text[i]):
                right_bracket = ")" if left_brackets_stack[-1] == "(" else "）"
                left_brackets_stack.pop()
                new_text = new_text[:i] + right_bracket + new_text[i + 1 :]

        # 以下为自定义的其他替换规则
        # 目的：只要左括号左右字符任一为中文，就将左右括号替换为中文括号
        # 将所有形如`中文()`的类型递归替换为`中文（）`
        pattern = re.compile(r"(?<=[\u4e00-\u9fff])\(([^(]*?)\)")
        while True:
            text = new_text
            new_text = re.sub(pattern, "（\\1）", new_text)
            if text == new_text:
                break

        # 将所有形如`(第一个字符为中文)`的类型递归替换为`（文本）`
        pattern = re.compile(r"\(([\u4e00-\u9fff][^\(]*?)\)")
        while True:
            text = new_text
            new_text = re.sub(pattern, "（\\1）", new_text)
            if text == new_text:
                break

        return new_text

    text = origin_text
    print(f"Origin: {origin_text}")
    return_result = [0, 0, origin_text]

    # 存储所有的latex块
    latex_blocks_pattern = re.compile(
        r"(?<!\\)\$(?<!\\)\$(.*?)(?<!\\)\$(?<!\\)\$|(?<!\\)\$(.*?)(?<!\\)\$|(?<!\\)`(.*?)(?<!\\)`|\[.*?\]\(.*?\)|(?<!\\)~(?<!\\)~(.*?)(?<!\\)~(?<!\\)~",
        re.S,
    )
    # [(start, end, text), ...]
    latex_blocks = [m.group() for m in latex_blocks_pattern.finditer(text)]

    # 将latex块替换为占位符
    text = re.sub(latex_blocks_pattern, "$__latex__or__code__part__$", text)

    # 处理括号匹配
    if do_match_brackets:
        # save seperated text lens

        text = remove_space_between_chinese(text)
        print(f"Removed space: {text}")
        text = match_brackets(text)

        if text is False:
            return_result[0] = -1
            return return_result

        # restore seperated text
        else:
            return_result[0] = 1

    # 处理 pangu.js
    if do_pangu_format:
        text = pangu.spacing_text(text)

        # 去除 Pangu.js 错误的在加粗语法**text**中添加的空格
        pattern = re.compile(r"(?<=\*\*)[^\*]*?(?=\*\*)")
        text = pattern.sub(lambda x: x.group().strip(), text)

        # Pangu.js 最后调用了 .strip() 方法，会移除行首空格，这里补上
        if re.match(r" +", origin_text):
            text = re.match(r" +", origin_text).group() + text.lstrip()

        # 同上原因，导致最后一行的换行符被去除，这里补上
        if not text.endswith("\n"):
            text += "\n"

        # 换回latex块
        text = re.sub(
            r"\$__latex__or__code__part__\$", lambda x: latex_blocks.pop(0), text
        )

        # 重新处理删除语法
        delete_pattern = re.compile(r"(?<!\\)~(?<!\\)~(.*?)(?<!\\)~(?<!\\)~")
        delete_blocks = [m.group() for m in delete_pattern.finditer(text)]
        for i, block in enumerate(delete_blocks):
            inside = block[2:-2]
            latex_blocks_pattern = re.compile(
                r"(?<!\\)\$(?<!\\)\$(.*?)(?<!\\)\$(?<!\\)\$|(?<!\\)\$(.*?)(?<!\\)\$|(?<!\\)`(.*?)(?<!\\)`|\[.*?\]\(.*?\)",
                re.S,
            )
            latex_blocks = [m.group() for m in latex_blocks_pattern.finditer(inside)]
            inside = re.sub(latex_blocks_pattern, "$__latex__or__code__part__$", inside)
            inside = pangu.spacing_text(inside)
            inside = re.sub(
                r"\$__latex__or__code__part__\$", lambda x: latex_blocks.pop(0), inside
            )
            delete_blocks[i] = "~~" + inside + "~~"
        text = re.sub(delete_pattern, lambda x: delete_blocks.pop(0), text)

        if text != origin_text:
            return_result[1] = 1

        return_result[2] = text

    return return_result


def format_file(
    file: str,
    show_info: bool = True,
    do_match_brackets: bool = True,
    do_pangu_format: bool = True,
):
    if not file.endswith((".md", "markdown")):
        return False

    if not do_match_brackets and not do_pangu_format:
        return False

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    code_block_flag = False
    latex_block_flag = False

    # 匹配括号
    do_bracket_flag = False
    do_pangu_flag = False
    error_match_flag = False
    error_match_list = []

    for i in range(len(lines)):
        line = lines[i]
        # 忽略图片行、空行
        pattern = re.compile(r"(<img src)|!\[.*?\]\(.*?\)|^\n$")
        if pattern.search(line):
            continue

        if re.match(r"```", line):
            code_block_flag = not code_block_flag
            continue

        elif re.match(r"\$\$", line) or re.search(r"\$\$\n?$", line):
            if not code_block_flag:
                if re.search(r"\$\$.*\$\$", line):
                    continue
                latex_block_flag = not latex_block_flag
                continue

        # 忽略代码块和行内公式
        if code_block_flag or latex_block_flag:
            continue

        # print('formatting line %d' % (i + 1))
        try:
            result = process_text(line, do_match_brackets, do_pangu_format)
        except Exception as e:
            print("File: %s Error line: %s" % (file, line))
            print(e)
            raise e

        if result[0] == -1:
            print("File: %s Match brackets Error, line: %d" % (file, i + 1))
            print("File: %s Error line: %s" % (file, line))
            error_match_flag = True
            error_match_list.append(i + 1)

        if result[0] == 1:
            # print("File: %s, line: %d brackets matched" % (file, i + 1))
            do_bracket_flag = True

        if result[1] == 1:
            # print("File: %s, line: %d pangu formatted" % (file, i + 1))
            do_pangu_flag = True

            if show_info:
                print([lines[i]], [result[2]], sep="\n")

        lines[i] = result[2]

    # print result
    print("Summary for File: %s" % file)
    if error_match_flag:
        print("File: %s Match brackets Error in %s" % (file, error_match_list))
    if do_bracket_flag and not error_match_flag:
        print("File: %s Match brackets Success" % file)
    elif not do_match_brackets and not error_match_flag:
        print("File: %s Match brackets No need" % file)
    if do_pangu_flag:
        print("File: %s Pangu format Success" % file)
    else:
        print("File: %s Pangu format No need" % file)
    print("----------------------------------------")

    with open(file, "w", encoding="utf-8") as f:
        f.writelines(lines)


parser = argparse.ArgumentParser(
    description="Format markdown file, including pangu format and bracket match."
)
parser.add_argument(
    "path", type=str, nargs="?", default=".", help="file or directory to format"
)
parser.add_argument(
    "-r",
    "--recursive",
    action="store_true",
    default=False,
    help="recursive format directory",
)
parser.add_argument(
    "--no-bracket", action="store_true", default=False, help="disable bracket match"
)
parser.add_argument(
    "--no-pangu", action="store_true", default=False, help="disable pangu format"
)

if __name__ == "__main__":
    args = parser.parse_args()
    path = args.path
    recursive = args.recursive
    do_bracket = not args.no_bracket
    do_pangu = not args.no_pangu

    if path.endswith((".md", ".markdown")):
        format_file(path, do_match_brackets=do_bracket, do_pangu_format=do_pangu)

    elif os.path.isdir(path):
        if recursive:
            md_files = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith((".md", ".markdown")):
                        md_files.append(os.path.join(root, file))
            print("Detect %d markdown files" % len(md_files))
            for file in md_files:
                format_file(
                    file,
                    show_info=False,
                    do_match_brackets=do_bracket,
                    do_pangu_format=do_pangu,
                )
        else:
            md_files = [
                file for file in os.listdir(path) if file.endswith((".md", ".markdown"))
            ]
            for file in md_files:
                format_file(
                    os.path.join(path, file),
                    show_info=False,
                    do_match_brackets=do_bracket,
                    do_pangu_format=do_pangu,
                )

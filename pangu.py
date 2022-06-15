#!/usr/bin/env python3
"""
Adapted from GitHub "hotoo/pangu.vim".
"""
import argparse
import re
import sys

hans = r'[\u4e00-\u9fa5\u3040-\u30FF]'


def make_parser():
    parser = argparse.ArgumentParser(description='自动格式化、规范化中文排版。')
    parser.add_argument(
        '--no-fullwidth-punctuation',
        dest='fullwidth_punctuation',
        action='store_false')
    parser.add_argument(
        '--no-fullwidth-punctuation-link',
        dest='fullwidth_punctuation_link',
        action='store_false')
    parser.add_argument(
        '--no-duplicate-punctuation',
        dest='duplicate_punctuation',
        action='store_false')
    parser.add_argument(
        '--no-fullwidth-alphabet',
        dest='fullwidth_alphabet',
        action='store_false')
    parser.add_argument('--no-spacing', dest='spacing', action='store_false')
    parser.add_argument(
        '--spacing-punctuation',
        dest='spacing_punctuation',
        action='store_true')
    parser.add_argument(
        '--no-trailing-whitespace',
        dest='trailing_whitespace',
        action='store_false',
        help='指定此选项以保留前后空白字符')
    parser.add_argument(
        '--date',
        type=int,
        default=2,
        help='0: 日期两端不留白；1: 日期两端留白；2: 日期每个数前留白。默认2')
    parser.add_argument(
        '--punctuation-brackets',
        dest='punctuation_brackets',
        default='【】',
        help='一对中文中括号。默认 `【】\'')
    parser.add_argument(
        '--punctuation-ellipsis',
        dest='punctuation_ellipsis',
        default='······',
        help='中文省略号。默认 `······\'')
    parser.add_argument(
        'filename',
        metavar='FILE',
        help='若为 `-\' 则从 stdin 读入、stdout 输出，否则修改 FILE',
    )
    return parser


def pangu_fullwidth_punctuation(l, punctuation_brackets):
    bracket_left, bracket_right = punctuation_brackets

    l = re.sub(r'({})\.($|\s+)'.format(hans), r'\1。', l)
    l = re.sub(r'({}),\s*'.format(hans), r'\1，', l)
    l = re.sub(r'({});\s*'.format(hans), r'\1；', l)
    l = re.sub(r'({})!\s*'.format(hans), r'\1！', l)
    l = re.sub(r'({}):\s*'.format(hans), r'\1：', l)
    l = re.sub(r'({})\?\s*'.format(hans), r'\1？', l)
    l = re.sub(r'({})\\\s*'.format(hans), r'\1、', l)

    # 处理一对圆括号。
    l = re.sub(r'\(({0}[^()]*|[^()]*{0})\)'.format(hans), r'（\1）', l)
    l = re.sub(r'\(({})'.format(hans), r'（\1', l)
    l = re.sub(r'({})\)'.format(hans), r'\1）', l)

    # 预处理，将中括号(【,】)更换为特定类型的中括号(『』)，
    # 避免处理过程中无法正常处理。
    # -- 不是很明白这里的逻辑，暂时搁置
    #l = l.replace(bracket_left, '〖')
    #l = l.replace(bracket_right, '〗')

    # 处理一对方括号。注意：不支持有嵌套的方括号。
    l = re.sub(r'\[({0}[^[\]]*|[^[\]]*{0})\]'.format(hans),
               r'{}\1{}'.format(bracket_left, bracket_right), l)
    l = re.sub(r'\[({})'.format(hans), r'{}\1'.format(bracket_left), l)
    l = re.sub(r'({})\]'.format(hans), r'\1{}'.format(bracket_right), l)
    # 处理一对书名号，注意：不支持有嵌套的书名号。
    l = re.sub(r'<({0}[^<>]*|[^<>]*{0})>'.format(hans), r'《\1》', l)
    l = re.sub(r'<({})'.format(hans), r'《\1', l)
    l = re.sub(r'({})>'.format(hans), r'\1》', l)

    # 双半角书名号 `<<名称>>` 特殊修复处理
    l = l.replace('<《', '《')
    l = l.replace('》>', '》')

    return l


def pangu_fullwidth_punctuation_link(l, punctuation_brackets):
    bracket_left, bracket_right = punctuation_brackets
    # 修复 markdown 链接所使用的标点。
    # 参考链接
    l = re.sub(
        r'[{0}[]([^{1}\]]+)[{1}\]][{0}[]([^{1}\]]+)[{1}\]]'.format(
            bracket_left, bracket_right), r'[\1][\2]', l)
    # 内联链接
    l = re.sub(
        r'[{0}[]([^{1}\]]+)[{1}\]][（(]([^{1})]+)[）)]'.format(
            bracket_left, bracket_right), r'[\1](\2)', l)
    # WiKi 链接：
    # - [『中文条目』] -> [[中文条目]]
    # - [[en 条目』] -> [[en 条目]]
    # - [『条目 en]] -> [[条目 en]]
    l = re.sub(
        r'\[[{0}[]([^{1}\]]+)[{1}\]]\]'.format(bracket_left, bracket_right),
        r'[[\1]]', l)
    # 修复 wiki 链接 [http://www.example.com/ 示例]
    l = re.sub(
        r'[{0}[](https?://\S+\s+[^{1}\]]+)[{1}\]]'.format(
            bracket_left, bracket_right), r'[\1]', l)
    return l


def pangu_duplicate_punctuation(l, punctuation_ellipsis):
    # 连续的句号转成省略号
    # - `……`
    # - `⋯⋯`
    # - `......`
    # - `······`
    # @see [中文省略号应该垂直居中还是沉底？](https://www.zhihu.com/question/19593470)
    l = re.sub(r'。{3,}', punctuation_ellipsis, l)

    # #11: 根据《标点符号用法》，重复的感叹号、问号不允许超过 3 个。
    # [标点符号用法 GB/T 15834 2011](http://www.moe.gov.cn/ewebeditor/uploadfile/2015/01/13/20150113091548267.pdf)
    l = re.sub(r'([！？])\1{3,}', r'\1\1\1', l)
    l = re.sub(r'([。，；：、“”【】〔〕『』〖〗〚〛《》])\1{1,}', r'\1', l)
    return l


def pangu_fullwidth_alphabet(l):
    fullwidth_alphabet = list(map(chr, range(ord('０'), ord('９') + 1)))
    fullwidth_alphabet.extend(map(chr, range(ord('Ａ'), ord('Ｚ') + 1)))
    fullwidth_alphabet.extend(map(chr, range(ord('ａ'), ord('ｚ') + 1)))
    fullwidth_alphabet.append('＠')
    # 65248 是相对应的全角和半角的 Unicode 偏差。
    for x in fullwidth_alphabet:
        l = l.replace(x, chr(ord(x) - 65248))
    return l


def pangu_spacing(l):
    l = re.sub(r'({})([a-zA-Z0-9])'.format(hans), r'\1 \2', l)
    l = re.sub(r'([a-zA-Z0-9])({})'.format(hans), r'\1 \2', l)
    return l


def pangu_spacing_punctuation(l):
    l = re.sub(r'({})([@&=\[$%\^\-+(\\])'.format(hans), r'\1 \2', l)
    l = re.sub(r'([!&;=\],.:?$%\^\-+)])({})'.format(hans), r'\1 \2', l)
    return l


def pangu_date_0(l):
    # 日期两端也不留白
    # 例：
    # 我在2017年8月7日生日。
    # 在2017年8月7日。
    l = re.sub(r'\s*(\d{4,5})\s*年\s*(\d{1,2})\s*月', r'\1年\2月', l)
    l = re.sub(r'\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', r'\1月\2日', l)
    l = re.sub(r'((\d{{4,5}}年)?\d{{1,2}}月(\d{{1,2}}日)?)\s+({})'.format(hans),
               r'\1\4', l)
    return l


def pangu_date_1(l):
    # 日期两端留白
    # 例：
    # 我在 2019年12月1日 生日。
    # 在 2017年8月7日。
    l = re.sub(r'(\d{4,5})\s*年\s*(\d{1,2})\s*月', r'\1年\2月', l)
    l = re.sub(r'(\d{1,2})\s*月\s*(\d{1,2})\s+日/', r'\1月\2日', l)
    l = re.sub(r'(\d{4,5})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s+日', r'\1年\2月\3日',
               l)
    # 两端留白
    l = re.sub(r'((\d{{4,5}}年)?\d{{1,2}}月(\d{{1,2}}日)?)({})'.format(hans),
               r'\1 \4', l)
    return l


def pangu_trailing_whitespace(l):
    l = re.sub(r'^ \[', '[', l, count=1)
    l = re.sub(r'\s+$', '', l, count=1)
    return l


def pangu_trans(l, args):
    # 汉字后的标点符号，转成全角符号。
    if args.fullwidth_punctuation:
        l = pangu_fullwidth_punctuation(l, args.punctuation_brackets)
    if args.fullwidth_punctuation_link:
        l = pangu_fullwidth_punctuation_link(l, args.punctuation_brackets)

    # TODO: 半角单双引号无法有效判断起始和结束，以正确替换成全角单双引号。
    # 可以考虑通过标识符号提醒。

    # 连续重复的标点符号规则
    if args.duplicate_punctuation:
        l = pangu_duplicate_punctuation(l, args.punctuation_ellipsis)

    # 全角数字、英文字符、英文标点。
    if args.fullwidth_alphabet:
        l = pangu_fullwidth_alphabet(l)

    # 汉字与其前后的英文字符、英文标点、数字间增加空白。
    if args.spacing:
        l = pangu_spacing(l)
    if args.spacing_punctuation:
        l = pangu_spacing_punctuation(l)

    # 默认日期每个数字都留白，向前兼容。
    # 例：
    # 在 2017 年 8 月 7 日生日。
    # 在2017年8月7日。
    if args.date == 0:
        l = pangu_date_0(l)
    elif args.date == 1:
        l = pangu_date_1(l)

    if args.trailing_whitespace:
        l = pangu_trailing_whitespace(l)

    return l


def main():
    args = make_parser().parse_args()
    if args.filename == '-':
        lines = list(sys.stdin)
    else:
        with open(args.filename) as infile:
            lines = list(infile)

    try:
        newline_at_eof = (lines[-1][-1] == '\n')
        lines = [l.rstrip('\n') for l in lines]

        trans_lines = []
        for l in lines:
            l = pangu_trans(l, args)
            trans_lines.append(l)

        new_content = '\n'.join(trans_lines)
        if newline_at_eof:
            new_content += '\n'

        if args.filename == '-':
            sys.stdout.write(new_content)
        else:
            with open(args.filename, 'w') as outfile:
                outfile.write(new_content)
    except BrokenPipeError:
        if args.filename != '-':
            raise
        sys.stderr.close()
    except KeyboardInterrupt:
        if args.filename != '-':
            raise


def test_pangu_fullwidth_punctuation():
    pb = '【】'

    assert pangu_fullwidth_punctuation('你好.', pb) == '你好。'
    assert pangu_fullwidth_punctuation('你好! ', pb) == '你好！'
    assert pangu_fullwidth_punctuation('你好:', pb) == '你好：'
    assert pangu_fullwidth_punctuation('你好;\t', pb) == '你好；'
    assert pangu_fullwidth_punctuation('你好?', pb) == '你好？'
    assert pangu_fullwidth_punctuation('你好\\', pb) == '你好、'
    assert pangu_fullwidth_punctuation('你好, 世界!', pb) == '你好，世界！'

    assert pangu_fullwidth_punctuation('(你好hola)', pb) == '（你好hola）'
    assert pangu_fullwidth_punctuation('（你好世界)', pb) == '（你好世界）'
    assert pangu_fullwidth_punctuation('(你好，世界)', pb) == '（你好，世界）'
    assert pangu_fullwidth_punctuation('[你好hola]', pb) == '【你好hola】'
    assert pangu_fullwidth_punctuation('【你好世界]', pb) == '【你好世界】'
    assert pangu_fullwidth_punctuation('[你好，世界]', pb) == '【你好，世界】'
    assert pangu_fullwidth_punctuation('<你好hola>', pb) == '《你好hola》'
    assert pangu_fullwidth_punctuation('《你好世界>', pb) == '《你好世界》'
    assert pangu_fullwidth_punctuation('<你好，世界>', pb) == '《你好，世界》'
    assert pangu_fullwidth_punctuation('<你好，世界>>', pb) == '《你好，世界》'
    assert pangu_fullwidth_punctuation('<<你好，世界>>', pb) == '《你好，世界》'
    assert pangu_fullwidth_punctuation('[(你好)]', pb) == '[（你好）]'


def test_pangu_fullwidth_punctuation_link():
    pb = '【】'

    assert pangu_fullwidth_punctuation_link('【链接】（example.com)', pb) \
           == '[链接](example.com)'
    assert pangu_fullwidth_punctuation_link('【链接】【1】', pb) == '[链接][1]'
    assert pangu_fullwidth_punctuation_link('[【中文】]', pb) == '[[中文]]'
    assert pangu_fullwidth_punctuation_link('[[en中文】]', pb) == '[[en中文]]'
    assert pangu_fullwidth_punctuation_link('[【中文en]]', pb) == '[[中文en]]'
    assert pangu_fullwidth_punctuation_link('【http://example.com 示例】', pb) \
           == '[http://example.com 示例]'
    # won't break this case
    assert pangu_fullwidth_punctuation_link('[【内容】内容](example.com)', pb) \
           == '[【内容】内容](example.com)'
    # fail to fix this case
    assert pangu_fullwidth_punctuation_link('[【内容】内容](example.com）', pb) \
           == '[【内容】内容](example.com）'


def test_pangu_duplicate_punctuation():
    pe = '······'

    assert pangu_duplicate_punctuation('。。。。', pe) == pe
    assert pangu_duplicate_punctuation('！！？？', pe) == '！！？？'
    assert pangu_duplicate_punctuation('！！！！', pe) == '！！！'
    assert pangu_duplicate_punctuation('。【', pe) == '。【'
    assert pangu_duplicate_punctuation('》》', pe) == '》'


def test_pangu_fullwidth_alphabet():
    assert pangu_fullwidth_alphabet('Ｚａ') == 'Za'


def test_pangu_spacing():
    assert pangu_spacing('你好world') == '你好 world'
    assert pangu_spacing('hello世界') == 'hello 世界'
    assert pangu_spacing('你好world再一次') == '你好 world 再一次'


def test_pangu_spacing_punctuation():
    assert pangu_spacing_punctuation('你好@sina.com') == '你好 @sina.com'
    assert pangu_spacing_punctuation(']你好++') == '] 你好 ++'


def test_pangu_date_0():
    assert pangu_date_0('在 2017 年 8 月 7 日生日') == '在2017年8月7日生日'


def test_pangu_date_1():
    assert pangu_date_1('在 2017 年 8 月 7 日生日') == '在 2017年8月7日 生日'


def test_pangu_trailing_whitespace():
    assert pangu_trailing_whitespace(' [ [') == '[ ['
    assert pangu_trailing_whitespace('你好 \t') == '你好'


if __name__ == '__main__':
    main()

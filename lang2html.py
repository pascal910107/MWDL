#!/usr/bin/env python3
'''
lang2html.py
A minimal converter from the Minimal Web Description Language (MWDL) to plain HTML.

使用方式:
    python lang2html.py input.mwdl output.html
    python lang2html.py input.mwdl            # 輸出到終端
'''

import re
import sys
from pathlib import Path

# ────────────────────────────── AST 節點 ──────────────────────────────
class Node:
    def __init__(self, elem, content=None, attrs=None, indent=0):
        self.elem = elem              # 元素類型 (Text、Image、Row ... )
        self.content = content        # 文字內容 (若有)
        self.attrs = attrs or {}      # 屬性字典
        self.children = []            # 子節點
        self.indent = indent          # 在原始檔中的縮排層級

    def add_child(self, node):
        self.children.append(node)

# ────────────────────────────── 語法分析 ──────────────────────────────
_ATTR_SPLIT_RE = re.compile(
    r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'  # 逗號但不在字串內
)

def _parse_attrs(segment: str) -> dict:
    if not segment:
        return {}
    segment = segment.strip()
    if segment.startswith('{') and segment.endswith('}'):
        segment = segment[1:-1]

    attrs = {}
    for part in _ATTR_SPLIT_RE.split(segment):
        if not part.strip():
            continue
        k, v = map(str.strip, part.split(':', 1))
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        attrs[k] = v
    return attrs


_LINE_RE = re.compile(r'([A-Za-z]+)\s*(.*)')  # 擷取元素名稱 + 其餘內容

def _parse_line(raw: str):
    stripped = raw.lstrip()
    # 支援 # 和 // 註解
    if not raw.strip() or stripped.startswith('#') or stripped.startswith('//'):
        return None
    
    indent = len(raw) - len(stripped)
    line = stripped

    # If 條件
    if line.startswith('If '):
        cond = line[3:].rstrip(':').strip()
        return indent, 'If', cond, {}, True

    has_children = line.endswith(':')
    if has_children:
        line = line[:-1].rstrip()

    m = _LINE_RE.match(line)
    if not m:
        raise ValueError(f'無法解析: {raw}')

    elem, rest = m.group(1), m.group(2).strip()
    content, attrs = None, {}

    if rest.startswith('"'):
        # 抓取 "..." 文字區
        cm = re.match(r'"((?:[^"\\]|\\.)*)"\s*(.*)', rest)
        if not cm:
            raise ValueError(f'引號未閉合: {raw}')
        content = cm.group(1)
        rest = cm.group(2).strip()

    if rest.startswith('{'):
        attrs = _parse_attrs(rest)

    return indent, elem, content, attrs, has_children


def _build_ast(lines):
    root = Node('ROOT', indent=-1)
    stack = [root]

    for ln, raw in enumerate(lines, 1):
        parsed = _parse_line(raw)
        if not parsed:
            continue
        indent, elem, content, attrs, has_children = parsed

        # 找出正確父節點 (依縮排)
        while indent <= stack[-1].indent:
            stack.pop()
        node = Node(elem, content, attrs, indent)
        stack[-1].add_child(node)
        if has_children:
            stack.append(node)
    return root

# ────────────────────────────── 轉譯 HTML ──────────────────────────────
_STYLE_MAP = {
    'color':'color',          'bgColor':'background-color',
    'fontWeight':'font-weight','font':'font-family',
    'fontSize':'font-size',   'size':'font-size',
    'margin':'margin',        'padding':'padding',
    'align':'text-align',     'width':'width',
    'height':'height',        'gap':'gap',
}

_TAG_MAP = {
    'Text':'p', 'Heading':'h', 'Image':'img', 'Link':'a',
    'Button':'button', 'Input':'input', 'Form':'form',
    'Section':'div', 'Container':'div',
    'Row':'div', 'Column':'div',
}

def _style_from_attrs(attrs: dict) -> str:
    css = []
    for k, v in attrs.items():
        if k in _STYLE_MAP:
            if re.match(r'^\d+$', str(v)):
                v = f'{v}px'
            css.append(f'{_STYLE_MAP[k]}:{v}')
    return ';'.join(css)

def _render(node: Node, depth=0) -> str:
    pad = '  ' * depth

    if node.elem == 'ROOT':
        return '\n'.join(_render(c, depth) for c in node.children)

    if node.elem == 'If':
        inner = '\n'.join(_render(c, depth) for c in node.children)
        return f'{pad}<!-- If {node.content} -->\n{inner}\n{pad}<!-- End If -->'

    tag = _TAG_MAP.get(node.elem, node.elem.lower())
    attrs_out = []

    # 樣式
    style = _style_from_attrs(node.attrs)
    if node.elem == 'Row':
        style = f'display:flex;flex-wrap:wrap;{style}'
    if style:
        attrs_out.append(f'style=\'{style}\'')

    # 其他屬性 / 特例
    for k, v in node.attrs.items():
        if k in _STYLE_MAP:
            continue
        if k == 'level' and node.elem == 'Heading':
            tag = f'h{v}'
        elif k == 'onClick':
            attrs_out.append(f'onclick=\'{v}()\'')
        elif k == 'onSubmit' and node.elem == 'Form':
            attrs_out.extend((f'action=\'{v}\'', 'method=\'post\''))
        else:
            attrs_out.append(f'{k}=\'{v}\'')

    attr_str = ' '.join(attrs_out)
    if tag in ('img', 'input'):
        return f'{pad}<{tag} {attr_str}/>'

    html = [f'{pad}<{tag} {attr_str}>']
    if node.content:
        html.append(f'{pad}  {node.content}')
    for c in node.children:
        html.append(_render(c, depth + 1))
    html.append(f'{pad}</{tag}>')
    return '\n'.join(html)

def convert(src_text: str) -> str:
    tree = _build_ast(src_text.splitlines())
    body = _render(tree)
    return (
        '<!DOCTYPE html>\n<html>\n<head>\n'
        '<meta charset="utf-8"/>\n<title>Generated</title>\n'
        '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
    )

# ────────────────────────────── CLI ──────────────────────────────
def main():
    if len(sys.argv) < 2:
        print('Usage: python lang2html.py input.mwdl [output.html]')
        sys.exit(1)

    src_path = Path(sys.argv[1])
    html_out = convert(src_path.read_text(encoding='utf-8'))

    if len(sys.argv) >= 3:
        Path(sys.argv[2]).write_text(html_out, encoding='utf-8')
    else:
        print(html_out)

if __name__ == '__main__':
    main()

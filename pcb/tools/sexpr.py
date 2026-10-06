"""Minimal S-expression reader/writer for KiCad files (no external deps)."""
import re

_TOK = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)')


class Sym(str):
    """Bare (unquoted) atom."""


def loads(text):
    pos, stack, cur = 0, [], []
    while True:
        m = _TOK.match(text, pos)
        if not m:
            break
        tok, pos = m.group(1), m.end()
        if tok == '(':
            stack.append(cur)
            cur = []
        elif tok == ')':
            done, cur = cur, stack.pop()
            cur.append(done)
        elif tok.startswith('"'):
            cur.append(tok[1:-1].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\'))
        else:
            cur.append(Sym(tok))
    return cur[0] if len(cur) == 1 else cur


def _atom(a):
    if isinstance(a, Sym):
        return str(a)
    if isinstance(a, bool):
        return 'yes' if a else 'no'
    if isinstance(a, (int, float)):
        s = f"{a:.4f}".rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    return '"' + str(a).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def dumps(e, ind=0):
    if not isinstance(e, list):
        return _atom(e)
    if all(not isinstance(x, list) for x in e):
        return '(' + ' '.join(_atom(x) for x in e) + ')'
    pad = '\t' * (ind + 1)
    head = [x for x in e if not isinstance(x, list)]
    out = '(' + ' '.join(_atom(x) for x in head)
    for x in e:
        if isinstance(x, list):
            out += '\n' + pad + dumps(x, ind + 1)
    return out + '\n' + '\t' * ind + ')'


def find(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]


def first(e, key):
    r = find(e, key)
    return r[0] if r else None


def S(*a):
    """Build a list node; first arg becomes a bare symbol."""
    return [Sym(a[0])] + list(a[1:])

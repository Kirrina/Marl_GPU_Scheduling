"""Check A/B ownership imports (stdlib only). CI must reject cross-side imports."""
from __future__ import annotations
import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src/gpusched'
A=('sim','baselines','calibration')
B=('learning','workload','eval')


def main() -> int:
    bad=[]
    for side, forbidden in ((A,B),(B,A)):
        for folder in side:
            for p in (SRC/folder).rglob('*.py'):
                tree=ast.parse(p.read_text(encoding='utf8'))
                for node in ast.walk(tree):
                    imports=[]
                    if isinstance(node,ast.ImportFrom):
                        imports=[node.module or '']
                    elif isinstance(node,ast.Import):
                        imports=[alias.name for alias in node.names]
                    for name in imports:
                        for f in forbidden:
                            if name == f'gpusched.{f}' or name.startswith(f'gpusched.{f}.'):
                                bad.append(f'{p.relative_to(ROOT)}:{node.lineno} forbidden {name}')
    if bad:
        print('OWNER IMPORT VIOLATIONS:\n'+'\n'.join(bad))
        return 1
    print('PASS import boundaries A <-> B (shared contracts only)')
    return 0

if __name__=='__main__':
    raise SystemExit(main())

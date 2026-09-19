#!/usr/bin/env python3
"""Static source checks only; never hardware qualification."""
import ast
import os
import re
import subprocess
from pathlib import Path

root = Path.cwd()
base = os.environ['NRDR_BASE']
pin = os.environ['JETLINK_PIN']
problems = []
def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()
def check(condition, label):
    print(('PASS ' if condition else 'FAIL ') + label)
    if not condition:
        problems.append(label)
def source(ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], text=True)
def module_path(name):
    aliases = {'jetlink': 'jetlink_repo/jetlink'}
    parts = name.split('.')
    stem = Path(aliases.get(parts[0], parts[0])).joinpath(*parts[1:])
    for p in (stem.with_suffix('.py'), stem / '__init__.py', stem.with_suffix('.pyx')):
        if p.is_file():
            return p
    if stem.is_dir() or list(stem.parent.glob(stem.name + '*.so')):
        return stem
    return None
def symbols(path):
    tree = ast.parse(path.read_text(), filename=str(path))
    result = set()
    dynamic = False
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            result.add(n.name)
            dynamic |= n.name == '__getattr__'
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            result.add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                dynamic |= a.name == '*'
                result.add(a.asname or a.name.split('.')[0])
    return result, dynamic

print('COMMIT', git('rev-parse', 'HEAD'))
print('BASE', base)
check(subprocess.run(['git', 'merge-base', '--is-ancestor', base, 'HEAD']).returncode == 0,
      'nrdr-clean pinned base is an ancestor')
for path in ('panda', 'opendbc_repo', 'openpilot/nrdr', 'openpilot/selfdrive/controls',
             'openpilot/selfdrive/car', 'openpilot/selfdrive/monitoring'):
    if path == 'openpilot/nrdr':
        changed_nrdr = set(git('diff', '--name-only', base, 'HEAD', '--', path).splitlines())
        check(changed_nrdr <= {'openpilot/nrdr/hooks/events.py', 'openpilot/nrdr/hooks/events_sp.py'},
              'NRDR changes limited to reviewed longitudinal gate and speed-limit alerts')
    else:
        check(git('rev-parse', f'{base}:{path}') == git('rev-parse', f'HEAD:{path}'),
              f'unchanged NRDR tree: {path}')
check(not Path('prebuilt').exists(), 'old prebuilt marker absent; target rebuild still required')
entry = git('ls-tree', 'HEAD', '--', 'jetlink_repo').split()
check(len(entry) >= 3 and entry[0] == '160000' and entry[2] == pin, 'exact Jetlink gitlink')
check(git('-C', 'jetlink_repo', 'rev-parse', 'HEAD') == pin, 'Jetlink checkout matches pin')
modules = Path('.gitmodules').read_text()
check(modules.count('[submodule ') == 1 and 'path = jetlink_repo' in modules,
      'only the Jetlink submodule was added')

keyfile = Path('openpilot/common/params_keys.h')
text = keyfile.read_text()
base_lines = source(base, str(keyfile)).splitlines()
check(all(line in text.splitlines() for line in base_lines), 'all original parameter lines preserved')
expected = ['JetlinkEnabled', 'JetlinkEndpoint', 'JetlinkModel', 'JetlinkEngineReady',
            'JetlinkSpec', 'JetlinkCachedModels', 'JetlinkModelPointers',
            'AcceleratorProgress', 'Offroad_AcceleratorUnavailable']
for key in expected:
    check(len(re.findall(r'\{"' + key + r'"\s*,', text)) == 1, 'unique parameter: ' + key)
rows = [s for s in text.splitlines() if '{"JetlinkEnabled"' in s]
check(len(rows) == 1 and 'BOOL' in rows[0] and '"1"' not in rows[0], 'Jetlink not default-enabled')
check('get_bool("JetlinkEnabled")' in Path('openpilot/sunnypilot/accelerators/jetlink/setup.sh').read_text(),
      'USB gadget setup requires opt-in')

changed = git('diff', '--no-renames', '--name-only', '--diff-filter=AM', base, 'HEAD').splitlines()
py_count = 0
missing = set()
for name in changed:
    path = Path(name)
    if not path.is_file() or path.is_symlink():
        continue
    if path.suffix in {'.py', '.sh', '.h', '.capnp'}:
        check(not re.search(r'^(?:<{7}|>{7}|={7})(?: |$)', path.read_text(), re.M), 'no merge markers: ' + name)
    if path.suffix == '.py':
        tree = ast.parse(path.read_text(), filename=name)
        py_count += 1
        for n in ast.walk(tree):
            if not isinstance(n, ast.ImportFrom) or n.level or not n.module:
                continue
            if not n.module.startswith(('openpilot.', 'jetlink.')):
                continue
            target = module_path(n.module)
            if target is None:
                missing.add((name, n.lineno, n.module, 'module'))
                continue
            if target.suffix != '.py' or n.module in ('openpilot.cereal', 'openpilot.cereal.messaging'):
                continue
            names, dynamic = symbols(target)
            if dynamic:
                continue
            for a in n.names:
                if a.name == '*' or a.name in names or module_path(n.module + '.' + a.name):
                    continue
                missing.add((name, n.lineno, n.module + '.' + a.name, 'symbol'))
    elif path.suffix == '.sh':
        check(subprocess.run(['bash', '-n', name]).returncode == 0, 'shell syntax: ' + name)
print('PARSED_PYTHON_FILES', py_count)
for name, line, imported, kind in sorted(missing):
    print(f'UNRESOLVED {kind}: {name}:{line}: {imported}')
check(not missing, 'changed Python files resolve local absolute imports statically')
for name in ('SConstruct', 'openpilot/selfdrive/modeld/compile_modeld.py',
             'openpilot/system/camerad/cameras/nv12_info.py',
             'openpilot/sunnypilot/accelerators/jetlink/compile_warp.py',
             'jetlink_repo/scripts/setup_gadget.sh'):
    check(Path(name).is_file(), 'build/setup input present: ' + name)
print('HARDWARE_QUALIFICATION: NOT PERFORMED. No comma GPU, CAN, cameras, or Jetson was exercised.')
print('INSTALLATION_STATUS: HOLD pending complete target build and non-actuating bench validation.')
if problems:
    raise SystemExit(f'{len(problems)} source-audit checks failed')

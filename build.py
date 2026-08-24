#!/usr/bin/env python3
"""Regenerate index.html from the runbook + template.

    python3 build-sections.py sections.json && python3 build.py

The page embeds the runbook so it works offline; this script is what keeps the
two in step. If you edit child-bounty-runbook.md, run this.
"""
import json, subprocess, sys, pathlib
here = pathlib.Path(__file__).parent
subprocess.run([sys.executable, here/'build-sections.py', here/'sections.json'], check=True)
tpl  = (here/'workbench.tpl.html').read_text()
secs = json.loads((here/'sections.json').read_text())
(here/'index.html').write_text(tpl.replace('__SECTIONS__', json.dumps(secs, ensure_ascii=False)))
print('wrote index.html')

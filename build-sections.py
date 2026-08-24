import re, json, html, sys

import pathlib
src = (pathlib.Path(__file__).parent / 'child-bounty-runbook.md').read_text()

def md(text):
    out, i, lines = [], 0, text.split('\n')
    while i < len(lines):
        L = lines[i]
        if L.startswith('```'):                              # fenced code
            i += 1; buf = []
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(html.escape(lines[i])); i += 1
            i += 1
            out.append('<pre><code>' + '\n'.join(buf) + '</code></pre>'); continue
        if L.startswith('|'):                                # table
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i]); i += 1
            cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows]
            body = [c for c in cells if not re.match(r'^[\s:\-]+$', ''.join(c))]
            if not body: continue
            t = '<table><thead><tr>' + ''.join(f'<th>{inl(c)}</th>' for c in body[0]) + '</tr></thead><tbody>'
            for r in body[1:]:
                t += '<tr>' + ''.join(f'<td>{inl(c)}</td>' for c in r) + '</tr>'
            out.append(t + '</tbody></table>'); continue
        m = re.match(r'^(#{3,4})\s+(.*)', L)
        if m:
            lvl = len(m.group(1)); out.append(f'<h{lvl}>{inl(m.group(2))}</h{lvl}>'); i += 1; continue
        if re.match(r'^\s*[-*]\s+', L):
            items = []
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(inl(re.sub(r'^\s*[-*]\s+', '', lines[i]))); i += 1
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'); continue
        if re.match(r'^\s*\d+\.\s+', L):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(inl(re.sub(r'^\s*\d+\.\s+', '', lines[i]))); i += 1
            out.append('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'); continue
        if L.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(re.sub(r'^>\s?', '', lines[i])); i += 1
            out.append('<blockquote>' + inl(' '.join(buf)) + '</blockquote>'); continue
        if L.strip() == '---': out.append('<hr>'); i += 1; continue
        if L.strip():
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|```|\||>|\s*[-*]\s|\s*\d+\.\s)', lines[i]):
                buf.append(lines[i]); i += 1
            out.append('<p>' + inl(' '.join(buf)) + '</p>'); continue
        i += 1
    return ''.join(out)

def inl(t):
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t

parts = re.split(r'\n## ', src)
sections = {}
for p in parts[1:]:
    title = p.split('\n', 1)[0].strip()
    body  = p.split('\n', 1)[1] if '\n' in p else ''
    key = 'intro'
    m = re.match(r'Step (\d)', title)
    if m: key = 's' + m.group(1)
    elif title.startswith('Pre-check'): key = 'pre'
    elif title.startswith('Roles'):     key = 'roles'
    elif title.startswith('Common'):    key = 'issues'
    sections[key] = {'title': title, 'html': md(body)}

json.dump(sections, open(sys.argv[1], 'w'))
print('sections:', ', '.join(f'{k} ({len(v["html"])//1000}k)' for k, v in sections.items()))

import re, sys, html as H

def inline(s):
    s = H.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
    return s

def convert(md):
    out, i, lines = [], 0, md.split('\n')
    while i < len(lines):
        L = lines[i]
        if L.startswith('|') and i+1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i+1]):
            hdr = [c.strip() for c in L.strip('|').split('|')]
            i += 2; rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip('|').split('|')]); i += 1
            out.append('<table><thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in hdr) + '</tr></thead><tbody>')
            for r in rows:
                out.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
            out.append('</tbody></table>'); continue
        if re.match(r'^---+\s*$', L): out.append('<hr>'); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)', L)
        if m: out.append('<h%d>%s</h%d>' % (len(m.group(1)), inline(m.group(2)), len(m.group(1)))); i += 1; continue
        if L.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].startswith('> '): buf.append(lines[i][2:]); i += 1
            out.append('<blockquote>%s</blockquote>' % inline(' '.join(buf))); continue
        if re.match(r'^\d+\.\s', L):
            out.append('<ol>')
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i]):
                out.append('<li>%s</li>' % inline(re.sub(r'^\d+\.\s', '', lines[i]))); i += 1
            out.append('</ol>'); continue
        if L.startswith('- '):
            out.append('<ul>')
            while i < len(lines) and lines[i].startswith('- '):
                out.append('<li>%s</li>' % inline(lines[i][2:])); i += 1
            out.append('</ul>'); continue
        if L.strip() == '': i += 1; continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#|\||>|-\s|\d+\.\s|---)', lines[i]):
            buf.append(lines[i]); i += 1
        out.append('<p>%s</p>' % inline(' '.join(buf)))
    return '\n'.join(out)

CSS = """
@page { size: A4; margin: 16mm 15mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.5 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:#16181D; margin:0; }
h1 { font-size:22pt; letter-spacing:-.5pt; margin:0 0 2pt; }
h1 + p { color:#666E7A; font-size:10pt; margin:0 0 14pt; }
h2 { font-size:14pt; letter-spacing:-.3pt; margin:20pt 0 7pt; padding-bottom:4pt;
  border-bottom:1.5px solid #E3E6EA; page-break-after:avoid; }
h3 { font-size:11.5pt; margin:13pt 0 5pt; page-break-after:avoid; }
p { margin:0 0 8pt; }
hr { border:0; border-top:1px solid #E3E6EA; margin:16pt 0; }
strong { font-weight:700; color:#000; }
code { font:9.5pt ui-monospace,"SF Mono",Menlo,monospace; background:#F1F3F5;
  padding:1px 4px; border-radius:3px; }
blockquote { margin:9pt 0; padding:8pt 11pt; background:#F6F8FA;
  border-left:3px solid #7A8798; border-radius:0 4px 4px 0; font-size:10pt; }
blockquote p { margin:0; }
ul,ol { margin:0 0 9pt; padding-left:17pt; }
li { margin-bottom:3.5pt; }
table { border-collapse:collapse; width:100%; margin:9pt 0 12pt; font-size:8.8pt;
  page-break-inside:avoid; }
th { background:#F1F3F5; text-align:left; font-weight:700; font-size:8.2pt;
  letter-spacing:.3pt; text-transform:uppercase; color:#4A525E; }
th,td { border:1px solid #DDE1E6; padding:4.5pt 6pt; vertical-align:top; }
tbody tr:nth-child(even) { background:#FAFBFC; }
"""

md = open(sys.argv[1]).read()
open(sys.argv[2],'w').write(
  '<!doctype html><meta charset="utf-8"><title>LoopNote submission</title>'
  '<style>%s</style>%s' % (CSS, convert(md)))
print("wrote", sys.argv[2])

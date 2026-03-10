const vscode = require('vscode');
const { exec, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// ─────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────

function getPython() {
  return vscode.workspace.getConfiguration('celes').get('pythonPath', 'python');
}

function runPython(script, args, input) {
  return new Promise((resolve, reject) => {
    const python = getPython();
    const proc = spawn(python, ['-c', script, ...args]);
    let stdout = '';
    let stderr = '';
    if (input) proc.stdin.write(input);
    proc.stdin.end();
    proc.stdout.on('data', d => stdout += d);
    proc.stderr.on('data', d => stderr += d);
    proc.on('close', code => resolve({ code, stdout, stderr }));
    proc.on('error', reject);
  });
}

// Inline Python validator — no file dependency needed
const VALIDATOR_SCRIPT = `
import sys, re, json

SELF_CLOSING = {'newline','pagebreak','insertspace'}
BLOCK_TAGS = {'title','header','line','blockquote','codeblock','image','linkimage','list','sublist','table','item','newline','pagebreak','insertspace'}
INLINE_TAGS = {'bold','italic','bold+italic','underline','strike','code','link','checkmark','nestquote','empty'}
VALID_BULLET = {'circle','number'}
VALID_ALIGN  = {'left','center','right'}
VALID_SIZE   = {'1','2','3','4','5','6'}

def find_brace(s, start):
    d = 0
    for i in range(start, len(s)):
        if s[i]=='{': d+=1
        elif s[i]=='}':
            d-=1
            if d==0: return i
    return -1

def parse_attrs(a):
    r={}
    for m in re.finditer(r'-(\w+)(?:=(?=\S)(.*?))?(?=\s+-\w|$)', a.strip(), re.DOTALL):
        r[m.group(1)] = m.group(2).strip() if m.group(2) else True
    return r

def split_line(line):
    line=line.strip()
    if line.startswith(';') or line.startswith('<!'): return [line]
    res=[]; i=0
    while i<len(line):
        if line[i]!='<': break
        te=line.find('>',i)
        if te==-1: res.append(line[i:]); break
        at=te+1
        if at<len(line) and line[at]=='{':
            cl=find_brace(line,at)
            if cl!=-1: res.append(line[i:cl+1]); i=cl+1; continue
        res.append(line[i:at]); i=at
    return res or [line]

def parse_tag(line):
    line=line.strip()
    if not line: return None
    if line.startswith(';'): return ('comment',{},'')
    if line.startswith('<!'): return ('declaration',{},'')
    if not line.startswith('<'): return ('error',{},f'Line does not start with tag')
    te=line.find('>')
    if te==-1: return ('error',{},f'Unclosed tag')
    hdr=line[1:te]
    m=re.match(r'^([\w+]+)(.*)',hdr,re.DOTALL)
    if not m: return ('error',{},f'Bad tag name')
    name=m.group(1).lower(); attrs=parse_attrs(m.group(2))
    rest=line[te+1:].strip()
    if not rest: return (name,attrs,None)
    if not rest.startswith('{'): return ('error',{},f'Missing braces after <{name}>')
    cl=find_brace(rest,0)
    if cl==-1: return ('error',{},f'Unclosed brace in <{name}>')
    return (name,attrs,rest[1:cl])

source = sys.stdin.read()
errors = []
tokens = []
for lineno, raw in enumerate(source.splitlines(), 1):
    if not raw.strip(): continue
    for s in split_line(raw):
        if not s.strip(): continue
        r = parse_tag(s)
        if r: tokens.append((lineno,)+r)

seen=[]
title_count=0
for i,(lineno,name,attrs,content) in enumerate(tokens):
    seen.append(name)
    if name in ('comment','declaration'): continue
    if name == 'error':
        errors.append({'line':lineno,'severity':'error','message':content}); continue
    all_known = BLOCK_TAGS|INLINE_TAGS|{'comment','declaration','error'}
    if name not in all_known:
        errors.append({'line':lineno,'severity':'error','message':f'Unknown tag <{name}>'}); continue
    if name not in SELF_CLOSING and content is None:
        errors.append({'line':lineno,'severity':'error','message':f'<{name}> requires {{...}} content'})
    if name=='title':
        title_count+=1
        if title_count>1: errors.append({'line':lineno,'severity':'warning','message':'Multiple <title> tags'})
    if name=='header':
        s=attrs.get('size')
        if not s: errors.append({'line':lineno,'severity':'error','message':'<header> missing -size'})
        elif str(s) not in VALID_SIZE: errors.append({'line':lineno,'severity':'error','message':f'<header -size={s}> must be 1-6'})
    if name=='line':
        a=attrs.get('align')
        if a and a not in VALID_ALIGN: errors.append({'line':lineno,'severity':'error','message':f'<line -align={a}> must be left/center/right'})
    if name in ('list','sublist'):
        b=attrs.get('bullet')
        if not b: errors.append({'line':lineno,'severity':'error','message':f'<{name}> missing -bullet'})
        elif b not in VALID_BULLET: errors.append({'line':lineno,'severity':'error','message':f'<{name} -bullet={b}> must be circle/number'})
    if name=='checkmark':
        if 'check' not in attrs and 'uncheck' not in attrs:
            errors.append({'line':lineno,'severity':'error','message':'<checkmark> needs -check or -uncheck'})
    if name=='linkimage' and 'image' not in attrs:
        errors.append({'line':lineno,'severity':'error','message':'<linkimage> missing -image attribute'})
    if name=='table' and content:
        cols=[c.strip() for c in content.split(',')]
        j=i+1
        while j<len(tokens) and tokens[j][1]=='item':
            cells=[c.strip() for c in (tokens[j][4] or '').split(',')]
            if len(cells)!=len(cols):
                errors.append({'line':tokens[j][0],'severity':'error','message':f'<item> has {len(cells)} cell(s) but table has {len(cols)} column(s)'})
            j+=1
print(json.dumps(errors))
`;

// Inline Python parser
const PARSER_SCRIPT = `
import sys
from html import escape
import re, json

def find_brace(s,start):
    d=0
    for i in range(start,len(s)):
        if s[i]=='{':d+=1
        elif s[i]=='}':
            d-=1
            if d==0:return i
    return -1

def parse_attrs(a):
    r={}
    for m in re.finditer(r'-(\w+)(?:=(?=\S)(.*?))?(?=\s+-\w|$)',a.strip(),re.DOTALL):
        r[m.group(1)]=m.group(2).strip() if m.group(2) else True
    return r

def split_line(line):
    line=line.strip()
    if line.startswith(';') or line.startswith('<!'): return [line]
    res=[]; i=0
    while i<len(line):
        if line[i]!='<': break
        te=line.find('>',i)
        if te==-1: res.append(line[i:]); break
        at=te+1
        if at<len(line) and line[at]=='{':
            cl=find_brace(line,at)
            if cl!=-1: res.append(line[i:cl+1]); i=cl+1; continue
        res.append(line[i:at]); i=at
    return res or [line]

def parse_tag(line):
    line=line.strip()
    if not line: return None
    if line.startswith(';'): return ('comment',{},'')
    if line.startswith('<!'): return ('declaration',{},'')
    if not line.startswith('<'): return ('error',{},line)
    te=line.find('>')
    if te==-1: return ('error',{},line)
    hdr=line[1:te]
    m=re.match(r'^([\w+]+)(.*)',hdr,re.DOTALL)
    if not m: return ('error',{},line)
    name=m.group(1).lower(); attrs=parse_attrs(m.group(2))
    rest=line[te+1:].strip()
    if not rest: return (name,attrs,None)
    if not rest.startswith('{'): return ('error',{},line)
    cl=find_brace(rest,0)
    if cl==-1: return ('error',{},line)
    return (name,attrs,rest[1:cl])

def inline_html(content, raw=False):
    if content is None: return ''
    if raw: return escape(content)
    res=''; i=0
    while i<len(content):
        ts=content.find('<',i)
        if ts==-1: res+=escape(content[i:]); break
        res+=escape(content[i:ts])
        te=content.find('>',ts)
        if te==-1: res+=escape(content[ts:]); break
        hdr=content[ts+1:te]
        m=re.match(r'^([\w+]+)(.*)',hdr,re.DOTALL)
        if not m: res+=escape(content[ts:te+1]); i=te+1; continue
        name=m.group(1).lower(); attrs=parse_attrs(m.group(2)); at=te+1
        inner=''; end=at
        if at<len(content) and content[at]=='{':
            cl=find_brace(content,at)
            if cl!=-1: inner=content[at+1:cl]; end=cl+1
        im=inline_html(inner)
        if name=='bold': res+=f'<strong>{im}</strong>'
        elif name=='italic': res+=f'<em>{im}</em>'
        elif name=='bold+italic': res+=f'<strong><em>{im}</em></strong>'
        elif name=='underline': res+=f'<u>{im}</u>'
        elif name=='strike': res+=f'<s>{im}</s>'
        elif name=='code': res+=f'<code>{escape(inner)}</code>'
        elif name=='newline': res+='<br>'
        elif name=='empty': res+=escape(inner)
        elif name=='nestquote': res+=f'<blockquote class="nested">{im}</blockquote>'
        elif name=='link':
            body=attrs.get('body',im)
            res+=f'<a href="{escape(inner)}">{escape(body)}</a>'
        elif name=='checkmark':
            ch='checked' if 'check' in attrs else ''
            res+=f'<input type="checkbox" {ch} disabled> {im}'
        else: res+=im
        i=end
    return res

source=sys.stdin.read()
tokens=[]
for lineno,raw in enumerate(source.splitlines(),1):
    if not raw.strip(): continue
    for s in split_line(raw):
        if not s.strip(): continue
        r=parse_tag(s)
        if r: tokens.append((lineno,)+r)

title='Celes Document'; body=[]; i=0
while i<len(tokens):
    _,name,attrs,content=tokens[i]
    if name in ('comment','declaration'): i+=1; continue
    if name=='title': title=content or ''; i+=1
    elif name=='header':
        sz=attrs.get('size','1')
        body.append(f'<h{sz}>{inline_html(content)}</h{sz}>'); i+=1
    elif name=='line':
        al=attrs.get('align','')
        st=f' style="text-align:{escape(al)}"' if al else ''
        body.append(f'<p{st}>{inline_html(content)}</p>'); i+=1
    elif name=='blockquote': body.append(f'<blockquote>{inline_html(content)}</blockquote>'); i+=1
    elif name=='codeblock': body.append(f'<pre><code>{escape(content or "")}</code></pre>'); i+=1
    elif name=='image': body.append(f'<img src="{escape(content or "")}" alt="">'); i+=1
    elif name=='linkimage':
        img=attrs.get('image','')
        body.append(f'<a href="{escape(content or "")}"><img src="{escape(img)}" alt=""></a>'); i+=1
    elif name=='table':
        cols=[c.strip() for c in (content or '').split(',')]
        hcells=''.join(f'<th>{escape(c)}</th>' for c in cols)
        rows=[f'<thead><tr>{hcells}</tr></thead>']; brows=[]; i+=1
        while i<len(tokens) and tokens[i][1]=='item':
            cells=[c.strip() for c in (tokens[i][3] or '').split(',')]
            brows.append('<tr>'+''.join(f'<td>{escape(c)}</td>' for c in cells)+'</tr>'); i+=1
        rows.append(f'<tbody>{"".join(brows)}</tbody>')
        body.append(f'<table>{"".join(rows)}</table>')
    elif name=='list':
        items=[]
        while i<len(tokens) and tokens[i][1]=='list':
            ia=tokens[i][2]; ic=tokens[i][3] or ''; bullet=ia.get('bullet','circle')
            lt='ol' if bullet=='number' else 'ul'; i+=1
            subs=[]
            while i<len(tokens) and tokens[i][1]=='sublist':
                sb=tokens[i][2].get('bullet','circle')
                st2='ol' if sb=='number' else 'ul'
                subs.append(f'<li>{inline_html(tokens[i][3] or "")}</li>'); i+=1
            sh=f'<{st2}>{"".join(subs)}</{st2}>' if subs else ''
            items.append((lt,ic,sh))
        if items:
            lt=items[0][0]
            lis=''.join(f'<li>{inline_html(c)}{s}</li>' for _,c,s in items)
            body.append(f'<{lt}>{lis}</{lt}>')
    elif name=='newline': body.append('<br>'); i+=1
    elif name=='pagebreak': body.append('<div style="page-break-after:always"></div>'); i+=1
    elif name=='insertspace': body.append('<hr>'); i+=1
    else: i+=1

html=f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{escape(title)}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:800px;margin:2rem auto;padding:0 1.5rem;line-height:1.7;color:#222}}
blockquote{{border-left:4px solid #ccc;margin:1em 0;padding:.4rem 1rem;color:#555}}
blockquote.nested{{border-left:4px solid #aaa;margin-left:1.5rem}}
pre{{background:#f5f5f5;padding:1rem;border-radius:5px;overflow-x:auto}}
code{{background:#f0f0f0;padding:.15em .4em;border-radius:3px;font-size:.92em}}
pre code{{background:none;padding:0}}
table{{border-collapse:collapse;width:100%;margin:1em 0}}
th,td{{border:1px solid #ccc;padding:.5rem 1rem;text-align:left}}
th{{background:#f0f0f0;font-weight:600}}
img{{max-width:100%;height:auto}}
hr{{border:none;border-top:1px solid #ddd;margin:2em 0}}
</style></head><body>
{"".join(body)}
</body></html>"""
print(html)
`;

// ─────────────────────────────────────────────
// DIAGNOSTICS
// ─────────────────────────────────────────────

const diagnosticCollection = vscode.languages.createDiagnosticCollection('celes');

async function validateDocument(document) {
  if (document.languageId !== 'celes') return;
  const source = document.getText();

  try {
    const result = await runPython(VALIDATOR_SCRIPT, [], source);
    const issues = JSON.parse(result.stdout || '[]');
    const diags = issues.map(e => {
      const line = Math.max(0, (e.line || 1) - 1);
      const range = document.lineAt(line).range;
      const severity = e.severity === 'error'
        ? vscode.DiagnosticSeverity.Error
        : vscode.DiagnosticSeverity.Warning;
      return new vscode.Diagnostic(range, e.message, severity);
    });
    diagnosticCollection.set(document.uri, diags);
  } catch (err) {
    // Python not found or other error — clear diagnostics silently
    diagnosticCollection.set(document.uri, []);
  }
}

// ─────────────────────────────────────────────
// LIVE PREVIEW
// ─────────────────────────────────────────────

let previewPanel = null;
let previewDocument = null;

async function openPreview(document) {
  if (!document) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'celes') {
      vscode.window.showErrorMessage('Open a .celes file first.');
      return;
    }
    document = editor.document;
  }

  previewDocument = document;

  if (previewPanel) {
    previewPanel.reveal(vscode.ViewColumn.Two);
  } else {
    previewPanel = vscode.window.createWebviewPanel(
      'celesPreview',
      'Celes Preview',
      vscode.ViewColumn.Two,
      { enableScripts: true }
    );
    previewPanel.onDidDispose(() => { previewPanel = null; });
  }

  await updatePreview(document);
}

async function updatePreview(document) {
  if (!previewPanel || !document) return;
  const source = document.getText();

  previewPanel.webview.html = `<!DOCTYPE html><html><body style="font-family:sans-serif;color:#888;padding:2rem">Rendering...</body></html>`;

  try {
    const result = await runPython(PARSER_SCRIPT, [], source);
    if (result.stdout.trim()) {
      previewPanel.webview.html = result.stdout;
    } else {
      previewPanel.webview.html = `<!DOCTYPE html><html><body style="font-family:sans-serif;color:#c00;padding:2rem">
        <strong>Preview error:</strong><pre>${result.stderr}</pre>
      </body></html>`;
    }
  } catch (err) {
    previewPanel.webview.html = `<!DOCTYPE html><html><body style="font-family:sans-serif;color:#c00;padding:2rem">
      <strong>Could not run Python.</strong><br>
      Check the <code>celes.pythonPath</code> setting.<br><br>
      <code>${err.message}</code>
    </body></html>`;
  }
}

// ─────────────────────────────────────────────
// ACTIVATION
// ─────────────────────────────────────────────

function activate(context) {
  // Validate on open and on change (debounced)
  let debounceTimer = null;

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(doc => validateDocument(doc)),
    vscode.workspace.onDidChangeTextDocument(e => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        validateDocument(e.document);
        if (previewPanel && previewDocument &&
            e.document.uri.toString() === previewDocument.uri.toString()) {
          updatePreview(e.document);
        }
      }, 500);
    }),
    vscode.workspace.onDidCloseTextDocument(doc => {
      diagnosticCollection.delete(doc.uri);
    })
  );

  // Validate already-open documents
  vscode.workspace.textDocuments.forEach(validateDocument);

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('celes.preview', () => {
      const editor = vscode.window.activeTextEditor;
      openPreview(editor ? editor.document : null);
    }),
    vscode.commands.registerCommand('celes.validate', () => {
      const editor = vscode.window.activeTextEditor;
      if (editor) validateDocument(editor.document);
    })
  );

  context.subscriptions.push(diagnosticCollection);
}

function deactivate() {
  diagnosticCollection.dispose();
}

module.exports = { activate, deactivate };

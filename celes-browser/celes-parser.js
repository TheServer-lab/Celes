// Celes 0.1.4 Parser - JavaScript
(function (global) {

  function findMatchingBrace(s, start) {
    let depth = 0;
    for (let i = start; i < s.length; i++) {
      if (s[i] === '{') depth++;
      else if (s[i] === '}') { depth--; if (depth === 0) return i; }
    }
    return -1;
  }

  function parseAttrs(attrStr) {
    const attrs = {};
    const re = /-(\w+)(?:=(\S+?))?(?=\s+-\w|$)/g;
    let m;
    while ((m = re.exec(attrStr)) !== null) {
      attrs[m[1]] = m[2] !== undefined ? m[2] : true;
    }
    return attrs;
  }

  function splitMultiTagLine(line) {
    line = line.trim();
    if (line.startsWith(';') || line.startsWith('<!')) return [line];
    const result = [];
    let i = 0;
    while (i < line.length) {
      if (line[i] !== '<') break;
      const tagEnd = line.indexOf('>', i);
      if (tagEnd === -1) { result.push(line.slice(i)); break; }
      const afterTag = tagEnd + 1;
      if (afterTag < line.length && line[afterTag] === '{') {
        const close = findMatchingBrace(line, afterTag);
        if (close !== -1) { result.push(line.slice(i, close + 1)); i = close + 1; continue; }
      }
      result.push(line.slice(i, afterTag));
      i = afterTag;
    }
    return result.length ? result : [line];
  }

  function parseTagLine(line) {
    line = line.trim();
    if (!line) return null;
    if (line.startsWith(';')) return ['comment', {}, line.slice(1).trim()];
    if (line.startsWith('<!')) return ['declaration', {}, line];
    if (!line.startsWith('<')) return ['error', {}, line];
    const tagEnd = line.indexOf('>');
    if (tagEnd === -1) return ['error', {}, line];
    const header = line.slice(1, tagEnd);
    const hm = header.match(/^([\w+]+)(.*)/s);
    if (!hm) return ['error', {}, line];
    const tagname = hm[1].toLowerCase();
    const attrs = parseAttrs(hm[2]);
    const rest = line.slice(tagEnd + 1).trim();
    if (!rest) return [tagname, attrs, null];
    if (!rest.startsWith('{')) return ['error', {}, 'Missing braces after <' + tagname + '>'];
    const close = findMatchingBrace(rest, 0);
    if (close === -1) return ['error', {}, 'Unclosed brace in <' + tagname + '>'];
    return [tagname, attrs, rest.slice(1, close)];
  }

  function tokenize(source) {
    const tokens = [];
    for (const raw of source.split('\n')) {
      if (!raw.trim()) continue;
      for (const single of splitMultiTagLine(raw)) {
        if (!single.trim()) continue;
        const result = parseTagLine(single);
        if (result) tokens.push(result);
      }
    }
    return tokens;
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function inlineToHtml(content, raw) {
    if (content === null || content === undefined) return '';
    if (raw) return esc(content);
    let result = '';
    let i = 0;
    while (i < content.length) {
      const ts = content.indexOf('<', i);
      if (ts === -1) { result += esc(content.slice(i)); break; }
      result += esc(content.slice(i, ts));
      const te = content.indexOf('>', ts);
      if (te === -1) { result += esc(content.slice(ts)); break; }
      const header = content.slice(ts + 1, te);
      const hm = header.match(/^([\w+]+)(.*)/s);
      if (!hm) { result += esc(content.slice(ts, te + 1)); i = te + 1; continue; }
      const name = hm[1].toLowerCase();
      const attrs = parseAttrs(hm[2]);
      const afterTag = te + 1;
      let inner = '', end = afterTag;
      if (afterTag < content.length && content[afterTag] === '{') {
        const close = findMatchingBrace(content, afterTag);
        if (close !== -1) { inner = content.slice(afterTag + 1, close); end = close + 1; }
      }
      const im = inlineToHtml(inner);
      if      (name === 'bold')        result += '<strong>' + im + '</strong>';
      else if (name === 'italic')      result += '<em>' + im + '</em>';
      else if (name === 'bold+italic') result += '<strong><em>' + im + '</em></strong>';
      else if (name === 'underline')   result += '<u>' + im + '</u>';
      else if (name === 'strike')      result += '<s>' + im + '</s>';
      else if (name === 'super')       result += '<sup>' + im + '</sup>';
      else if (name === 'sub')         result += '<sub>' + im + '</sub>';
      else if (name === 'mark')        result += '<mark>' + im + '</mark>';
      else if (name === 'code')        result += '<code>' + esc(inner) + '</code>';
      else if (name === 'newline')     result += '<br>';
      else if (name === 'empty')       result += esc(inner);
      else if (name === 'nestquote')   result += '<blockquote class="nested">' + im + '</blockquote>';
      else if (name === 'link') {
        const body = attrs.body || im;
        result += '<a href="' + esc(inner) + '">' + esc(body) + '</a>';
      }
      else if (name === 'button') {
        const body = attrs.body || im;
        result += '<a href="' + esc(inner) + '" class="celes-button">' + esc(body) + '</a>';
      }
      else if (name === 'checkmark') {
        const checked = 'check' in attrs ? 'checked' : '';
        result += '<input type="checkbox" ' + checked + ' disabled> ' + im;
      }
      else result += im;
      i = end;
    }
    return result;
  }

  function parseCeles(source) {
    const tokens = tokenize(source);
    let title = 'Celes Document';
    const body = [];
    let i = 0;

    while (i < tokens.length) {
      const name  = tokens[i][0];
      const attrs = tokens[i][1];
      const content = tokens[i][2];

      if (name === 'comment' || name === 'declaration') { i++; continue; }

      if (name === 'title') {
        title = content || ''; i++;

      } else if (name === 'author' || name === 'date') {
        i++;

      } else if (name === 'section') {
        body.push('<div class="celes-section"><span class="celes-section-label">' + esc(content || '') + '</span></div>');
        i++;

      } else if (name === 'header') {
        const sz = attrs.size || '1';
        body.push('<h' + sz + '>' + inlineToHtml(content) + '</h' + sz + '>');
        i++;

      } else if (name === 'line') {
        const al = attrs.align || '';
        const st = al ? ' style="text-align:' + esc(al) + '"' : '';
        body.push('<p' + st + '>' + inlineToHtml(content) + '</p>');
        i++;

      } else if (name === 'blockquote') {
        body.push('<blockquote>' + inlineToHtml(content) + '</blockquote>');
        i++;

      } else if (name === 'codeblock') {
        body.push('<pre><code>' + esc(content || '') + '</code></pre>');
        i++;

      } else if (name === 'image') {
        body.push('<img src="' + esc(content || '') + '" alt="">');
        i++;

      } else if (name === 'linkimage') {
        const img = attrs.image || '';
        body.push('<a href="' + esc(content || '') + '"><img src="' + esc(img) + '" alt=""></a>');
        i++;

      } else if (name === 'table') {
        const cols = (content || '').split(',').map(function(c) { return c.trim(); });
        const hcells = cols.map(function(c) { return '<th>' + esc(c) + '</th>'; }).join('');
        const rows = ['<thead><tr>' + hcells + '</tr></thead>'];
        const brows = [];
        i++;
        while (i < tokens.length && tokens[i][0] === 'item') {
          const cells = (tokens[i][2] || '').split(',').map(function(c) { return c.trim(); });
          brows.push('<tr>' + cells.map(function(c) { return '<td>' + esc(c) + '</td>'; }).join('') + '</tr>');
          i++;
        }
        rows.push('<tbody>' + brows.join('') + '</tbody>');
        body.push('<table>' + rows.join('') + '</table>');

      } else if (name === 'list') {
        const items = [];
        while (i < tokens.length && tokens[i][0] === 'list') {
          const ia = tokens[i][1];
          const ic = tokens[i][2];
          const bullet = ia.bullet || 'circle';
          const lt = bullet === 'number' ? 'ol' : 'ul';
          i++;
          const subs = [];
          let subType = 'ul';
          while (i < tokens.length && tokens[i][0] === 'sublist') {
            const sb = tokens[i][1].bullet || 'circle';
            subType = sb === 'number' ? 'ol' : 'ul';
            const subContent = tokens[i][2] || '';
            i++;
            const subsubs = [];
            let subsubType = 'ul';
            while (i < tokens.length && tokens[i][0] === 'subsublist') {
              const ssb = tokens[i][1].bullet || 'circle';
              subsubType = ssb === 'number' ? 'ol' : 'ul';
              subsubs.push('<li>' + inlineToHtml(tokens[i][2] || '') + '</li>');
              i++;
            }
            const ssh = subsubs.length ? '<' + subsubType + '>' + subsubs.join('') + '</' + subsubType + '>' : '';
            subs.push('<li>' + inlineToHtml(subContent) + ssh + '</li>');
          }
          const sh = subs.length ? '<' + subType + '>' + subs.join('') + '</' + subType + '>' : '';
          items.push([lt, ic, sh]);
        }
        if (items.length) {
          const lt = items[0][0];
          const lis = items.map(function(it) { return '<li>' + inlineToHtml(it[1]) + it[2] + '</li>'; }).join('');
          body.push('<' + lt + '>' + lis + '</' + lt + '>');
        }

      } else if (name === 'newline') {
        body.push('<br>'); i++;
      } else if (name === 'pagebreak') {
        body.push('<div style="page-break-after:always"></div>'); i++;
      } else if (name === 'insertspace') {
        body.push('<hr>'); i++;
      } else if (name === 'error') {
        body.push('<div class="celes-error">&#9888; ' + esc(content || '') + '</div>'); i++;
      } else {
        i++;
      }
    }

    return { title: title, body: body.join('\n') };
  }

  global.CelesParser = { parseCeles: parseCeles };

})(typeof window !== 'undefined' ? window : globalThis);

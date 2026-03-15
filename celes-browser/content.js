// Celes Renderer — content script v0.1.5

(function () {
  const url = window.location.href;

  const isCelesFile = /\.celes(\?.*)?$/.test(url.split('#')[0]);
  if (!isCelesFile) return;

  function getRawSource() {
    const pre = document.querySelector('pre');
    if (pre && pre.textContent.trim().startsWith('<!Celes')) return pre.textContent;
    const bodyText = document.body ? document.body.innerText : '';
    if (bodyText.trim().startsWith('<!Celes')) return bodyText;
    return document.documentElement.innerText || '';
  }

  function init() {
    const source = getRawSource();
    if (!source || !source.trim().startsWith('<!Celes')) return;

    if (typeof CelesParser === 'undefined') {
      console.error('[Celes] Parser not loaded');
      return;
    }

    const { title, bgColor, body } = CelesParser.parseCeles(source);
    const filename = decodeURIComponent(url.split('/').pop().split('?')[0]);

    const css = `
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

      body {
        font-family: system-ui, -apple-system, sans-serif;
        line-height: 1.75;
        color: #1a1a1a;
        background: ${bgColor ? bgColor : '#ffffff'};
      }

      #celes-bar {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 0.5rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.85rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.4);
        font-family: system-ui, sans-serif;
      }
      #celes-bar .badge {
        background: #D4622A;
        color: #fff;
        font-weight: 700;
        font-size: 0.68rem;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        flex-shrink: 0;
      }
      #celes-bar .doc-title {
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 300px;
      }
      #celes-bar .filename {
        opacity: 0.45;
        font-family: monospace;
        font-size: 0.8rem;
        margin-left: auto;
        white-space: nowrap;
      }
      #celes-bar button {
        background: #313244;
        border: none;
        color: #cdd6f4;
        padding: 0.3rem 0.85rem;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.8rem;
        font-family: system-ui, sans-serif;
        flex-shrink: 0;
      }
      #celes-bar button:hover { background: #45475a; }

      #celes-content {
        max-width: 820px;
        margin: 2.5rem auto;
        padding: 0 1.5rem 5rem;
      }

      h1, h2, h3, h4, h5, h6 { line-height: 1.3; margin-top: 1.8em; margin-bottom: 0.5em; color: #111; }
      h1 { font-size: 2.1rem; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
      h2 { font-size: 1.55rem; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
      h3 { font-size: 1.25rem; }
      h4 { font-size: 1.1rem; }
      h5, h6 { font-size: 1rem; }

      p { margin: 0.85em 0; }

      blockquote {
        border-left: 4px solid #D4622A;
        margin: 1.2em 0;
        padding: 0.5rem 1.2rem;
        color: #555;
        background: #fff8f5;
        border-radius: 0 5px 5px 0;
        font-style: italic;
      }
      blockquote.nested {
        border-left: 4px solid #cba6f7;
        margin-left: 1.5rem;
        background: #fdf8ff;
      }

      pre {
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 1.2rem;
        border-radius: 8px;
        overflow-x: auto;
        margin: 1.2em 0;
        font-size: 0.9em;
        line-height: 1.6;
      }
      code {
        background: #f0f0f0;
        padding: 0.15em 0.45em;
        border-radius: 4px;
        font-size: 0.88em;
        font-family: 'Fira Code', 'Cascadia Code', monospace;
      }
      pre code { background: none; padding: 0; color: inherit; font-size: 1em; }

      ul, ol { padding-left: 1.8rem; margin: 0.75em 0; }
      li { margin: 0.3em 0; line-height: 1.65; }

      table { border-collapse: collapse; width: 100%; margin: 1.2em 0; font-size: 0.95em; }
      th, td { border: 1px solid #ddd; padding: 0.55rem 1rem; text-align: left; }
      th { background: #f5f5f5; font-weight: 600; }
      tr:nth-child(even) td { background: #fafafa; }

      img { max-width: 100%; height: auto; border-radius: 6px; }
      a { color: #D4622A; text-decoration: none; }
      a:hover { text-decoration: underline; }

      hr { border: none; border-top: 1px solid #e0e0e0; margin: 2em 0; }
      input[type="checkbox"] { margin-right: 0.4em; }

      sup, sub { font-size: 0.75em; line-height: 0; position: relative; vertical-align: baseline; }
      sup { top: -0.5em; }
      sub { bottom: -0.25em; }

      mark { background: #fff176; color: #000; padding: 0.05em 0.25em; border-radius: 2px; }

      .celes-button {
        display: inline-block;
        background: #D4622A;
        color: #fff !important;
        padding: 0.35em 0.9em;
        border-radius: 5px;
        text-decoration: none !important;
        font-size: 0.9em;
        font-weight: 500;
        margin: 0 0.1em;
      }
      .celes-button:hover { background: #b84e1e !important; }

      .celes-section {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2.5em 0 1.2em;
      }
      .celes-section::before, .celes-section::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #e0e0e0;
      }
      .celes-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        white-space: nowrap;
      }

      .celes-error {
        color: #c00;
        background: #fff0f0;
        border: 1px solid #fcc;
        padding: 0.4rem 0.8rem;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.9em;
        margin: 0.6em 0;
      }

      /* 0.1.5 */
      .celes-video {
        width: 100%;
        margin: 1em 0;
        border-radius: 8px;
        background: #000;
      }
      .celes-audio {
        width: 100%;
        margin: 1em 0;
      }

      #celes-source {
        display: none;
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 2rem;
        font-family: 'Fira Code', 'Cascadia Code', monospace;
        font-size: 0.88em;
        white-space: pre-wrap;
        word-break: break-word;
        max-width: 820px;
        margin: 2rem auto;
        border-radius: 8px;
      }
    `;

    document.title = title;
    document.head.innerHTML =
      '<meta charset="UTF-8">' +
      '<meta name="viewport" content="width=device-width, initial-scale=1.0">' +
      '<title>' + title + '</title>' +
      '<style>' + css + '</style>';

    document.body.innerHTML =
      '<div id="celes-bar">' +
        '<span class="badge">Celes 0.1.5</span>' +
        '<span class="doc-title">' + title + '</span>' +
        '<span class="filename">' + filename + '</span>' +
        '<button id="toggle-source-btn">View Source</button>' +
      '</div>' +
      '<div id="celes-content">' + body + '</div>' +
      '<pre id="celes-source"></pre>';

    document.getElementById('celes-source').textContent = source;

    let showingSource = false;
    document.getElementById('toggle-source-btn').addEventListener('click', function() {
      showingSource = !showingSource;
      document.getElementById('celes-content').style.display = showingSource ? 'none' : '';
      document.getElementById('celes-source').style.display  = showingSource ? 'block' : 'none';
      document.getElementById('toggle-source-btn').textContent = showingSource ? 'View Rendered' : 'View Source';
    });
  }

  init();
})();

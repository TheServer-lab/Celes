// Celes Renderer — content script
// Detects when a .celes file is opened directly and renders it as HTML.

(function () {
  const url = window.location.href;
  const isCelesFile = url.endsWith('.celes') || url.includes('.celes?');

  if (!isCelesFile) return;

  // Get the raw text — when a plain text file is opened in the browser
  // the content is inside <pre> or directly in <body>
  function getRawSource() {
    const pre = document.querySelector('pre');
    if (pre) return pre.textContent;
    return document.body ? document.body.innerText : '';
  }

  const source = getRawSource();
  if (!source || !source.trim().startsWith('<!Celes')) return;

  const { title, body } = CelesParser.parseCeles(source);

  // Replace the entire page
  document.title = title;
  document.head.innerHTML = `
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style>
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

      body {
        font-family: system-ui, -apple-system, sans-serif;
        line-height: 1.7;
        color: #1a1a1a;
        background: #ffffff;
        padding: 0;
      }

      /* Top bar */
      #celes-bar {
        position: sticky;
        top: 0;
        z-index: 100;
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 0.5rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.85rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
      }
      #celes-bar .badge {
        background: #89b4fa;
        color: #1e1e2e;
        font-weight: 700;
        font-size: 0.7rem;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
      }
      #celes-bar .filename {
        opacity: 0.6;
        font-family: monospace;
        margin-left: auto;
      }
      #celes-bar button {
        background: #313244;
        border: none;
        color: #cdd6f4;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.8rem;
        transition: background 0.15s;
      }
      #celes-bar button:hover { background: #45475a; }

      /* Content */
      #celes-content {
        max-width: 820px;
        margin: 2.5rem auto;
        padding: 0 1.5rem 4rem;
      }

      h1, h2, h3, h4, h5, h6 {
        line-height: 1.3;
        margin-top: 1.8em;
        margin-bottom: 0.5em;
        color: #111;
      }
      h1 { font-size: 2.2rem; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
      h2 { font-size: 1.6rem; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
      h3 { font-size: 1.3rem; }

      p { margin: 0.9em 0; }

      blockquote {
        border-left: 4px solid #89b4fa;
        margin: 1.2em 0;
        padding: 0.5rem 1.2rem;
        color: #555;
        background: #f8f9ff;
        border-radius: 0 5px 5px 0;
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
      }
      code {
        background: #f0f0f0;
        padding: 0.15em 0.45em;
        border-radius: 4px;
        font-size: 0.88em;
        font-family: 'Fira Code', 'Cascadia Code', monospace;
      }
      pre code { background: none; padding: 0; color: inherit; font-size: 1em; }

      ul, ol { padding-left: 1.8rem; margin: 0.8em 0; }
      li { margin: 0.3em 0; }

      table {
        border-collapse: collapse;
        width: 100%;
        margin: 1.2em 0;
        font-size: 0.95em;
      }
      th, td { border: 1px solid #ddd; padding: 0.6rem 1rem; text-align: left; }
      th { background: #f5f5f5; font-weight: 600; }
      tr:nth-child(even) td { background: #fafafa; }

      img { max-width: 100%; height: auto; border-radius: 6px; }
      a { color: #89b4fa; text-decoration: none; }
      a:hover { text-decoration: underline; }

      hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 2em 0;
      }

      input[type="checkbox"] { margin-right: 0.4em; }

      mark { background: #fff176; color: #000; padding: 0.05em 0.25em; border-radius: 2px; }

      .celes-button {
        display: inline-block;
        background: #1a73e8;
        color: #fff !important;
        padding: 0.3em 0.85em;
        border-radius: 5px;
        text-decoration: none !important;
        font-size: 0.9em;
        font-weight: 500;
        margin: 0 0.1em;
        transition: background 0.15s;
      }
      .celes-button:hover { background: #1558b0; }

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
        background: #ddd;
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

      /* Source view toggle */
      #celes-source {
        display: none;
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 2rem;
        font-family: monospace;
        font-size: 0.88em;
        white-space: pre-wrap;
        word-break: break-all;
        max-width: 820px;
        margin: 2rem auto;
      }
    </style>
  `;

  // Get filename from URL
  const filename = url.split('/').pop().split('?')[0];

  document.body.innerHTML = `
    <div id="celes-bar">
      <span class="badge">Celes</span>
      <span>${title}</span>
      <span class="filename">${filename}</span>
      <button id="toggle-source-btn">View Source</button>
    </div>
    <div id="celes-content">${body}</div>
    <pre id="celes-source"></pre>
  `;

  // Source toggle
  document.getElementById('celes-source').textContent = source;
  let showingSource = false;
  document.getElementById('toggle-source-btn').addEventListener('click', () => {
    showingSource = !showingSource;
    document.getElementById('celes-content').style.display = showingSource ? 'none' : '';
    document.getElementById('celes-source').style.display = showingSource ? 'block' : 'none';
    document.getElementById('toggle-source-btn').textContent = showingSource ? 'View Rendered' : 'View Source';
  });

})();

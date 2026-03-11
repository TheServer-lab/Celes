chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const url = tabs[0]?.url || '';
  const isCeles = /\.celes(\?.*)?$/.test(url.split('#')[0]);
  const isFileUrl = url.startsWith('file://');

  const dot = document.getElementById('dot');
  const text = document.getElementById('status-text');
  const warning = document.getElementById('file-warning');

  if (isCeles) {
    dot.classList.remove('inactive');
    text.textContent = 'Rendering active';
    if (isFileUrl) {
      warning.style.display = 'block';
    }
  } else {
    text.textContent = 'Not a .celes file';
  }
});

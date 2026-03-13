"""
Celes Desktop — standalone GUI editor
Built with pywebview + PyInstaller
"""

import sys
import os
import json
import webview

# ── Resolve asset path (works both dev and bundled .exe) ──────────────
def resource(relative):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller extracts to _MEIPASS at runtime
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


# ── Python API exposed to JavaScript via window.pywebview.api ─────────
class CelesAPI:

    def __init__(self):
        self._current_file = None
        self._window = None

    def set_window(self, window):
        self._window = window

    # ── FILE → OPEN ──────────────────────────────────────────────────
    def open_file(self):
        """Show native open dialog, return {path, content} or None."""
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=('Celes Files (*.celes)', 'All Files (*.*)'),
        )
        if not result:
            return None
        path = result[0]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._current_file = path
            return {'path': path, 'name': os.path.basename(path), 'content': content}
        except Exception as e:
            return {'error': str(e)}

    # ── FILE → SAVE ──────────────────────────────────────────────────
    def save_file(self, content):
        """Save to current file path. Returns {path} or {error}."""
        if not self._current_file:
            return self.save_file_as(content)
        try:
            with open(self._current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return {'path': self._current_file}
        except Exception as e:
            return {'error': str(e)}

    # ── FILE → SAVE AS ───────────────────────────────────────────────
    def save_file_as(self, content):
        """Show native save dialog. Returns {path} or None."""
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename='document.celes',
            file_types=('Celes Files (*.celes)', 'All Files (*.*)'),
        )
        if not result:
            return None
        path = result if isinstance(result, str) else result[0]
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._current_file = path
            return {'path': path, 'name': os.path.basename(path)}
        except Exception as e:
            return {'error': str(e)}

    # ── EXPORT → HTML ────────────────────────────────────────────────
    def export_html(self, html_content):
        """Save rendered HTML to disk."""
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename='document.html',
            file_types=('HTML Files (*.html)', 'All Files (*.*)'),
        )
        if not result:
            return None
        path = result if isinstance(result, str) else result[0]
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return {'path': path}
        except Exception as e:
            return {'error': str(e)}

    # ── WINDOW TITLE ─────────────────────────────────────────────────
    def set_title(self, filename):
        if self._window:
            title = f'Celes — {filename}' if filename else 'Celes'
            self._window.set_title(title)

    # ── APP INFO ─────────────────────────────────────────────────────
    def get_version(self):
        return '0.1.4'


# ── MAIN ──────────────────────────────────────────────────────────────
def main():
    api = CelesAPI()
    editor_path = resource('assets/editor.html')

    window = webview.create_window(
        title='Celes',
        url=f'file://{editor_path}',
        js_api=api,
        width=1280,
        height=820,
        min_size=(900, 600),
        text_select=True,
        confirm_close=True,
    )

    api.set_window(window)

    # Inject desktop mode flag + keyboard shortcuts after DOM loads
    def on_loaded():
        window.evaluate_js("""
            // Signal desktop mode — enables native file menu
            window.__CELES_DESKTOP__ = true;
            window.__CELES_VERSION__ = '0.1.4';

            if (typeof initDesktopMenu === 'function') {
                initDesktopMenu();
            }
        """)

    window.events.loaded += on_loaded

    webview.start(debug=False)


if __name__ == '__main__':
    main()

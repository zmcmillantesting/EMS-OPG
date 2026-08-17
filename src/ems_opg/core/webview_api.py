"""
Methods exposed to the frontend as window.pywebview.api.* inside the
PyWebView window. Lets JS trigger a native "Save As" dialog instead of the
browser-only Blob-download trick, which PyWebView's embedded browser
engines don't reliably support.
"""

import webview


class WebviewApi:

    def save_file(self, filename, content):
        """
        Prompt the operator for a save location via a native dialog, then
        write `content` there. Returns {"saved": False} if the operator
        cancels the dialog.
        """

        result = webview.active_window().create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=filename,
            file_types=("CSV Files (*.csv)", "All files (*.*)"),
        )

        if not result:
            return {"saved": False}

        path = result if isinstance(result, str) else result[0]

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)

        return {"saved": True, "path": path}

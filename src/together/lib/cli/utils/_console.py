from rich.theme import Theme
from rich.console import Console

custom_theme = Theme(
    {
        # Text styles
        "primary": "#caaef5",  # Purple 300 ⭐ (lighter when bold)
        "secondary": "dim #caaef5",  # Purple 500 ⭐ (mid-tone without bold)
        "accent": "#ff68d4",  # Pink 500 ⭐
        "muted": "#98a0b3",  # Grey 400 ⭐
        # Semantic styles
        "success": "bold #0dce74",  # Green 400 ⭐
        "info": "#64afff",  # Blue 500 ⭐
        "warning": "bold #ff815d",  # Red 500 ⭐
        "error": "bold #c63800",  # Red 700 ⭐
        # UI elements
        "prompt": "#ba92ff",  # Purple 500 ⭐ (no bold)
        "prompt.choices": "#caaef5",  # Purple 300 ⭐
        "prompt.default": "dim #98a0b3",  # Grey 400 ⭐
        # Table styles
        "table.header": "#414858",  # Purple 300 ⭐ (lighter when bold)
        "table.border": "#626b84",  # Grey 600 ⭐
        "table.row": "#c4c9d4",  # Grey 300 ⭐
        # Progress/Loading
        "progress.description": "#caaef5",  # Purple 300 ⭐
        "progress.percentage": "bold #caaef5",  # Purple 300 ⭐ (lighter when bold)
        "bar.complete": "#ba92ff",  # Purple 500 ⭐ (no bold)
        "bar.finished": "#0dce74",  # Green 400 ⭐
        "bar.pulse": "#ff68d4",  # Pink 500 ⭐
    }
)

console = Console(theme=custom_theme)

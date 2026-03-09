#!/usr/bin/env python3
"""
Demo script showcasing the CLI style guide with brand colors.
Run this to see all the styled components in action.
"""

from rich.box import ROUNDED
from rich.theme import Theme
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.columns import Columns
import time

# Custom theme with brand colors (using only core starred colors)
custom_theme = Theme({
    # Text styles
    "primary": "#caaef5",       # Purple 300 ⭐ (lighter when bold)
    "secondary": "dim #caaef5",          # Purple 500 ⭐ (mid-tone without bold)
    "accent": "#ff68d4",             # Pink 500 ⭐
    "muted": "#98a0b3",              # Grey 400 ⭐
    "dim": "dim #626b84",            # Grey 600 ⭐

    # Semantic styles
    "success": "bold #0dce74",       # Green 400 ⭐
    "info": "#64afff",               # Blue 500 ⭐
    "warning": "bold #ff815d",       # Red 500 ⭐
    "error": "bold #c63800",         # Red 700 ⭐

    # UI elements
    "prompt": "#ba92ff",             # Purple 500 ⭐ (no bold)
    "prompt.choices": "#caaef5",     # Purple 300 ⭐
    "prompt.default": "dim #98a0b3", # Grey 400 ⭐

    # Table styles
    "table.header": "#414858",  # Purple 300 ⭐ (lighter when bold)
    "table.border": "#626b84",       # Grey 600 ⭐
    "table.row": "#c4c9d4",          # Grey 300 ⭐

    # Progress/Loading
    "progress.description": "#caaef5",     # Purple 300 ⭐
    "progress.percentage": "bold #caaef5", # Purple 300 ⭐ (lighter when bold)
    "bar.complete": "#ba92ff",             # Purple 500 ⭐ (no bold)
    "bar.finished": "#0dce74",             # Green 400 ⭐
    "bar.pulse": "#ff68d4",                # Pink 500 ⭐
})

console = Console(theme=custom_theme)


def demo_tables():
    """Demonstrate table styles."""
    console.print()
    console.print("[primary]═══ Tables Demo ═══[/primary]")
    console.print()

    # Create a data table with generous spacing
    table = Table(
        title="[primary]Available Models[/primary]",
        header_style="table.header",
        border_style="table.border",
        show_header=True,
        box=ROUNDED,
        padding=(0, 2),  # Generous horizontal padding
        # title_style="bold #caaef5",
        # title_justify="left",
    )

    table.add_column("Model", style="primary")
    table.add_column("Type", style="secondary")
    table.add_column("Status", style="success", justify="center")
    table.add_column("Context", style="muted", justify="right")
    table.add_column("Created", style="muted")

    # Add sample data
    models = [
        ("meta-llama/Llama-3-70b", "chat", "✓ active", "8k", "2024-01-15"),
        ("mistralai/Mistral-7B-v0.1", "completion", "✓ active", "32k", "2024-01-14"),
        ("Qwen/Qwen2-72B", "chat", "✓ active", "4k", "2024-01-13"),
        ("togethercomputer/GPT-NeoXT", "completion", "[error]⊘ inactive[error]", "2k", "2024-01-10"),
    ]

    for row in models:
        table.add_row(*row)

    console.print(table)
    console.print()


def demo_status_messages():
    """Demonstrate status message styles."""
    console.print()
    console.print("[primary]═══ Status Messages Demo ═══[/primary]")
    console.print()

    console.print("[success]✓[/success] Model deployed to production")
    console.print("[info]ℹ[/info] Using default configuration")
    console.print("[warning]⚠[/warning] Rate limit approaching")
    console.print("[error]✗[/error] API key required")
    console.print()


def demo_panels():
    """Demonstrate panel styles (card-based design)."""
    console.print()
    console.print("[primary]═══ Panels & Cards Demo ═══[/primary]")
    console.print()

    # Welcome/header panel
    console.print(Panel(
        "[primary]Together AI - Model Training[/primary]\n"
        "[secondary]Train custom models on your data[/secondary]",
        border_style="primary",
        padding=(1, 2),
    ))

    console.print()

    # Info panel with cleaner messaging
    console.print(Panel(
        "Set your API key to get started:\n\n"
        "[dim]export TOGETHER_API_KEY='your-key-here'[/dim]",
        title="[info]Setup Required[/info]",
        border_style="info",
        padding=(1, 3),
    ))

    console.print()

    # Configuration card
    console.print(Panel(
        "[info]Endpoint:[/info] https://api.together.xyz\n"
        "[info]Model:[/info] meta-llama/Llama-3-70b\n"
        "[info]Context:[/info] 8k tokens",
        title="[primary]Configuration[/primary]",
        border_style="table.border",
        padding=(1, 2),
    ))

    console.print()


def demo_prompts():
    """Demonstrate prompt styles (non-interactive demo)."""
    console.print()
    console.print("[primary]═══ Create Flow Demo ═══[/primary]")
    console.print()

    console.print(Panel(
        "[primary]Fine-Tune Setup[/primary]\n"
        "[secondary]Let's configure your training job[/secondary]",
        border_style="primary",
        padding=(1, 2),
    ))

    console.print()
    console.print("[dim]Step 1 of 3[/dim]")
    console.print("[prompt]Select base model:[/prompt] [prompt.choices](llama-3/mistral-7b/qwen-72b)[/prompt.choices]")
    console.print("[muted]→ llama-3[/muted]")

    console.print()
    console.print("[dim]Step 2 of 3[/dim]")
    console.print("[prompt]Training dataset:[/prompt] [prompt.default][./data/train.jsonl][/prompt.default]")
    console.print("[muted]→ ./data/train.jsonl[/muted]")

    console.print()
    console.print("[dim]Step 3 of 3[/dim]")
    console.print("[accent]Ready to start training? (Y/n)[/accent]")
    console.print("[muted]→ y[/muted]")

    console.print()
    console.print("[success]✓[/success] Training job created")
    console.print()


def demo_loading():
    """Demonstrate loading indicators."""
    console.print()
    console.print("[primary]═══ Loading Indicators Demo ═══[/primary]")
    console.print()

    # Spinner
    with console.status(
        "[progress.description]Loading models...[/progress.description]",
        spinner="dots",
        spinner_style="bar.pulse",
    ) as status:
        time.sleep(1.5)

    console.print("[success]✓[/success] Models loaded")
    console.print()

    # Progress bar
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bar.pulse"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(
            complete_style="bar.complete",
            finished_style="bar.finished",
        ),
        TaskProgressColumn(style="progress.percentage"),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[progress.description]Uploading training data...",
            total=100
        )

        for i in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)

        progress.update(task, description="[success]Upload complete[/success]")
        time.sleep(0.5)

    console.print()


def demo_columns():
    """Demonstrate column layout (dashboard cards)."""
    console.print()
    console.print("[primary]═══ Dashboard Demo ═══[/primary]")
    console.print()

    panels = [
        Panel(
            "[success]125[/success] models\n"
            "[secondary]Available[/secondary]",
            title="[primary]Catalog[/primary]",
            border_style="table.border",
            padding=(1, 2),
        ),
        Panel(
            "[accent]3[/accent] active\n"
            "[secondary]Training[/secondary]",
            title="[primary]Jobs[/primary]",
            border_style="table.border",
            padding=(1, 2),
        ),
        Panel(
            "[info]5000[/info] credits\n"
            "[secondary]Remaining[/secondary]",
            title="[primary]Balance[/primary]",
            border_style="table.border",
            padding=(1, 2),
        ),
    ]

    console.print(Columns(panels, equal=True, expand=True))
    console.print()


def main():
    """Run all demos."""
    console.clear()

    # Header
    console.print(Panel(
        "[primary]Together AI CLI - Style Guide Demo[/primary]\n"
        "[secondary]Showcasing brand colors with Rich library[/secondary]",
        border_style="primary",
        padding=(1, 2),
    ))

    demo_tables()
    demo_status_messages()
    demo_panels()
    demo_prompts()
    demo_loading()
    demo_columns()

    # Footer
    console.print(Panel(
        "[dim]End of demo - See CLI_STYLE_GUIDE.md for implementation details[/dim]",
        border_style="dim",
    ))


if __name__ == "__main__":
    main()

# CLI Style Guide - Rich Library

## Design Principles

Inspired by together.ai's modern, tech-forward aesthetic:

1. **Generous Whitespace** - Let content breathe with ample padding and line spacing
2. **Card-Based Layouts** - Use panels and borders to create visual containers
3. **Clear Hierarchy** - Bold headings, structured sections, obvious visual priority
4. **Professional yet Approachable** - Confident technical tone without jargon
5. **Deep Blues & Purples** - Core brand colors with cyan/teal accents for highlights
6. **Spacious Information Architecture** - Avoid dense walls of text, separate sections clearly

---

## Color Palette

**Core colors only** - Using starred/locked colors from your brand palette (400-500 range):

### Primary Colors
- **Brand Purple** (Primary accent): `#ba92ff` (500 ⭐), `#caaef5` (300 ⭐)
- **Brand Pink** (Secondary accent): `#ff68d4` (500 ⭐), `#fc92e3` (300 ⭐)
- **Brand Red** (Alerts): `#ff815d` (500 ⭐), `#c63800` (700 ⭐)

### Neutral Colors
- **Brand Grey** (Text/borders): `#98a0b3` (400 ⭐), `#626b84` (600 ⭐), `#c4c9d4` (300 ⭐)
- **Brand Steel** (Subtle backgrounds): `#8eafd0` (500 ⭐), `#aec7e1` (300 ⭐)

### Accent Colors
- **Brand Blue** (Info): `#64afff` (500 ⭐)
- **Brand Green** (Success): `#0dce74` (400 ⭐)
- **Brand Teal** (Highlights): `#00c7d1` (500 ⭐)

### Semantic Colors
- **Error**: `#c63800` (Red 700 ⭐)
- **Warning**: `#ff815d` (Red 500 ⭐)

---

## Rich Theme Configuration

```python
from rich.theme import Theme
from rich.console import Console

# Define your custom theme (using only core starred colors)
custom_theme = Theme({
    # Text styles
    "primary": "bold #caaef5",       # Purple 300 ⭐ (lighter when bold)
    "secondary": "#ba92ff",          # Purple 500 ⭐ (mid-tone without bold)
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
    "table.header": "bold #caaef5",  # Purple 300 ⭐ (lighter when bold)
    "table.border": "#626b84",       # Grey 600 ⭐
    "table.row": "#c4c9d4",          # Grey 300 ⭐
    "table.row.alt": "#98a0b3",      # Grey 400 ⭐

    # Progress/Loading
    "progress.description": "#caaef5",     # Purple 300 ⭐
    "progress.percentage": "bold #caaef5", # Purple 300 ⭐ (lighter when bold)
    "bar.complete": "#ba92ff",             # Purple 500 ⭐ (no bold)
    "bar.finished": "#0dce74",             # Green 400 ⭐
    "bar.pulse": "#ff68d4",                # Pink 500 ⭐
})

console = Console(theme=custom_theme)
```

---

## Tables

**Design Note**: Tables are your "cards" - use generous padding and spacing to mirror the website's spacious aesthetic.

### Basic Table Style

```python
from rich.table import Table
from rich.console import Console

console = Console(theme=custom_theme)

def create_data_table(title, data, columns):
    """Create a styled table for displaying data."""
    table = Table(
        title=f"[primary]{title}[/primary]",
        header_style="table.header",
        border_style="table.border",
        show_header=True,
        show_lines=False,
        padding=(0, 2),  # Generous horizontal padding
        title_style="bold #caaef5",
        title_justify="left",
    )

    # Add columns
    for col in columns:
        table.add_column(
            col["name"],
            style=col.get("style", "table.row"),
            justify=col.get("justify", "left"),
            no_wrap=col.get("no_wrap", False),
        )

    # Add rows with alternating styles
    for i, row in enumerate(data):
        style = "table.row" if i % 2 == 0 else "dim"
        table.add_row(*row, style=style)

    return table
```

### Example Usage

```python
# Example: List models
columns = [
    {"name": "Model ID", "style": "primary"},
    {"name": "Type", "style": "secondary"},
    {"name": "Status", "style": "success", "justify": "center"},
    {"name": "Created", "style": "muted"},
]

data = [
    ["together-ai/model-1", "chat", "✓ active", "2024-01-15"],
    ["together-ai/model-2", "completion", "✓ active", "2024-01-14"],
    ["together-ai/model-3", "embedding", "⊘ inactive", "2024-01-10"],
]

# Add breathing room before and after tables
console.print()
table = create_data_table("Available Models", data, columns)
console.print(table)
console.print()
```

### Compact Table (for many rows)

```python
def create_compact_table(data):
    """Minimal table for dense data."""
    table = Table(
        border_style="dim #6b7280",
        show_edge=False,
        show_header=True,
        padding=(0, 1),
        collapse_padding=True,
    )
    # Add columns...
    return table
```

---

## User Prompts (Create Flows)

### Using Rich Prompt

```python
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.console import Console
from rich.panel import Panel

console = Console(theme=custom_theme)

def create_flow_example():
    """Example create flow with beautiful prompts."""

    # Title panel
    console.print(Panel(
        "[primary]Create New Fine-Tune Job[/primary]",
        border_style="primary",
        padding=(1, 2),
    ))

    # Step-by-step prompts
    console.print("\n[dim]Step 1 of 4[/dim]")
    model = Prompt.ask(
        "[prompt]Select base model[/prompt]",
        choices=["llama-3", "mistral-7b", "qwen-72b"],
        default="llama-3",
    )

    console.print("\n[dim]Step 2 of 4[/dim]")
    dataset = Prompt.ask(
        "[prompt]Training dataset path[/prompt]",
        default="./data/train.jsonl",
    )

    console.print("\n[dim]Step 3 of 4[/dim]")
    epochs = IntPrompt.ask(
        "[prompt]Number of epochs[/prompt]",
        default=3,
    )

    console.print("\n[dim]Step 4 of 4[/dim]")
    confirm = Confirm.ask(
        "[accent]Start training now?[/accent]",
        default=True,
    )

    if confirm:
        console.print("\n[success]✓[/success] Job created successfully!")
    else:
        console.print("\n[muted]Cancelled[/muted]")
```

### Custom Styled Prompts

```python
from rich.text import Text

def styled_prompt(label, description=None, required=True):
    """Create a beautifully styled prompt."""

    # Build prompt text
    prompt_text = Text()
    prompt_text.append("  → ", style="#ec4899")  # Brand pink arrow
    prompt_text.append(label, style="bold #a78bfa")  # Brand purple label

    if required:
        prompt_text.append(" *", style="#ef4444")  # Red asterisk

    if description:
        prompt_text.append(f"\n    {description}", style="dim #9ca3af")

    prompt_text.append("\n    ", style="")

    console.print(prompt_text, end="")
    return input()
```

### Multi-Select Style

```python
from rich.panel import Panel
from rich.columns import Columns

def show_options(title, options, selected=None):
    """Display options with visual selection indicators."""
    selected = selected or []

    option_texts = []
    for i, option in enumerate(options):
        if option in selected:
            indicator = "[success]●[/success]"
            style = "bold #a78bfa"
        else:
            indicator = "[dim]○[/dim]"
            style = "muted"

        option_texts.append(f"{indicator} [{style}]{option}[/{style}]")

    console.print(Panel(
        "\n".join(option_texts),
        title=f"[primary]{title}[/primary]",
        border_style="table.border",
        padding=(1, 2),
    ))
```

---

## Loading Indicators

### Spinner Styles

```python
from rich.spinner import Spinner
from rich.live import Live
from rich.table import Table
import time

def loading_spinner(text="Loading"):
    """Show a loading spinner with brand colors."""
    with console.status(
        f"[progress.description]{text}...[/progress.description]",
        spinner="dots",
        spinner_style="bar.pulse",  # Brand pink
    ) as status:
        # Your async operation here
        time.sleep(2)

    console.print(f"[success]✓[/success] {text} complete")
```

### Progress Bar

```python
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

def create_progress_bar():
    """Styled progress bar for long operations."""
    return Progress(
        SpinnerColumn(spinner_name="dots", style="bar.pulse"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(
            complete_style="bar.complete",
            finished_style="bar.finished",
            pulse_style="bar.pulse",
        ),
        TaskProgressColumn(style="progress.percentage"),
        TimeRemainingColumn(),
        console=console,
    )

# Usage
with create_progress_bar() as progress:
    task = progress.add_task(
        "[progress.description]Uploading dataset...",
        total=100
    )

    for i in range(100):
        time.sleep(0.05)
        progress.update(task, advance=1)

    progress.update(task, description="[success]Upload complete[/success]")
```

### Live Updating Table

```python
from rich.live import Live

def stream_results():
    """Show live-updating table during streaming operation."""
    table = Table(
        title="[primary]Training Metrics[/primary]",
        header_style="table.header",
    )
    table.add_column("Epoch", style="secondary")
    table.add_column("Loss", style="accent")
    table.add_column("Accuracy", style="success")

    with Live(table, console=console, refresh_per_second=4):
        for epoch in range(1, 11):
            time.sleep(0.5)
            table.add_row(
                str(epoch),
                f"{1.5 / epoch:.4f}",
                f"{85 + epoch:.1f}%"
            )
```

---

## Panels & Cards

**Design Note**: Panels are the CLI equivalent of the website's card-based layouts. Use them liberally to create visual containers and hierarchy.

### Welcome/Header Panels

```python
from rich.panel import Panel

# Use at the start of commands for context
console.print()
console.print(Panel(
    "[primary]Together AI - Fine-Tuning[/primary]\n"
    "[secondary]Train custom models on your data[/secondary]",
    border_style="primary",
    padding=(1, 2),
))
console.print()
```

### Information Cards

```python
# Group related information in visual containers
console.print(Panel(
    "[info]API Endpoint:[/info] https://api.together.xyz\n"
    "[info]Model:[/info] meta-llama/Llama-3-70b\n"
    "[info]Context:[/info] 8k tokens",
    title="[primary]Configuration[/primary]",
    border_style="table.border",
    padding=(1, 2),
))
```

### Emphasis on Whitespace

Always add empty lines before and after panels:

```python
console.print()  # Breathing room before
console.print(panel)
console.print()  # Breathing room after
```

---

## Status Messages

### Success, Info, Warning, Error

```python
def show_status(message, status="info"):
    """Display status messages with appropriate styling."""
    icons = {
        "success": "✓",
        "info": "ℹ",
        "warning": "⚠",
        "error": "✗",
    }

    icon = icons.get(status, "→")
    console.print(f"[{status}]{icon}[/{status}] {message}")

# Usage
show_status("Model deployed successfully", "success")
show_status("Using default configuration", "info")
show_status("Rate limit approaching", "warning")
show_status("Authentication failed", "error")
```

### Panels for Important Info

```python
from rich.panel import Panel
from rich.text import Text

def info_panel(title, content, style="info"):
    """Create an informational panel."""
    console.print(Panel(
        content,
        title=f"[{style}]{title}[/{style}]",
        border_style=style,
        padding=(1, 2),
    ))

# Usage
info_panel(
    "API Key Required",
    "Export your API key: [dim]export TOGETHER_API_KEY='your-key'[/dim]",
    style="warning"
)
```

---

## Layout Examples

### Dashboard View

```python
from rich.layout import Layout
from rich.panel import Panel

def show_dashboard():
    """Create a dashboard layout."""
    layout = Layout()

    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )

    layout["header"].update(Panel(
        "[primary]Together AI CLI[/primary]",
        border_style="primary",
    ))

    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    # Add content to each section
    # ...

    console.print(layout)
```

### Side-by-Side Comparison

```python
from rich.columns import Columns

def show_comparison(items):
    """Show items in columns."""
    panels = []
    for item in items:
        panels.append(Panel(
            item["content"],
            title=f"[secondary]{item['title']}[/secondary]",
            border_style="table.border",
        ))

    console.print(Columns(panels, equal=True, expand=True))
```

---

## Best Practices

### Color Usage Guidelines

All colors are core starred colors from your brand palette:

1. **Purple with Bold** (`#caaef5` - 300 ⭐): Headers, table headers, important bold text
   - Use lighter purple when combining with bold to avoid intensity
2. **Purple Regular** (`#ba92ff` - 500 ⭐): Prompts, progress bars, regular text
   - Use mid-tone purple for non-bold elements
3. **Pink** (`#ff68d4` - 500 ⭐): Accents, highlights, interactive elements
4. **Green** (`#0dce74` - 400 ⭐): Success states, confirmations, active status
5. **Blue** (`#64afff` - 500 ⭐): Information, neutral states
6. **Grey** (`#98a0b3` - 400 ⭐): Muted text, borders
7. **Grey Dark** (`#626b84` - 600 ⭐): Disabled states, dim text, table borders

**Key Pattern**: Bold purple → use lighter shade (300). Regular purple → use mid-tone (500).

### Accessibility

- Use bold text for important information
- Don't rely solely on color for meaning (use icons + color)
- Provide dim/muted variants for less important content
- Test in both light and dark terminal themes

### Spacing & Whitespace

Following the website's spacious aesthetic:

- **Always add empty lines** before and after major elements (tables, panels, sections)
- Use `console.print()` liberally to create breathing room
- Prefer `padding=(1, 2)` or `padding=(1, 3)` in panels for generous spacing
- Separate command sections with double line breaks
- Don't cram information - let each element have space

```python
# Good: Generous spacing
console.print()
console.print(panel)
console.print()
console.print(table)
console.print()

# Bad: Cramped
console.print(panel)
console.print(table)
```

### Messaging & Tone

Match the website's professional yet approachable voice:

- **Confident, not arrogant**: "Model deployed" not "Model successfully deployed (obviously)"
- **Clear, not jargon-heavy**: "Training started" not "Training job instantiated"
- **Helpful, not condescending**: "API key required" not "You forgot to set your API key"
- **Forward-looking**: "Building your model" not "Processing..."
- **Human-friendly**: Use contractions, natural phrasing

```python
# Good examples
"✓ Model deployed to production"
"Training your model on 1,000 examples"
"Let's set up your fine-tune job"

# Avoid
"SUCCESS: Model deployment operation completed successfully"
"Initiating training procedure on dataset"
"Fine-tune job configuration wizard"
```

### Consistency

- Always use themed console for output
- Stick to defined color roles (don't use success color for warnings)
- Use consistent spacing and padding (generous!)
- Keep table styles uniform across commands

---

## Quick Reference

```python
# Import and setup
from rich.console import Console
from rich.theme import Theme

console = Console(theme=custom_theme)

# Common patterns
console.print("[primary]Important text[/primary]")
console.print("[success]✓[/success] Success message")
console.print("[error]✗[/error] Error message")
console.print("[dim]Less important info[/dim]")

# Prompts
from rich.prompt import Prompt, Confirm
value = Prompt.ask("[prompt]Enter value[/prompt]")
confirmed = Confirm.ask("[accent]Continue?[/accent]")

# Progress
with console.status("[progress.description]Loading...", spinner="dots"):
    # do work
    pass

# Tables
from rich.table import Table
table = Table(header_style="table.header", border_style="table.border")
```

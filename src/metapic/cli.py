#!/usr/bin/env python3
"""
MetaPic CLI - Command Line Interface

This module provides the command-line interface for MetaPic Enhanced.
It offers three main commands: extract, rename, and stats.

The CLI is built using Typer for beautiful terminal output and Rich for
enhanced formatting. All commands integrate with the statistics tracking
system for comprehensive analytics.

Usage:
    metapic extract samples/ --out metadata.ndjson
    metapic stats
    metapic rename metadata.ndjson --pattern "{model}-{i:04d}"

Author: MetaPic Enhanced Team
Version: 2.0
"""

from __future__ import annotations
from pathlib import Path
import json
import orjson
from typing import Optional
import typer
from rich import print
from rich.table import Table

from .utils import iter_images
from .extract import exiftool_batch
from .plugins import run_parse_chain
from .models import ImageMeta
from .normalize import Normalizer
from .bulk import plan_rename
from .core.statistics_tracker import stats_tracker

# Initialize Typer CLI application
app = typer.Typer(add_completion=False, help="MetaPic CLI")

@app.command()
def extract(
    path: str = typer.Argument(..., help="File or directory"),
    out: Optional[Path] = typer.Option(None, "--out", help="Write NDJSON here"),
    skip_parse: bool = typer.Option(False, "--skip-parse", help="Only run exiftool"),
):
    """
    Extract metadata from AI-generated images.
    
    This command processes images using exiftool for raw metadata extraction,
    then applies specialized parsers for different AI platforms (A1111, ComfyUI,
    NovelAI, etc.). The results are displayed in a beautiful table or saved to
    NDJSON format for further processing.
    
    Args:
        path: Path to image file or directory containing images
        out: Optional output file path for NDJSON format
        skip_parse: Skip AI-specific parsing, only extract raw EXIF data
        
    Examples:
        metapic extract samples/
        metapic extract samples/ --out metadata.ndjson
        metapic extract single_image.png --skip-parse
    """
    files = list(iter_images([path]))
    if not files:
        typer.echo("No images found.")
        raise typer.Exit(code=1)

    raw = exiftool_batch(files)
    norm = Normalizer()

    rows = []
    for f in files:
        r = raw.get(str(f), {})
        parsed = run_parse_chain(r) if not skip_parse else {}
        parsed.update(norm.parse_text_block(parsed.get("prompt", "")))

        # Build kwargs safely; avoid duplicating 'path', 'metadata_raw', 'parsed_raw'
        explicit = {"path", "metadata_raw", "parsed_raw"}
        field_names = set(ImageMeta.model_fields.keys()) - explicit

        kwargs = {}
        for k in field_names:
            v = parsed.get(k)
            if v is None:
                continue
            if k == "size_bytes" and isinstance(v, str):
                # skip human-readable sizes; prefer numeric FileSize#
                continue
            kwargs[k] = v

        meta = ImageMeta(
            path=str(f),
            metadata_raw=r,
            parsed_raw=parsed,
            **kwargs,
        )
        rows.append(meta)
        
        # Add to statistics
        stats_tracker.add_image_metadata(meta)

    if out:
        with open(out, "wb") as fo:
            for m in rows:
                fo.write(orjson.dumps(m.model_dump()) + b"\n")
        print(f"[green]Wrote[/green] {len(rows)} records to {out}")
    else:
        table = Table(title="MetaPic Extract")
        for col in ["path", "model", "sampler", "steps", "cfg", "seed"]:
            table.add_column(col)
        for m in rows:
            table.add_row(
                m.path,
                str(m.model),
                str(m.sampler),
                str(m.steps),
                str(m.cfg),
                str(m.seed),
            )
        print(table)

@app.command()
def rename(
    ndjson: Path = typer.Argument(..., help="NDJSON produced by extract"),
    pattern: str = typer.Option("{title}-{i:04d}", help="Filename pattern"),
    dry_run: bool = typer.Option(True, help="Only show plan"),
):
    """
    Batch rename images based on metadata.
    
    This command reads metadata from an NDJSON file (produced by the extract
    command) and renames files according to a customizable pattern. The pattern
    can include metadata fields like model, steps, CFG scale, seed, etc.
    
    Args:
        ndjson: Path to NDJSON file containing metadata
        pattern: Filename pattern with placeholders (default: "{title}-{i:04d}")
        dry_run: Preview changes without actually renaming files
        
    Pattern Variables:
        {title}: Auto-generated title from metadata
        {model}: AI model name
        {steps}: Number of steps
        {cfg}: CFG scale value
        {seed}: Generation seed
        {i}: Sequential index (zero-padded)
        
    Examples:
        metapic rename metadata.ndjson --pattern "{model}-{i:04d}"
        metapic rename metadata.ndjson --pattern "{model}-s{steps}-cfg{cfg}" --no-dry-run
    """
    rows = []
    with open(ndjson, "rb") as f:
        for line in f:
            rows.append(ImageMeta(**json.loads(line)))
    plan = plan_rename(rows, pattern=pattern)
    for src, dst in plan.items():
        print(f"{src} -> {dst}")
    if not dry_run:
        for src, dst in plan.items():
            Path(src).rename(dst)
        print("Done.")

@app.command()
def stats(
    export: Optional[Path] = typer.Option(None, "--export", help="Export statistics to file"),
):
    """
    Show comprehensive processing statistics.
    
    This command displays detailed analytics about processed images, including
    model usage frequency, tag analysis, dimension distribution, and more.
    Statistics are automatically collected during metadata extraction.
    
    Args:
        export: Optional file path to export statistics in JSON format
        
    Examples:
        metapic stats
        metapic stats --export analytics.json
        
    Statistics Include:
        - Total images processed
        - Unique models and their usage frequency
        - Most common positive and negative tags
        - Image dimension distribution
        - Sampler and CFG scale analysis
    """
    summary = stats_tracker.get_statistics_summary()
    
    if export:
        import json
        with open(export, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"[green]Statistics exported to[/green] {export}")
    else:
        # Display statistics in a table
        table = Table(title="MetaPic Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Images", str(summary['total_images']))
        table.add_row("Unique Models", str(summary['unique_models']))
        table.add_row("Unique Positive Tags", str(summary['unique_positive_tags']))
        table.add_row("Unique Negative Tags", str(summary['unique_negative_tags']))
        table.add_row("Unique Dimensions", str(summary['unique_dimensions']))
        table.add_row("Unique Samplers", str(summary['unique_samplers']))
        
        print(table)
        
        # Show top models
        if summary['top_models']:
            models_table = Table(title="Top Models")
            models_table.add_column("Model", style="cyan")
            models_table.add_column("Count", style="green")
            
            for model, count in summary['top_models'][:10]:
                models_table.add_row(model, str(count))
            
            print(models_table)
        
        # Show top positive tags
        if summary['top_positive_tags']:
            tags_table = Table(title="Top Positive Tags")
            tags_table.add_column("Tag", style="cyan")
            tags_table.add_column("Count", style="green")
            
            for tag, count in summary['top_positive_tags'][:15]:
                tags_table.add_row(tag, str(count))
            
            print(tags_table)

if __name__ == "__main__":
    app()

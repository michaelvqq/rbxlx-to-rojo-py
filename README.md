# rbxlx-to-rojo-py

Python port of the rbxlx-to-rojo Rust tool for converting Roblox place files to Rojo projects.

## Overview

This is a Python conversion of the original Rust implementation. It converts Roblox XML place files (`.rbxlx`, `.rbxmx`) into Rojo project structures.

## Structure

- `cli.py` - Command-line interface and main entry point
- `lib.py` - Core processing logic for tree traversal and instruction generation
- `filesystem.py` - Filesystem operations and project file generation
- `structures.py` - Data structures and base classes
- `rbx_dom.py` - Roblox XML file parser and DOM representation

## Features

- Parse Roblox XML files (.rbxlx, .rbxmx)
- Generate Rojo project structure with proper folder hierarchy
- Handle Scripts, LocalScripts, and ModuleScripts
- Generate .meta.json files for special instances
- Respect Roblox services (Workspace, ReplicatedStorage, etc.)
- (NOT SUPPORTED) Binary format support (.rbxl, .rbxm) - not yet implemented

## Dependencies

No external dependencies required! Uses only Python standard library:
- `xml.etree.ElementTree` - For XML parsing
- `pathlib` - For path operations
- `json` - For JSON serialization
- `tkinter` - For file dialogs (optional, falls back to CLI input)

## Usage

### Basic Usage

```bash
python cli.py [input_file] [output_directory]
```

### Examples

```bash
# With arguments
python cli.py MyPlace.rbxlx ./output

# Without arguments (will show file dialogs)
python cli.py
```

If arguments are not provided, the script will prompt you to select files using a file dialog (requires tkinter).

### Converting Binary Files

If you have a binary Roblox file (`.rbxl` or `.rbxm`), you need to convert it to XML format first:

1. Open the file in Roblox Studio
2. Go to File → Save As
3. Choose "Roblox XML Model Files (*.rbxlx)" or "Roblox XML Place Files (*.rbxmx)"
4. Save and use the XML file with this tool

## Current Status

 **Working:** XML file parsing and Rojo project generation for `.rbxlx` and `.rbxmx` files

 **Not implemented:** Binary format support for `.rbxl` and `.rbxm` files (use XML format instead)

## Differences from Rust Version

- Uses python lel

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd rbxlx-to-rojo-py

# No dependencies to install! Just run it
python cli.py
```

## Contributing

This is a port of the original Rust implementation. When adding features, try to maintain compatibility with the original design where possible.

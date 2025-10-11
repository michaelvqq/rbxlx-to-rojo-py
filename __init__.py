"""rbxlx-to-rojo-py - Convert Roblox place files to Rojo projects."""

__version__ = "0.0.1"

from .structures import (
    TreePartition,
    MetaFile,
    Instruction,
    AddToTreeInstruction,
    CreateFileInstruction,
    CreateFolderInstruction,
    InstructionReader,
    create_partition,
    create_add_to_tree_instruction,
)

from .filesystem import FileSystem, Project
from .lib import process_instructions
from .rbx_dom import Instance, WeakDom, from_reader_default, from_str_default

__all__ = [
    'TreePartition',
    'MetaFile',
    'Instruction',
    'AddToTreeInstruction',
    'CreateFileInstruction',
    'CreateFolderInstruction',
    'InstructionReader',
    'FileSystem',
    'Project',
    'process_instructions',
    'create_partition',
    'create_add_to_tree_instruction',
    'Instance',
    'WeakDom',
    'from_reader_default',
    'from_str_default',
]

"""Data structures for rbxlx-to-rojo conversion."""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from pathlib import Path
from abc import ABC, abstractmethod
import json


@dataclass
class TreePartition:
    """Represents a partition of the Roblox tree structure."""
    class_name: str
    children: Dict[str, 'TreePartition'] = field(default_factory=dict)
    ignore_unknown_instances: bool = True
    path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "$className": self.class_name,
            "$ignoreUnknownInstances": self.ignore_unknown_instances
        }
        
        if self.path is not None:
            path_str = str(self.path).replace("\\", "/")
            result["$path"] = path_str
        
        for name, child in self.children.items():
            result[name] = child.to_dict()
        
        return result


@dataclass
class MetaFile:
    """Represents a .meta.json file."""
    class_name: Optional[str] = None
    ignore_unknown_instances: bool = True
    properties: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "ignoreUnknownInstances": self.ignore_unknown_instances
        }
        
        if self.class_name is not None:
            result["className"] = self.class_name

        if self.properties:
            result["properties"] = self.properties
        
        return result


@dataclass
class Instruction:
    """Base class for filesystem instructions."""
    pass


@dataclass
class AddToTreeInstruction(Instruction):
    """Instruction to add an item to the project tree."""
    name: str
    partition: TreePartition


@dataclass
class CreateFileInstruction(Instruction):
    """Instruction to create a file."""
    filename: Path
    contents: bytes


@dataclass
class CreateFolderInstruction(Instruction):
    """Instruction to create a folder."""
    folder: Path


class InstructionReader(ABC):
    """Abstract base class for reading and processing instructions."""
    
    def finish_instructions(self):
        """Called when all instructions have been processed."""
        pass
    
    @abstractmethod
    def read_instruction(self, instruction: Instruction):
        """Process a single instruction."""
        pass
    
    def read_instructions(self, instructions: List[Instruction]):
        """Process a list of instructions."""
        for instruction in instructions:
            self.read_instruction(instruction)


def create_partition(instance, path: Path) -> TreePartition:
    """Create a TreePartition from an instance."""
    return TreePartition(
        class_name=instance.class_name,
        children={},
        ignore_unknown_instances=True,
        path=path
    )


def create_add_to_tree_instruction(instance, path: Path) -> AddToTreeInstruction:
    """Create an AddToTree instruction from an instance."""
    return AddToTreeInstruction(
        name=instance.name,
        partition=create_partition(instance, path)
    )

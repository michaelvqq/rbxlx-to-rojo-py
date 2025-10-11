"""Roblox file format parsers for XML and binary files."""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Instance:
    """Represents a Roblox instance."""
    
    def __init__(self, class_name: str, name: str = "", referent: Optional[str] = None):
        self.class_name = class_name
        self.name = name
        self.referent = referent or str(id(self))
        self.properties: Dict[str, Any] = {}
        self.children_refs: List[str] = []
        self.parent_ref: Optional[str] = None
    
    def get_property(self, name: str) -> Optional[Any]:
        """Get a property value."""
        return self.properties.get(name)
    
    def get_children(self) -> List[str]:
        """Get list of child referents."""
        return self.children_refs


class WeakDom:
    """Represents a weak DOM tree of Roblox instances."""
    
    def __init__(self, root_instance: Instance):
        self._root_ref = root_instance.referent
        self._instances: Dict[str, Instance] = {root_instance.referent: root_instance}
    
    def root_ref(self) -> str:
        """Get the root instance referent."""
        return self._root_ref
    
    def get_by_ref(self, ref: str) -> Optional[Instance]:
        """Get an instance by its referent."""
        return self._instances.get(ref)
    
    def insert(self, parent_ref: str, instance: Instance):
        """Insert an instance as a child of another."""
        parent = self.get_by_ref(parent_ref)
        if parent:
            parent.children_refs.append(instance.referent)
            instance.parent_ref = parent_ref
            self._instances[instance.referent] = instance
    
    def add_instance(self, instance: Instance):
        """Add an instance to the DOM."""
        self._instances[instance.referent] = instance


def parse_property_value(prop_elem) -> Any:
    """Parse a property value from an XML element."""
    prop_type = prop_elem.tag
    prop_text = prop_elem.text or ""
    
    # Handle different property types
    if prop_type == "string":
        return prop_text
    elif prop_type == "bool":
        return prop_text.lower() == "true"
    elif prop_type in ("int", "int64"):
        return int(prop_text) if prop_text else 0
    elif prop_type in ("float", "double"):
        return float(prop_text) if prop_text else 0.0
    elif prop_type == "ProtectedString":
        return prop_text
    elif prop_type == "Content":
        return prop_text
    elif prop_type == "BinaryString":
        # Binary strings are base64 encoded in XML
        import base64
        try:
            return base64.b64decode(prop_text).decode('utf-8', errors='ignore')
        except:
            return prop_text
    else:
        # For unknown types, just return the text
        return prop_text


def parse_instance(item_elem, parent_ref: str, dom: WeakDom):
    """Recursively parse an instance and its children from XML."""
    class_name = item_elem.get("class", "Unknown")
    referent = item_elem.get("referent", None)
    
    instance = Instance(class_name=class_name, referent=referent)
    
    properties_elem = item_elem.find("Properties")
    if properties_elem is not None:
        for prop_elem in properties_elem:
            prop_name = prop_elem.get("name", "Unknown")
            prop_value = parse_property_value(prop_elem)
            instance.properties[prop_name] = prop_value
            
            if prop_name == "Name":
                instance.name = prop_value
    
    if parent_ref:
        dom.insert(parent_ref, instance)
    else:
        dom.add_instance(instance)
    
    for child_elem in item_elem.findall("Item"):
        parse_instance(child_elem, instance.referent, dom)


def from_reader_default(file_reader) -> WeakDom:
    """
    Parse a Roblox XML file (rbxlx/rbxmx) from a file reader.
    Returns a WeakDom instance.
    """
    try:
        tree = ET.parse(file_reader)
        root_elem = tree.getroot()
        
        if root_elem.tag != "roblox":
            raise ValueError("Not a valid Roblox XML file")
        
        root_instance = Instance(class_name="DataModel", name="DataModel")
        dom = WeakDom(root_instance)
        
        for item_elem in root_elem.findall("Item"):
            parse_instance(item_elem, root_instance.referent, dom)
        
        return dom
    
    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {e}")


def from_str_default(xml_string: str) -> WeakDom:
    """
    Parse a Roblox XML string.
    Returns a WeakDom instance.
    """
    import io
    return from_reader_default(io.StringIO(xml_string))


# Placeholder for binary format support
def from_reader_default_binary(file_reader) -> WeakDom:
    """
    Parse a Roblox binary file (rbxl/rbxm).
    This is a placeholder - full implementation would require the binary format spec.
    """
    raise NotImplementedError(
        "Binary Roblox file parsing is not yet implemented. "
        "Please convert your file to XML format (.rbxlx or .rbxmx) using Roblox Studio."
    )

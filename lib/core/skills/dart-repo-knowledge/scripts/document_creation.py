"""Markdown document creation from Dart doc JSON.

This module provides the DocumentCreation class which handles:
- Converting dartdoc JSON to structured Markdown
- Extracting class, enum, mixin, extension, and typedef documentation
- Organizing members (constructors, fields, methods, getters, setters)
- Adding layer metadata (data/domain/presentation)
- Including Jira ticket references
- Including pull request links

Example:
    from src import DocumentCreation

    documents = DocumentCreation.create_markdown_document_from_dart_doc_json(
        file_name="button",
        json_data=dartdoc_json,
        jira_tickets_markdown="## Related Jira Tickets\\n\\n- [MC-123](https://...)",
        pr_tickets_markdown="## Related Pull Requests\\n\\n- [#42](https://...)"
    )

    for markdown, metadata in documents:
        print(f"Generated: {metadata['name']} ({metadata['kind']})")
"""

import os
import re
import json
from typing import Dict, List, Tuple, Any

class DocumentCreation:
    @staticmethod
    def create_markdown_document_from_dart_doc_json(
        file_name: str,
        json_data: Dict[str, Any],
        jira_tickets_markdown: str = "",
        jira_tickets_list: List[str] = None,
        pr_tickets_markdown: str = "",
        pr_list: List[str] = None,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Creates markdown documents from Dart documentation JSON.
        
        This static method processes JSON data from Dart documentation and generates structured 
        markdown documents that include file name, source information, and details about
        declarations (class, enum, mixin, extension, typedef) including their members such as
        constructors, fields, methods, getters, setters, and other components.
        
        Args:
            file_name (str): The name of the file to be used as the document title.
            json_data (Dict[str, Any]): JSON data containing Dart documentation information.
            jira_tickets_markdown (str): Pre-formatted Markdown section for Jira tickets.
            jira_tickets_list (List[str]): Raw list of Jira ticket IDs for metadata.
            pr_tickets_markdown (str): Pre-formatted Markdown section for pull requests.
            pr_list (List[str]): Raw list of PR IDs (numeric strings) for metadata.
            
        Returns:
            List[Tuple[str, Dict[str, Any]]]: A list of tuples, each containing:
                - A formatted markdown document as a string with the component documentation
                - Metadata dictionary with component information (kind, name, description, library)
                
        Example:
            ```python
            documents = DocumentCreation.create_markdown_document_from_dart_doc_json("button", json_data)
            for markdown, metadata in documents:
                print(f"Generated documentation for {metadata['name']} ({metadata['kind']})")
                # You can access other metadata fields like:
                # - metadata['description'] - The component description
                # - metadata['library'] - The library name (if available)
                # - metadata['jira_tickets'] - Comma-separated Jira ticket IDs
                # - metadata['pull_requests'] - Comma-separated PR IDs
            ```
        """
        documents = []

        # Process each item in the json data
        for item in json_data:
            header_document = []

            # Add component name as title
            header_document.append(f"# File: {file_name}")

            # Extract source file information
            source = None
            if "source" in item:
                source = item["source"]
                header_document.append(f"\nSource: {source}")

            # Add Jira tickets to header
            if jira_tickets_markdown:
                header_document.append(jira_tickets_markdown)

            # Add pull request links to header
            if pr_tickets_markdown:
                header_document.append(pr_tickets_markdown)

            # Extract library information
            library = None
            if "directives" in item:
                for directive in item["directives"]:
                    if directive.get("kind") == "library" and "name" in directive:
                        library = directive["name"]
                        break
                    
            # Extract class declarations
            if "declarations" in item:
                for declaration in item["declarations"]:
                    kind = declaration.get("kind", "")
                    name = declaration.get("name", "")
                    description = declaration.get("description", "")

                    document_parts = []
                    metadata = {
                        "kind": kind,
                        "name": name,
                        "description": description,
                        "file_name": file_name
                    }

                    # Add source path and infer layer
                    if source:
                        metadata["source"] = source
                        parts = source.replace("\\", "/").split("/")
                        # Strip leading 'lib/' prefix
                        if parts and parts[0] == "lib":
                            parts = parts[1:]
                        _known_layers = {
                            "data", "domain", "presentation",
                        }
                        metadata["layer"] = next(
                            (p for p in parts
                             if p in _known_layers),
                            "",
                        )

                    if jira_tickets_list:
                        metadata["jira_tickets"] = (
                            ", ".join(jira_tickets_list)
                        )

                    if pr_list:
                        metadata["pull_requests"] = (
                            ", ".join(pr_list)
                        )

                    if library:
                        metadata["library"] = library

                    if kind in ["class", "enum", "mixin", "extension", "typedef"]:
                        # Add declaration information based on kind
                        document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration(declaration))

                        # Add values information (for enums)
                        if "values" in declaration:
                            document_parts.append(f"\n## Values: {name}")
                            for value in declaration["values"]:
                                document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration_member(value))
                        
                        # Add member information
                        if "members" in declaration:
                            constructor = list()
                            fields = list()
                            methods = list()
                            getters = list()
                            setters = list()
                            others = list()
                            
                            for member in declaration["members"]:
                                kind = member.get("kind", "")
                                if kind == "constructor":
                                    constructor.append(member)
                                elif kind == "field":
                                    fields.append(member)
                                elif kind == "method":
                                    methods.append(member)
                                elif kind == "getter":
                                    getters.append(member)
                                elif kind == "setter":
                                    setters.append(member)
                                else:
                                    others.append(member)
                            
                            # Add constructor information
                            if constructor:
                                document_parts.append(f"\n## Constructors: {name}")
                                for member in constructor:
                                    document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration_member(member))

                            # Add field information
                            if fields:
                                document_parts.append(f"\n## Fields: {name}")
                                for member in fields:
                                    document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration_member(member))

                            # Add method information
                            if methods:
                                document_parts.append(f"\n## Methods: {name}")
                                for member in methods:
                                    document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration_member(member))

                            # Add getter information
                            if getters:
                                document_parts.append(f"\n## Getters: {name}")
                                for member in getters:
                                    document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration_member(member))

                            # Add setter information
                            if setters:
                                document_parts.append(f"\n## Setters: {name}")
                                for member in setters:
                                    document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration_member(member))

                            # Add other member information
                            if others:
                                document_parts.append(f"\n## Others: {name}")
                                for member in others:
                                    document_parts.append("\n" + DocumentCreation.__create_markdown_document_from_dart_doc_json_declaration_member(member))
                    
                    if document_parts:
                        documents.append(("\n".join(header_document + document_parts), metadata))

        return documents

    @staticmethod
    def __create_markdown_document_from_dart_doc_json_declaration(
        declaration: Dict[str, Any]
    ) -> str:
        document_parts = []
    
        # Add class name and description
        name = declaration.get("name", "")
        description = declaration.get("description", "")

        document_parts.append(f"## Class: {name}")

        # Add abstract status
        is_abstract = declaration.get("abstract", False)
        if is_abstract:
            document_parts.append("\nThis is an abstract class.")

        # Add inheritance information
        extends = declaration.get("extends", "")
        if extends:
            document_parts.append(f"\nExtends: {extends}")
        
        if description:
            # Clean up description (remove excessive newlines, etc.)
            document_parts.append(f"\n## Description: {name}")
            description = re.sub(r'\n{3,}', '\n\n', description)
            document_parts.append(f"\n{description}")
        
        return "\n".join(document_parts)

    @staticmethod
    def __create_markdown_document_from_dart_doc_json_declaration_member(
        member: Dict[str, Any]
    ) -> str:
        document_parts = []
    
        kind = member.get("kind", "")
        name = member.get("name", "")
        description = member.get("description", "")

        # Modifiers
        modifiers = ""
        if "factory" in member:
            modifiers += "(factory) "
        if "static" in member:
            modifiers += "(static) "
        if "final" in member:
            modifiers += "(final) "
        if "const" in member:
            modifiers += "(const) "
        
        # Format based on member kind
        if kind == "constructor":
            document_parts.append(f"### Constructor: {name} {modifiers}")
        elif kind == "field":
            document_parts.append(f"### Field: {name} {modifiers}")
        elif kind == "method":
            document_parts.append(f"### Method: {name} {modifiers}")
        elif kind == "getter":
            document_parts.append(f"### Getter: {name} {modifiers}")
        elif kind == "setter":
            document_parts.append(f"### Setter: {name} {modifiers}")
        else:
            document_parts.append(f"### {kind.capitalize()}: {name} {modifiers}")

        # Add type and return type
        field_type = member.get("type", "")
        if field_type:
            document_parts.append(f"\nType: {field_type}")
        return_type = member.get("returns", "")
        if return_type:
            document_parts.append(f"\nReturns: {return_type}")
        
        # Add description
        if description:
            document_parts.append(f"\n{description}")
        
        # Add parameters
        if "parameters" in member:
            params = member.get("parameters", [])
            if params:
                document_parts.append("\nParameters:")
                for param in params.get("all", []):
                    param_name = param.get("name", "")
                    param_type = param.get("type", "")
                    required = param.get("required", False)
                    
                    param_info = f"- {param_name}"
                    if param_type:
                        param_info += f" ({param_type})"
                    if required:
                        param_info += " (required)"
                    
                    document_parts.append(param_info)
        
        return "\n".join(document_parts)
    

if __name__ == "__main__":
    file_name = "color_token_library"
    json_path = os.path.join(os.path.dirname(__file__), "../dataset/color_token_library.json")
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    document = DocumentCreation.create_markdown_document_from_dart_doc_json(
        file_name=file_name,
        json_data=json_data
    )

    markdown, metadata = document[0]
    print(document[0])
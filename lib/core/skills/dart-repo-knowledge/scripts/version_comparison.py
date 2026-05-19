import os
import json
import glob
from typing import Dict, List, Any, Tuple, Optional


class VersionComparison:
    @staticmethod
    def load_version_data(dataset_dir: str, version: str) -> Dict[str, Any]:
        """
        Load all JSON documentation files for a specific version.

        Args:
            dataset_dir: Base dataset directory
            version: Version string (e.g., "v2.2.0")

        Returns:
            Dictionary mapping component names to their JSON data
        """
        version_dir = os.path.join(dataset_dir, version)

        if not os.path.exists(version_dir):
            return {}

        components = {}
        json_files = glob.glob(os.path.join(version_dir, "*.json"))

        for json_file in json_files:
            file_name = os.path.splitext(os.path.basename(json_file))[0]
            try:
                with open(json_file, 'r') as f:
                    components[file_name] = json.load(f)
            except json.JSONDecodeError:
                continue

        return components

    @staticmethod
    def extract_component_metadata(json_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract component metadata from dartdoc JSON data.

        Args:
            json_data: Raw JSON data from dartdoc_json

        Returns:
            List of component metadata dictionaries
        """
        components = []

        for item in json_data:
            if "declarations" not in item:
                continue

            for declaration in item["declarations"]:
                kind = declaration.get("kind", "")
                if kind not in ["class", "enum", "mixin", "extension", "typedef"]:
                    continue

                component = {
                    "kind": kind,
                    "name": declaration.get("name", ""),
                    "description": declaration.get("description", ""),
                    "abstract": declaration.get("abstract", False),
                    "extends": declaration.get("extends", ""),
                    "constructors": [],
                    "methods": [],
                    "fields": [],
                    "getters": [],
                    "setters": [],
                    "values": []
                }

                # Extract members
                if "members" in declaration:
                    for member in declaration["members"]:
                        member_kind = member.get("kind", "")
                        member_data = {
                            "name": member.get("name", ""),
                            "type": member.get("type", ""),
                            "returns": member.get("returns", ""),
                            "description": member.get("description", ""),
                            "static": member.get("static", False),
                            "final": member.get("final", False),
                            "const": member.get("const", False),
                            "factory": member.get("factory", False),
                            "parameters": member.get("parameters", {})
                        }

                        if member_kind == "constructor":
                            component["constructors"].append(member_data)
                        elif member_kind == "method":
                            component["methods"].append(member_data)
                        elif member_kind == "field":
                            component["fields"].append(member_data)
                        elif member_kind == "getter":
                            component["getters"].append(member_data)
                        elif member_kind == "setter":
                            component["setters"].append(member_data)

                # Extract enum values
                if "values" in declaration:
                    for value in declaration["values"]:
                        component["values"].append({
                            "name": value.get("name", ""),
                            "description": value.get("description", "")
                        })

                components.append(component)

        return components

    @staticmethod
    def compare_members(
        old_members: List[Dict],
        new_members: List[Dict],
        member_type: str
    ) -> Dict[str, Any]:
        """
        Compare members (constructors, methods, fields, etc.) between versions.

        Args:
            old_members: Members from old version
            new_members: Members from new version
            member_type: Type of member (constructor, method, field, etc.)

        Returns:
            Dictionary with added, removed, and modified members
        """
        old_names = {m["name"]: m for m in old_members}
        new_names = {m["name"]: m for m in new_members}

        added = []
        removed = []
        modified = []

        # Find added members
        for name, member in new_names.items():
            if name not in old_names:
                added.append(member)

        # Find removed members
        for name, member in old_names.items():
            if name not in new_names:
                removed.append(member)

        # Find modified members
        for name in old_names:
            if name in new_names:
                old_member = old_names[name]
                new_member = new_names[name]

                # Compare key fields
                changes = {}

                if old_member.get("type") != new_member.get("type"):
                    changes["type"] = {
                        "old": old_member.get("type", ""),
                        "new": new_member.get("type", "")
                    }

                if old_member.get("returns") != new_member.get("returns"):
                    changes["returns"] = {
                        "old": old_member.get("returns", ""),
                        "new": new_member.get("returns", "")
                    }

                if old_member.get("parameters") != new_member.get("parameters"):
                    changes["parameters"] = {
                        "old": old_member.get("parameters", {}),
                        "new": new_member.get("parameters", {})
                    }

                # Check modifiers
                for modifier in ["static", "final", "const", "factory"]:
                    if old_member.get(modifier) != new_member.get(modifier):
                        changes[modifier] = {
                            "old": old_member.get(modifier, False),
                            "new": new_member.get(modifier, False)
                        }

                if changes:
                    modified.append({
                        "name": name,
                        "changes": changes,
                        "old": old_member,
                        "new": new_member
                    })

        return {
            "added": added,
            "removed": removed,
            "modified": modified
        }

    @staticmethod
    def compare_versions(
        dataset_dir: str,
        from_version: str,
        to_version: str,
        component_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare two versions of Mekari Pixel to identify changes.

        Args:
            dataset_dir: Base dataset directory
            from_version: Starting version (e.g., "v1.30.0")
            to_version: Target version (e.g., "v2.2.0")
            component_filter: Optional list of component names to compare

        Returns:
            Comprehensive comparison results
        """
        # Load data for both versions
        old_data = VersionComparison.load_version_data(dataset_dir, from_version)
        new_data = VersionComparison.load_version_data(dataset_dir, to_version)

        if not old_data:
            raise ValueError(f"No data found for version {from_version}. Please generate documentation first.")
        if not new_data:
            raise ValueError(f"No data found for version {to_version}. Please generate documentation first.")

        # Extract all components from both versions
        old_components = {}
        for file_name, json_data in old_data.items():
            for component in VersionComparison.extract_component_metadata(json_data):
                old_components[component["name"]] = component

        new_components = {}
        for file_name, json_data in new_data.items():
            for component in VersionComparison.extract_component_metadata(json_data):
                new_components[component["name"]] = component

        # Apply component filter if provided
        if component_filter:
            old_components = {k: v for k, v in old_components.items() if k in component_filter}
            new_components = {k: v for k, v in new_components.items() if k in component_filter}

        # Identify added, removed, and modified components
        added_components = []
        removed_components = []
        modified_components = []

        old_names = set(old_components.keys())
        new_names = set(new_components.keys())

        # Added components
        for name in new_names - old_names:
            added_components.append({
                "name": name,
                "kind": new_components[name]["kind"],
                "description": new_components[name]["description"]
            })

        # Removed components
        for name in old_names - new_names:
            removed_components.append({
                "name": name,
                "kind": old_components[name]["kind"],
                "description": old_components[name]["description"]
            })

        # Modified components
        for name in old_names & new_names:
            old_comp = old_components[name]
            new_comp = new_components[name]

            changes = {}

            # Compare constructors
            constructor_diff = VersionComparison.compare_members(
                old_comp["constructors"],
                new_comp["constructors"],
                "constructor"
            )
            if any(constructor_diff.values()):
                changes["constructors"] = constructor_diff

            # Compare methods
            method_diff = VersionComparison.compare_members(
                old_comp["methods"],
                new_comp["methods"],
                "method"
            )
            if any(method_diff.values()):
                changes["methods"] = method_diff

            # Compare fields
            field_diff = VersionComparison.compare_members(
                old_comp["fields"],
                new_comp["fields"],
                "field"
            )
            if any(field_diff.values()):
                changes["fields"] = field_diff

            # Compare getters
            getter_diff = VersionComparison.compare_members(
                old_comp["getters"],
                new_comp["getters"],
                "getter"
            )
            if any(getter_diff.values()):
                changes["getters"] = getter_diff

            # Compare setters
            setter_diff = VersionComparison.compare_members(
                old_comp["setters"],
                new_comp["setters"],
                "setter"
            )
            if any(setter_diff.values()):
                changes["setters"] = setter_diff

            # Check if kind or description changed
            if old_comp["kind"] != new_comp["kind"]:
                changes["kind"] = {"old": old_comp["kind"], "new": new_comp["kind"]}

            if old_comp["description"] != new_comp["description"]:
                changes["description_changed"] = True

            if changes:
                modified_components.append({
                    "name": name,
                    "kind": new_comp["kind"],
                    "changes": changes
                })

        return {
            "summary": {
                "from_version": from_version,
                "to_version": to_version,
                "added": len(added_components),
                "removed": len(removed_components),
                "modified": len(modified_components)
            },
            "added_components": added_components,
            "removed_components": removed_components,
            "modified_components": modified_components
        }

"""
Knowledge graph storage for project entities, relationships, and canon rules.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from config.settings import STORAGE_CONFIG


class GraphStore:
    def __init__(self, project_name: str, base_dir: Optional[str] = None):
        self.project_name = project_name
        self.base_dir = base_dir or str(STORAGE_CONFIG.legacy_graphs_dir)
        os.makedirs(self.base_dir, exist_ok=True)

        self.path = os.path.join(self.base_dir, f"{project_name}_graph.json")

        # Load or initialize
        if not os.path.exists(self.path):
            self._init_empty_graph()

        self.data = self._load()

    def _init_empty_graph(self) -> None:
        """Initialize empty graph structure"""
        empty = {
            "entities": {
                "character": {},
                "location": {},
                "faction": {},
                "artifact": {},
                "concept": {},
            },
            "relationships": [],
            "events": [],
            "canon_rules": [],
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(empty, f, indent=2)

    def _load(self) -> Dict[str, Any]:
        """Load graph from disk"""
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self) -> None:
        """Save graph to disk"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add_entity(
        self,
        entity_type: str,
        entity_id: str,
        name: str,
        summary: str = "",
        tags: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add entity to graph"""
        tags = tags or []
        attributes = attributes or {}

        if entity_type not in self.data["entities"]:
            self.data["entities"][entity_type] = {}

        self.data["entities"][entity_type][entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "summary": summary,
            "tags": tags,
            "attributes": attributes,
        }
        self._save()

    def get_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by type and ID"""
        return self.data["entities"].get(entity_type, {}).get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> Dict[str, Any]:
        """Get all entities of a specific type"""
        return self.data["entities"].get(entity_type, {})

    def add_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        description: str = "",
    ) -> None:
        """Add relationship between entities"""
        self.data["relationships"].append(
            {
                "id": f"{from_id}->{to_id}:{rel_type}",
                "from_id": from_id,
                "to_id": to_id,
                "type": rel_type,
                "description": description,
            }
        )
        self._save()

    def get_relationships_for(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all relationships involving an entity"""
        return [
            rel
            for rel in self.data["relationships"]
            if rel["from_id"] == entity_id or rel["to_id"] == entity_id
        ]

    def add_event(
        self,
        event_id: str,
        name: str,
        summary: str = "",
        order: Optional[int] = None,
        time: Optional[str] = None,
        involved_entities: Optional[List[str]] = None,
    ) -> None:
        """Add event to graph"""
        involved_entities = involved_entities or []
        self.data["events"].append(
            {
                "id": event_id,
                "name": name,
                "summary": summary,
                "order": order,
                "time": time,
                "involved_entities": involved_entities,
            }
        )
        self._save()

    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events"""
        return self.data["events"]

    def add_canon_rule(
        self,
        rule_id: str,
        rule: str,
        scope: Optional[List[str]] = None,
        notes: str = "",
    ) -> None:
        """Add canon rule to graph"""
        scope = scope or []
        self.data["canon_rules"].append(
            {
                "id": rule_id,
                "rule": rule,
                "scope": scope,
                "notes": notes,
            }
        )
        self._save()

    def get_canon_rules(self) -> List[Dict[str, Any]]:
        """Get all canon rules"""
        return self.data["canon_rules"]

    def get_raw_graph(self) -> Dict[str, Any]:
        """Get raw graph data"""
        return self.data

    def replace_graph(self, new_graph: Dict[str, Any]) -> None:
        """Replace entire graph"""
        self.data = new_graph
        self._save()

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """Flatten all entity types into a single list"""
        flat = []
        for etype, items in self.data["entities"].items():
            for eid, ent in items.items():
                flat.append(ent)
        return flat

    def get_all_relationships(self) -> List[Dict[str, Any]]:
        """Return relationships as-is (already a list)"""
        return self.data.get("relationships", [])
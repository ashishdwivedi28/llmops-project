"""
Config loader — reads from Firestore in production, falls back to local JSON in dev.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, cast

logger = logging.getLogger(__name__)

_LOCAL_CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.json"

# Simple in-process cache to avoid hitting Firestore on every request
_cache: dict[str, Any] = {}
_CACHE_TTL_SECONDS = 60

_cache_timestamps: dict[str, float] = {}


def load_config(app_id: str) -> dict[str, Any]:
    """Load configuration for app_id.

    In production (FIRESTORE_PROJECT set): reads from Firestore with 60s cache.
    In development: reads from config/config.json.

    Raises:
        KeyError: If app_id is not found.
    """
    project = os.getenv("FIRESTORE_PROJECT")

    if project:
        return _load_from_firestore(app_id, project)
    else:
        return _load_from_json(app_id)


def _load_from_firestore(app_id: str, project: str) -> dict[str, Any]:
    """Load config and active prompt from Firestore."""
    now = time.time()
    if app_id in _cache and (now - _cache_timestamps.get(app_id, 0)) < _CACHE_TTL_SECONDS:
        return cast(dict[str, Any], _cache[app_id])

    try:
        from google.cloud import firestore  # type: ignore

        db = firestore.Client(project=project)

        doc = db.collection("configs").document(app_id).get()
        if not doc.exists:
            raise KeyError(f"app_id '{app_id}' not found in Firestore.")

        config = doc.to_dict()

        # Load active prompt version
        active_version = config.get("active_prompt_version", "v1")
        prompt_doc = (
            db.collection("configs")
            .document(app_id)
            .collection("prompts")
            .document(active_version)
            .get()
        )
        if prompt_doc.exists:
            config.update(prompt_doc.to_dict())

        _cache[app_id] = config
        _cache_timestamps[app_id] = now
        return cast(dict[str, Any], config)

    except KeyError:
        raise
    except Exception as e:
        logger.warning(f"Firestore load failed for {app_id}, falling back to JSON: {e}")
        return _load_from_json(app_id)


def _load_from_json(app_id: str) -> dict[str, Any]:
    """Load config from local config.json (development fallback)."""
    with open(_LOCAL_CONFIG_PATH) as f:
        all_configs = json.load(f)
    if app_id not in all_configs:
        raise KeyError(f"app_id '{app_id}' not found. Valid: {list(all_configs.keys())}")
    return cast(dict[str, Any], all_configs[app_id])


def invalidate_cache(app_id: str | None = None) -> None:
    """Clear the config cache. Call after a config update."""
    if app_id:
        _cache.pop(app_id, None)
        _cache_timestamps.pop(app_id, None)
    else:
        _cache.clear()
        _cache_timestamps.clear()

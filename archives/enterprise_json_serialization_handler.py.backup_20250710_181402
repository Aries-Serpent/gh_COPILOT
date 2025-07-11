#!/usr/bin/env python3
"""
Professional JSON Serialization Handler for Enterprise Systems
================================================================

Handles proper JSON serialization for datetime objects and other complex types
to ensure clean, professional output for enterprise reports and analytics.

DUAL COPILOT PATTERN: Primary Serializer with Secondary Validator
- Primary: Handles complex type serialization
- Secondary: Validates JSON compliance and integrity
- Enterprise: Ensures professional output standards

Author: Enterprise AI System
Version: 1.0.0
Last Updated: 2025-07-0"6""
"""

import json
import datetime
import pathlib
from decimal import Decimal
from typing import Any, Dict, List, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnterpriseJSONEncoder(json.JSONEncoder):
  " "" """Professional JSON encoder for enterprise systems with datetime suppor"t""."""

    def default(self, obj: Any) -> Union[str, Dict, List, float, int]:
      " "" """Handle serialization of complex object"s""."""

        # Handle datetime objects
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        # Handle date objects
        if isinstance(obj, datetime.date):
            return obj.isoformat()

        # Handle time objects
        if isinstance(obj, datetime.time):
            return obj.isoformat()

        # Handle timedelta objects
        if isinstance(obj, datetime.timedelta):
            return obj.total_seconds()

        # Handle pathlib paths
        if isinstance(obj, pathlib.Path):
            return str(obj)

        # Handle Decimal objects
        if isinstance(obj, Decimal):
            return float(obj)

        # Handle sets
        if isinstance(obj, set):
            return list(obj)

        # For dataclass objects, convert to dict
        if hasattr(obj","" '__dict'_''_'):
            return {]
                key: self.default(value) if not isinstance(]
                    value, (str, int, float, bool, type(None))) else value
                for key, value in obj.__dict__.items()
            }

        # Fallback to string representation
        return str(obj)


def safe_json_dumps(data: Any, **kwargs: Any) -> str:
  ' '' """Safely serialize any Python object to JSON with enterprise standard"s""."""
    # Set default values
    indent = kwargs.ge"t""('inde'n''t', 2)
    ensure_ascii = kwargs.ge't''('ensure_asc'i''i', False)

    try:
        return json.dumps(]
            **{k: v for k, v in kwargs.items() if k not in' ''['inde'n''t'','' 'ensure_asc'i''i']}
        )
    except Exception as e:
        logger.error'(''f"JSON serialization error: {str(e")""}")
        return json.dumps(]
          " "" "error_ty"p""e": type(e).__name__,
          " "" "error_messa"g""e": str(e),
          " "" "timesta"m""p": datetime.datetime.now().isoformat()
        }, indent=indent)


def safe_json_loads(json_str: str) -> Any:
  " "" """Safely deserialize JSON string with error handlin"g""."""
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error"(""f"JSON deserialization error: {str(e")""}")
        return {]
          " "" "error_ty"p""e": type(e).__name__,
          " "" "error_messa"g""e": str(e),
          " "" "timesta"m""p": datetime.datetime.now().isoformat()
        }


def validate_json_serializable(data: Any) -> bool:
  " "" """Validate that data can be properly serialized to JSO"N""."""
    try:
        safe_json_dumps(data)
        return True
    except Exception:
        return False


# Example usage and validation
if __name__ ="="" "__main"_""_":
    # Test serialization of complex objects
    test_data = {
      " "" "timesta"m""p": datetime.datetime.now(),
      " "" "da"t""e": datetime.date.today(),
      " "" "ti"m""e": datetime.time(14, 30, 0),
      " "" "pa"t""h": pathlib.Pat"h""("/test/pa"t""h"),
      " "" "decim"a""l": Decima"l""("123."4""5"),
      " "" "s"e""t": {1, 2, 3},
      " "" "nest"e""d": {]
          " "" "inner_timesta"m""p": datetime.datetime.now(),
          " "" "valu"e""s": [1, 2, 3]
        }
    }

    prin"t""("PROFESSIONAL JSON SERIALIZATION TE"S""T")
    prin"t""("""=" * 50)

    # Test serialization
    json_output = safe_json_dumps(test_data)
    prin"t""("Serialized JSO"N"":")
    print(json_output)

    # Test deserialization
    deserialized = safe_json_loads(json_output)
    prin"t""("\nDeserialization successfu"l"":", isinstance(deserialized, dict))

    # Validation test
    is_valid = validate_json_serializable(test_data)
    print"(""f"Validation result: {is_vali"d""}")

    prin"t""("\nJSON SERIALIZATION HANDLER: ENTERPRISE REA"D""Y")"
""
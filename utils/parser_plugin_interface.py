# parser_plugin_interface.py
from typing import Dict, Any

class ParserPluginInterface:
    """
    Each parser plugin must implement:
      - detect(metadata: Dict[str, Any]) -> bool
      - parse(metadata: Dict[str, Any]) -> Dict[str, Any]
    """

    @staticmethod
    def detect(metadata: Dict[str, Any]) -> bool:
        raise NotImplementedError

    @staticmethod
    def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

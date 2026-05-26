'''MCP memory server using fastmcp.

Example implementation of tasks in task description.
'''
import json
import fnmatch
from pathlib import Path
from datetime import datetime
from fastmcp import FastMCP

def current_ts() -> str:
    return datetime.utcnow().isoformat() + "Z"

class MemoryServer:
    def __init__(self, storage_path: str = "./memory_data.json"):
        self.mcp = FastMCP("Memory-Server")
        self.storage_path = Path(storage_path)
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save_memory({})

    def _load_memory(self) -> dict:
        with self.storage_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_memory(self, data: dict) -> None:
        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @self.mcp.tool()
    def save(self, key: str, value: any) -> bool:
        mem = self._load_memory()
        mem[key] = {"value": value, "timestamp": current_ts()}
        self._save_memory(mem)
        return True

    @self.mcp.tool()
    def get(self, key: str):
        mem = self._load_memory()
        return mem.get(key)

    @self.mcp.tool()
    def delete(self, key: str) -> bool:
        mem = self._load_memory()
        if key in mem:
            del mem[key]
            self._save_memory(mem)
            return True
        return False

    @self.mcp.tool()
    def list_keys(self, pattern: str = "*") -> list:
        mem = self._load_memory()
        return [k for k in mem if fnmatch.fnmatch(k, pattern)]

    @self.mcp.tool()
    def save_with_namespace(self, key: str, value: any, namespace: str = "default") -> bool:
        full_key = f"{namespace}:{key}"
        return self.save(full_key, value)

    @self.mcp.tool()
    def get_by_namespace(self, namespace: str = "default"):
        mem = self._load_memory()
        prefix = f"{namespace}:"
        return [{k[len(prefix):]: v} for k, v in mem.items() if k.startswith(prefix)]

if __name__ == "__main__":
    srv = MemoryServer()
    srv.mcp.run(transport="stdio", show_banner=False, log_level="ERROR")

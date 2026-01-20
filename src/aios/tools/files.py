"""
Files toolkit for AI-Native OS.

Provides tools for file system operations with safety checks.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    name: str
    size: int
    is_dir: bool
    extension: str
    modified: float

    @property
    def size_human(self) -> str:
        """Human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024
        return f"{self.size:.1f} TB"


class FilesToolkit:
    """Toolkit for file system operations.

    Provides safe file operations with configurable path restrictions.
    """

    def __init__(
        self,
        allowed_paths: Optional[List[str]] = None,
        blocked_paths: Optional[List[str]] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
    ):
        """Initialize files toolkit.

        Args:
            allowed_paths: List of allowed base paths.
            blocked_paths: List of blocked paths.
            max_file_size: Maximum file size for read/write operations.
        """
        self.allowed_paths = [Path(p).resolve() for p in (allowed_paths or [str(Path.home()), "/tmp"])]
        self.blocked_paths = [Path(p).resolve() for p in (blocked_paths or [
            "/etc", "/boot", "/root", "/sys", "/proc", "/dev"
        ])]
        self.max_file_size = max_file_size

    def _is_path_allowed(self, path: str) -> tuple[bool, str]:
        """Check if a path is allowed for operations.

        Returns:
            Tuple of (allowed, reason)
        """
        try:
            resolved = Path(path).resolve()
        except Exception as e:
            return False, f"Invalid path: {e}"

        # Check blocked paths first
        for blocked in self.blocked_paths:
            try:
                resolved.relative_to(blocked)
                return False, f"Path is in blocked directory: {blocked}"
            except ValueError:
                pass  # Not relative to blocked path, continue

        # Check if in allowed paths
        for allowed in self.allowed_paths:
            try:
                resolved.relative_to(allowed)
                return True, f"Path is within allowed directory: {allowed}"
            except ValueError:
                pass  # Not relative to this allowed path

        return False, f"Path is not within any allowed directory: {self.allowed_paths}"

    def read_file(self, path: str, max_lines: Optional[int] = None) -> str:
        """Read contents of a file.

        Args:
            path: Path to file.
            max_lines: Maximum number of lines to read.

        Returns:
            File contents or error message.
        """
        allowed, reason = self._is_path_allowed(path)
        if not allowed:
            return f"Access denied: {reason}"

        file_path = Path(path)
        if not file_path.exists():
            return f"File not found: {path}"

        if not file_path.is_file():
            return f"Not a file: {path}"

        if file_path.stat().st_size > self.max_file_size:
            return f"File too large (max {self.max_file_size} bytes)"

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                if max_lines:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append(f"... (truncated at {max_lines} lines)")
                            break
                        lines.append(line)
                    return ''.join(lines)
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, path: str, content: str, append: bool = False) -> str:
        """Write content to a file.

        Args:
            path: Path to file.
            content: Content to write.
            append: If True, append to file instead of overwriting.

        Returns:
            Success message or error.
        """
        allowed, reason = self._is_path_allowed(path)
        if not allowed:
            return f"Access denied: {reason}"

        if len(content.encode('utf-8')) > self.max_file_size:
            return f"Content too large (max {self.max_file_size} bytes)"

        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)

            action = "appended to" if append else "written to"
            return f"Successfully {action} {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def list_directory(self, path: str = ".", pattern: Optional[str] = None) -> str:
        """List contents of a directory.

        Args:
            path: Directory path.
            pattern: Optional glob pattern to filter results.

        Returns:
            Formatted directory listing or error.
        """
        allowed, reason = self._is_path_allowed(path)
        if not allowed:
            return f"Access denied: {reason}"

        dir_path = Path(path)
        if not dir_path.exists():
            return f"Directory not found: {path}"

        if not dir_path.is_dir():
            return f"Not a directory: {path}"

        try:
            if pattern:
                items = list(dir_path.glob(pattern))
            else:
                items = list(dir_path.iterdir())

            if not items:
                return f"Directory is empty: {path}"

            # Format output
            lines = [f"Contents of {path}:", ""]
            for item in sorted(items, key=lambda x: (not x.is_dir(), x.name.lower())):
                stat = item.stat()
                size = stat.st_size
                is_dir = item.is_dir()

                # Format size
                if is_dir:
                    size_str = "<DIR>"
                elif size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size/1024/1024:.1f}MB"

                lines.append(f"  {size_str:>10}  {item.name}{'/' if is_dir else ''}")

            return '\n'.join(lines)
        except Exception as e:
            return f"Error listing directory: {e}"

    def search_files(self, path: str, pattern: str, content: Optional[str] = None) -> str:
        """Search for files by name or content.

        Args:
            path: Base path to search.
            pattern: Glob pattern for file names.
            content: Optional text to search within files.

        Returns:
            List of matching files or error.
        """
        allowed, reason = self._is_path_allowed(path)
        if not allowed:
            return f"Access denied: {reason}"

        base_path = Path(path)
        if not base_path.exists():
            return f"Path not found: {path}"

        try:
            matches = []
            for file_path in base_path.rglob(pattern):
                if not file_path.is_file():
                    continue

                # Check if path is still allowed (might have traversed outside)
                if not self._is_path_allowed(str(file_path))[0]:
                    continue

                if content:
                    # Search within file
                    try:
                        if file_path.stat().st_size <= self.max_file_size:
                            with open(file_path, 'r', errors='ignore') as f:
                                if content.lower() in f.read().lower():
                                    matches.append(str(file_path))
                    except:
                        pass
                else:
                    matches.append(str(file_path))

                if len(matches) >= 100:
                    matches.append("... (truncated at 100 results)")
                    break

            if not matches:
                return f"No files found matching '{pattern}'" + (f" containing '{content}'" if content else "")

            return f"Found {len(matches)} file(s):\n" + '\n'.join(f"  {m}" for m in matches)
        except Exception as e:
            return f"Error searching files: {e}"

    def file_info(self, path: str) -> str:
        """Get detailed information about a file.

        Args:
            path: Path to file.

        Returns:
            File information or error.
        """
        allowed, reason = self._is_path_allowed(path)
        if not allowed:
            return f"Access denied: {reason}"

        file_path = Path(path)
        if not file_path.exists():
            return f"File not found: {path}"

        try:
            stat = file_path.stat()
            info = FileInfo(
                path=str(file_path.resolve()),
                name=file_path.name,
                size=stat.st_size,
                is_dir=file_path.is_dir(),
                extension=file_path.suffix,
                modified=stat.st_mtime
            )

            from datetime import datetime
            mod_time = datetime.fromtimestamp(info.modified).strftime('%Y-%m-%d %H:%M:%S')

            return f"""File: {info.name}
Path: {info.path}
Type: {'Directory' if info.is_dir else f'File ({info.extension or "no extension"})'}
Size: {info.size_human}
Modified: {mod_time}"""
        except Exception as e:
            return f"Error getting file info: {e}"

    def delete_file(self, path: str) -> str:
        """Delete a file (requires confirmation in actual use).

        Args:
            path: Path to file.

        Returns:
            Success message or error.
        """
        allowed, reason = self._is_path_allowed(path)
        if not allowed:
            return f"Access denied: {reason}"

        file_path = Path(path)
        if not file_path.exists():
            return f"File not found: {path}"

        try:
            if file_path.is_dir():
                shutil.rmtree(file_path)
                return f"Deleted directory: {path}"
            else:
                file_path.unlink()
                return f"Deleted file: {path}"
        except Exception as e:
            return f"Error deleting: {e}"

    def get_tools(self) -> list:
        """Get tool definitions for CAMEL integration.

        Returns:
            List of tool functions.
        """
        def read_file(path: str) -> str:
            """Read the contents of a file.

            Args:
                path: The path to the file to read

            Returns:
                The file contents or an error message
            """
            return self.read_file(path)

        def write_file(path: str, content: str) -> str:
            """Write content to a file. Creates the file if it doesn't exist.

            Args:
                path: The path to the file to write
                content: The content to write to the file

            Returns:
                Success message or error
            """
            return self.write_file(path, content)

        def list_directory(path: str = ".") -> str:
            """List the contents of a directory.

            Args:
                path: The directory path to list (default: current directory)

            Returns:
                A formatted listing of directory contents
            """
            return self.list_directory(path)

        def search_files(path: str, pattern: str) -> str:
            """Search for files matching a pattern.

            Args:
                path: The base path to search in
                pattern: Glob pattern to match (e.g., "*.py", "**/*.txt")

            Returns:
                List of matching files
            """
            return self.search_files(path, pattern)

        def get_file_info(path: str) -> str:
            """Get detailed information about a file or directory.

            Args:
                path: The path to inspect

            Returns:
                File information including size, type, and modification time
            """
            return self.file_info(path)

        return [read_file, write_file, list_directory, search_files, get_file_info]

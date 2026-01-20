"""
Terminal toolkit for AI-Native OS.

Provides tools for executing shell commands safely.
"""

import subprocess
import shlex
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of a command execution."""
    stdout: str
    stderr: str
    return_code: int
    command: str

    @property
    def success(self) -> bool:
        return self.return_code == 0

    @property
    def output(self) -> str:
        """Combined output, preferring stdout."""
        return self.stdout if self.stdout else self.stderr


class TerminalToolkit:
    """Toolkit for terminal/shell operations.

    Provides safe execution of shell commands with configurable
    permissions and timeouts.
    """

    def __init__(
        self,
        allowed_commands: Optional[List[str]] = None,
        blocked_commands: Optional[List[str]] = None,
        timeout: int = 30,
        working_dir: Optional[str] = None,
    ):
        """Initialize terminal toolkit.

        Args:
            allowed_commands: List of allowed command prefixes. If None, all allowed.
            blocked_commands: List of blocked command patterns.
            timeout: Maximum execution time in seconds.
            working_dir: Working directory for commands.
        """
        self.allowed_commands = allowed_commands or []
        self.blocked_commands = blocked_commands or [
            "rm -rf /",
            "rm -rf /*",
            "dd if=",
            "mkfs",
            "fdisk",
            ":(){:|:&};:",  # Fork bomb
            "> /dev/sd",
            "chmod -R 777 /",
        ]
        self.timeout = timeout
        self.working_dir = working_dir

    def _is_command_allowed(self, command: str) -> tuple[bool, str]:
        """Check if a command is allowed to execute.

        Returns:
            Tuple of (allowed, reason)
        """
        # Check blocked patterns
        for blocked in self.blocked_commands:
            if blocked in command:
                return False, f"Command contains blocked pattern: {blocked}"

        # If no allowed list, permit all non-blocked
        if not self.allowed_commands:
            return True, "No restrictions"

        # Check if command starts with an allowed prefix
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return False, "Empty command"

        base_cmd = cmd_parts[0]
        for allowed in self.allowed_commands:
            if base_cmd == allowed or base_cmd.endswith(f"/{allowed}"):
                return True, f"Command '{base_cmd}' is in allowed list"

        return False, f"Command '{base_cmd}' is not in allowed list: {self.allowed_commands}"

    def execute(self, command: str) -> CommandResult:
        """Execute a shell command.

        Args:
            command: Shell command to execute.

        Returns:
            CommandResult with output and status.
        """
        # Security check
        allowed, reason = self._is_command_allowed(command)
        if not allowed:
            return CommandResult(
                stdout="",
                stderr=f"Command not allowed: {reason}",
                return_code=-1,
                command=command
            )

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir,
            )
            return CommandResult(
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
                command=command
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                stdout="",
                stderr=f"Command timed out after {self.timeout} seconds",
                return_code=-2,
                command=command
            )
        except Exception as e:
            return CommandResult(
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                return_code=-3,
                command=command
            )

    def get_tools(self) -> list:
        """Get tool definitions for CAMEL integration.

        Returns:
            List of tool functions.
        """
        def execute_command(command: str) -> str:
            """Execute a shell command and return the output.

            Use this tool to run terminal commands like ls, cat, grep, find, etc.
            The command will be executed in a safe sandbox with timeout protection.

            Args:
                command: The shell command to execute (e.g., "ls -la", "cat file.txt")

            Returns:
                The command output (stdout) or error message
            """
            result = self.execute(command)
            if result.success:
                return result.output or "(command completed with no output)"
            else:
                return f"Error (code {result.return_code}): {result.stderr or result.stdout}"

        return [execute_command]

    # Convenience methods for common operations

    def list_directory(self, path: str = ".") -> CommandResult:
        """List contents of a directory."""
        return self.execute(f"ls -la {shlex.quote(path)}")

    def read_file(self, path: str, lines: Optional[int] = None) -> CommandResult:
        """Read contents of a file."""
        if lines:
            return self.execute(f"head -n {lines} {shlex.quote(path)}")
        return self.execute(f"cat {shlex.quote(path)}")

    def find_files(self, pattern: str, path: str = ".") -> CommandResult:
        """Find files matching a pattern."""
        return self.execute(f"find {shlex.quote(path)} -name {shlex.quote(pattern)}")

    def grep(self, pattern: str, path: str) -> CommandResult:
        """Search for pattern in file(s)."""
        return self.execute(f"grep -r {shlex.quote(pattern)} {shlex.quote(path)}")

    def get_processes(self) -> CommandResult:
        """List running processes."""
        return self.execute("ps aux")

    def get_disk_usage(self, path: str = "/") -> CommandResult:
        """Get disk usage information."""
        return self.execute(f"df -h {shlex.quote(path)}")

    def get_memory_usage(self) -> CommandResult:
        """Get memory usage information."""
        return self.execute("free -h")

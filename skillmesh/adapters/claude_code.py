from __future__ import annotations
import asyncio
import json
import subprocess
import os
from typing import Optional
from skillmesh.adapters.base import AgentAdapter
from skillmesh.models.context import ExecutionContext


class ClaudeCodeAdapter(AgentAdapter):
    """
    Claude Code adapter that runs Claude Code as a subprocess
    and communicates via Bridge API.
    """

    def __init__(
        self,
        claude_path: Optional[str] = None,
        base_url: str = "http://localhost:8080",
    ):
        """
        Initialize Claude Code adapter.

        Args:
            claude_path: Path to claude CLI. Defaults to 'claude'.
            base_url: Bridge API base URL.
        """
        self._name = "claude_code"
        self.claude_path = claude_path or os.environ.get("CLAUDE_PATH", "claude")
        self.base_url = base_url.rstrip("/")
        self._process: Optional[subprocess.Popen] = None
        self._port: int = 8080

    @property
    def name(self) -> str:
        """Return the adapter name."""
        return self._name

    async def start(self) -> None:
        """Start Claude Code in bridge mode as a subprocess."""
        if self._process is not None:
            return

        # Start Claude Code in remote-control (bridge) mode
        env = os.environ.copy()
        env["CLAUDE_PORT"] = str(self._port)

        self._process = subprocess.Popen(
            [self.claude_path, "remote-control"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to be ready
        await asyncio.sleep(2)

    async def stop(self) -> None:
        """Stop the Claude Code subprocess."""
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    async def execute(
        self,
        prompt: str,
        context: ExecutionContext,
        **kwargs,
    ) -> str:
        """
        Execute a prompt via Claude Code Bridge API.

        Args:
            prompt: The prompt to send
            context: Execution context

        Returns:
            Response text from Claude Code
        """
        import httpx

        url = f"{self.base_url}/v1/messages"

        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        # Substitute variables in prompt
        from skillmesh.utils.template import TemplateEngine
        prompt = TemplateEngine.substitute(prompt, context.variables)

        payload = {
            "model": kwargs.get("model", "claude-sonnet-4-20250514"),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("content", [{}])[0].get("text", "")
        except httpx.HTTPError as e:
            raise RuntimeError(f"Claude Code API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to execute prompt: {e}")
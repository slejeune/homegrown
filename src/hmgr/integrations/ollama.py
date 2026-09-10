from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class OllamaError(RuntimeError):
    """Raised when Ollama cannot be reached or returns an invalid response."""


class Ollama:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        data = None
        headers = {}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise OllamaError(
                f"Unable to connect to Ollama at {self.base_url}: {exc}"
            ) from exc
        except TimeoutError as exc:
            raise OllamaError(
                f"Ollama request timed out after {self.timeout}s."
            ) from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama returned invalid JSON.") from exc

    def list_models(self) -> list[dict[str, Any]]:
        """Return the models currently installed in Ollama."""
        response = self._request("GET", "/api/tags")

        models = response.get("models", [])

        if not isinstance(models, list):
            raise OllamaError("Ollama returned an unexpected model list.")

        return [model for model in models if isinstance(model, dict)]

    @staticmethod
    def _normalise_model_name(name: str) -> str:
        """
        Normalize an Ollama model name.

        Examples:
            llama3.1       -> llama3.1
            llama3.1:latest -> llama3.1
            llama3.1:8b    -> llama3.1:8b
        """
        name = name.strip()

        if name.endswith(":latest"):
            return name[: -len(":latest")]

        return name

    def model_installed(self, model: str) -> bool:
        """
        Check whether a model is installed.

        Treats `llama3.1` and `llama3.1:latest` as equivalent.
        Other tags remain distinct, e.g. `llama3.1:8b`.
        """
        requested = self._normalise_model_name(model)

        for installed_model in self.list_models():
            installed_name = installed_model.get("name")

            if not isinstance(installed_name, str):
                continue

            if self._normalise_model_name(installed_name) == requested:
                return True

        return False

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        format_schema: dict[str, Any] | None = None,
        temperature: float = 0.2,
        num_ctx: int | None = None,
    ) -> str:
        """Send a chat request to Ollama and return the model content."""

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                **({"num_ctx": num_ctx} if num_ctx is not None else {}),
            },
        }

        if format_schema is not None:
            payload["format"] = format_schema

        response = self._request(
            "POST",
            "/api/chat",
            payload,
        )

        message = response.get("message")

        if not isinstance(message, dict):
            raise OllamaError("Ollama response did not contain a valid message.")

        content = message.get("content")

        if not isinstance(content, str):
            raise OllamaError("Ollama response did not contain message content.")

        return content

    def chat_json(
        self,
        model: str,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
        *,
        temperature: float = 0.2,
        num_ctx: int | None = None,
    ) -> dict[str, Any]:
        """Ask Ollama for structured JSON and parse the response."""

        content = self.chat(
            model,
            messages,
            format_schema=schema,
            temperature=temperature,
            num_ctx=num_ctx,
        )

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama returned invalid JSON.") from exc

        if not isinstance(result, dict):
            raise OllamaError("Ollama returned JSON, but the result was not an object.")

        return result

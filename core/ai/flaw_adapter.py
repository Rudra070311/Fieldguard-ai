from __future__ import annotations
from typing import Any, Mapping, Optional

class FlawAdapter:
    def __init__(
        self,
        client,
        settings,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.client = client
        self.settings = settings
        self.model = model or settings.ai.flaw_model
        self.timeout = timeout or settings.ai.timeout_seconds

    async def analyze(self, prompt: str, *, system_prompt: Optional[str] = None, context: Optional[Mapping[str, Any]] = None, temperature: float = 0.0,) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        content = prompt

        if context:
            content = (
                f"{prompt}\n\n"
                f"Context:\n{dict(context)}"
            )

        messages.append(
            {
                "role": "user",
                "content": content,
            }
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            timeout=self.timeout,
        )

        if not response.choices:
            raise RuntimeError("Flaw returned no choices.")

        result = response.choices[0].message.content

        if not result:
            raise RuntimeError("Flaw returned an empty response.")

        return result.strip()

    async def reason_about_risk(self, risk_data: Mapping[str, Any],) -> str:
        return await self.analyze(
            "Analyze the supplied authentication risk signals "
            "and explain the security significance of the result.",
            system_prompt=(
                "You are an authentication-security reasoning engine. "
                "Do not invent signals, identities, or events. "
                "Use only the supplied evidence."
            ),
            context=risk_data,
            temperature=0.0,
        )
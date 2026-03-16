import os
from pathlib import Path
from typing import Literal, TypedDict, Union

DEVIN_LOCAL_PATH = "/opt/.devin"

CURSOR: Literal["cursor"] = "cursor"
CURSOR_CLI: Literal["cursor-cli"] = "cursor-cli"
CLAUDE: Literal["claude"] = "claude"
COWORK: Literal["cowork"] = "cowork"
DEVIN: Literal["devin"] = "devin"
REPLIT: Literal["replit"] = "replit"
GEMINI: Literal["gemini"] = "gemini"
CODEX: Literal["codex"] = "codex"
ANTIGRAVITY: Literal["antigravity"] = "antigravity"
AUGMENT_CLI: Literal["augment-cli"] = "augment-cli"
OPENCODE: Literal["opencode"] = "opencode"
GITHUB_COPILOT: Literal["github-copilot"] = "github-copilot"
GITHUB_COPILOT_CLI: Literal["github-copilot-cli"] = "github-copilot-cli"

KnownAgentNames = Literal[
    "cursor",
    "cursor-cli",
    "claude",
    "cowork",
    "devin",
    "replit",
    "gemini",
    "codex",
    "antigravity",
    "augment-cli",
    "opencode",
    "github-copilot",
]


class KnownAgentDetails(TypedDict):
    name: KnownAgentNames


class AgentResultAgent(TypedDict):
    is_agent: Literal[True]
    agent: KnownAgentDetails


class AgentResultNone(TypedDict):
    is_agent: Literal[False]
    agent: None


AgentResult = Union[AgentResultAgent, AgentResultNone]

KNOWN_AGENTS = {
    "CURSOR": CURSOR,
    "CURSOR_CLI": CURSOR_CLI,
    "CLAUDE": CLAUDE,
    "COWORK": COWORK,
    "DEVIN": DEVIN,
    "REPLIT": REPLIT,
    "GEMINI": GEMINI,
    "CODEX": CODEX,
    "ANTIGRAVITY": ANTIGRAVITY,
    "AUGMENT_CLI": AUGMENT_CLI,
    "OPENCODE": OPENCODE,
    "GITHUB_COPILOT": GITHUB_COPILOT,
}


def determine_agent() -> AgentResult:
    ai_agent = os.environ.get("AI_AGENT")
    if ai_agent:
        name = ai_agent.strip()
        if name:
            if name in (GITHUB_COPILOT, GITHUB_COPILOT_CLI):
                return {"is_agent": True, "agent": {"name": GITHUB_COPILOT}}
            return {"is_agent": True, "agent": {"name": name}}  # type: ignore[return-value]

    if os.environ.get("CURSOR_TRACE_ID"):
        return {"is_agent": True, "agent": {"name": CURSOR}}

    if os.environ.get("CURSOR_AGENT"):
        return {"is_agent": True, "agent": {"name": CURSOR_CLI}}

    if os.environ.get("GEMINI_CLI"):
        return {"is_agent": True, "agent": {"name": GEMINI}}

    if (
        os.environ.get("CODEX_SANDBOX")
        or os.environ.get("CODEX_CI")
        or os.environ.get("CODEX_THREAD_ID")
    ):
        return {"is_agent": True, "agent": {"name": CODEX}}

    if os.environ.get("ANTIGRAVITY_AGENT"):
        return {"is_agent": True, "agent": {"name": ANTIGRAVITY}}

    if os.environ.get("AUGMENT_AGENT"):
        return {"is_agent": True, "agent": {"name": AUGMENT_CLI}}

    if os.environ.get("OPENCODE_CLIENT"):
        return {"is_agent": True, "agent": {"name": OPENCODE}}

    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE"):
        if os.environ.get("CLAUDE_CODE_IS_COWORK"):
            return {"is_agent": True, "agent": {"name": COWORK}}
        return {"is_agent": True, "agent": {"name": CLAUDE}}

    if os.environ.get("REPL_ID"):
        return {"is_agent": True, "agent": {"name": REPLIT}}

    if (
        os.environ.get("COPILOT_MODEL")
        or os.environ.get("COPILOT_ALLOW_ALL")
        or os.environ.get("COPILOT_GITHUB_TOKEN")
    ):
        return {"is_agent": True, "agent": {"name": GITHUB_COPILOT}}

    if Path(DEVIN_LOCAL_PATH).exists():
        return {"is_agent": True, "agent": {"name": DEVIN}}

    return {"is_agent": False, "agent": None}

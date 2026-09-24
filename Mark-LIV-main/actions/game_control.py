"""Launch games and execute explicit, user-approved game input sequences."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

try:
    import pyautogui
except Exception:
    pyautogui = None


_STEAM_APP_IDS = {
    "stormworks": "573090",
    "stormworks build and rescue": "573090",
    "red dead redemption 2": "1174180",
    "rdr2": "1174180",
    "grand theft auto v": "271590",
    "gta v": "271590",
    "minecraft": "1672970",
}

_PROCESS_NAMES = {
    "stormworks": ("stormworks", "stormworks64"),
    "red dead redemption 2": ("rdr2", "rdr2.exe"),
    "rdr2": ("rdr2", "rdr2.exe"),
    "grand theft auto v": ("gta5", "gta5.exe"),
    "gta v": ("gta5", "gta5.exe"),
    "minecraft": ("java", "minecraftlauncher"),
}


def _key(value: Any) -> str:
    return " ".join(str(value or "").lower().strip().split())


def _process_running(game: str) -> bool:
    names = _PROCESS_NAMES.get(game, (game,))
    try:
        if platform.system() == "Windows":
            output = subprocess.run(
                ["tasklist"], capture_output=True, text=True, timeout=5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            ).stdout.lower()
            return any(name.lower() in output for name in names)
        output = subprocess.run(
            ["ps", "-A", "-o", "comm="], capture_output=True, text=True, timeout=5,
        ).stdout.lower()
        return any(name.lower() in output for name in names)
    except Exception:
        return False


def _launch_uri(uri: str) -> None:
    system = platform.system()
    if system == "Windows":
        subprocess.Popen(["cmd", "/c", "start", "", uri],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif system == "Darwin":
        subprocess.Popen(["open", uri], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    elif shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", uri], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    else:
        raise RuntimeError("No desktop URI launcher is available on this system")


def _launch_game(game: str, platform_name: str = "steam",
                 app_id: str | None = None) -> str:
    if not game:
        return "Please specify which game to launch."
    if _process_running(game):
        return f"{game} is already running."

    launcher = _key(platform_name) or "steam"
    resolved_id = str(app_id or _STEAM_APP_IDS.get(game, "")).strip()
    if launcher == "steam":
        if not resolved_id:
            return (f"I cannot launch '{game}' because its Steam AppID is unknown. "
                    "Provide app_id explicitly.")
        uri = f"steam://run/{resolved_id}"
    elif launcher == "epic":
        uri = f"com.epicgames.launcher://apps/{resolved_id}?action=launch"
    else:
        return f"Unsupported game platform '{platform_name}'. Use Steam or Epic."

    try:
        _launch_uri(uri)
    except Exception as exc:
        return f"Could not send the launch command for {game}: {exc}"

    time.sleep(2.0)
    if _process_running(game):
        return f"Launched {game}."
    return (f"Launch command sent for {game}, but its process is not visible yet. "
            "The game may still be loading or may use a different process name.")


def _execute_steps(raw_steps: Any, confirm: bool) -> str:
    if not confirm:
        return "Build input was not executed because confirm=true was not provided."
    if pyautogui is None:
        return "Build input requires PyAutoGUI. Run: python -m pip install pyautogui"

    if isinstance(raw_steps, str):
        try:
            steps = json.loads(raw_steps)
        except json.JSONDecodeError as exc:
            return f"Build input was not executed because steps is not valid JSON: {exc}"
    else:
        steps = raw_steps
    if not isinstance(steps, list) or not steps:
        return "No build steps were supplied, so nothing was changed in the game."
    if len(steps) > 500:
        return "Game input was rejected: maximum 500 steps per call."

    pyautogui.PAUSE = 0.08
    executed = 0
    try:
        for step in steps:
            if not isinstance(step, dict):
                return f"Build stopped after {executed} steps: each step must be an object."
            kind = _key(step.get("type"))
            if kind == "press":
                pyautogui.press(str(step["key"]))
            elif kind == "hotkey":
                keys = step.get("keys", [])
                if not isinstance(keys, list) or not keys:
                    return f"Build stopped after {executed} steps: hotkey needs keys."
                pyautogui.hotkey(*(str(key) for key in keys))
            elif kind == "write":
                pyautogui.write(str(step.get("text", "")), interval=0.02)
            elif kind == "key_down":
                pyautogui.keyDown(str(step["key"]))
            elif kind == "key_up":
                pyautogui.keyUp(str(step["key"]))
            elif kind == "click":
                pyautogui.click(int(step["x"]), int(step["y"]))
            elif kind == "mouse_down":
                pyautogui.mouseDown(button=str(step.get("button", "left")))
            elif kind == "mouse_up":
                pyautogui.mouseUp(button=str(step.get("button", "left")))
            elif kind == "move":
                pyautogui.moveTo(int(step["x"]), int(step["y"]), duration=0.15)
            elif kind == "screen_click":
                description = str(step.get("description", "")).strip()
                if not description:
                    return f"Game input stopped after {executed} steps: screen_click needs description."
                from actions.computer_control import computer_control
                result = computer_control({
                    "action": "screen_click",
                    "description": description,
                })
                if result.startswith("Element not found") or "failed" in result.lower():
                    return f"Game input stopped after {executed} steps: {result}"
            elif kind == "sleep":
                delay = min(10.0, max(0.0, float(step.get("seconds", 0.2))))
                time.sleep(delay)
            else:
                return f"Build stopped after {executed} steps: unsupported step '{kind}'."
            executed += 1
    except (KeyError, TypeError, ValueError) as exc:
        return f"Build stopped after {executed} steps: invalid step data ({exc})."
    except Exception as exc:
        return f"Build stopped after {executed} steps: {exc}"
    return f"Executed {executed} approved game input steps. Verify the game state before continuing."


def _save_lua(code: Any, filename: Any, confirm: bool) -> str:
    if not confirm:
        return "Lua was not saved because confirm=true was not provided."
    source = str(code or "").strip()
    if not source:
        return "No Lua code was supplied."
    safe_name = "".join(ch for ch in str(filename or "game_script.lua")
                        if ch.isalnum() or ch in "._-")
    if not safe_name.endswith(".lua"):
        safe_name += ".lua"
    directory = Path.home() / "MARK-LIV-game-scripts"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / safe_name
    path.write_text(source + "\n", encoding="utf-8")
    return f"Saved Lua script to {path}. It was not executed automatically."


def game_control(parameters=None, player=None) -> str:
    params = parameters or {}
    game = _key(params.get("game"))
    action = _key(params.get("action", "launch"))
    platform_name = _key(params.get("platform", "steam"))

    if action in {"launch", "open", "start"}:
        result = _launch_game(game, platform_name, params.get("app_id"))
    elif action in {"lua", "lua_code", "script"}:
        result = _save_lua(params.get("code"), params.get("filename"),
                           bool(params.get("confirm")))
        if params.get("steps"):
            launch_result = _launch_game(game, platform_name, params.get("app_id"))
            if "Could not" in launch_result or "cannot launch" in launch_result:
                return launch_result
            result = f"{result} {launch_result} {_execute_steps(params.get('steps'), bool(params.get('confirm')))}"
    elif action in {"build", "build_vehicle", "execute_build", "place_block", "customize", "play"}:
        launch_result = _launch_game(game, platform_name, params.get("app_id"))
        if "Could not" in launch_result or "cannot launch" in launch_result:
            return launch_result
        result = f"{launch_result} {_execute_steps(params.get('steps'), bool(params.get('confirm')))}"
    else:
        return f"Unsupported game action '{action}'. Use launch or build_vehicle."

    if player:
        try:
            player.write_log(f"[GameControl] {result}")
        except Exception:
            pass
    return result


TOOL = {
    "name": "game_control",
    "description": (
        "Launch an installed Steam or Epic game and control it with explicit, approved "
        "input steps. Supports launch, play, place_block, customize, build_vehicle, "
        "and lua. Use screen_click steps for visual interaction; never claim success "
        "unless the inputs were executed."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "launch | play | place_block | customize | build_vehicle | lua"},
            "game": {"type": "STRING", "description": "Installed game name, such as Stormworks"},
            "platform": {"type": "STRING", "description": "steam or epic"},
            "app_id": {"type": "STRING", "description": "Optional Steam AppID or Epic app identifier"},
            "confirm": {"type": "BOOLEAN", "description": "Must be true before keyboard/mouse build steps run"},
            "steps": {"type": "STRING", "description": "JSON array of press, key_down, key_up, hotkey, write, click, mouse_down, mouse_up, move, screen_click, and sleep steps"},
            "code": {"type": "STRING", "description": "Lua source to save for the selected game"},
            "filename": {"type": "STRING", "description": "Lua filename, saved under MARK-LIV-game-scripts"},
        },
        "required": ["game", "action"],
    },
    "handler": game_control,
}

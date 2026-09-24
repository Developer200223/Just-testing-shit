"""Game-player AI plugin for building, survival tasks, and combat loops.

This plugin is intentionally lightweight and deterministic: it gives the agent a
clear playbook rather than pretending to "see" the game world. The app can then
chain these plans into a real in-game routine while the broader automation layer
handles cursor, keyboard, and screen recognition.
"""

import re

PLUGIN = {
    "name": "game_player_ai",
    "description": (
        "Use this for block placement, building vehicles, mining and crafting loops, "
        "Red Dead Redemption 2 survival tasks such as skinning animals, fishing, "
        "missions, combat, cover, horse riding, and escaping lawmen. It can also "
        "plan how to level up the user, manage resource loops, and keep the player "
        "safe during shootouts or long survival runs."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "game": {"type": "STRING", "description": "Game or scenario, e.g. minecraft, red dead redemption 2, rdr2, or general"},
            "action": {"type": "STRING", "description": "Task type such as build_vehicle, place_block, farm_resources, mine, craft, combat, hide, ride_horse, evade_sheriffs, mission, level_up"},
            "target": {"type": "STRING", "description": "What to build, collect, defeat, or pursue"},
            "resource": {"type": "STRING", "description": "Resource to gather, such as wood, iron, stone, fish, pelt, herbs, ammo, or food"},
            "context": {"type": "STRING", "description": "Optional situational details, such as being chased, being in cover, low on health, or under pressure"},
        },
        "required": ["game", "action"],
    },
}


def _normalize_game(value: str) -> str:
    if not value:
        return "general"
    value = value.strip().lower()
    if "red dead" in value or "rdr2" in value or "red dead redemption" in value:
        return "rdr2"
    if "minecraft" in value:
        return "minecraft"
    if "stormworks" in value:
        return "stormworks"
    return value


def _clean_action(value: str) -> str:
    if not value:
        return "plan"
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")


def _normalize_action(value: str) -> str:
    v = _clean_action(value)
    aliases = {
        "build": "build_vehicle",
        "build_vehicle": "build_vehicle",
        "place_block": "place_block",
        "place_blocks": "place_block",
        "block": "place_block",
        "farm": "farm_resources",
        "farm_resources": "farm_resources",
        "resource": "farm_resources",
        "gather": "farm_resources",
        "mine": "farm_resources",
        "mining": "farm_resources",
        "craft": "farm_resources",
        "loot": "farm_resources",
        "collect": "farm_resources",
        "combat": "combat",
        "fight": "combat",
        "hide": "hide_and_cover",
        "cover": "hide_and_cover",
        "take_cover": "hide_and_cover",
        "stealth": "hide_and_cover",
        "sneak": "hide_and_cover",
        "ride": "ride_horse",
        "ride_horse": "ride_horse",
        "horse": "ride_horse",
        "mission": "mission",
        "missions": "mission",
        "level": "level_up",
        "level_up": "level_up",
        "xp": "level_up",
        "escape": "evade_sheriffs",
        "evade": "evade_sheriffs",
        "sheriff": "evade_sheriffs",
        "lawman": "evade_sheriffs",
        "witness": "evade_sheriffs",
        "hunt": "farm_resources",
        "fish": "farm_resources",
        "skin": "farm_resources",
        "survive": "farm_resources",
        "heal": "farm_resources",
        "explore": "farm_resources",
    }
    return aliases.get(v, v)


def _minecraft_build_vehicle(target: str | None) -> str:
    vehicle = target or "vehicle"
    return (
        f"Build the {vehicle} by placing a structural frame first with stone or iron blocks, "
        "then lock in the chassis, add a stable axle or wheel base, and top it with a proper "
        "engine block and steering. Keep the block pattern wide and level, use support pillars on "
        "the lower corners, and finish by placing any seats, controls, and anchor blocks before testing "
        "the drive system."
    )


def _minecraft_place_block(block: str | None) -> str:
    material = block or "stone"
    return (
        f"Place {material} blocks in a stable, connected pattern. Start with a flat base, keep the center "
        "aligned, and reinforce the edges with support blocks before adding decorative or functional pieces. "
        "Only place the next block when the previous layer is solid and the structure is level."
    )


def _minecraft_farm_loop(resource: str | None, target: str | None) -> str:
    resource_name = resource or "materials"
    target_name = target or "next build"
    return (
        f"Farm {resource_name} in a tight loop: harvest, refine, and store the output in a dedicated chest line. "
        f"Keep the route short and repeatable so the next {target_name} is built without wasted time. "
        "Prioritize the materials that unlock the next step, then pause the loop only when the storage is full or the build is ready."
    )


def _rdr2_resource_loop(resource: str | None, target: str | None) -> str:
    resource_name = resource or "resources"
    target_name = target or "objective"
    return (
        f"Start the {target_name} loop by checking the nearest safe area, then gather {resource_name} by using the "
        "best nearby source: skin animals only after the kill, fish where the water is calm and the bait matches the "
        "zone, collect herbs or salvage from the environment, and keep the route efficient. Return to camp, process the "
        "haul, upgrade gear, and then move back out to repeat the loop."
    )


def _rdr2_mission_plan(target: str | None) -> str:
    objective = target or "main objective"
    return (
        f"Complete the {objective} by clearing the route, taking the safest path, keeping a horse nearby, and chaining "
        "only the actions that advance the mission. If the quest involves NPCs, avoid ambushes, use cover, and keep "
        "ammo and horse stamina in reserve. Finish the task cleanly, collect the payout, and then leave the area before "
        "lawmen or hostile threats regroup."
    )


def _rdr2_combat_plan(context: str | None) -> str:
    situation = context or "hostile engagement"
    return (
        f"In {situation}, move to cover immediately, fire only at clear targets, and use the environment "
        "to break the line of sight. Keep the player mobile, switch weapons when needed, and reload before the next "
        "exchange. If enemies are close, use short bursts, stay behind cover, and only expose the body when a shot is "
        "already lined up."
    )


def _rdr2_evasion_plan(context: str | None) -> str:
    situation = context or "being chased by sheriffs"
    return (
        f"When {situation}, do not surrender. Break line of sight, run toward cover, and move behind terrain, trees, "
        "or building corners so the sheriffs must re-aim. Use the horse to create distance, keep the player moving, and "
        "return fire only when the pursuers are committed to a shot. If they are already firing or chasing, shoot back from "
        "cover and keep the horse under control while escaping the law."
    )


def _rdr2_horse_plan() -> str:
    return (
        "Mount the horse, steady the reins, keep the saddle balanced, and ride with a smooth pace instead of a full sprint "
        "unless a chase requires it. Use the horse for distance and mobility, then dismount only when cover, a clear shot, "
        "or a resource node is more important than travel speed."
    )


def _level_up_plan() -> str:
    return (
        "Level up the user by combining profitable loops with safe progression: complete missions for major XP, do repeatable "
        "resource runs for steady gains, finish combat encounters without unnecessary risk, and spend time improving key stats "
        "that match the current goal. Keep the build balanced and avoid risky fights while the progression path is still weak."
    )


def _stormworks_plan(action: str, target: str | None, resource: str | None, context: str | None) -> str:
    target_name = target or "machine"
    resource_name = resource or "parts"
    scenario = context or "general operation"
    if action in {"build_anything", "build", "anything"}:
        return (
            f"For Stormworks, build the {target_name} from the structural core outward: chassis, power routing, cooling, control stack, support bays, and access panels. Keep fuel, electrical, and sensitive modules isolated, leave maintenance room, and protect critical systems so a single fault does not disable the whole build."
        )
    if action in {"submarine", "hovercraft", "armored_vehicle", "aircraft", "industrial_base"}:
        return (
            f"For a Stormworks {action} build, start with the structural shell, then place the primary propulsion or power source, then isolate critical systems and add access panels. Keep weight, trim, and thermal balance controlled, and reserve safe maintenance spaces so the machine can be repaired and upgraded without destabilizing the whole design."
        )
    if action in {"build_vehicle", "vehicle", "advanced_vehicle"}:
        return (
            f"Build the {target_name} around a compact, balanced frame for {scenario}. Keep the weight centered, place the power system near the center of mass, and leave clean access for fuel, batteries, wiring, and emergency repairs. Use a wide base, protect the drivetrain, and test the trim before you push the craft into rough conditions."
        )
    if action in {"engine_bay", "engine_room", "engine", "jet_engine", "fuel_compartment", "hull", "port", "room", "compartment", "bay", "microcontroller", "electrical_system"}:
        return (
            f"Design the {target_name} as a protected, modular section for {scenario}: keep the main system central, isolate fuel and electrical paths, reserve maintenance space, and build in redundancy so failures are contained and easy to access during repair."
        )
    if action in {"repair_vehicle", "repair", "fix", "engine"}:
        return (
            f"Repair the {target_name} by checking power flow, fuel delivery, and the drivetrain before changing anything else. In {scenario}, isolate the damage, fix the root cause, and test the machine in short cycles so the next failure is not hidden by the first one."
        )
    if action in {"manage_power", "power", "generator"}:
        return (
            f"Manage the power on the {target_name} for {scenario}: keep the output stable, route it cleanly to the essential systems, and protect the load with backup batteries or reserves if the system is under stress. Use short cable runs and clear junctions so a single fault cannot disable the vehicle."
        )
    if action in {"gather_resources", "farm_resources", "resource", "collect", "craft"}:
        return (
            f"Gather {resource_name} in a repeatable loop for {target_name}. Prioritize the parts that unlock the next vehicle or repair step, keep the route short, and return to storage before the run becomes inefficient."
        )
    if action in {"watch_tutorials", "tutorial", "reference", "web_help", "research"}:
        return (
            f"Use Steam Workshop, YouTube, and a general web search to reference {target_name or 'the build'} before changing the design. Validate the main concept against a few proven tutorials, then adapt the layout to your exact loadout, power constraints, and mission needs."
        )
    if action == "mission":
        return (
            f"Complete the {target_name} objective by checking the route, fuel level, and safety margins before the run. Keep a fallback path and enough stored power to handle a damaged or isolated machine without losing the whole craft."
        )
    if action in {"survive", "survival"}:
        return (
            f"When {scenario}, keep the vehicle stable and the crew safe: reduce speed, isolate the failing system, protect the power route, and only push forward when the craft can still handle the current load and terrain."
        )
    return (
        f"For Stormworks, prioritize a stable chassis, clean power routing, and a simple maintenance loop. Keep the {target_name} safe, easy to repair, and efficient enough to complete the current {scenario} objective without a total system failure."
    )


def _general_game_plan(game: str, action: str, target: str | None, resource: str | None, context: str | None) -> str:
    objective = target or "the current objective"
    resource_name = resource or "needed materials"
    details = context or "the player should stay safe and efficient"
    return (
        f"For {game or 'this game'}, use a safe objective loop: secure the route to {objective}, gather {resource_name}, "
        f"and stay ready for the next action. Keep the player mobile, maintain cover or structural support when needed, and "
        f"only escalate when {details}. Return to the plan after each objective and confirm the next step before committing."
    )


def run(parameters: dict, player=None, session_memory=None) -> str:
    """Return a compact, action-oriented game plan.

    The plugin intentionally prefers explicit, game-aware tactical guidance instead
    of vague generic language. This makes it useful both in conversation and as a
    planning layer for a higher-level automation system.
    """
    try:
        game = _normalize_game(str(parameters.get("game", "") or ""))
        action = _normalize_action(str(parameters.get("action", "") or ""))
        target = parameters.get("target")
        resource = parameters.get("resource")
        context = parameters.get("context")

        if player is not None:
            try:
                player.write_log(f"JARVIS: game_player_ai -> {game}/{action}")
            except Exception:
                pass

        if game == "minecraft":
            if action == "place_block":
                return _minecraft_place_block(str(resource or target or "stone"))
            if action == "build_vehicle":
                return _minecraft_build_vehicle(str(target or "vehicle"))
            if action == "farm_resources":
                return _minecraft_farm_loop(str(resource), str(target))
            if action == "combat":
                return "Use ranged attacks from cover, keep the player moving, and only engage when the target is in sight and the exit path is clear."
            if action == "hide_and_cover":
                return "Find a wall, tree, or structure with a clean angle, keep the target in the open, and step out only to shoot when you can reload safely."
            if action == "level_up":
                return _level_up_plan()
            return _general_game_plan(game, action, target, resource, context)

        if game == "rdr2":
            if action == "place_block":
                return (
                    "In this game loop, the equivalent is to place or build a stable camp or camp asset: choose a clear, defensible position, "
                    "set the base, then reinforce it with practical items before using it for longer sessions."
                )
            if action == "build_vehicle":
                return (
                    "Use the horse and camp infrastructure as the vehicle layer: secure a mount, keep the gear organized, and use the horse as the primary transport while moving resources and equipment between objectives."
                )
            if action == "farm_resources":
                return _rdr2_resource_loop(resource, target)
            if action == "mission":
                return _rdr2_mission_plan(target)
            if action == "combat":
                return _rdr2_combat_plan(context)
            if action == "hide_and_cover":
                return "Take cover behind solid objects, break the enemy angle, and only fire when the line of sight is controlled. Keep the player low, reload in cover, and move before the enemy can flank."
            if action == "ride_horse":
                return _rdr2_horse_plan()
            if action == "evade_sheriffs":
                return _rdr2_evasion_plan(context)
            if action == "level_up":
                return _level_up_plan()
            return _general_game_plan(game, action, target, resource, context)

        if game == "stormworks":
            return _stormworks_plan(action, target, resource, context)

        if action == "place_block":
            return _minecraft_place_block(str(resource or target or "stone"))
        if action == "build_vehicle":
            return _minecraft_build_vehicle(str(target or "vehicle"))
        if action == "farm_resources":
            return _rdr2_resource_loop(resource, target)
        if action == "combat":
            return _rdr2_combat_plan(context)
        if action == "hide_and_cover":
            return "Move to cover before firing, keep the target in a narrow angle, and only step out when the shot and the escape route are both safe."
        if action == "ride_horse":
            return _rdr2_horse_plan()
        if action == "evade_sheriffs":
            return _rdr2_evasion_plan(context)
        if action == "mission":
            return _rdr2_mission_plan(target)
        if action == "level_up":
            return _level_up_plan()

        return _general_game_plan(game, action, target, resource, context)
    except Exception as exc:
        return f"Sir, the game_player_ai plugin failed: {exc}"

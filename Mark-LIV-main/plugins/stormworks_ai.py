"""Stormworks-focused game-planning plugin.

This plugin gives the agent a practical design and survival loop for Stormworks:
vehicle construction, engine/power planning, repair troubleshooting, safe mission
loops, and complete internal layouts such as engine bays, engine rooms, hulls,
compartments, ports, microcontrollers, electrical systems, fuel compartments,
and bays for everything. It does not try to control the game directly; it
returns a clear tactical/development plan the higher-level automation layer can
follow.
"""

import re
import webbrowser
from urllib.parse import quote_plus

PLUGIN = {
    "name": "stormworks_ai",
    "description": (
        "Use this for Stormworks vehicle design, power systems, engines, jet engines, "
        "fuel compartments, hulls, ports, engine bays, engine rooms, submarines, hovercraft, "
        "armored vehicles, aircraft, industrial bases, advanced vehicles, microcontrollers, "
        "electrical systems, compartments, rooms, bays, repair loops, resource gathering, "
        "marine survival, and mission planning. Good for balancing thrust, fuel, buoyancy, "
        "stability, redundancy, and emergency repairs; it can also open Steam, YouTube, "
        "and web tutorials when a build needs reference material."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Task such as build_anything, build_vehicle, design_boat, design_car, design_jet, submarine, hovercraft, armored_vehicle, aircraft, industrial_base, engine_bay, engine_room, jet_engine, fuel_compartment, hull, port, advanced_vehicle, microcontroller, electrical_system, room, compartment, bay, repair_vehicle, manage_power, gather_resources, mission, survive, level_up, watch_tutorials, tutorial_reference, web_help"
            },
            "target": {"type": "STRING", "description": "Vehicle, machine, room, engine bay, compartment, or objective to build or repair"},
            "resource": {"type": "STRING", "description": "Resource or component such as metal, fuel, batteries, wiring, computers, parts, or cargo"},
            "context": {"type": "STRING", "description": "Optional scenario such as broken engine, low fuel, rough seas, overloaded craft, tight cabin, or power loss"},
        },
        "required": ["action"],
    },
}


def _clean_action(value: str) -> str:
    if not value:
        return "plan"
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")


def _normalize_action(value: str) -> str:
    v = _clean_action(value)
    aliases = {
        "build": "build_anything",
        "build_anything": "build_anything",
        "anything": "build_anything",
        "build_vehicle": "build_vehicle",
        "vehicle": "build_vehicle",
        "design": "build_vehicle",
        "design_vehicle": "build_vehicle",
        "boat": "design_boat",
        "design_boat": "design_boat",
        "car": "design_car",
        "design_car": "design_car",
        "plane": "design_jet",
        "jet": "design_jet",
        "jet_engine": "jet_engine",
        "design_jet": "design_jet",
        "helicopter": "design_jet",
        "submarine": "submarine",
        "submarines": "submarine",
        "hovercraft": "hovercraft",
        "hovercrafts": "hovercraft",
        "armored_vehicle": "armored_vehicle",
        "armoured_vehicle": "armored_vehicle",
        "armored": "armored_vehicle",
        "armour": "armored_vehicle",
        "aircraft": "aircraft",
        "airplane": "aircraft",
        "plane_vehicle": "aircraft",
        "industrial_base": "industrial_base",
        "industrial_build": "industrial_base",
        "base_layout": "industrial_base",
        "factory": "industrial_base",
        "engine_bay": "engine_bay",
        "enginebay": "engine_bay",
        "engine_room": "engine_room",
        "engineroom": "engine_room",
        "engine_room_bay": "engine_room",
        "fuel_compartment": "fuel_compartment",
        "fuel_room": "fuel_compartment",
        "fuel_tank": "fuel_compartment",
        "hull": "hull",
        "hull_design": "hull",
        "port": "port",
        "ports": "port",
        "advanced_vehicle": "advanced_vehicle",
        "advanced_vehicles": "advanced_vehicle",
        "microcontroller": "microcontroller",
        "microcontrollers": "microcontroller",
        "controller": "microcontroller",
        "electrical": "electrical_system",
        "electrical_system": "electrical_system",
        "electrical_systems": "electrical_system",
        "room": "room",
        "rooms": "room",
        "compartment": "compartment",
        "compartments": "compartment",
        "bay": "bay",
        "bays": "bay",
        "cargo_bay": "bay",
        "cockpit": "room",
        "repair": "repair_vehicle",
        "repair_vehicle": "repair_vehicle",
        "fix": "repair_vehicle",
        "engine": "repair_vehicle",
        "power": "manage_power",
        "power_system": "manage_power",
        "manage_power": "manage_power",
        "generator": "manage_power",
        "fuel": "manage_power",
        "resource": "gather_resources",
        "gather": "gather_resources",
        "gather_resources": "gather_resources",
        "collect": "gather_resources",
        "mission": "mission",
        "missions": "mission",
        "survive": "survive",
        "survival": "survive",
        "level": "level_up",
        "level_up": "level_up",
        "xp": "level_up",
        "base": "build_base",
        "build_base": "build_base",
        "craft": "gather_resources",
        "tutorial": "watch_tutorials",
        "tutorials": "watch_tutorials",
        "watch_tutorials": "watch_tutorials",
        "reference": "watch_tutorials",
        "references": "watch_tutorials",
        "web_help": "watch_tutorials",
        "help_build": "watch_tutorials",
        "steam": "watch_tutorials",
        "youtube": "watch_tutorials",
        "search": "watch_tutorials",
        "research": "watch_tutorials",
    }
    return aliases.get(v, v)


def _build_anything_plan(target: str | None, context: str | None) -> str:
    system = target or "machine"
    scenario = context or "general operation"
    return (
        f"Design the {system} for {scenario} by building the central structure first, then layering the critical systems outward: main chassis, power path, cooling, safety, controls, and access panels. Keep the mass centered, isolate fuel and electrical lines from each other, leave room for maintenance, and add redundant protection so a single fault does not disable the whole machine."
    )


def _submarine_plan(target: str | None, context: str | None) -> str:
    craft = target or "submarine"
    scenario = context or "deep water"
    return (
        f"Build the {craft} for {scenario} with a compact, pressure-resistant body and a stable ballast system. Keep the weight balanced, place the main drive and battery banks low and central, and isolate the crew and electronics from fuel, heat, and pressure-sensitive systems. Add redundant power and ballast controls and leave service access to the core systems without compromising the pressure shell."
    )


def _hovercraft_plan(target: str | None, context: str | None) -> str:
    craft = target or "hovercraft"
    scenario = context or "rough shallow water"
    return (
        f"Design the {craft} for {scenario} with a wide, low center of gravity and a smooth cushion path. Keep the main thrust and lift systems centered, protect the fuel and electrical runs from splash and impact, and keep the crew area separated from the engine and lift fan space. Use a stable skirt and simple control routing so the craft stays level under turning, acceleration, and rough water."
    )


def _armored_vehicle_plan(target: str | None, context: str | None) -> str:
    vehicle = target or "armored vehicle"
    scenario = context or "hostile patrol or rough terrain"
    return (
        f"Build the {vehicle} for {scenario} with a rigid frame, a protected power path, and a strong but accessible cabin layout. Center the engine and fuel tanks, shield the electrical system, and keep the main weapon or tool systems mounted with stable support so they do not twist the chassis under recoil or rough terrain. Leave service access to batteries, radiant components, and armor joints without exposing the crew to every hit."
    )


def _aircraft_plan(target: str | None, context: str | None) -> str:
    craft = target or "aircraft"
    scenario = context or "fast transit or surveillance"
    return (
        f"Design the {craft} for {scenario} with a balanced wing or support layout, a clean center of mass, and protected propulsion routing. Keep the fuel, battery, and electrical systems away from the cockpit and control surfaces, and use short confidence-building wiring paths for the primary flight logic. Add redundancy to key control systems and keep maintenance access open without compromising the aerodynamic form."
    )


def _industrial_base_plan(target: str | None, context: str | None) -> str:
    base = target or "industrial base"
    scenario = context or "continuous production"
    return (
        f"Build the {base} for {scenario} with a clear production flow, protected power routing, and a simple logistics loop. Put storage near the workline, keep fuel and machine bays insulated, and reserve a clean maintenance path around major machines. Scale the layout so the production chain stays efficient without creating a single bottleneck or a single point of failure."
    )


def _reference_help_plan(target: str | None, context: str | None) -> str:
    topic = target or "Stormworks build"
    scenario = context or "general reference"
    queries = [
        f"Stormworks {topic} tutorial",
        f"Stormworks {topic} build guide",
        f"Stormworks {topic} Steam workshop",
    ]
    try:
        for query in queries:
            url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            webbrowser.open(url)
        webbrowser.open(f"https://store.steampowered.com/search/?term={quote_plus('Stormworks ' + (target or 'build'))}")
        webbrowser.open(f"https://duckduckgo.com/?q={quote_plus('Stormworks ' + (target or 'build') + ' tutorial')}")
    except Exception:
        pass
    return (
        f"Use reference tutorials for {topic} in {scenario}: open the best YouTube build videos, check the Steam Workshop and Steam search results, and compare a few tutorials before committing. Favor the design that matches your exact loadout and scale, then adapt it to your craft instead of copying it blindly."
    )


def _vehicle_build_plan(target: str | None, context: str | None) -> str:
    vehicle = target or "vehicle"
    scenario = context or "general use"
    return (
        f"Build the {vehicle} around a simple, balanced chassis for {scenario}. Keep the weight centered, place the main engine or propulsion system near the center of mass, add a stable support frame, and route controls so the operator can access them without blocking the cabin. Use a wide base, keep the drivetrain aligned, and leave room for fuel, batteries, and emergency repair access."
    )


def _boat_plan(target: str | None, context: str | None) -> str:
    boat = target or "boat"
    scenario = context or "open water"
    return (
        f"Design the {boat} for {scenario} by keeping the hull symmetrical, placing the engine low and centered, and making sure the buoyancy and trim are stable under load. Add enough floatation to keep the craft level, use a compact fuel path, and keep the steering and controls protected from spray. Test the trim first, then tune thrust and balance before using it in rough water."
    )


def _car_plan(target: str | None, context: str | None) -> str:
    car = target or "car"
    scenario = context or "rough terrain"
    return (
        f"Build the {car} for {scenario} with a low, rigid frame, evenly placed suspension, and enough traction to resist wheel spin under load. Keep the engine and fuel system protected, center the mass, and use a simple braking and steering layout so the vehicle remains controllable in a tight turn or a rough patch."
    )


def _jet_plan(target: str | None, context: str | None) -> str:
    craft = target or "jet craft"
    scenario = context or "high-speed flight"
    return (
        f"Design the {craft} for {scenario} with a clean thrust path, balanced center of mass, and minimal drag. Place the engine or jet component forward and centered, use a compact intake and exhaust flow, and keep the fuel and control links protected so the craft remains stable during acceleration, climb, and turns."
    )


def _engine_bay_plan(target: str | None, context: str | None) -> str:
    bay = target or "engine bay"
    scenario = context or "general performance"
    return (
        f"Build the {bay} for {scenario} as a protected, ventilated compartment with a rigid frame, strong mounts, and easy access for service. Keep the engine centered, route fuel and cooling lines neatly, leave clearance around the exhaust and moving parts, and add firewall or barrier protection so a failure cannot spread to the crew or fuel stores."
    )


def _engine_room_plan(target: str | None, context: str | None) -> str:
    room = target or "engine room"
    scenario = context or "multi-system operation"
    return (
        f"Layout the {room} for {scenario} with a central equipment spine, protected access routes, and clear maintenance lanes. Keep the primary engine, generator, and high-heat components near the center, separate hazardous fluids from crew space, and leave enough walkway and valves for safe repair, cooling checks, and modular swaps."
    )


def _jet_engine_plan(target: str | None, context: str | None) -> str:
    engine = target or "jet engine"
    scenario = context or "high-thrust operation"
    return (
        f"Design the {engine} for {scenario} with a straight, efficient intake path, a balanced exhaust route, and strong mount points around the turbine or jet core. Protect the fuel line, use short clean wiring, and keep the controls, sensors, and cooling loops positioned so the engine remains stable during rapid throttle changes."
    )


def _fuel_compartment_plan(target: str | None, context: str | None) -> str:
    tank = target or "fuel compartment"
    scenario = context or "extended operation"
    return (
        f"Build the {tank} for {scenario} with a sealed, redundant storage layout and a protected fuel path to the engine. Keep the main tank low and well-supported, isolate it from the crew and electrical systems, and add a second reserve line or backup tank so the fuel system can survive a puncture or a bad connection."
    )


def _hull_plan(target: str | None, context: str | None) -> str:
    hull = target or "hull"
    scenario = context or "rough water"
    return (
        f"Design the {hull} for {scenario} with a strong central spine, balanced buoyancy, and even weight distribution across the body. Keep ballast, engines, and compartments spaced evenly, protect the lower hull from impacts, and leave room for access panels, fuel storage, and suspension or mount points without compromising structural integrity."
    )


def _port_plan(target: str | None, context: str | None) -> str:
    port = target or "port"
    scenario = context or "loading and docking"
    return (
        f"Build the {port} for {scenario} with stable dock supports, clear access lanes, and protected cargo routes. Keep the power and control lines separate from loading areas, add weather protection where needed, and maintain a simple workflow so goods, crew, and equipment can move without crowding or damaging the hull or structure."
    )


def _advanced_vehicle_plan(target: str | None, context: str | None) -> str:
    vehicle = target or "advanced vehicle"
    scenario = context or "high-load operation"
    return (
        f"Build the {vehicle} for {scenario} with modular subsystems, redundant power paths, and a clean control stack. Keep the engine, fuel, electrical, and safety loops separate but connected through smart routing, use protected compartments for critical hardware, and leave service access for sensors, batteries, and control modules without compromising the vehicle layout."
    )


def _microcontroller_plan(target: str | None, context: str | None) -> str:
    controller = target or "microcontroller system"
    scenario = context or "automation and control"
    return (
        f"Design the {controller} for {scenario} with an organized control layout, clean signal routing, and dedicated protection for logic boards and sensor inputs. Keep the logic modules near the systems they control, isolate them from heat and vibration, and maintain a simple, reliable data path so the automation layer stays understandable and resistant to single-point failure."
    )


def _electrical_system_plan(target: str | None, context: str | None) -> str:
    system = target or "electrical system"
    scenario = context or "continuous operation"
    return (
        f"Build the {system} for {scenario} with short cable runs, protected junctions, and a clear power hierarchy. Keep the main feed centralized, separate critical and non-critical loads, add redundant backup power where needed, and label or isolate circuits so a single fault cannot take out the whole vehicle, room, or bay."
    )


def _room_plan(target: str | None, context: str | None) -> str:
    room = target or "room"
    scenario = context or "crew or machine operation"
    return (
        f"Lay out the {room} for {scenario} as a protected, access-friendly space. Put the highest-risk systems in the most stable area, reserve clear walkways, and cluster controls, storage, and maintenance access so the room stays efficient without cluttering the main structure."
    )


def _compartment_plan(target: str | None, context: str | None) -> str:
    compartment = target or "compartment"
    scenario = context or "sealed operation"
    return (
        f"Build the {compartment} for {scenario} with a strong shell, secure mounts, and isolation from the rest of the machine. Separate hazardous or heat-heavy elements from crew, electronics, and fuel, add clear service access, and leave breathing room around the main systems so the compartment remains inspectable and repairable."
    )


def _bay_plan(target: str | None, context: str | None) -> str:
    bay = target or "bay"
    scenario = context or "assembly and storage"
    return (
        f"Design the {bay} for {scenario} as a modular, accessible section with a clear front-to-back flow. Place the main component in the center, keep access paths clear, and reserve quick-reach zones for tools, power, and maintenance. Build the bay to allow rapid swap-outs without disturbing adjacent systems or rooms."
    )


def _repair_plan(target: str | None, context: str | None) -> str:
    system = target or "vehicle"
    issue = context or "mechanical failure"
    return (
        f"Repair the {system} by triaging {issue} in order: check power flow, confirm fuel or battery feed, inspect the drivetrain, then verify the control systems and attachment integrity. After each fix, run a short test cycle so the failure does not hide behind a second issue. Keep a spare tool kit, isolate damaged modules, and avoid repeated patchwork until the underlying fault is fixed."
    )


def _power_plan(target: str | None, context: str | None) -> str:
    system = target or "power system"
    issue = context or "power efficiency and redundancy"
    return (
        f"Manage the {system} for {issue}: keep the main generator or engine producing stable output, route power through efficient lines, and connect backup batteries or reserves before the load becomes critical. Balance the drivetrain and power draw with the current demand, then protect the system with short, clean cable runs and emergency cutoffs so a single fault does not take the whole vehicle down."
    )


def _resource_plan(resource: str | None, target: str | None) -> str:
    material = resource or "materials"
    objective = target or "current build"
    return (
        f"Gather {material} in a repeatable loop for {objective}: collect the required components, keep the route efficient, and bring them back to a central workbench or storage area. Prioritize parts that unlock the next build step, then stop the loop only when the stock is enough for the next repair or vehicle upgrade."
    )


def _mission_plan(target: str | None, context: str | None) -> str:
    objective = target or "objective"
    scenario = context or "on land or water"
    return (
        f"Complete the {objective} with a measured run in {scenario}: preload the vehicle with the required fuel and spare components, check the route and hazards, and keep a safe fallback path if the system fails. Prefer a simple mission loop that advances the objective without exposing the craft to avoidable damage or total loss."
    )


def _survival_plan(context: str | None) -> str:
    scenario = context or "a damaged or isolated craft"
    return (
        f"When {scenario}, keep the vehicle stable and the crew safe: reduce speed, isolate the failing system, keep your route short, and prioritize repairs or escape options that preserve mobility. Maintain power reserves, stabilize the craft, and only push forward when the vessel can safely handle the current load and conditions."
    )


def _level_up_plan() -> str:
    return (
        "Level up the build by improving the core loop: keep the main vehicle stable, learn efficient power distribution, practice quick repair triage, and accumulate repeatable mission success. Focus on the systems that unlock safer transportation and lower the chance of total failure during longer runs."
    )


def run(parameters: dict, player=None, session_memory=None) -> str:
    """Return a compact Stormworks tactical plan."""
    try:
        action = _normalize_action(str(parameters.get("action", "") or ""))
        target = parameters.get("target")
        resource = parameters.get("resource")
        context = parameters.get("context")

        if player is not None:
            try:
                player.write_log(f"JARVIS: stormworks_ai -> {action}")
            except Exception:
                pass

        if action == "build_anything":
            return _build_anything_plan(str(target), str(context))
        if action == "submarine":
            return _submarine_plan(str(target), str(context))
        if action == "hovercraft":
            return _hovercraft_plan(str(target), str(context))
        if action == "armored_vehicle":
            return _armored_vehicle_plan(str(target), str(context))
        if action == "aircraft":
            return _aircraft_plan(str(target), str(context))
        if action == "industrial_base":
            return _industrial_base_plan(str(target), str(context))
        if action == "build_vehicle":
            return _vehicle_build_plan(str(target), str(context))
        if action == "design_boat":
            return _boat_plan(str(target), str(context))
        if action == "design_car":
            return _car_plan(str(target), str(context))
        if action == "design_jet":
            return _jet_plan(str(target), str(context))
        if action == "engine_bay":
            return _engine_bay_plan(str(target), str(context))
        if action == "engine_room":
            return _engine_room_plan(str(target), str(context))
        if action == "jet_engine":
            return _jet_engine_plan(str(target), str(context))
        if action == "fuel_compartment":
            return _fuel_compartment_plan(str(target), str(context))
        if action == "hull":
            return _hull_plan(str(target), str(context))
        if action == "port":
            return _port_plan(str(target), str(context))
        if action == "advanced_vehicle":
            return _advanced_vehicle_plan(str(target), str(context))
        if action == "microcontroller":
            return _microcontroller_plan(str(target), str(context))
        if action == "electrical_system":
            return _electrical_system_plan(str(target), str(context))
        if action == "room":
            return _room_plan(str(target), str(context))
        if action == "compartment":
            return _compartment_plan(str(target), str(context))
        if action == "bay":
            return _bay_plan(str(target), str(context))
        if action == "repair_vehicle":
            return _repair_plan(str(target), str(context))
        if action == "manage_power":
            return _power_plan(str(target), str(context))
        if action == "gather_resources":
            return _resource_plan(str(resource), str(target))
        if action == "mission":
            return _mission_plan(str(target), str(context))
        if action == "survive":
            return _survival_plan(str(context))
        if action == "build_base":
            return "Build the base with a clear anchor point, stable support structure, protected storage, and a simple route for fuel and material access. Keep the layout compact and redundant so a single failure does not leave the base crippled."
        if action == "watch_tutorials":
            return _reference_help_plan(str(target), str(context))
        if action == "level_up":
            return _level_up_plan()

        return (
            "Use a disciplined Stormworks loop: build a stable vehicle, confirm the power and fuel path, test the controls, fix the underlying faults, and only then push the craft into longer missions or rough conditions."
        )
    except Exception as exc:
        return f"Sir, the stormworks_ai plugin failed: {exc}"

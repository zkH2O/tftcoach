"""
Helper script to update game_assets.py with current TFT set data.
Run this after executing tft_data_scraper.py to sync your local assets.
"""

import json
import sys
from pathlib import Path


def load_static_data(json_path: str = "data/tft_static_ref.json") -> dict:
    """Load the scraped static data"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found. Run tft_data_scraper.py first.")
        sys.exit(1)


def generate_champions_dict(static_data: dict) -> str:
    """Generate CHAMPIONS dictionary for game_assets.py"""
    champions = static_data.get('champions', {})

    lines = ["CHAMPIONS: dict[str, dict[str, int]] = {"]

    for char_id, data in sorted(champions.items()):
        name = data.get('name', char_id.title())
        cost = data.get('cost', 1)
        traits = data.get('traits', [])

        # Pad traits to 3 (some champions have 1-3 traits)
        trait1 = traits[0] if len(traits) > 0 else ""
        trait2 = traits[1] if len(traits) > 1 else ""
        trait3 = traits[2] if len(traits) > 2 else ""

        lines.append(f'    "{name}": {{"Gold": {cost}, "Board Size": 1, "Trait1": "{trait1}", "Trait2": "{trait2}", "Trait3": "{trait3}"}},')

    lines.append("}")

    return "\n".join(lines)


def generate_items_sets(static_data: dict) -> dict:
    """Generate item sets for game_assets.py"""
    items = static_data.get('items', {})

    # Categorize items based on their recipes
    basic_items = set()
    combined_items = set()

    for item_id, data in items.items():
        name = data.get('name', '').replace(' ', '').replace("'", "")
        if not name:
            continue

        components = data.get('from', [])

        # Basic items have no recipe (from is None or empty)
        if not components or len(components) == 0:
            basic_items.add(name)
        else:
            combined_items.add(name)

    return {
        'basic': basic_items,
        'combined': combined_items
    }


def update_game_assets_file(static_data: dict, output_path: str = "data/game_assets.py"):
    """Update the game_assets.py file with current set data"""

    # Generate champions
    champions_code = generate_champions_dict(static_data)

    # Generate items
    item_sets = generate_items_sets(static_data)

    # Build the new file content
    content = f'''"""
Contains static item & champion data
Auto-generated from CDragon data - Last updated: {static_data.get('timestamp', 'Unknown')}
"""

# Note: Item categorization is simplified. You may need to manually categorize
# support items, ornn items, and non-craftable items based on game knowledge.

BASIC_ITEM: set[str] = {{
    {', '.join(f'"{item}"' for item in sorted(item_sets['basic']))}
}}

COMBINED_ITEMS: set[str] = {{
    {', '.join(f'"{item}"' for item in sorted(item_sets['combined']))}
}}

SUPPORT_ITEM: set[str] = {{
    # TODO: Manually categorize support items from COMBINED_ITEMS
}}

NON_CRAFTABLE_ITEMS: set[str] = {{
    # TODO: Add emblems and other non-craftable items
}}

ORNN_ITEMS: set[str] = {{
    # TODO: Add Ornn-specific items
}}

ITEMS: set[str] = BASIC_ITEM.union(COMBINED_ITEMS).union(SUPPORT_ITEM).union(NON_CRAFTABLE_ITEMS).union(ORNN_ITEMS)

{champions_code}


ROUNDS: set[str] = {{"1-1", "1-2", "1-3", "1-4",
                    "2-1", "2-2", "2-3", "2-4", "2-5", "2-6", "2-7", "2-8",
                    "3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7", "3-8",
                    "4-1", "4-2", "4-3", "4-4", "4-5", "4-6", "4-7", "4-8",
                    "5-1", "5-2", "5-3", "5-4", "5-5", "5-6", "5-7", "5-8",
                    "6-1", "6-2", "6-3", "6-4", "6-5", "6-6", "6-7", "6-8",
                    "7-1", "7-2", "7-3", "7-4", "7-5", "7-6", "7-7", "7-8"}}

SECOND_ROUND: set[str] = {{"1-2"}}

CAROUSEL_ROUND: set[str] = {{"1-1", "2-4", "3-4", "4-4", "5-4", "6-4", "7-4"}}

PVE_ROUND: set[str] = {{"1-3", "1-4", "2-7", "3-7", "4-7", "5-7", "6-7", "7-7"}}

PVP_ROUND: set[str] = {{"2-1", "2-2", "2-3", "2-5", "2-6",
                       "3-1", "3-2", "3-3", "3-5", "3-6",
                       "4-1", "4-2", "4-3", "4-5", "4-6",
                       "5-1", "5-2", "5-3", "5-5", "5-6",
                       "6-1", "6-2", "6-3", "6-5", "6-6",
                       "7-1", "7-2", "7-3", "7-5", "7-6"}}

PICKUP_ROUNDS: set[str] = {{"2-1", "3-1", "4-1", "5-1", "6-1", "7-1"}}

ANVIL_ROUNDS: set[str] = {{"2-1", "2-5", "3-1", "3-5", "4-1", "4-5", "5-1", "5-5", "6-1", "6-5", "7-1", "7-5"}}

AUGMENT_ROUNDS: set[str] = {{"2-1", "3-2", "4-2"}}

ITEM_PLACEMENT_ROUNDS: set[str] = {{"2-2", "3-2", "4-2", "5-2",
                                   "6-2", "7-2", "2-5", "3-5", "4-5", "5-5", "6-5", "7-5"}}

ENCOUNTER_ROUNDS: set[str] = {{"0-0"}}

FINAL_COMP_ROUND = "4-5"

# TODO: Generate FULL_ITEMS mapping from CDragon recipe data
FULL_ITEMS = {{}}


def champion_board_size(champion: str) -> int:
    """Takes a string (champion name) and returns board size of champion"""
    return CHAMPIONS[champion]["Board Size"]


def champion_gold_cost(champion: str) -> int:
    """Takes a string (champion name) and returns gold of champion"""
    return CHAMPIONS[champion]["Gold"]
'''

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated {output_path}")
    print(f"  - {len(static_data.get('champions', {}))} champions")
    print(f"  - {len(item_sets['basic'])} basic items")
    print(f"  - {len(item_sets['combined'])} combined items")
    print("\nNOTE: You may need to manually categorize:")
    print("  - SUPPORT_ITEM")
    print("  - NON_CRAFTABLE_ITEMS (emblems, etc.)")
    print("  - ORNN_ITEMS")
    print("  - FULL_ITEMS (item recipes)")


def main():
    """Main entry point"""
    print("=" * 60)
    print("TFT Game Assets Updater")
    print("=" * 60)
    print()

    # Load scraped data
    print("Loading tft_static_ref.json...")
    static_data = load_static_data()

    # Update game_assets.py
    print("Updating game_assets.py...")
    update_game_assets_file(static_data)

    print("\n" + "=" * 60)
    print("Update complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
Debug script to inspect all TFT sets in CDragon and find the current one
"""

import requests
import json


def inspect_cdragon_sets():
    """Fetch and display all sets from CDragon"""
    print("Fetching CDragon data...")
    url = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"

    response = requests.get(url, timeout=30)
    data = response.json()

    print(f"\n{'='*80}")
    print("ALL TFT SETS IN CDRAGON")
    print(f"{'='*80}\n")

    # Check the 'sets' metadata
    sets_metadata = data.get('sets', {})
    print("SETS METADATA:")
    print(json.dumps(sets_metadata, indent=2))
    print()

    # Check setData
    set_data_list = data.get('setData', [])
    print(f"\nSETDATA: Found {len(set_data_list)} sets\n")

    for idx, set_info in enumerate(set_data_list):
        name = set_info.get('name', 'Unknown')
        mutator = set_info.get('mutator', 'N/A')
        number = set_info.get('number', 'N/A')

        num_champions = len(set_info.get('champions', []))
        num_traits = len(set_info.get('traits', []))
        num_items = len(set_info.get('items', []))

        marker = " ← LAST (currently used)" if idx == len(set_data_list) - 1 else ""

        print(f"[{idx}] {name}")
        print(f"    Number: {number}")
        print(f"    Mutator: {mutator}")
        print(f"    Champions: {num_champions}, Traits: {num_traits}, Items: {num_items}{marker}")
        print()

    print(f"\n{'='*80}")
    print("FINDING SET 16 (Lore and Legends)")
    print(f"{'='*80}\n")

    # Search for Set 16
    for idx, set_info in enumerate(set_data_list):
        number = set_info.get('number')
        name = set_info.get('name', 'Unknown')

        # Check if this is Set 16
        if number == 16 or 'Lore' in name or 'Legends' in name or number == '16':
            print(f"✓ FOUND at index [{idx}]:")
            print(f"  Name: {name}")
            print(f"  Number: {number}")
            print(f"  Mutator: {set_info.get('mutator', 'N/A')}")
            print(f"  Champions: {len(set_info.get('champions', []))}")
            print(f"  Traits: {len(set_info.get('traits', []))}")
            print(f"  Items: {len(set_info.get('items', []))}")
            print()

    print("\nRECOMMENDATION:")
    print("Look for a set with:")
    print("  - number: 16")
    print("  - name containing 'Lore' or 'Legends'")
    print("  - OR use the 'sets' metadata to identify the active set")


if __name__ == "__main__":
    inspect_cdragon_sets()

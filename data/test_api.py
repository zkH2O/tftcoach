"""
Quick API test script to verify Riot API connectivity and responses
"""

import requests
import json


def test_challenger_league(api_key: str, region: str = 'na1'):
    """Test fetching Challenger league"""
    print(f"\n{'='*60}")
    print("Testing Challenger League API")
    print(f"{'='*60}")

    url = f"https://{region}.api.riotgames.com/tft/league/v1/challenger"
    headers = {'X-Riot-Token': api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            print(f"✓ Success! Found {len(entries)} Challenger players")

            if entries:
                # Show first entry structure
                print(f"\nFirst entry structure:")
                print(f"Keys: {list(entries[0].keys())}")
                print(f"Sample entry:")
                print(json.dumps(entries[0], indent=2))
            return data
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_summoner_lookup(api_key: str, summoner_id: str, region: str = 'na1'):
    """Test summoner lookup"""
    print(f"\n{'='*60}")
    print(f"Testing Summoner Lookup: {summoner_id}")
    print(f"{'='*60}")

    url = f"https://{region}.api.riotgames.com/tft/summoner/v1/summoners/{summoner_id}"
    headers = {'X-Riot-Token': api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Summoner data retrieved")
            print(f"Keys: {list(data.keys())}")
            print(f"PUUID: {data.get('puuid', 'NOT FOUND')[:20]}...")
            return data
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_match_ids(api_key: str, puuid: str, routing: str = 'americas'):
    """Test match ID retrieval"""
    print(f"\n{'='*60}")
    print(f"Testing Match IDs for PUUID")
    print(f"{'='*60}")

    url = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
    headers = {'X-Riot-Token': api_key}
    params = {'count': 5}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            match_ids = response.json()
            print(f"✓ Success! Retrieved {len(match_ids)} match IDs")
            print(f"Sample: {match_ids[:3]}")
            return match_ids
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_cdragon():
    """Test CDragon static data"""
    print(f"\n{'='*60}")
    print("Testing CDragon Static Data")
    print(f"{'='*60}")

    url = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"

    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! CDragon data retrieved")
            print(f"Root keys: {list(data.keys())}")

            sets = data.get('setData', [])
            print(f"Number of sets: {len(sets)}")

            # Look for Set 16
            print(f"\n{'='*60}")
            print("Looking for Set 16 (Lore and Legends)...")
            print(f"{'='*60}")

            set_16_found = False
            for idx, set_info in enumerate(sets):
                set_num = set_info.get('number')
                if set_num == 16 or set_num == '16':
                    set_16_found = True
                    print(f"✓ Found Set 16 at index {idx}:")
                    print(f"  Name: {set_info.get('name', 'Unknown')}")
                    print(f"  Champions: {len(set_info.get('champions', []))}")
                    print(f"  Traits: {len(set_info.get('traits', []))}")
                    print(f"  Items: {len(set_info.get('items', []))}")
                    break

            if not set_16_found:
                print("✗ Set 16 NOT FOUND!")
                print("\nAvailable sets (last 5):")
                for idx in range(max(0, len(sets) - 5), len(sets)):
                    set_info = sets[idx]
                    print(f"  [{idx}] {set_info.get('name', 'Unknown')} (number: {set_info.get('number', 'N/A')})")

            if sets:
                current_set = sets[-1]
                print(f"\nLast set in array:")
                print(f"  Name: {current_set.get('name', 'Unknown')}")
                print(f"  Number: {current_set.get('number', 'N/A')}")
                print(f"  Champions: {len(current_set.get('champions', []))}")

            # Check items at root level
            root_items = data.get('items', [])
            print(f"\nItems at root level: {len(root_items)}")

            return data
        else:
            print(f"✗ Failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    print("=" * 60)
    print("TFT API Connectivity Test")
    print("=" * 60)

    # Test CDragon (no API key needed)
    test_cdragon()

    # Get API key
    print("\n" + "=" * 60)
    api_key = input("Enter your RIOT_API_KEY (or press Enter to skip Riot API tests): ").strip()

    if not api_key:
        print("Skipping Riot API tests")
        return

    region = input("Enter region (default: na1): ").strip() or "na1"
    routing = input("Enter routing (default: americas): ").strip() or "americas"

    # Test 1: Challenger League
    challenger_data = test_challenger_league(api_key, region)

    if challenger_data:
        entries = challenger_data.get('entries', [])
        if entries:
            # Test 2: Summoner Lookup
            first_entry = entries[0]
            summoner_id = first_entry.get('summonerId')

            if summoner_id:
                summoner_data = test_summoner_lookup(api_key, summoner_id, region)

                if summoner_data:
                    # Test 3: Match IDs
                    puuid = summoner_data.get('puuid')
                    if puuid:
                        test_match_ids(api_key, puuid, routing)

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

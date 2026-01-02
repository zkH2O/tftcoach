"""
TFT Data Extraction Pipeline
Senior Data Engineering implementation for TFT ML training dataset generation.

This module fetches:
1. Static game data from Community Dragon (CDragon)
2. Match data from Riot Games Official API
3. Merges data into ML-ready format
"""

import requests
import pandas as pd
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for API rate limiting"""
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 120.0


class CDragonClient:
    """Client for fetching static TFT data from Community Dragon"""

    CDRAGON_URL = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"

    def __init__(self):
        self.static_data: Optional[Dict] = None

    def fetch_static_data(self) -> Dict:
        """
        Fetch complete static game data from CDragon.

        Returns:
            Dict containing champions, traits, items, and augments
        """
        logger.info("Fetching static data from CDragon...")

        try:
            response = requests.get(self.CDRAGON_URL, timeout=30)
            response.raise_for_status()
            self.static_data = response.json()
            logger.info("Successfully fetched CDragon static data")
            return self.static_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch CDragon data: {e}")
            raise

    def find_current_set(self, target_set_number: int = 16) -> Optional[Dict]:
        """
        Find the current active TFT set.

        Args:
            target_set_number: The set number to look for (default: 16 for "Lore and Legends")

        Returns:
            The set data dictionary or None
        """
        if not self.static_data:
            raise ValueError("Static data not loaded. Call fetch_static_data() first.")

        sets_data = self.static_data.get('setData', [])

        if not sets_data:
            logger.warning("No set data found in CDragon response")
            return None

        # Find all sets matching the target number
        matching_sets = []
        for idx, set_info in enumerate(sets_data):
            set_num = set_info.get('number')
            if set_num == target_set_number or set_num == str(target_set_number):
                matching_sets.append((idx, set_info))

        if not matching_sets:
            logger.warning(f"Could not find Set {target_set_number}. Using last set in array (may be incorrect)")
            current_set = sets_data[-1]
            logger.info(f"Using set: {current_set.get('name', 'Unknown')} (number: {current_set.get('number', 'N/A')})")
            return current_set

        # If multiple sets found, prefer the base set (without special mode suffix)
        if len(matching_sets) > 1:
            logger.info(f"Found {len(matching_sets)} variants of Set {target_set_number}")

            # Look for the base set (mutator = "TFTSet{number}" without suffix)
            base_mutator = f"TFTSet{target_set_number}"
            for idx, set_info in matching_sets:
                mutator = set_info.get('mutator', '')
                if mutator == base_mutator:
                    logger.info(f"Using base set at index {idx}: {set_info.get('name', 'Unknown')} (mutator: {mutator})")
                    return set_info

            # Fallback to first match if no exact base set found
            logger.warning(f"No exact base set found. Using first match.")

        # Return the first (or only) matching set
        idx, set_info = matching_sets[0]
        mutator = set_info.get('mutator', 'N/A')
        logger.info(f"Using Set {target_set_number} at index {idx}: {set_info.get('name', 'Unknown')} (mutator: {mutator})")
        return set_info

    def extract_champions(self, target_set_number: int = 16) -> Dict[str, Dict]:
        """Extract champion data with stats and traits"""
        if not self.static_data:
            raise ValueError("Static data not loaded. Call fetch_static_data() first.")

        champions = {}
        current_set = self.find_current_set(target_set_number)

        if not current_set:
            logger.error("Could not find current set")
            return champions

        logger.info(f"Extracting champions from: {current_set.get('name', 'Unknown')} (Set {current_set.get('number', 'N/A')})")

        for champion in current_set.get('champions', []):
            char_id = champion.get('characterName', '').lower()
            if not char_id:
                continue

            champions[char_id] = {
                'name': champion.get('name', ''),
                'cost': champion.get('cost', 0),
                'traits': champion.get('traits', []),
                'stats': champion.get('stats', {}),
            }

        logger.info(f"Extracted {len(champions)} champions")
        return champions

    def extract_traits(self, target_set_number: int = 16) -> Dict[str, Dict]:
        """Extract trait data"""
        if not self.static_data:
            raise ValueError("Static data not loaded. Call fetch_static_data() first.")

        traits = {}
        current_set = self.find_current_set(target_set_number)

        if not current_set:
            return traits

        for trait in current_set.get('traits', []):
            trait_id = trait.get('name', '').lower()
            if not trait_id:
                continue

            traits[trait_id] = {
                'display_name': trait.get('display_name', ''),
                'effects': trait.get('effects', []),
            }

        logger.info(f"Extracted {len(traits)} traits")
        return traits

    def extract_items(self, target_set_number: int = 16) -> Dict[str, Dict]:
        """Extract item data"""
        if not self.static_data:
            raise ValueError("Static data not loaded. Call fetch_static_data() first.")

        items = {}

        # Get root-level items dictionary for lookups
        root_items = {}
        root_items_list = self.static_data.get('items', [])
        for root_item in root_items_list:
            if isinstance(root_item, dict):
                item_id = str(root_item.get('id', root_item.get('apiName', '')))
                if item_id:
                    root_items[item_id] = root_item

        # Get set-specific items
        current_set = self.find_current_set(target_set_number)
        if current_set:
            items_data = current_set.get('items', [])
        else:
            items_data = []

        if not items_data:
            logger.warning("No items found in set data. Using root level items...")
            items_data = root_items_list

        # Process items
        for item in items_data:
            # Handle two cases:
            # 1. Item is a string (item ID) - look up full data from root_items
            # 2. Item is a dict (full item object)

            if isinstance(item, str):
                # Item is just an ID string - look up in root items
                item_id = item
                item_obj = root_items.get(item_id)
                if not item_obj:
                    continue

                items[item_id] = {
                    'name': item_obj.get('name', ''),
                    'description': item_obj.get('desc', ''),
                    'from': item_obj.get('from', item_obj.get('composition', [])),
                }

            elif isinstance(item, dict):
                # Item is a full object
                item_id = str(item.get('id', item.get('apiName', '')))
                if not item_id:
                    continue

                items[item_id] = {
                    'name': item.get('name', ''),
                    'description': item.get('desc', ''),
                    'from': item.get('from', item.get('composition', [])),
                }

        logger.info(f"Extracted {len(items)} items")
        return items

    def save_static_data(self, output_path: str = "data/tft_static_ref.json", target_set_number: int = 16):
        """Save processed static data to JSON file"""
        static_ref = {
            'timestamp': datetime.now().isoformat(),
            'set_number': target_set_number,
            'champions': self.extract_champions(target_set_number),
            'traits': self.extract_traits(target_set_number),
            'items': self.extract_items(target_set_number),
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(static_ref, f, indent=2, ensure_ascii=False)

        logger.info(f"Static data saved to {output_path}")
        return static_ref


class RiotAPIClient:
    """Client for Riot Games TFT API with rate limiting"""

    # API Endpoints by region
    REGIONS = {
        'na1': 'https://na1.api.riotgames.com',
        'americas': 'https://americas.api.riotgames.com',
    }

    def __init__(self, api_key: str, region: str = 'na1', routing: str = 'americas'):
        self.api_key = api_key
        self.region_base = self.REGIONS[region]
        self.routing_base = self.REGIONS[routing]
        self.rate_limit_config = RateLimitConfig()
        self.headers = {'X-Riot-Token': self.api_key}

    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = min(
            self.rate_limit_config.base_delay * (2 ** attempt),
            self.rate_limit_config.max_delay
        )
        return delay

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request with exponential backoff for rate limiting.

        Args:
            url: Full API endpoint URL
            params: Optional query parameters

        Returns:
            JSON response or None if all retries failed
        """
        for attempt in range(self.rate_limit_config.max_retries):
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=10)

                # Success
                if response.status_code == 200:
                    return response.json()

                # Rate limited - apply exponential backoff
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 1))
                    delay = max(retry_after, self._exponential_backoff(attempt))
                    logger.warning(f"Rate limited. Waiting {delay}s before retry {attempt + 1}/{self.rate_limit_config.max_retries}")
                    time.sleep(delay)
                    continue

                # Other errors
                logger.error(f"API request failed: {response.status_code}")
                logger.error(f"URL: {url}")
                logger.error(f"Response: {response.text[:500]}")  # First 500 chars

                if response.status_code == 403:
                    logger.error("403 Forbidden - Check your API key validity and permissions")
                elif response.status_code == 404:
                    logger.error("404 Not Found - Endpoint or resource doesn't exist")

                response.raise_for_status()

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception on attempt {attempt + 1}: {e}")
                if attempt < self.rate_limit_config.max_retries - 1:
                    time.sleep(self._exponential_backoff(attempt))
                    continue
                raise

        logger.error(f"Failed after {self.rate_limit_config.max_retries} attempts")
        return None

    def get_challenger_league(self) -> List[Dict]:
        """
        Fetch Challenger league entries.

        Returns:
            List of challenger player entries with summonerId
        """
        url = f"{self.region_base}/tft/league/v1/challenger"
        logger.info("Fetching Challenger league data...")

        data = self._make_request(url)
        if not data:
            return []

        entries = data.get('entries', [])
        logger.info(f"Found {len(entries)} Challenger players")
        return entries

    def get_summoner_by_id(self, summoner_id: str) -> Optional[Dict]:
        """
        Get summoner data including PUUID.

        Args:
            summoner_id: Encrypted summoner ID

        Returns:
            Summoner data including puuid
        """
        url = f"{self.region_base}/tft/summoner/v1/summoners/{summoner_id}"
        return self._make_request(url)

    def get_match_ids_by_puuid(self, puuid: str, count: int = 20) -> List[str]:
        """
        Get match IDs for a player.

        Args:
            puuid: Player UUID
            count: Number of matches to retrieve

        Returns:
            List of match IDs
        """
        url = f"{self.routing_base}/tft/match/v1/matches/by-puuid/{puuid}/ids"
        params = {'count': count}

        match_ids = self._make_request(url, params)
        if match_ids:
            logger.info(f"Retrieved {len(match_ids)} match IDs for PUUID")
            return match_ids
        return []

    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """
        Get detailed match data.

        Args:
            match_id: Match identifier

        Returns:
            Complete match data including all participants
        """
        url = f"{self.routing_base}/tft/match/v1/matches/{match_id}"
        return self._make_request(url)


class TFTDataPipeline:
    """Main pipeline orchestrator for TFT data extraction"""

    def __init__(self, api_key: str, target_set_number: int = 16):
        self.cdragon = CDragonClient()
        self.riot_api = RiotAPIClient(api_key)
        self.static_data: Optional[Dict] = None
        self.match_data: List[Dict] = []
        self.target_set_number = target_set_number

    def extract_static_data(self) -> Dict:
        """Step 1: Extract and save static data"""
        logger.info("=" * 60)
        logger.info(f"STEP 1: Extracting Static Data from CDragon (Set {self.target_set_number})")
        logger.info("=" * 60)

        self.cdragon.fetch_static_data()
        self.static_data = self.cdragon.save_static_data(target_set_number=self.target_set_number)
        return self.static_data

    def extract_match_data(self, num_players: int = 10, matches_per_player: int = 20) -> List[Dict]:
        """Step 2: Extract match data from Riot API"""
        logger.info("=" * 60)
        logger.info("STEP 2: Extracting Match Data from Riot API")
        logger.info("=" * 60)

        # Get Challenger players
        challenger_entries = self.riot_api.get_challenger_league()
        if not challenger_entries:
            logger.error("Failed to fetch Challenger league")
            return []

        # Limit to requested number of players
        challenger_entries = challenger_entries[:num_players]
        logger.info(f"Processing top {len(challenger_entries)} Challenger players")

        all_matches = []
        processed_match_ids = set()

        for idx, entry in enumerate(challenger_entries, 1):
            # Modern API returns puuid directly in the entry
            puuid = entry.get('puuid')
            if not puuid:
                # Fallback: try old API structure with summonerId
                summoner_id = entry.get('summonerId')
                if summoner_id:
                    logger.info(f"[{idx}/{len(challenger_entries)}] Using legacy summonerId lookup")
                    try:
                        summoner_data = self.riot_api.get_summoner_by_id(summoner_id)
                        if summoner_data:
                            puuid = summoner_data.get('puuid')
                    except Exception as e:
                        logger.warning(f"  Failed to lookup summoner: {e}")

                if not puuid:
                    logger.warning(f"[{idx}/{len(challenger_entries)}] Skipping entry - no puuid found. Entry keys: {list(entry.keys())}")
                    continue

            logger.info(f"[{idx}/{len(challenger_entries)}] Processing player (LP: {entry.get('leaguePoints', 'N/A')})")

            # Get match IDs
            try:
                match_ids = self.riot_api.get_match_ids_by_puuid(puuid, matches_per_player)
                logger.info(f"  Retrieved {len(match_ids)} match IDs")
            except Exception as e:
                logger.error(f"  Error fetching match IDs: {e}")
                continue

            # Fetch match details
            for match_id in match_ids:
                if match_id in processed_match_ids:
                    continue

                match_details = self.riot_api.get_match_details(match_id)
                if match_details:
                    all_matches.append(match_details)
                    processed_match_ids.add(match_id)
                    logger.info(f"  Fetched match {match_id} ({len(all_matches)} total matches)")

                # Rate limiting courtesy delay
                time.sleep(0.5)

            # Delay between players
            time.sleep(1)

        logger.info(f"Total matches collected: {len(all_matches)}")
        self.match_data = all_matches
        return all_matches

    def build_training_dataframe(self) -> pd.DataFrame:
        """Step 3: Merge data and create ML training dataset"""
        logger.info("=" * 60)
        logger.info("STEP 3: Building Training DataFrame")
        logger.info("=" * 60)

        if not self.match_data:
            logger.error("No match data available")
            return pd.DataFrame()

        rows = []

        for match in self.match_data:
            info = match.get('info', {})
            game_version = info.get('game_version', '')
            tft_set_number = info.get('tft_set_number', 0)

            participants = info.get('participants', [])

            for participant in participants:
                # Extract relevant features
                row = {
                    'match_id': match.get('metadata', {}).get('match_id', ''),
                    'game_version': game_version,
                    'tft_set': tft_set_number,
                    'placement': participant.get('placement', 0),
                    'level': participant.get('level', 0),
                    'last_round': participant.get('last_round', 0),
                    'gold_left': participant.get('gold_left', 0),
                    'total_damage_to_players': participant.get('total_damage_to_players', 0),

                    # Augments
                    'augments': json.dumps(participant.get('augments', [])),

                    # Traits
                    'traits': json.dumps([
                        {
                            'name': trait.get('name', ''),
                            'tier_current': trait.get('tier_current', 0),
                            'num_units': trait.get('num_units', 0)
                        }
                        for trait in participant.get('traits', [])
                        if trait.get('tier_current', 0) > 0  # Only active traits
                    ]),

                    # Units
                    'units': json.dumps([
                        {
                            'character_id': unit.get('character_id', ''),
                            'tier': unit.get('tier', 0),
                            'items': unit.get('itemNames', []),
                        }
                        for unit in participant.get('units', [])
                    ]),

                    # Companion (for potential features)
                    'companion': participant.get('companion', {}).get('content_ID', ''),
                }

                rows.append(row)

        df = pd.DataFrame(rows)
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)}")

        return df

    def save_training_data(self, df: pd.DataFrame, output_path: str = "data/tft_training_data.csv"):
        """Save the training dataframe to CSV"""
        df.to_csv(output_path, index=False)
        logger.info(f"Training data saved to {output_path}")
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"\nSample data preview:")
        logger.info(df.head())

    def run_full_pipeline(self, num_players: int = 10, matches_per_player: int = 20):
        """Execute complete data extraction pipeline"""
        logger.info("=" * 60)
        logger.info("TFT DATA EXTRACTION PIPELINE - START")
        logger.info("=" * 60)

        start_time = time.time()

        try:
            # Step 1: Static Data
            self.extract_static_data()

            # Step 2: Match Data
            self.extract_match_data(num_players, matches_per_player)

            # Step 3: Build DataFrame
            df = self.build_training_dataframe()

            # Step 4: Save
            self.save_training_data(df)

            elapsed_time = time.time() - start_time
            logger.info("=" * 60)
            logger.info(f"PIPELINE COMPLETED SUCCESSFULLY in {elapsed_time:.2f}s")
            logger.info("=" * 60)

            return df

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise


def main():
    """Main entry point"""
    print("=" * 60)
    print("TFT Data Extraction Pipeline")
    print("Senior Data Engineering Implementation")
    print("=" * 60)
    print()

    # Get API key from user
    api_key = input("Enter your RIOT_API_KEY: ").strip()

    if not api_key:
        print("Error: API key is required")
        return

    print()
    set_number = input("TFT Set number (default 16 for 'Lore and Legends'): ").strip()
    set_number = int(set_number) if set_number else 16

    num_players = input("Number of Challenger players to sample (default 10): ").strip()
    num_players = int(num_players) if num_players else 10

    matches_per_player = input("Matches per player (default 20): ").strip()
    matches_per_player = int(matches_per_player) if matches_per_player else 20

    print()
    print(f"Configuration:")
    print(f"  - TFT Set: {set_number}")
    print(f"  - Players: {num_players}")
    print(f"  - Matches per player: {matches_per_player}")
    print(f"  - Estimated total matches: ~{num_players * matches_per_player}")
    print()

    # Run pipeline
    pipeline = TFTDataPipeline(api_key, target_set_number=set_number)
    pipeline.run_full_pipeline(num_players, matches_per_player)


if __name__ == "__main__":
    main()

# TFT Data Pipeline

This directory contains the data extraction and management pipeline for the TFT Coach project.

## Overview

The pipeline fetches current TFT set data from two sources:
1. **CDragon** - Static game data (champions, items, traits)
2. **Riot Games API** - Live match data from Challenger players

## Files

- `tft_data_scraper.py` - Main data extraction pipeline
- `update_game_assets.py` - Helper to update `game_assets.py` with current set data
- `game_assets.py` - Static game reference data (champions, items, rounds)
- `comps.py` - Team composition configurations

## Quick Start

### 1. Get a Riot API Key

1. Go to https://developer.riotgames.com/
2. Sign in with your Riot account
3. Register your application (or use development key for testing)
4. Copy your API key

### 2. Run the Data Scraper

```bash
python data/tft_data_scraper.py
```

You'll be prompted for:
- Your Riot API key
- Number of Challenger players to sample (default: 10)
- Matches per player (default: 20)

The script will:
- Fetch static data from CDragon → `data/tft_static_ref.json`
- Fetch match data from Riot API
- Generate training dataset → `data/tft_training_data.csv`

### 3. Update Game Assets (Optional)

To sync the current set data into `game_assets.py`:

```bash
python data/update_game_assets.py
```

This updates `game_assets.py` with champions and items from the latest set.

**Note:** You'll need to manually categorize some items (Support, Ornn, Non-Craftable).

## Output Files

After running the pipeline, you'll have:

```
/data
├── tft_static_ref.json       # CDragon static data (champions, traits, items)
├── tft_training_data.csv     # ML training dataset (match results)
├── game_assets.py            # Updated with current set (if you ran update script)
└── comps.py                  # Your team composition (manually edit)
```

## Data Schema

### tft_static_ref.json

```json
{
  "timestamp": "2025-12-28T...",
  "champions": {
    "championName": {
      "name": "Display Name",
      "cost": 3,
      "traits": ["Trait1", "Trait2"],
      "stats": { ... }
    }
  },
  "traits": { ... },
  "items": { ... }
}
```

### tft_training_data.csv

Columns:
- `match_id` - Unique match identifier
- `game_version` - Game patch version
- `tft_set` - Set number
- `placement` - Final placement (1-8) **[TARGET VARIABLE]**
- `level` - Player level
- `gold_left` - Remaining gold
- `augments` - Selected augments (JSON array)
- `traits` - Active traits with tiers (JSON array)
- `units` - Board composition (JSON array with character_id, tier, items)

## Rate Limiting

The scraper implements exponential backoff for Riot API rate limits:
- Base delay: 1 second
- Max delay: 120 seconds
- Max retries: 5

The script includes courtesy delays between requests to avoid hitting rate limits.

## API Rate Limits (Riot Games)

**Development Key:**
- 20 requests per second
- 100 requests per 2 minutes

**Production Key:**
- Higher limits (apply through Riot Developer Portal)

## Troubleshooting

### "Failed to fetch CDragon data"
- Check your internet connection
- CDragon URL may have changed (check https://communitydragon.org/)

### "Rate limited" or HTTP 429
- Normal - the script handles this automatically with exponential backoff
- If persistent, reduce `num_players` or `matches_per_player`

### "No set data found in CDragon response"
- CDragon JSON structure may have changed
- Check the raw JSON at: https://raw.communitydragon.org/latest/cdragon/tft/en_us.json

## Next Steps

After collecting data:
1. Use `tft_training_data.csv` to train your ML model
2. Update `comps.py` with meta compositions from high-placement matches
3. Periodically re-run the scraper to stay current with the meta

## Example: Quick Data Collection

```python
from data.tft_data_scraper import TFTDataPipeline

# Initialize with your API key
pipeline = TFTDataPipeline(api_key="RGAPI-YOUR-KEY")

# Run full pipeline (10 players, 20 matches each)
df = pipeline.run_full_pipeline(num_players=10, matches_per_player=20)

# Access the data
print(f"Collected {len(df)} game records")
print(df.head())
```

## Contributing

When the TFT set changes:
1. Run `tft_data_scraper.py` to get new static data
2. Run `update_game_assets.py` to sync `game_assets.py`
3. Manually update item categories (Support, Ornn, etc.)
4. Test that vision OCR still works with new champion names

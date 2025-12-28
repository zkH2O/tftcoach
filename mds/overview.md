TFT "Ear-Whisperer" AI Coach: Technical Architecture
1. Objective
To build a modular, undetectable, and set-agnostic AI coaching system that provides real-time strategic advice through Voice/TTS.

2. System Overview (The "Agentic Committee")
The system is divided into three distinct layers to ensure that a game patch or a new Set does not break the core code.

Tier 1: Perception (The Eyes)
Module: ScreenScanner

Tech: MSS (Capture), YOLOv11 (Object Detection), OpenCV (Processing).

Set-Agnostic Strategy:

Do not train YOLO to recognize "Darius" or "Caitlyn."

Train YOLO to recognize generic classes: Champion_Icon, Item_Icon, Gold_Text, Stage_Text.

The Translation Step: Crop the detected Champion_Icon. Use a Perceptual Hash (pHash) or a small CLIP model to compare that crop against a local /assets/set13/ folder.

Benefit: When Set 14 drops, you only replace the images in the /assets/ folder. No retraining required.

Tier 2: Knowledge & RAG (The Brain)
Module: MetaScraper & KnowledgeBase

Tech: Playwright (Scraping), ChromaDB (Vector DB).

Workflow:

Daily Job: Scrape Tactics.tools or MetaTFT for the top 20 compositions, including item priority and augment win rates.

Vectorization: Convert these guides into text embeddings and store them in ChromaDB.

Real-time Retrieval: When the ScreenScanner identifies your items (e.g., "Recurve Bow, BF Sword"), the system queries the DB: "What are the S-Tier lines for these components?"

Tier 3: Reasoning & Strategy (The Coach)
Module: StrategistAgent

Tech: Gemini 1.5 Flash (Low latency) or GPT-4o-mini.

The Prompting Strategy (The Critic):

Feed the LLM the game_state.json (Board, Bench, Shop, Gold, Stage, Opponent Comps).

Feed the LLM the retrieved RAG context (The Meta).

Instruction: "Zi is playing [Comp A]. 3 other players are also building [Comp A]. Provide a pivot strategy or an aggressive leveling timing to out-tempo them."

3. Data Flow & Execution Loop
Capture (1 FPS): Grab screen → YOLO detects bounding boxes.

Identify: Compare boxes to local assets → Map to unit names.

Lobby Analysis: Every 30s, the system triggers a "Scout" (simulates 1 keypress) to update the "Contestation Matrix."

Inference: Package state into JSON → Send to LLM.

Output: LLM response is converted to audio via Pyttsx3 or ElevenLabs.

4. MLOps: The "Set-Switch" Protocol
When a new Set (e.g., Set 14) is released, follow these steps:

Asset Update: Run a script to scrape unit icons from the Riot CDN or Wiki into the /assets/ folder.

Mapping: Re-generate the pHash manifest for the new icons.

RAG Refresh: Wipe the ChromaDB collection and run the scraper on the new Set's meta-data pages.

Result: Your AI is now "Challenger" level in the new Set within 15 minutes of the patch.

5. Security & Safety (Vanguard Evasion)
Zero-Hook Policy: Never read game memory. Only use screenshots.

Passive Input: The AI should never move the mouse.

Keypress Mimicry: If you automate scouting (pressing 1), use a Gaussian distribution for delays (e.g., time.sleep(random.gauss(0.2, 0.05))) to avoid "perfect" robotic timing.

Overlay Risk: Avoid drawing on the game window. Use a second monitor or Voice-only feedback.

6. Implementation Roadmap
[ ] Phase 1: Build the MSS capture loop and generic YOLOv11 detector.

[ ] Phase 2: Implement the pHash unit identification (Set-Agnosticism).

[ ] Phase 3: Build the Tactics.tools scraper and Vector DB integration.

[ ] Phase 4: Connect the LLM and test the "Ear-Whisperer" via TTS.
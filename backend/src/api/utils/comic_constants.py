# backend/src/api/utils/comic_constants.py

# Panel sizes
PANEL_WIDTH = 1024
PANEL_HEIGHT = 1024
PANEL_GUTTER = 60
PANEL_MARGIN = 60

# Bubble size ratios (relative to panel)
BUBBLE_MAX_WIDTH_RATIO = 0.25  # 25% of panel width
BUBBLE_MAX_HEIGHT_RATIO = 0.22 # 22% of panel height
BUBBLE_MIN_WIDTH_RATIO = 0.10
BUBBLE_MIN_HEIGHT_RATIO = 0.10

# Font sizes
FONT_SIZES = {
    "speech": 24,
    "thought": 20,
    "narration": 18,
    "sound_effect": 32,
    "scream": 28,
    "title": 40,
    "sfx_low": 24,
    "sfx_medium": 32,
    "sfx_high": 36,
    "sfx_extreme": 48,
}
# Padding
BUBBLE_PADDING = {
    "speech": 12,
    "thought": 12,
    "narration": 10,
    "sound_effect": 8,
    "scream": 10,
} 
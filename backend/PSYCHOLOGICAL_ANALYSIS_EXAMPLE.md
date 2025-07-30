# 🧠 Psychological Analysis System - Example

## 📊 How It Works

The psychological analysis system analyzes user's comic prompts across all three worlds to generate AI-powered psychological insights. Here's how it works:

### **1. Data Collection**
The system collects comic data from all three worlds:

```python
# Get comics from each world
imagination_comics = [
    {
        "concept": "a girl with dark long hair was sitting around the window",
        "genre": "drama",
        "world_type": "imagination_world"
    },
    {
        "concept": "a magical forest with glowing butterflies",
        "genre": "fantasy", 
        "world_type": "imagination_world"
    }
]

mind_comics = [
    {
        "concept": "a detective ponders over a mysterious case",
        "genre": "mystery",
        "world_type": "mind_world"
    },
    {
        "concept": "a scientist contemplates the nature of reality",
        "genre": "sci-fi",
        "world_type": "mind_world"
    }
]

dream_comics = [
    {
        "concept": "a surreal dream with floating objects",
        "genre": "fantasy",
        "world_type": "dream_world"
    },
    {
        "concept": "a shadowy figure in a misty landscape",
        "genre": "horror",
        "world_type": "dream_world"
    }
]
```

### **2. AI Analysis Prompt**
The system sends this data to Azure OpenAI with a structured prompt:

```
Analyze the user's comic creation patterns across three psychological worlds. For each world, identify:

1. **Dominant emotional tone** - What emotional atmosphere prevails?
2. **Most common genre(s)** - What story types does the user prefer?
3. **Recurring symbols or story elements** - What motifs appear repeatedly?
4. **Typical character role** - What character archetypes dominate (hero, observer, victim, wanderer, etc.)?

Then synthesize a single, psychologically informed assumption about the user based on cross-world patterns.

**Imagination World Data:**
Concepts: ["a girl with dark long hair was sitting around the window", "a magical forest with glowing butterflies"]
Genres: ["drama", "fantasy"]
Count: 2

**Mind World Data:**
Concepts: ["a detective ponders over a mysterious case", "a scientist contemplates the nature of reality"]
Genres: ["mystery", "sci-fi"]
Count: 2

**Dream World Data:**
Concepts: ["a surreal dream with floating objects", "a shadowy figure in a misty landscape"]
Genres: ["fantasy", "horror"]
Count: 2
```

### **3. AI Response**
The AI generates a structured JSON response:

```json
{
  "world_profiles": {
    "imagination_world": {
      "dominant_emotional_tone": "contemplative and magical",
      "most_common_genres": ["drama", "fantasy"],
      "recurring_symbols": ["windows", "nature", "magical elements", "solitary figures"],
      "typical_character_role": "observer/contemplator",
      "psychological_theme": "introspective exploration of inner worlds"
    },
    "mind_world": {
      "dominant_emotional_tone": "analytical and curious",
      "most_common_genres": ["mystery", "sci-fi"],
      "recurring_symbols": ["puzzles", "scientific concepts", "intellectual challenges"],
      "typical_character_role": "investigator/thinker",
      "psychological_theme": "intellectual problem-solving and philosophical inquiry"
    },
    "dream_world": {
      "dominant_emotional_tone": "mysterious and unsettling",
      "most_common_genres": ["fantasy", "horror"],
      "recurring_symbols": ["shadows", "floating objects", "mist", "surreal elements"],
      "typical_character_role": "wanderer/explorer",
      "psychological_theme": "exploration of subconscious and unknown territories"
    }
  },
  "cross_world_patterns": {
    "emotional_consistency": "User consistently explores introspective and contemplative themes across all worlds",
    "genre_evolution": "Progression from magical realism (imagination) to intellectual inquiry (mind) to surreal exploration (dream)",
    "character_development": "Evolution from observer to investigator to explorer, showing increasing agency",
    "symbolic_connections": "Recurring themes of exploration, mystery, and the unknown across all worlds"
  },
  "psychological_assumption": "This user is a contemplative individual who uses creative expression as a means of intellectual and emotional exploration. They show a preference for introspective themes and demonstrate a natural progression from passive observation to active investigation to deep exploration of the unknown. Their creative patterns suggest someone who values both analytical thinking and intuitive understanding.",
  "confidence_level": 0.85,
  "recommendation_areas": [
    "Encourage exploration of more complex character interactions",
    "Suggest experimenting with different narrative perspectives",
    "Recommend exploring collaborative storytelling themes"
  ]
}
```

### **4. API Response**
The endpoint returns this structured data:

```json
{
  "user_id": 123,
  "analysis_date": "2025-07-23T23:15:30.123456",
  "world_profiles": {
    "imagination_world": {
      "world_type": "imagination_world",
      "dominant_emotional_tone": "contemplative and magical",
      "most_common_genres": ["drama", "fantasy"],
      "recurring_symbols": ["windows", "nature", "magical elements", "solitary figures"],
      "typical_character_role": "observer/contemplator",
      "psychological_theme": "introspective exploration of inner worlds",
      "comic_count": 2
    },
    "mind_world": {
      "world_type": "mind_world", 
      "dominant_emotional_tone": "analytical and curious",
      "most_common_genres": ["mystery", "sci-fi"],
      "recurring_symbols": ["puzzles", "scientific concepts", "intellectual challenges"],
      "typical_character_role": "investigator/thinker",
      "psychological_theme": "intellectual problem-solving and philosophical inquiry",
      "comic_count": 2
    },
    "dream_world": {
      "world_type": "dream_world",
      "dominant_emotional_tone": "mysterious and unsettling", 
      "most_common_genres": ["fantasy", "horror"],
      "recurring_symbols": ["shadows", "floating objects", "mist", "surreal elements"],
      "typical_character_role": "wanderer/explorer",
      "psychological_theme": "exploration of subconscious and unknown territories",
      "comic_count": 2
    }
  },
  "cross_world_patterns": {
    "emotional_consistency": "User consistently explores introspective and contemplative themes across all worlds",
    "genre_evolution": "Progression from magical realism (imagination) to intellectual inquiry (mind) to surreal exploration (dream)",
    "character_development": "Evolution from observer to investigator to explorer, showing increasing agency",
    "symbolic_connections": "Recurring themes of exploration, mystery, and the unknown across all worlds"
  },
  "psychological_assumption": "This user is a contemplative individual who uses creative expression as a means of intellectual and emotional exploration. They show a preference for introspective themes and demonstrate a natural progression from passive observation to active investigation to deep exploration of the unknown. Their creative patterns suggest someone who values both analytical thinking and intuitive understanding.",
  "confidence_level": 0.85,
  "recommendation_areas": [
    "Encourage exploration of more complex character interactions",
    "Suggest experimenting with different narrative perspectives", 
    "Recommend exploring collaborative storytelling themes"
  ]
}
```

## 🎯 Usage Examples

### **1. Generate Psychological Assumptions**
```bash
curl -X POST "https://mindtoon.space/api/analytics/psychological-assumptions/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **2. Get Saved Psychological Insights**
```bash
curl -X GET "https://mindtoon.space/api/analytics/insights/123?insight_type=psychological_assumptions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **3. iOS Integration**
```swift
// Generate psychological assumptions
let psychologicalProfile = await APIClient.shared.generatePsychologicalAssumptions(userId: currentUser.id)

// Display world-specific insights
for (world, profile) in psychologicalProfile.world_profiles {
    print("\(world): \(profile.psychological_theme)")
    print("Emotional tone: \(profile.dominant_emotional_tone)")
    print("Character role: \(profile.typical_character_role)")
}

// Show main psychological assumption
print("Psychological Profile: \(psychologicalProfile.psychological_assumption)")
print("Confidence: \(psychologicalProfile.confidence_level * 100)%")

// Display recommendations
for recommendation in psychologicalProfile.recommendation_areas {
    print("Recommendation: \(recommendation)")
}
```

## 🧠 Psychological Insights Explained

### **1. World-Specific Analysis**

#### **Imagination World**
- **Emotional Tone**: Contemplative and magical
- **Genres**: Drama, fantasy
- **Symbols**: Windows, nature, magical elements
- **Character Role**: Observer/contemplator
- **Theme**: Introspective exploration of inner worlds

#### **Mind World** 
- **Emotional Tone**: Analytical and curious
- **Genres**: Mystery, sci-fi
- **Symbols**: Puzzles, scientific concepts
- **Character Role**: Investigator/thinker
- **Theme**: Intellectual problem-solving

#### **Dream World**
- **Emotional Tone**: Mysterious and unsettling
- **Genres**: Fantasy, horror
- **Symbols**: Shadows, floating objects, mist
- **Character Role**: Wanderer/explorer
- **Theme**: Exploration of subconscious

### **2. Cross-World Patterns**

#### **Emotional Consistency**
- User consistently explores introspective themes
- Preference for contemplative atmospheres
- Balance between analytical and intuitive thinking

#### **Genre Evolution**
- Progression from magical realism → intellectual inquiry → surreal exploration
- Shows increasing complexity and depth
- Demonstrates creative growth over time

#### **Character Development**
- Evolution from observer → investigator → explorer
- Shows increasing agency and engagement
- Reflects personal growth through creative expression

### **3. Psychological Assumption**
The AI synthesizes all this data into a single, psychologically informed assumption about the user's creative personality and preferences.

## 🎨 Dashboard Visualization Ideas

### **1. World Comparison Chart**
```javascript
// Compare emotional tones across worlds
const emotionalTones = {
  imagination: "contemplative and magical",
  mind: "analytical and curious", 
  dream: "mysterious and unsettling"
};
```

### **2. Character Role Evolution**
```javascript
// Show character development progression
const characterEvolution = [
  "observer/contemplator",
  "investigator/thinker", 
  "wanderer/explorer"
];
```

### **3. Symbol Network**
```javascript
// Visualize recurring symbols across worlds
const symbolNetwork = {
  imagination: ["windows", "nature", "magical elements"],
  mind: ["puzzles", "scientific concepts"],
  dream: ["shadows", "floating objects", "mist"]
};
```

## 🚀 Benefits

### **1. Personalized Insights**
- AI-generated psychological profiles
- Cross-world pattern recognition
- Confidence-scored assumptions

### **2. Creative Recommendations**
- Actionable suggestions for growth
- Genre and theme recommendations
- Character development guidance

### **3. Dashboard Ready**
- Structured JSON for visualization
- World-specific breakdowns
- Trend analysis capabilities

### **4. Story Suggestions**
- Genre recommendations based on patterns
- Character archetype suggestions
- Theme development guidance

This system provides deep psychological insights that can be used for personalized recommendations, creative guidance, and user engagement! 🎉 
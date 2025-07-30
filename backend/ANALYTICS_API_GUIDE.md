# MindToon Analytics API Guide

## Overview

The MindToon Analytics system (Analyst) provides comprehensive tracking and analysis of user comic generation behavior. The system tracks user inputs (prompt, genre, art style, world) and generates insights without modifying the core comic generation logic.

## Key Features

- **📊 Data Tracking**: Track every comic generation with user inputs
- **📈 Visual Analytics**: Generate chart-ready data for genre, art style, and world distributions
- **🔍 Pattern Analysis**: Use LLM to analyze prompt themes and creative patterns
- **📅 Weekly Insights**: Generate weekly summaries of user behavior
- **🎯 Smart Triggers**: Unlock insights every 5 comics generated

## API Endpoints

### Base URL
```
/api/analytics
```

### Authentication
All endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Core Endpoints

### 1. Add Analytics Entry
**POST** `/api/analytics/entry`

Add a new comic generation entry to analytics tracking.

**Request Body:**
```json
{
  "prompt": "A superhero saving a city from a giant robot",
  "genre": "action",
  "art_style": "comic book",
  "world_type": "imagination_world",
  "comic_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "message": "Analytics entry added successfully",
  "entry_id": 456
}
```

### 2. Get Analytics Summary
**GET** `/api/analytics/summary`

Get comprehensive analytics summary for the current user, optionally filtered by world type.

**Query Parameters:**
- `world_type` (optional): Filter by world type (`imagination_world`, `mind_world`, `dream_world`)

**Examples:**
```
GET /api/analytics/summary                    # All comics
GET /api/analytics/summary?world_type=imagination_world  # Only Imagination World
GET /api/analytics/summary?world_type=mind_world         # Only Mind World
GET /api/analytics/summary?world_type=dream_world        # Only Dream World
```

**Response:**
```json
{
  "total_entries": 15,
  "genre_distribution": [
    {
      "genre": "action",
      "count": 5,
      "percentage": 33.33
    },
    {
      "genre": "fantasy",
      "count": 3,
      "percentage": 20.0
    }
  ],
  "art_style_distribution": [
    {
      "art_style": "comic book",
      "count": 8,
      "percentage": 53.33
    }
  ],
  "world_distribution": [
    {
      "world_type": "imagination_world",
      "count": 10,
      "percentage": 66.67
    }
  ],
  "time_series": [
    {
      "date": "2024-01-15",
      "count": 2,
      "genres": ["action", "fantasy"],
      "art_styles": ["comic book", "watercolor"]
    }
  ],
  "recent_prompts": [
    "A superhero saving a city from a giant robot",
    "A peaceful garden with magical creatures"
  ],
  "insights_available": true
}
```

## Chart Data Endpoints

### 3. Genre Distribution Chart
**GET** `/api/analytics/charts/genre-distribution`

Get genre distribution data formatted for bar charts.

**Response:**
```json
{
  "success": true,
  "chart_type": "bar",
  "title": "Your Genre Preferences",
  "data": {
    "labels": ["action", "fantasy", "mystery"],
    "data": [5, 3, 2],
    "percentages": [33.33, 20.0, 13.33]
  }
}
```

### 4. Art Style Distribution Chart
**GET** `/api/analytics/charts/art-style-distribution`

Get art style distribution data formatted for pie charts.

**Response:**
```json
{
  "success": true,
  "chart_type": "pie",
  "title": "Your Art Style Preferences",
  "data": {
    "labels": ["comic book", "watercolor", "digital art"],
    "data": [8, 4, 3],
    "percentages": [53.33, 26.67, 20.0]
  }
}
```

### 5. World Distribution Chart
**GET** `/api/analytics/charts/world-distribution`

Get world distribution data formatted for pie charts.

**Response:**
```json
{
  "success": true,
  "chart_type": "pie",
  "title": "Your World Preferences",
  "data": {
    "labels": ["imagination_world", "dream_world", "mind_world"],
    "data": [10, 3, 2],
    "percentages": [66.67, 20.0, 13.33]
  }
}
```

### 6. Time Series Chart
**GET** `/api/analytics/charts/time-series`

Get time series data for trend charts (last 30 days).

**Response:**
```json
{
  "success": true,
  "chart_type": "line",
  "title": "Your Comic Generation Trends",
  "data": {
    "labels": ["2024-01-10", "2024-01-11", "2024-01-12"],
    "data": [2, 1, 3],
    "genres": [["action", "fantasy"], ["mystery"], ["sci-fi", "romance", "action"]],
    "art_styles": [["comic book", "watercolor"], ["noir"], ["digital art", "soft pastels", "comic book"]]
  }
}
```

## Insight Endpoints

### 7. Generate Pattern Analysis
**POST** `/api/analytics/insights/patterns`

Generate LLM-based pattern analysis of user's creative prompts.

**Response:**
```json
{
  "success": true,
  "insight_type": "pattern_analysis",
  "title": "Your Creative Patterns",
  "description": "Analysis of your comic generation themes and creative expression",
  "data": {
    "themes": ["adventure", "heroism", "fantasy"],
    "emotions": ["excitement", "wonder", "mystery"],
    "language_style": "descriptive",
    "creativity_indicators": ["imaginative scenarios", "diverse characters"],
    "summary": "You show a strong preference for adventurous and fantastical themes with imaginative storytelling.",
    "total_prompts_analyzed": 15,
    "analysis_date": "2024-01-15T10:30:00"
  },
  "created_at": "2024-01-15T10:30:00"
}
```

### 8. Get Weekly Insight
**GET** `/api/analytics/insights/weekly`

Get weekly insight based on user's comic generation patterns.

**Response:**
```json
{
  "top_genres": [
    {
      "genre": "action",
      "count": 3,
      "percentage": 50.0
    }
  ],
  "top_art_styles": [
    {
      "art_style": "comic book",
      "count": 4,
      "percentage": 66.67
    }
  ],
  "world_distribution": [
    {
      "world_type": "imagination_world",
      "count": 5,
      "percentage": 83.33
    }
  ],
  "prompt_patterns": {
    "themes": ["adventure", "heroism"],
    "emotions": ["excitement", "determination"],
    "language_style": "action-oriented",
    "creativity_indicators": ["dynamic scenarios", "heroic themes"],
    "summary": "This week you focused on action-packed adventures with heroic themes."
  },
  "total_comics": 6,
  "week_start": "2024-01-08",
  "week_end": "2024-01-15"
}
```

### 9. Get User Insights
**GET** `/api/analytics/insights`

Get all insights for the current user.

**Query Parameters:**
- `insight_type` (optional): Filter by insight type

**Response:**
```json
[
  {
    "success": true,
    "insight_type": "pattern_analysis",
    "title": "Your Creative Patterns",
    "description": "Analysis of your comic generation themes and creative expression",
    "data": {
      "themes": ["adventure", "fantasy"],
      "emotions": ["excitement", "wonder"],
      "summary": "You show diverse creative interests."
    },
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### 10. Check Insights Availability
**GET** `/api/analytics/insights/available`

Check if insights are available for the user (every 5 comics).

**Response:**
```json
{
  "insights_available": true,
  "total_comics": 15,
  "next_insight_at": 20
}
```

## Data Models

### World Types
- `imagination_world`: Fantasy and creative scenarios
- `mind_world`: Real-world and logical scenarios  
- `dream_world`: Dream-like and surreal scenarios

### Analytics Entry
```python
{
  "id": 123,
  "user_id": 456,
  "prompt": "User's comic prompt",
  "genre": "action",
  "art_style": "comic book",
  "world_type": "imagination_world",
  "comic_id": 789,
  "created_at": "2024-01-15T10:30:00"
}
```

## Frontend Integration

### SwiftUI Chart Integration

The API provides chart-ready data that can be easily integrated with SwiftUI charting libraries:

```swift
// Example: Bar Chart for Genre Distribution
struct GenreChartView: View {
    @State private var chartData: [String: Any] = [:]
    
    var body: some View {
        VStack {
            Text("Your Genre Preferences")
                .font(.title)
            
            // Use your preferred charting library
            // Chart data format:
            // labels: ["action", "fantasy", "mystery"]
            // data: [5, 3, 2]
            // percentages: [33.33, 20.0, 13.33]
        }
    }
}
```

### Chart Types Supported

1. **Bar Charts**: Genre distribution, art style trends
2. **Pie Charts**: World distribution, art style preferences
3. **Line Charts**: Time series trends over 30 days
4. **Area Charts**: Cumulative generation patterns

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `401`: Unauthorized (missing/invalid token)
- `404`: Not found (no data available)
- `500`: Internal server error

Error responses include descriptive messages:
```json
{
  "detail": "Failed to get analytics summary: Database connection error"
}
```

## Rate Limiting

- Pattern analysis: 1 request per minute per user
- Weekly insights: 1 request per hour per user
- Chart data: No limits
- Analytics entries: No limits

## Privacy & Security

- All analytics data is user-specific and private
- No data is shared between users
- LLM analysis focuses on creative patterns, not personal content
- Users can request data deletion through existing account deletion endpoints

## Testing

Run the test script to verify the analytics system:

```bash
cd MindToon/backend
python test_analytics.py
```

This will test all core functionality and provide a summary of the system's capabilities. 
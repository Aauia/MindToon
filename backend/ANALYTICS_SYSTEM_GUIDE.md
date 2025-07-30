# 🎯 MindToon Analytics System Guide

## 📊 Overview

The MindToon Analytics System now works with **existing comics data** from your database instead of requiring manual analytics entries. The system automatically analyzes all comics that users have created and provides insights based on their actual creative patterns.

## 🔄 Key Changes

### **Before (Manual Analytics)**
- Required manual entry of analytics data
- Separate `AnalyticsEntry` table
- Manual tracking of each comic generation

### **After (Automatic Analytics)**
- Works directly with existing `ComicsPage` data
- Automatic analysis of all user comics
- No manual data entry required
- Real-time insights based on actual comic data

## 🌍 World-Based Analytics

The system supports filtering analytics by the three worlds:

- **Imagination World** (`imagination_world`)
- **Mind World** (`mind_world`) 
- **Dream World** (`dream_world`)

You can get analytics for:
- **All worlds combined** (default)
- **Specific world only** (using `world_type` parameter)

## 📈 Available Analytics Endpoints

### **1. Basic Analytics Summary**
```http
GET /api/analytics/summary/{user_id}?world_type=imagination_world
```

**Response:**
```json
{
  "total_entries": 15,
  "genre_distribution": [
    {"genre": "drama", "count": 8, "percentage": 53.33},
    {"genre": "comedy", "count": 4, "percentage": 26.67},
    {"genre": "fantasy", "count": 3, "percentage": 20.0}
  ],
  "art_style_distribution": [
    {"art_style": "anime", "count": 10, "percentage": 66.67},
    {"art_style": "comic book", "count": 5, "percentage": 33.33}
  ],
  "world_distribution": [
    {"world_type": "imagination_world", "count": 15, "percentage": 100.0}
  ],
  "time_series": [...],
  "recent_prompts": ["a girl with dark long hair...", ...],
  "insights_available": true
}
```

### **2. Weekly Insights**
```http
GET /api/analytics/insights/weekly/{user_id}?world_type=mind_world
```

**Response:**
```json
{
  "top_genres": [...],
  "top_art_styles": [...],
  "world_distribution": [...],
  "prompt_patterns": {
    "themes": ["introspection", "philosophical"],
    "emotions": ["contemplative", "curious"],
    "language_style": "descriptive",
    "creativity_indicators": ["complex concepts", "deep thinking"],
    "summary": "User shows preference for intellectual and thought-provoking content"
  },
  "total_comics": 7,
  "week_start": "2025-07-16",
  "week_end": "2025-07-23"
}
```

### **3. Pattern Analysis (AI-Powered)**
```http
POST /api/analytics/insights/patterns/{user_id}?world_type=dream_world
```

**Response:**
```json
{
  "success": true,
  "insight_type": "pattern_analysis",
  "title": "Your Creative Patterns",
  "description": "Analysis of your comic generation themes and creative expression",
  "data": {
    "themes": ["surreal", "subconscious"],
    "emotions": ["mysterious", "dreamy"],
    "language_style": "descriptive",
    "creativity_indicators": ["imaginative concepts", "surreal elements"],
    "summary": "User explores dream-like and surreal themes",
    "total_comics_analyzed": 12,
    "world_type": "dream_world",
    "analysis_date": "2025-07-23T23:15:30.123456"
  },
  "created_at": "2025-07-23T23:15:30.123456"
}
```

### **4. Chart Data for Frontend**
```http
GET /api/analytics/charts/genre-distribution/{user_id}?world_type=imagination_world
```

**Response:**
```json
{
  "success": true,
  "chart_type": "bar",
  "title": "Your Genre Preferences",
  "world_type": "imagination_world",
  "data": {
    "labels": ["drama", "comedy", "fantasy"],
    "data": [8, 4, 3],
    "percentages": [53.33, 26.67, 20.0]
  }
}
```

### **5. User Analytics Overview**
```http
GET /api/analytics/user/{user_id}/overview
```

**Response:**
```json
{
  "user_id": 123,
  "total_comics": 25,
  "worlds": {
    "imagination_world": {
      "total_comics": 15,
      "top_genre": "drama",
      "top_art_style": "anime"
    },
    "mind_world": {
      "total_comics": 7,
      "top_genre": "mystery",
      "top_art_style": "realistic"
    },
    "dream_world": {
      "total_comics": 3,
      "top_genre": "fantasy",
      "top_art_style": "watercolor"
    }
  },
  "overall_stats": {
    "top_genre": "drama",
    "top_art_style": "anime",
    "insights_available": true
  }
}
```

### **6. Creativity Score**
```http
GET /api/analytics/user/{user_id}/creativity-score?world_type=imagination_world
```

**Response:**
```json
{
  "user_id": 123,
  "world_type": "imagination_world",
  "creativity_score": 85.5,
  "factors": {
    "genre_diversity": 80.0,
    "art_style_diversity": 75.0,
    "concept_complexity": 90.0,
    "activity_level": 95.0
  },
  "stats": {
    "total_comics": 15,
    "unique_genres": 4,
    "unique_art_styles": 3,
    "avg_concept_length": 89.2
  }
}
```

### **7. Recent Activity**
```http
GET /api/analytics/user/{user_id}/recent-activity?world_type=mind_world&limit=5
```

**Response:**
```json
{
  "user_id": 123,
  "world_type": "mind_world",
  "total_comics": 7,
  "recent_activity": [
    {
      "id": 456,
      "title": "Comic: A detective ponders...",
      "concept": "A detective ponders over a mysterious case",
      "genre": "mystery",
      "art_style": "realistic",
      "world_type": "mind_world",
      "created_at": "2025-07-23T23:10:59.258044",
      "is_favorite": true,
      "view_count": 3
    }
  ]
}
```

## 🎨 World-Specific Analytics

### **Imagination World Analytics**
```http
GET /api/analytics/imagination-world/{user_id}
```

### **Mind World Analytics**
```http
GET /api/analytics/mind-world/{user_id}
```

### **Dream World Analytics**
```http
GET /api/analytics/dream-world/{user_id}
```

## 📊 Chart Types Available

### **1. Genre Distribution (Bar Chart)**
- Shows user's genre preferences
- Filterable by world type
- Includes percentages and counts

### **2. Art Style Distribution (Pie Chart)**
- Shows user's art style preferences
- Filterable by world type
- Visual representation of preferences

### **3. World Distribution (Pie Chart)**
- Shows distribution across all three worlds
- Only available when not filtering by specific world

### **4. Time Series (Line Chart)**
- Shows comic creation trends over time
- Last 30 days of activity
- Filterable by world type

## 🤖 AI-Powered Insights

### **Pattern Analysis**
- Analyzes user's comic concepts using LLM
- Identifies recurring themes and emotions
- Provides creativity indicators
- Generates personalized summaries

### **Weekly Insights**
- Focuses on last 7 days of activity
- Combines statistical analysis with AI insights
- Provides actionable creative feedback

## 🎯 Usage Examples

### **Example 1: Get User's Overall Analytics**
```bash
curl -X GET "https://mindtoon.space/api/analytics/summary/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Example 2: Get Imagination World Analytics**
```bash
curl -X GET "https://mindtoon.space/api/analytics/summary/123?world_type=imagination_world" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Example 3: Get AI-Powered Pattern Analysis**
```bash
curl -X POST "https://mindtoon.space/api/analytics/insights/patterns/123?world_type=mind_world" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Example 4: Get Chart Data for Frontend**
```bash
curl -X GET "https://mindtoon.space/api/analytics/charts/genre-distribution/123?world_type=dream_world" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Integration with iOS App

### **1. Analytics Dashboard**
```swift
// Get user's analytics overview
let overview = await APIClient.shared.getUserAnalyticsOverview(userId: currentUser.id)

// Display world-specific stats
for (world, stats) in overview.worlds {
    print("\(world): \(stats.total_comics) comics")
}
```

### **2. Chart Integration**
```swift
// Get chart data for visualization
let chartData = await APIClient.shared.getGenreChartData(
    userId: currentUser.id, 
    worldType: selectedWorld
)

// Use with charting library
chartView.updateChart(with: chartData)
```

### **3. AI Insights**
```swift
// Get AI-powered insights
let insights = await APIClient.shared.getPatternInsights(
    userId: currentUser.id,
    worldType: selectedWorld
)

// Display insights to user
insightsView.displayInsights(insights)
```

## 🚀 Benefits of New System

### **1. Automatic Analysis**
- No manual data entry required
- Real-time insights based on actual comic data
- Immediate availability of analytics

### **2. World-Based Organization**
- Separate analytics for each world
- Understand user preferences per world
- Targeted insights for different creative contexts

### **3. AI-Powered Insights**
- LLM analysis of comic concepts
- Pattern recognition and theme identification
- Personalized creative feedback

### **4. Comprehensive Analytics**
- Genre and art style preferences
- Time series analysis
- Creativity scoring
- Recent activity tracking

### **5. Frontend Ready**
- Chart data formatted for visualization
- Multiple chart types supported
- Easy integration with iOS app

## 📈 Analytics Features

### **Statistical Analysis**
- Genre distribution and percentages
- Art style preferences
- World-based organization
- Time series trends
- Activity levels

### **AI Analysis**
- Theme identification
- Emotional pattern recognition
- Language style analysis
- Creativity indicators
- Personalized summaries

### **Creativity Scoring**
- Genre diversity assessment
- Art style variety
- Concept complexity analysis
- Activity level evaluation
- Overall creativity score

This new analytics system provides comprehensive insights into user behavior and creative patterns while being completely automatic and working with existing data! 🎉 
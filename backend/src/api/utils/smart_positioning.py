import cv2
import numpy as np
from PIL import Image, ImageDraw
from typing import List, Tuple, Dict, Optional
import face_recognition

class SmartTextPositioner:
    """
    Intelligent text positioning system that analyzes images to place speech bubbles
    near characters and avoid overlapping important content.
    """
    
    def __init__(self):
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        except Exception as e:
            print(f"Warning: Could not load OpenCV cascades: {e}")
            self.face_cascade = None
            self.eye_cascade = None
        self.placed_bubbles = []  # Track already placed bubbles to prevent overlaps
    
    def analyze_image(self, image: Image.Image) -> Dict:
        """
        Analyze image to detect faces, characters, and optimal text placement areas.
        Returns comprehensive analysis data.
        """
        # Convert PIL to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        analysis = {
            'faces': [],
            'characters': [],
            'free_zones': [],
            'safe_areas': [],
            'image_regions': self._analyze_regions(opencv_image),
            'width': image.size[0],
            'height': image.size[1]
        }
        
        # Detect faces using OpenCV if available
        if self.face_cascade is not None:
            try:
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                for (x, y, w, h) in faces:
                    face_info = {
                        'bbox': (x, y, w, h),
                        'center': (x + w//2, y + h//2),
                        'area': w * h,
                        'confidence': 0.8  # OpenCV default confidence
                    }
                    analysis['faces'].append(face_info)
                    
                    # Create character zone around face (larger area)
                    char_zone = {
                        'bbox': (max(0, x-w//2), max(0, y-h//2), w*2, h*2),
                        'face_center': face_info['center'],
                        'type': 'character'
                    }
                    analysis['characters'].append(char_zone)
            except Exception as e:
                print(f"Warning: Face detection failed: {e}")
        else:
            # Fallback: create generic character zones if no face detection
            width, height = image.size
            # Assume characters might be in common positions
            generic_positions = [
                (width//4, height//3, width//6, height//4),    # Left character
                (width*3//4, height//3, width//6, height//4),  # Right character
            ]
            for i, (x, y, w, h) in enumerate(generic_positions):
                char_zone = {
                    'bbox': (x-w//2, y-h//2, w, h),
                    'face_center': (x, y),
                    'type': 'character'
                }
                analysis['characters'].append(char_zone)
        
        # Find free zones for text placement
        analysis['free_zones'] = self._find_free_zones(image, analysis['characters'])
        analysis['safe_areas'] = self._calculate_safe_areas(image, analysis['characters'])
        
        return analysis
    
    def _analyze_regions(self, opencv_image) -> Dict:
        """Analyze image regions for content density and importance."""
        height, width = opencv_image.shape[:2]
        
        # Divide image into grid for analysis
        grid_size = 8
        cell_w, cell_h = width // grid_size, height // grid_size
        
        regions = {
            'top_left': (0, 0, cell_w*3, cell_h*3),
            'top_right': (width-cell_w*3, 0, cell_w*3, cell_h*3),
            'bottom_left': (0, height-cell_h*3, cell_w*3, cell_h*3),
            'bottom_right': (width-cell_w*3, height-cell_h*3, cell_w*3, cell_h*3),
            'center': (cell_w*2, cell_h*2, cell_w*4, cell_h*4),
            'top_center': (cell_w*2, 0, cell_w*4, cell_h*2),
            'bottom_center': (cell_w*2, height-cell_h*2, cell_w*4, cell_h*2)
        }
        
        return regions
    
    def _find_free_zones(self, image: Image.Image, characters: List[Dict]) -> List[Dict]:
        """Find areas of the image with low content density, suitable for text."""
        width, height = image.size
        free_zones = []
        
        # Standard comic text zones
        potential_zones = [
            {'name': 'top_left', 'bbox': (20, 20, width//3, height//4)},
            {'name': 'top_right', 'bbox': (width*2//3, 20, width//3-20, height//4)},
            {'name': 'bottom_left', 'bbox': (20, height*3//4, width//3, height//4-20)},
            {'name': 'bottom_right', 'bbox': (width*2//3, height*3//4, width//3-20, height//4-20)},
            {'name': 'top_center', 'bbox': (width//3, 20, width//3, height//5)},
            {'name': 'bottom_center', 'bbox': (width//3, height*4//5, width//3, height//5-20)},
        ]
        
        for zone in potential_zones:
            # Check if zone conflicts with character positions
            conflicts = False
            for char in characters:
                if self._zones_overlap(zone['bbox'], char['bbox']):
                    conflicts = True
                    break
            
            if not conflicts:
                zone['priority'] = self._calculate_zone_priority(zone, image)
                free_zones.append(zone)
        
        # Sort by priority (higher priority = better for text)
        free_zones.sort(key=lambda x: x['priority'], reverse=True)
        return free_zones
    
    def _calculate_safe_areas(self, image: Image.Image, characters: List[Dict]) -> List[Dict]:
        """Calculate safe areas around characters for speech bubble placement."""
        width, height = image.size
        safe_areas = []
        
        for i, char in enumerate(characters):
            char_x, char_y, char_w, char_h = char['bbox']
            face_center = char['face_center']
            
            # Define safe zones around character for speech bubbles
            bubble_zones = [
                {
                    'position': 'above',
                    'bbox': (face_center[0] - 100, max(0, char_y - 150), 200, 120),
                    'tail_point': (face_center[0], char_y),
                    'character_id': i
                },
                {
                    'position': 'below',
                    'bbox': (face_center[0] - 100, min(height-120, char_y + char_h + 30), 200, 120),
                    'tail_point': (face_center[0], char_y + char_h),
                    'character_id': i
                },
                {
                    'position': 'left',
                    'bbox': (max(0, char_x - 220), face_center[1] - 60, 200, 120),
                    'tail_point': (char_x, face_center[1]),
                    'character_id': i
                },
                {
                    'position': 'right',
                    'bbox': (min(width-200, char_x + char_w + 20), face_center[1] - 60, 200, 120),
                    'tail_point': (char_x + char_w, face_center[1]),
                    'character_id': i
                }
            ]
            
            # Filter zones that fit within image boundaries
            valid_zones = []
            for zone in bubble_zones:
                x, y, w, h = zone['bbox']
                if x >= 0 and y >= 0 and x + w <= width and y + h <= height:
                    zone['priority'] = self._calculate_bubble_zone_priority(zone, char, characters)
                    valid_zones.append(zone)
            
            safe_areas.extend(valid_zones)
        
        return safe_areas
    
    def _zones_overlap(self, zone1: Tuple[int, int, int, int], zone2: Tuple[int, int, int, int]) -> bool:
        """Check if two rectangular zones overlap."""
        x1, y1, w1, h1 = zone1
        x2, y2, w2, h2 = zone2
        
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    def _calculate_zone_priority(self, zone: Dict, image: Image.Image) -> float:
        """Calculate priority score for a free zone (higher = better for text)."""
        # Prefer upper areas for narration, avoid center for speeches
        x, y, w, h = zone['bbox']
        
        priority = 1.0
        
        # Upper areas are better for narration
        if zone['name'].startswith('top'):
            priority += 0.3
        
        # Corner areas are safer
        if 'left' in zone['name'] or 'right' in zone['name']:
            priority += 0.2
        
        # Larger areas are better
        area_score = (w * h) / (image.size[0] * image.size[1])
        priority += area_score * 0.5
        
        return priority
    
    def _calculate_bubble_zone_priority(self, zone: Dict, character: Dict, all_characters: List[Dict]) -> float:
        """Calculate priority for speech bubble zones around characters."""
        priority = 1.0
        
        # Prefer above/side positions over below
        if zone['position'] == 'above':
            priority += 0.4
        elif zone['position'] in ['left', 'right']:
            priority += 0.3
        elif zone['position'] == 'below':
            priority += 0.1
        
        # Check for conflicts with other characters
        for other_char in all_characters:
            if other_char != character and self._zones_overlap(zone['bbox'], other_char['bbox']):
                priority -= 0.5
        
        return priority
    
    def get_optimal_position(self, speaker_name: str, dialogue_type: str, image_analysis: Dict, 
                           characters_map: Dict[str, int], bubble_size: Tuple[int, int] = (200, 120)) -> Tuple[int, int, str]:
        """
        Find the optimal position for a text bubble based on speaker and dialogue type.
        Includes collision detection to prevent overlapping bubbles.
        Returns (x, y, speaker_position) tuple.
        """
        bubble_width, bubble_height = bubble_size
        
        # Get candidate positions based on dialogue type
        candidate_positions = []
        
        if dialogue_type == "narration":
            # Narration goes in free zones, preferably top
            for zone in image_analysis['free_zones']:
                if zone['name'].startswith('top'):
                    x, y, w, h = zone['bbox']
                    candidate_positions.append((x + 20, y + 20, "center", zone['priority']))
            
            # Add other free zones as fallback
            for zone in image_analysis['free_zones']:
                if not zone['name'].startswith('top'):
                    x, y, w, h = zone['bbox']
                    candidate_positions.append((x + 20, y + 20, "center", zone['priority'] * 0.8))
        
        elif dialogue_type in ["speech", "thought"] and speaker_name in characters_map:
            # Find character in analysis
            char_id = characters_map[speaker_name]
            if char_id < len(image_analysis['characters']):
                # Find best safe area for this character
                char_safe_areas = [area for area in image_analysis['safe_areas'] 
                                 if area.get('character_id') == char_id]
                
                for area in char_safe_areas:
                    x, y, w, h = area['bbox']
                    candidate_positions.append((x, y, area['position'], area['priority']))
        
        # Add free zones as fallback
        for zone in image_analysis['free_zones']:
            x, y, w, h = zone['bbox']
            candidate_positions.append((x + 20, y + 20, "center", zone['priority'] * 0.6))
        
        # Sort by priority (highest first)
        candidate_positions.sort(key=lambda x: x[3], reverse=True)
        
        # Find first position without collision
        for x, y, speaker_pos, priority in candidate_positions:
            bubble_rect = (x, y, bubble_width, bubble_height)
            
            if not self._has_collision(bubble_rect):
                # Found a good position without collision
                self.placed_bubbles.append(bubble_rect)
                return (x, y, speaker_pos)
        
        # If all positions have collisions, try to find alternative positions
        final_position = self._find_collision_free_position(
            candidate_positions[0] if candidate_positions else (50, 50, "center", 1.0),
            bubble_size,
            image_analysis
        )
        
        return final_position
    
    def _has_collision(self, bubble_rect: Tuple[int, int, int, int]) -> bool:
        """Check if bubble collides with any already placed bubbles."""
        for placed_rect in self.placed_bubbles:
            if self._zones_overlap(bubble_rect, placed_rect):
                return True
        return False
    
    def _find_collision_free_position(self, base_position: Tuple[int, int, str, float], 
                                    bubble_size: Tuple[int, int], image_analysis: Dict) -> Tuple[int, int, str]:
        """Find a collision-free position by trying offsets from the base position."""
        base_x, base_y, speaker_pos, _ = base_position
        bubble_width, bubble_height = bubble_size
        
        # Try various offsets to avoid collisions
        offsets = [
            (0, 0),          # Original position
            (30, 0),         # Right
            (-30, 0),        # Left  
            (0, 30),         # Down
            (0, -30),        # Up
            (50, 0),         # Further right
            (-50, 0),        # Further left
            (0, 50),         # Further down
            (0, -50),        # Further up
            (30, 30),        # Diagonal down-right
            (-30, 30),       # Diagonal down-left
            (30, -30),       # Diagonal up-right
            (-30, -30),      # Diagonal up-left
            (70, 0),         # Much further right
            (-70, 0),        # Much further left
        ]
        
        for dx, dy in offsets:
            test_x = max(10, base_x + dx)
            test_y = max(10, base_y + dy)
            test_rect = (test_x, test_y, bubble_width, bubble_height)
            
            # Check image boundaries
            if (test_x + bubble_width < image_analysis.get('width', 800) - 10 and 
                test_y + bubble_height < image_analysis.get('height', 600) - 10):
                
                if not self._has_collision(test_rect):
                    self.placed_bubbles.append(test_rect)
                    return (test_x, test_y, speaker_pos)
        
        # If still no position found, place with minimum overlap
        final_x = max(10, min(base_x, image_analysis.get('width', 800) - bubble_width - 10))
        final_y = max(10, min(base_y, image_analysis.get('height', 600) - bubble_height - 10))
        final_rect = (final_x, final_y, bubble_width, bubble_height)
        self.placed_bubbles.append(final_rect)
        
        return (final_x, final_y, speaker_pos)
    
    def reset_placement_tracking(self):
        """Reset the tracking of placed bubbles (call this for each new panel)."""
        self.placed_bubbles = []
    
    def create_character_mapping(self, character_names: List[str], image_analysis: Dict) -> Dict[str, int]:
        """
        Create mapping between character names and detected faces/positions.
        This is a simplified version - in practice, this could use more sophisticated
        character recognition or be based on the order of appearance.
        """
        mapping = {}
        
        # Simple approach: map characters to faces by order
        for i, char_name in enumerate(character_names):
            if i < len(image_analysis['characters']):
                mapping[char_name] = i
        
        return mapping

def analyze_and_position_smart(image: Image.Image, dialogues: List, character_names: List[str] = None) -> List:
    """
    Main function to analyze image and return dialogues with smart positioning.
    Prevents bubble overlapping by tracking placement positions.
    """
    positioner = SmartTextPositioner()
    
    # Reset placement tracking for this panel
    positioner.reset_placement_tracking()
    
    # Analyze the image
    analysis = positioner.analyze_image(image)
    
    # Create character mapping
    char_names = character_names or []
    char_mapping = positioner.create_character_mapping(char_names, analysis)
    
    # Update dialogue positions with collision detection
    positioned_dialogues = []
    
    for dialogue in dialogues:
        # Estimate bubble size based on text length (rough approximation)
        text_length = len(getattr(dialogue, 'text', ''))
        estimated_width = min(max(text_length * 12, 300), 500)  # 12px per char, min 300, max 500
        estimated_height = max(120, text_length // 40 * 30 + 120)  # Height based on text wrapping
        bubble_size = (estimated_width, estimated_height)
        
        # Get optimal position with collision detection
        x, y, speaker_pos = positioner.get_optimal_position(
            getattr(dialogue, 'speaker', ''),
            getattr(dialogue, 'type', 'speech'),
            analysis,
            char_mapping,
            bubble_size
        )
        
        # Create new dialogue with smart positioning
        if hasattr(dialogue, '__dict__'):
            # Copy existing dialogue and update position
            new_dialogue = type(dialogue)(**dialogue.__dict__)
            new_dialogue.position = speaker_pos
            # Store coordinates for advanced positioning
            if hasattr(new_dialogue, 'x_coord'):
                new_dialogue.x_coord = x
                new_dialogue.y_coord = y
        else:
            new_dialogue = dialogue
        
        positioned_dialogues.append(new_dialogue)
    
    print(f"🎯 Smart positioning: Placed {len(positioned_dialogues)} bubbles, {len(positioner.placed_bubbles)} tracked positions")
    
    return positioned_dialogues, analysis

from PIL import Image
from typing import List, Tuple, Dict, Optional

class SimpleTextPositioner:
    """
    Lightweight text positioning system that prevents bubble overlaps
    without requiring computer vision libraries.
    """
    
    def __init__(self):
        self.placed_bubbles = []  # Track already placed bubbles to prevent overlaps
    
    def get_standard_positions(self, image_width: int, image_height: int) -> List[Dict]:
        """Define smart comic bubble zones that avoid common character placement areas"""
        margin = max(20, int(min(image_width, image_height) * 0.03))  # Adaptive margin
        
        # ADAPTIVE positioning based on panel aspect ratio for narrative layout
        aspect_ratio = image_width / image_height
        
        # Calculate zone dimensions that avoid character faces (typically in center)
        if aspect_ratio > 2.0:  # Very wide panels (like Panel 4: 1536x640)
            # For wide panels, use horizontal strips
            zone_w = (image_width - 4*margin) // 4  # More horizontal divisions
            zone_h = (image_height - 3*margin) // 2   # Fewer vertical divisions
        elif aspect_ratio < 0.6:  # Very tall panels (like Panel 1: 640x1536)  
            # For tall panels, use vertical strips
            zone_w = (image_width - 3*margin) // 2   # Fewer horizontal divisions
            zone_h = (image_height - 5*margin) // 4  # More vertical divisions
        else:  # Normal aspect ratios (squares and slight rectangles)
            zone_w = (image_width - 4*margin) // 3
            zone_h = (image_height - 4*margin) // 3 
        
        # Minimum zone dimensions
        zone_h = max(zone_h, 80)
        zone_w = max(zone_w, 120)
        
        # Define zones based on aspect ratio - AVOID CENTER where characters usually are
        zones = []
        
        if aspect_ratio > 2.0:  # Very wide panels (Panel 4: 1536x640)
            # For wide panels, focus on horizontal positioning
            zones = [
                {'name': 'wide_left', 'bbox': (margin, margin, zone_w, zone_h), 'priority': 0.95},
                {'name': 'wide_left_center', 'bbox': (margin + zone_w, margin, zone_w, zone_h), 'priority': 0.85},
                {'name': 'wide_right_center', 'bbox': (margin + 2*zone_w, margin, zone_w, zone_h), 'priority': 0.85},
                {'name': 'wide_right', 'bbox': (margin + 3*zone_w, margin, zone_w, zone_h), 'priority': 0.95},
                {'name': 'wide_bottom_left', 'bbox': (margin, margin + zone_h, zone_w, zone_h), 'priority': 0.9},
                {'name': 'wide_bottom_right', 'bbox': (margin + 3*zone_w, margin + zone_h, zone_w, zone_h), 'priority': 0.9},
            ]
        elif aspect_ratio < 0.6:  # Very tall panels (Panel 1: 640x1536)
            # For tall panels, focus on vertical positioning  
            zones = [
                {'name': 'tall_top_left', 'bbox': (margin, margin, zone_w, zone_h), 'priority': 0.95},
                {'name': 'tall_top_right', 'bbox': (margin + zone_w, margin, zone_w, zone_h), 'priority': 0.95},
                {'name': 'tall_upper_left', 'bbox': (margin, margin + zone_h, zone_w, zone_h), 'priority': 0.9},
                {'name': 'tall_upper_right', 'bbox': (margin + zone_w, margin + zone_h, zone_w, zone_h), 'priority': 0.9},
                {'name': 'tall_lower_left', 'bbox': (margin, margin + 2*zone_h, zone_w, zone_h), 'priority': 0.85},
                {'name': 'tall_lower_right', 'bbox': (margin + zone_w, margin + 2*zone_h, zone_w, zone_h), 'priority': 0.85},
                {'name': 'tall_bottom_left', 'bbox': (margin, margin + 3*zone_h, zone_w, zone_h), 'priority': 0.9},
                {'name': 'tall_bottom_right', 'bbox': (margin + zone_w, margin + 3*zone_h, zone_w, zone_h), 'priority': 0.9},
            ]
        else:  # Normal aspect ratios (squares and slight rectangles)
            # Standard 3x3 grid for normal panels
            zones = [
                # Top row - GOOD for narration and off-screen dialogue
                {'name': 'top_left', 'bbox': (margin, margin, zone_w, zone_h), 'priority': 0.95},
                {'name': 'top_center', 'bbox': (margin + zone_w, margin, zone_w, zone_h), 'priority': 0.75},  # Lower priority - might cover characters
                {'name': 'top_right', 'bbox': (margin + 2*zone_w, margin, zone_w, zone_h), 'priority': 0.95},
                
                # Middle row - CENTER has LOW priority (character faces often here)
                {'name': 'mid_left', 'bbox': (margin, margin + zone_h, zone_w, zone_h), 'priority': 0.85},
                {'name': 'mid_center', 'bbox': (margin + zone_w, margin + zone_h, zone_w, zone_h), 'priority': 0.2},  # VERY LOW - character area
                {'name': 'mid_right', 'bbox': (margin + 2*zone_w, margin + zone_h, zone_w, zone_h), 'priority': 0.85},
                
                # Bottom row - GOOD for speech from characters
                {'name': 'bottom_left', 'bbox': (margin, margin + 2*zone_h, zone_w, zone_h), 'priority': 0.9},
                {'name': 'bottom_center', 'bbox': (margin + zone_w, margin + 2*zone_h, zone_w, zone_h), 'priority': 0.9},
                {'name': 'bottom_right', 'bbox': (margin + 2*zone_w, margin + 2*zone_h, zone_w, zone_h), 'priority': 0.9},
            ]
        
        # Add universal edge zones for all aspect ratios (useful for overflow)
        zones.extend([
            {'name': 'edge_top', 'bbox': (margin, margin//2, image_width - 2*margin, margin), 'priority': 0.8},
            {'name': 'edge_left', 'bbox': (margin//2, margin, margin, image_height - 2*margin), 'priority': 0.8},
            {'name': 'edge_right', 'bbox': (image_width - margin*1.5, margin, margin, image_height - 2*margin), 'priority': 0.8},
            {'name': 'edge_bottom', 'bbox': (margin, image_height - margin*1.5, image_width - 2*margin, margin), 'priority': 0.8},
        ])
        
        return zones
    
    def zones_overlap(self, zone1: Tuple[int, int, int, int], zone2: Tuple[int, int, int, int]) -> bool:
        """Check if two rectangular zones overlap with GENEROUS safety margin."""
        x1, y1, w1, h1 = zone1
        x2, y2, w2, h2 = zone2
        
        # Much more generous safety margin to prevent any visual conflicts
        horizontal_margin = max(40, int((w1 + w2) * 0.1))  # 10% of combined width or 40px minimum
        vertical_margin = max(30, int((h1 + h2) * 0.1))    # 10% of combined height or 30px minimum
        
        return not (x1 + w1 + horizontal_margin < x2 or 
                   x2 + w2 + horizontal_margin < x1 or 
                   y1 + h1 + vertical_margin < y2 or 
                   y2 + h2 + vertical_margin < y1)
    
    def find_collision_free_position(self, preferred_zone: Dict, bubble_size: Tuple[int, int], 
                                    image_width: int, image_height: int) -> Tuple[int, int]:
        """Find a collision-free position within the preferred zone with multiple fallback attempts."""
        bubble_width, bubble_height = bubble_size
        zone_x, zone_y, zone_w, zone_h = preferred_zone['bbox']
        
        # Try many more positions with better spacing
        attempts = [
            # Original zone position
            (zone_x, zone_y),
            # Multiple positions within the zone
            (zone_x + 10, zone_y + 10),
            (zone_x + zone_w//4, zone_y + zone_h//4),
            (zone_x + zone_w//2, zone_y + zone_h//2),
            (zone_x + zone_w*3//4, zone_y + zone_h*3//4),
            # Edge positions within zone
            (zone_x, zone_y + zone_h//2),
            (zone_x + zone_w//2, zone_y),
            (zone_x + zone_w//2, zone_y + zone_h//2),
            # Further offsets to avoid collisions
            (zone_x + 50, zone_y),
            (zone_x, zone_y + 50),
            (zone_x + 50, zone_y + 50),
            (zone_x - 30, zone_y - 30),
            (zone_x + 80, zone_y + 20),
            (zone_x + 20, zone_y + 80),
            # Corner alternatives
            (zone_x + zone_w - bubble_width, zone_y),
            (zone_x, zone_y + zone_h - bubble_height),
            (zone_x + zone_w - bubble_width, zone_y + zone_h - bubble_height),
        ]
        
        for x, y in attempts:
            # Ensure position is within image bounds with adequate margins
            x = max(15, min(x, image_width - bubble_width - 15))
            y = max(15, min(y, image_height - bubble_height - 15))
            
            test_zone = (x, y, bubble_width, bubble_height)
            
            # Check for collision with all existing bubbles
            has_collision = False
            for placed_bubble in self.placed_bubbles:
                if self.zones_overlap(test_zone, placed_bubble):
                    has_collision = True
                    break
            
            if not has_collision:
                # Found a good position!
                return (x, y)
        
        # If all positions in preferred zone failed, try alternative zones
        print(f"⚠️ Could not find collision-free position in preferred zone, trying alternatives...")
        
        # Use emergency fallback positions with guaranteed spacing
        emergency_positions = [
            (20, 20),  # Top-left corner
            (image_width - bubble_width - 20, 20),  # Top-right corner  
            (20, image_height - bubble_height - 20),  # Bottom-left corner
            (image_width - bubble_width - 20, image_height - bubble_height - 20),  # Bottom-right corner
            (image_width//2 - bubble_width//2, 20),  # Top-center
            (image_width//2 - bubble_width//2, image_height - bubble_height - 20),  # Bottom-center
            (20, image_height//2 - bubble_height//2),  # Mid-left
            (image_width - bubble_width - 20, image_height//2 - bubble_height//2),  # Mid-right
        ]
        
        for x, y in emergency_positions:
            test_zone = (x, y, bubble_width, bubble_height)
            has_collision = False
            for placed_bubble in self.placed_bubbles:
                if self.zones_overlap(test_zone, placed_bubble):
                    has_collision = True
                    break
            
            if not has_collision:
                print(f"✅ Found emergency position at ({x}, {y})")
                return (x, y)
        
        # Final fallback - place with minimal overlap
        final_x = max(20, min(zone_x, image_width - bubble_width - 20))
        final_y = max(20, min(zone_y, image_height - bubble_height - 20))
        print(f"⚠️ Using final fallback position ({final_x}, {final_y}) - may have minimal overlap")
        return (final_x, final_y)
    
    def get_optimal_position(self, dialogue_type: str, bubble_size: Tuple[int, int], 
                           image_width: int, image_height: int) -> Tuple[int, int, str]:
        """Get optimal position for a dialogue bubble."""
        zones = self.get_standard_positions(image_width, image_height)
        
        # Sort zones by priority for different dialogue types
        if dialogue_type == "narration":
            # Prefer top and bottom zones for narration
            priority_order = ['top_center', 'bottom_center', 'top_left', 'top_right', 
                            'bottom_left', 'bottom_right', 'mid_left', 'mid_right', 'mid_center']
        elif dialogue_type in ["speech", "thought"]:
            # Prefer side and corner zones for speech
            priority_order = ['top_left', 'top_right', 'bottom_left', 'bottom_right',
                            'mid_left', 'mid_right', 'top_center', 'bottom_center', 'mid_center']
        elif dialogue_type == "sound_effect":
            # Sound effects can go anywhere, prefer center and dramatic positions
            priority_order = ['mid_center', 'top_center', 'bottom_center', 'top_left', 
                            'top_right', 'bottom_left', 'bottom_right', 'mid_left', 'mid_right']
        else:
            # Default order
            priority_order = ['top_left', 'top_right', 'bottom_left', 'bottom_right', 
                            'top_center', 'bottom_center', 'mid_left', 'mid_right', 'mid_center']
        
        # Find the best available zone
        zones_dict = {zone['name']: zone for zone in zones}
        
        for zone_name in priority_order:
            if zone_name in zones_dict:
                zone = zones_dict[zone_name]
                x, y = self.find_collision_free_position(zone, bubble_size, image_width, image_height)
                
                # Determine speaker position based on zone
                if 'left' in zone_name:
                    speaker_pos = 'left'
                elif 'right' in zone_name:
                    speaker_pos = 'right'
                elif 'top' in zone_name:
                    speaker_pos = 'top'
                elif 'bottom' in zone_name:
                    speaker_pos = 'bottom'
                else:
                    speaker_pos = 'center'
                
                return (x, y, speaker_pos)
        
        # Fallback
        return (50, 50, 'center')
    
    def reset_placement_tracking(self):
        """Reset the tracking of placed bubbles (call this for each new panel)."""
        self.placed_bubbles = []


def simple_position_dialogues(image: Image.Image, dialogues: List, character_names: List[str] = None) -> List:
    """
    Simple positioning function that works without computer vision libraries.
    """
    positioner = SimpleTextPositioner()
    positioner.reset_placement_tracking()
    
    image_width, image_height = image.size
    positioned_dialogues = []
    
    for i, dialogue in enumerate(dialogues):
        try:
            # Estimate bubble size based on text length with proper scaling for frame size
            text_length = len(getattr(dialogue, 'text', ''))
            
            # Scale bubble size relative to frame size - more conservative
            base_width_factor = min(image_width / 800, 1.2)  # Allow slight scaling up for larger frames
            base_height_factor = min(image_height / 600, 1.2)
            
            # Calculate bubble dimensions as percentage of frame size - narrower and taller
            min_bubble_width = int(image_width * 0.15)   # Reduce minimum width to 15%
            max_bubble_width = int(image_width * 0.35)   # Reduce maximum width to 35%  
            min_bubble_height = int(image_height * 0.2)  # Increase minimum height to 20%
            max_bubble_height = int(image_height * 0.4)  # Increase maximum height to 40%
            
            # Estimate based on text length - favor taller, narrower bubbles
            chars_per_line = max(15, int(max_bubble_width / 15))  # Fewer chars per line (15px per char)
            estimated_lines = max(2, (text_length // chars_per_line) + 1)  # Encourage more lines
            
            estimated_width = max(min_bubble_width, min(text_length * 6, max_bubble_width))  # Reduce width multiplier
            estimated_height = max(min_bubble_height, min(estimated_lines * 30 + 50, max_bubble_height))  # Increase height
            
            bubble_size = (estimated_width, estimated_height)
            
            print(f"📏 Bubble {i}: text_len={text_length}, size={bubble_size}, frame={image_width}x{image_height}")
            
            # Calculate optimal position
            x, y, speaker_pos = positioner.get_optimal_position(
                getattr(dialogue, 'type', 'speech'),
                bubble_size,
                image_width,
                image_height
            )
            
            # IMPORTANT: Track this bubble position to prevent future overlaps
            bubble_rect = (x, y, bubble_size[0], bubble_size[1])
            positioner.placed_bubbles.append(bubble_rect)
            print(f"📍 Tracked bubble position: ({x}, {y}) size: {bubble_size}")
            
            # Create new dialogue with positioning - FORCE coordinate setting
            if hasattr(dialogue, '__dict__'):
                new_dialogue = type(dialogue)(**dialogue.__dict__)
                new_dialogue.position = speaker_pos
                # ALWAYS set coordinates, create attributes if they don't exist
                new_dialogue.x_coord = x
                new_dialogue.y_coord = y
                print(f"🎯 Set coordinates for '{getattr(new_dialogue, 'text', 'unknown')[:30]}...': ({x}, {y})")
            else:
                # For non-object dialogues, try to add attributes
                new_dialogue = dialogue
                try:
                    new_dialogue.x_coord = x
                    new_dialogue.y_coord = y
                    new_dialogue.position = speaker_pos
                    print(f"🎯 Set coordinates for dialogue: ({x}, {y})")
                except AttributeError:
                    print(f"⚠️ Could not set coordinates on dialogue object")
                    pass
            
            positioned_dialogues.append(new_dialogue)
            
        except Exception as e:
            print(f"❌ Error positioning bubble {i}: {e}")
            # Add original dialogue if positioning fails
            positioned_dialogues.append(dialogue)
    
    print(f"🔧 Manual collision avoidance: {len(positioned_dialogues)} bubbles positioned")
    
    return positioned_dialogues, {'simple_positioning': True, 'width': image_width, 'height': image_height} 
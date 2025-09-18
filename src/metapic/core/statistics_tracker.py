#!/usr/bin/env python3
"""
Enhanced Statistics Tracker for MetaPic
Integrates advanced statistics from H:\\Metapic with modern architecture
"""

from __future__ import annotations
import json
import os
import re
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict, Counter
from pathlib import Path
import time

from ..models import ImageMeta

class StatisticsTracker:
    """Track comprehensive statistics about models, tags, and processed images"""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.stats_file = self.data_dir / 'metapic_statistics.json'
        self.model_mapping_file = self.data_dir / 'model_name_mappings.json'
        
        self.stats = self.load_statistics()
        self.model_name_mappings = self.load_model_mappings()
        
    def load_statistics(self) -> Dict[str, Any]:
        """Load statistics from file with proper type conversion"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    loaded_stats = json.load(f)
                
                # Convert loaded data back to proper types
                stats = {
                    'processed_images': set(loaded_stats.get('processed_images', [])),
                    'models': Counter(loaded_stats.get('models', {})),
                    'positive_tags': Counter(loaded_stats.get('positive_tags', {})),
                    'negative_tags': Counter(loaded_stats.get('negative_tags', {})),
                    'total_images_processed': loaded_stats.get('total_images_processed', 0),
                    'last_update': loaded_stats.get('last_update'),
                    'file_formats': Counter(loaded_stats.get('file_formats', {})),
                    'dimensions': Counter(loaded_stats.get('dimensions', {})),
                    'samplers': Counter(loaded_stats.get('samplers', {})),
                    'cfg_ranges': Counter(loaded_stats.get('cfg_ranges', {})),
                    'step_ranges': Counter(loaded_stats.get('step_ranges', {}))
                }
                return stats
            except Exception as e:
                print(f"Error loading statistics: {e}")
        
        # Default empty statistics
        return {
            'processed_images': set(),
            'models': Counter(),
            'positive_tags': Counter(),
            'negative_tags': Counter(),
            'total_images_processed': 0,
            'last_update': None,
            'file_formats': Counter(),
            'dimensions': Counter(),
            'samplers': Counter(),
            'cfg_ranges': Counter(),
            'step_ranges': Counter()
        }
    
    def save_statistics(self):
        """Save statistics to file with proper serialization"""
        try:
            # Convert sets and Counters to JSON-serializable format
            serializable_stats = {
                'processed_images': list(self.stats['processed_images']),
                'models': dict(self.stats['models']),
                'positive_tags': dict(self.stats['positive_tags']),
                'negative_tags': dict(self.stats['negative_tags']),
                'total_images_processed': self.stats['total_images_processed'],
                'last_update': time.strftime('%Y-%m-%d %H:%M:%S'),
                'file_formats': dict(self.stats['file_formats']),
                'dimensions': dict(self.stats['dimensions']),
                'samplers': dict(self.stats['samplers']),
                'cfg_ranges': dict(self.stats['cfg_ranges']),
                'step_ranges': dict(self.stats['step_ranges'])
            }
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving statistics: {e}")
    
    def load_model_mappings(self) -> Dict[str, str]:
        """Load model name mappings for normalization"""
        if self.model_mapping_file.exists():
            try:
                with open(self.model_mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading model mappings: {e}")
        return {}
    
    def save_model_mappings(self):
        """Save model name mappings"""
        try:
            with open(self.model_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_name_mappings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving model mappings: {e}")
    
    def normalize_model_name(self, model_name: str) -> str:
        """Normalize model name using mappings"""
        if not model_name:
            return ""
        
        # Check if we have a mapping for this model
        normalized = self.model_name_mappings.get(model_name, model_name)
        
        # If no mapping exists, try to create one
        if normalized == model_name:
            # Look for similar models
            for existing_model in self.model_name_mappings.keys():
                if self._models_similar(model_name, existing_model):
                    normalized = self.model_name_mappings[existing_model]
                    self.model_name_mappings[model_name] = normalized
                    break
        
        return normalized
    
    def _models_similar(self, model1: str, model2: str) -> bool:
        """Check if two model names are similar enough to be the same model"""
        # Simple similarity check - can be enhanced
        model1_clean = re.sub(r'[^a-zA-Z0-9]', '', model1.lower())
        model2_clean = re.sub(r'[^a-zA-Z0-9]', '', model2.lower())
        
        # Check if one contains the other
        return model1_clean in model2_clean or model2_clean in model1_clean
    
    def add_image_metadata(self, meta: ImageMeta):
        """Add image metadata to statistics"""
        # Create unique identifier for the image
        image_id = f"{meta.path}:{meta.size_bytes}:{meta.seed}"
        
        # Skip if already processed
        if image_id in self.stats['processed_images']:
            return
        
        # Add to processed images
        self.stats['processed_images'].add(image_id)
        self.stats['total_images_processed'] += 1
        
        # Track models
        if meta.model:
            normalized_model = self.normalize_model_name(meta.model)
            self.stats['models'][normalized_model] += 1
        
        # Track file formats
        if meta.format:
            self.stats['file_formats'][meta.format] += 1
        
        # Track dimensions
        if meta.width and meta.height:
            dimension_str = f"{meta.width}x{meta.height}"
            self.stats['dimensions'][dimension_str] += 1
        
        # Track samplers
        if meta.sampler:
            self.stats['samplers'][meta.sampler] += 1
        
        # Track CFG ranges
        if meta.cfg is not None:
            cfg_range = self._get_cfg_range(meta.cfg)
            self.stats['cfg_ranges'][cfg_range] += 1
        
        # Track step ranges
        if meta.steps is not None:
            step_range = self._get_step_range(meta.steps)
            self.stats['step_ranges'][step_range] += 1
        
        # Extract and track tags
        self._extract_and_track_tags(meta)
    
    def _get_cfg_range(self, cfg: float) -> str:
        """Get CFG range category"""
        if cfg < 5:
            return "1-5"
        elif cfg < 7:
            return "5-7"
        elif cfg < 10:
            return "7-10"
        elif cfg < 15:
            return "10-15"
        else:
            return "15+"
    
    def _get_step_range(self, steps: int) -> str:
        """Get step range category"""
        if steps < 10:
            return "1-10"
        elif steps < 20:
            return "10-20"
        elif steps < 30:
            return "20-30"
        elif steps < 50:
            return "30-50"
        else:
            return "50+"
    
    def _extract_and_track_tags(self, meta: ImageMeta):
        """Extract tags from prompts and track them"""
        # Extract positive tags
        if meta.prompt:
            tags = self._extract_tags_from_text(meta.prompt)
            for tag in tags:
                self.stats['positive_tags'][tag] += 1
        
        # Extract negative tags
        if meta.negative_prompt:
            tags = self._extract_tags_from_text(meta.negative_prompt)
            for tag in tags:
                self.stats['negative_tags'][tag] += 1
    
    def _extract_tags_from_text(self, text: str) -> List[str]:
        """Extract individual tags from prompt text"""
        if not text:
            return []
        
        # Split by common separators and clean up
        tags = []
        for separator in [',', ';', '\n', '|']:
            if separator in text:
                parts = text.split(separator)
                for part in parts:
                    tag = part.strip().strip('()[]{}')
                    if tag and len(tag) > 1:
                        tags.append(tag)
                break
        
        # If no separators found, treat as single tag
        if not tags:
            tag = text.strip()
            if tag and len(tag) > 1:
                tags.append(tag)
        
        return tags
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get a summary of current statistics"""
        return {
            'total_images': self.stats['total_images_processed'],
            'unique_models': len(self.stats['models']),
            'unique_positive_tags': len(self.stats['positive_tags']),
            'unique_negative_tags': len(self.stats['negative_tags']),
            'unique_dimensions': len(self.stats['dimensions']),
            'unique_samplers': len(self.stats['samplers']),
            'top_models': self.stats['models'].most_common(10),
            'top_positive_tags': self.stats['positive_tags'].most_common(20),
            'top_negative_tags': self.stats['negative_tags'].most_common(20),
            'file_format_distribution': dict(self.stats['file_formats']),
            'dimension_distribution': dict(self.stats['dimensions']),
            'sampler_distribution': dict(self.stats['samplers']),
            'cfg_distribution': dict(self.stats['cfg_ranges']),
            'step_distribution': dict(self.stats['step_ranges'])
        }
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get detailed model statistics"""
        models = self.stats['models']
        return {
            'total_unique_models': len(models),
            'most_used_models': models.most_common(20),
            'model_frequency': dict(models),
            'model_mappings': self.model_name_mappings.copy()
        }
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get detailed tag statistics"""
        positive_tags = self.stats['positive_tags']
        negative_tags = self.stats['negative_tags']
        
        return {
            'positive_tags': {
                'total_unique': len(positive_tags),
                'most_common': positive_tags.most_common(50),
                'frequency': dict(positive_tags)
            },
            'negative_tags': {
                'total_unique': len(negative_tags),
                'most_common': negative_tags.most_common(50),
                'frequency': dict(negative_tags)
            },
            'combined_tags': {
                'total_unique': len(positive_tags) + len(negative_tags),
                'most_common': (positive_tags + negative_tags).most_common(50)
            }
        }
    
    def consolidate_tags(self, tag_mappings: Dict[str, str]):
        """Consolidate tags using provided mappings"""
        # Consolidate positive tags
        consolidated_positive = Counter()
        for tag, count in self.stats['positive_tags'].items():
            consolidated_tag = tag_mappings.get(tag, tag)
            consolidated_positive[consolidated_tag] += count
        
        # Consolidate negative tags
        consolidated_negative = Counter()
        for tag, count in self.stats['negative_tags'].items():
            consolidated_tag = tag_mappings.get(tag, tag)
            consolidated_negative[consolidated_tag] += count
        
        # Update statistics
        self.stats['positive_tags'] = consolidated_positive
        self.stats['negative_tags'] = consolidated_negative
        
        # Save updated statistics
        self.save_statistics()
    
    def clear_statistics(self):
        """Clear all statistics"""
        self.stats = {
            'processed_images': set(),
            'models': Counter(),
            'positive_tags': Counter(),
            'negative_tags': Counter(),
            'total_images_processed': 0,
            'last_update': None,
            'file_formats': Counter(),
            'dimensions': Counter(),
            'samplers': Counter(),
            'cfg_ranges': Counter(),
            'step_ranges': Counter()
        }
        self.save_statistics()
    
    def export_statistics(self, file_path: str, format: str = 'json'):
        """Export statistics to file"""
        if format.lower() == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.get_statistics_summary(), f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Global statistics tracker instance
stats_tracker = StatisticsTracker()

import json
import os
import re
from typing import Dict, List, Set
from collections import defaultdict, Counter
from PyQt5.QtCore import QSettings

class StatisticsTracker:
    """Track statistics about models, tags, and processed images"""
    
    def __init__(self):
        self.settings = QSettings('MetaPicPick', 'Statistics')
        self.stats_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'metapicpick_statistics.json')
        self.model_mapping_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'model_name_mappings.json')
        self.stats = self.load_statistics()
        self.model_name_mappings = self.load_model_mappings()
        
    def load_statistics(self) -> Dict:
        """Load statistics from file"""
        if os.path.exists(self.stats_file):
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
                    'last_update': loaded_stats.get('last_update')
                }
                return stats
            except Exception as e:
                print(f"Error loading statistics: {e}")
        
        # Default empty statistics
        return {
            'processed_images': set(),  # Set of processed image paths/hashes
            'models': Counter(),        # Model name -> count
            'positive_tags': Counter(), # Tag -> count from positive prompts
            'negative_tags': Counter(), # Tag -> count from negative prompts
            'total_images_processed': 0,
            'last_update': None
        }
    
    def save_statistics(self):
        """Save statistics to file"""
        try:
            # Convert set to list for JSON serialization
            stats_to_save = self.stats.copy()
            stats_to_save['processed_images'] = list(self.stats['processed_images'])
            stats_to_save['models'] = dict(self.stats['models'])
            stats_to_save['positive_tags'] = dict(self.stats['positive_tags'])
            stats_to_save['negative_tags'] = dict(self.stats['negative_tags'])
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving statistics: {e}")
    
    def get_image_identifier(self, image_path: str, metadata: Dict) -> str:
        """Get unique identifier for an image to prevent double counting"""
        # Use combination of file path, size, and key metadata for identification
        try:
            file_stat = os.stat(image_path)
            file_size = file_stat.st_size
            file_mtime = int(file_stat.st_mtime)
            
            # Include key metadata that would make images unique
            seed = metadata.get('seed', '')
            model_hash = metadata.get('model_hash', '')
            
            identifier = f"{image_path}|{file_size}|{file_mtime}|{seed}|{model_hash}"
            return identifier
        except Exception:
            # Fallback to just file path if stat fails
            return image_path
    
    def normalize_tag(self, tag: str) -> str:
        """Normalize a tag to handle common variations"""
        if not tag:
            return tag
            
        # Convert to lowercase and clean spaces
        normalized = ' '.join(tag.lower().split())
        
        # Handle common variations
        tag_mappings = {
            # Number + girl/boy variations
            '1 girl': '1girl',
            '2 girls': '2girls', 
            '3 girls': '3girls',
            '4 girls': '4girls',
            '5 girls': '5girls',
            'multiple girls': 'multiple_girls',
            '1 boy': '1boy',
            '2 boys': '2boys',
            'multiple boys': 'multiple_boys',
            
            # Common tag variations
            'large breast': 'large_breasts',
            'large breasts': 'large_breasts',
            'big breast': 'large_breasts',
            'big breasts': 'large_breasts',
            'medium breast': 'medium_breasts',
            'medium breasts': 'medium_breasts',
            'small breast': 'small_breasts',
            'small breasts': 'small_breasts',
            
            # Quality variations
            'high quality': 'high_quality',
            'best quality': 'best_quality',
            'worst quality': 'worst_quality',
            'low quality': 'low_quality',
            'normal quality': 'normal_quality',
            
            # Hair variations
            'long hair': 'long_hair',
            'short hair': 'short_hair',
            'blue hair': 'blue_hair',
            'blonde hair': 'blonde_hair',
            'brown hair': 'brown_hair',
            'black hair': 'black_hair',
            'red hair': 'red_hair',
            'white hair': 'white_hair',
            
            # Eye variations
            'blue eyes': 'blue_eyes',
            'brown eyes': 'brown_eyes',
            'green eyes': 'green_eyes',
            'red eyes': 'red_eyes',
            'yellow eyes': 'yellow_eyes',
            
            # Common underscored tags
            'looking at viewer': 'looking_at_viewer',
            'from behind': 'from_behind',
            'very long hair': 'very_long_hair',
            'perfect face': 'perfect_face',
            'detailed face': 'detailed_face',
            'detailed eyes': 'detailed_eyes',
            'bad anatomy': 'bad_anatomy',
            'bad hands': 'bad_hands',
            'missing limb': 'missing_limb',
            'extra limb': 'extra_limb',
            'floating limbs': 'floating_limbs',
            
            # Remove common pluralization inconsistencies
            'hand': 'hands',  # Usually want plural
            'finger': 'fingers',
            'limb': 'limbs',
        }
        
        # Apply mappings
        if normalized in tag_mappings:
            return tag_mappings[normalized]
            
        # Handle underscore variations (prefer underscored versions)
        if ' ' in normalized:
            underscored = normalized.replace(' ', '_')
            # Check if underscored version is more common pattern
            if any(pattern in underscored for pattern in ['_hair', '_eyes', '_breasts', '_quality', '_girl']):
                return underscored
        
        return normalized
    
    def extract_tags_from_prompt(self, prompt: str) -> Set[str]:
        """Extract tags/keywords from a prompt string with enhanced normalization"""
        if not prompt:
            return set()
        
        # Remove LoRA syntax: <lora:name:weight>
        prompt = re.sub(r'<lora:[^>]+>', '', prompt)
        
        # Remove weight syntax: (tag:weight) or (tag)
        prompt = re.sub(r'\([^)]*:\d*\.?\d*\)', lambda m: m.group(0).split(':')[0][1:], prompt)
        prompt = re.sub(r'\(([^)]*)\)', r'\1', prompt)
        
        # Remove brackets and other syntax
        prompt = re.sub(r'[<>\[\]{}]', '', prompt)
        
        # Split by common delimiters
        tags = re.split(r'[,\n]+', prompt)
        
        # Clean and filter tags
        clean_tags = set()
        for tag in tags:
            tag = tag.strip()
            if tag:
                # Remove common connecting words and very short tags
                if len(tag) >= 3 and tag.lower() not in {
                    'and', 'the', 'with', 'for', 'from', 'are', 'was', 'were', 'been',
                    'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may',
                    'might', 'can', 'must', 'very', 'too', 'also', 'just', 'only'
                }:
                    # Normalize tag with enhanced consolidation
                    normalized_tag = self.normalize_tag(tag)
                    clean_tags.add(normalized_tag)
        
        return clean_tags
    
    def normalize_model_name(self, model_path_or_name: str) -> str:
        """Extract and normalize model name from full path or raw name"""
        if not model_path_or_name:
            return "Unknown Model"
        
        # Check if we have a custom mapping first
        if model_path_or_name in self.model_name_mappings:
            return self.model_name_mappings[model_path_or_name]
        
        # Extract filename from path
        model_name = os.path.basename(model_path_or_name)
        
        # Remove common file extensions
        extensions_to_remove = ['.safetensors', '.ckpt', '.pt', '.pth', '.bin']
        for ext in extensions_to_remove:
            if model_name.lower().endswith(ext):
                model_name = model_name[:-len(ext)]
                break
        
        # Remove common prefixes/suffixes that add noise
        prefixes_to_remove = ['checkpoint_', 'model_', 'final_']
        suffixes_to_remove = ['_final', '_checkpoint', '_model', '_v1', '_v2', '_v3', '_epoch']
        
        for prefix in prefixes_to_remove:
            if model_name.lower().startswith(prefix):
                model_name = model_name[len(prefix):]
                break
        
        for suffix in suffixes_to_remove:
            if model_name.lower().endswith(suffix):
                model_name = model_name[:-len(suffix)]
                break
        
        # Clean up underscores and spaces
        model_name = model_name.replace('_', ' ').strip()
        model_name = ' '.join(model_name.split())  # Remove extra spaces
        
        return model_name if model_name else "Unknown Model"
    
    def load_model_mappings(self) -> Dict[str, str]:
        """Load custom model name mappings from file"""
        if os.path.exists(self.model_mapping_file):
            try:
                with open(self.model_mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading model mappings: {e}")
        return {}
    
    def save_model_mappings(self):
        """Save custom model name mappings to file"""
        try:
            os.makedirs(os.path.dirname(self.model_mapping_file), exist_ok=True)
            with open(self.model_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_name_mappings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving model mappings: {e}")
    
    def set_model_name_mapping(self, original_name: str, custom_name: str):
        """Set a custom mapping for a model name"""
        self.model_name_mappings[original_name] = custom_name
        self.save_model_mappings()
    
    def remove_model_name_mapping(self, original_name: str):
        """Remove a custom mapping for a model name"""
        if original_name in self.model_name_mappings:
            del self.model_name_mappings[original_name]
            self.save_model_mappings()
    
    def get_all_model_mappings(self) -> Dict[str, str]:
        """Get all model name mappings"""
        return self.model_name_mappings.copy()
    
    def consolidate_model_names(self):
        """Apply normalization to all existing model names in statistics"""
        print("Consolidating model names...")
        
        new_models = Counter()
        consolidation_log = []
        
        for original_model, count in self.stats['models'].items():
            normalized_model = self.normalize_model_name(original_model)
            new_models[normalized_model] += count
            
            if original_model != normalized_model:
                consolidation_log.append(f"{original_model} -> {normalized_model}")
        
        models_before = len(self.stats['models'])
        self.stats['models'] = new_models
        models_after = len(self.stats['models'])
        
        print(f"Model names: {models_before} -> {models_after} (reduced by {models_before - models_after})")
        if consolidation_log:
            print("Model name changes:")
            for change in consolidation_log[:10]:  # Show first 10 changes
                print(f"  {change}")
            if len(consolidation_log) > 10:
                print(f"  ... and {len(consolidation_log) - 10} more")
        
        # Save updated statistics
        import datetime
        self.stats['last_update'] = datetime.datetime.now().isoformat()
        self.save_statistics()
        
        return {
            'models_before': models_before,
            'models_after': models_after,
            'changes_made': len(consolidation_log)
        }
    
    def process_image_metadata(self, image_path: str, metadata: Dict) -> bool:
        """Process metadata from an image and update statistics. Returns True if processed, False if already seen."""
        
        # Check if we've already processed this image
        image_id = self.get_image_identifier(image_path, metadata)
        if image_id in self.stats['processed_images']:
            return False  # Already processed
        
        # Mark as processed
        self.stats['processed_images'].add(image_id)
        self.stats['total_images_processed'] += 1
        
        # Extract and count model
        model_name = metadata.get('model_name')
        if model_name and model_name.strip():
            # Clean model name (remove hash references)
            clean_model = model_name.strip()
            if clean_model.lower().startswith('hash:'):
                # Try to get actual model name if it's just a hash reference
                clean_model = metadata.get('model_hash', clean_model)
            
            # Normalize the model name
            normalized_model = self.normalize_model_name(clean_model)
            self.stats['models'][normalized_model] += 1
        
        # Extract and count positive prompt tags
        positive_prompt = metadata.get('positive_prompt', '')
        if positive_prompt:
            positive_tags = self.extract_tags_from_prompt(positive_prompt)
            for tag in positive_tags:
                self.stats['positive_tags'][tag] += 1
        
        # Extract and count negative prompt tags
        negative_prompt = metadata.get('negative_prompt', '')
        if negative_prompt:
            negative_tags = self.extract_tags_from_prompt(negative_prompt)
            for tag in negative_tags:
                self.stats['negative_tags'][tag] += 1
        
        # Save statistics
        import datetime
        self.stats['last_update'] = datetime.datetime.now().isoformat()
        self.save_statistics()
        
        return True  # Successfully processed new image
    
    def get_top_models(self, limit: int = 10) -> List[tuple]:
        """Get top models by usage count. Use limit=0 for all."""
        if limit == 0:
            return self.stats['models'].most_common()
        return self.stats['models'].most_common(limit)
    
    def get_top_positive_tags(self, limit: int = 50) -> List[tuple]:
        """Get top positive prompt tags by usage count. Use limit=0 for all."""
        if limit == 0:
            return self.stats['positive_tags'].most_common()
        return self.stats['positive_tags'].most_common(limit)
    
    def get_top_negative_tags(self, limit: int = 50) -> List[tuple]:
        """Get top negative prompt tags by usage count. Use limit=0 for all."""
        if limit == 0:
            return self.stats['negative_tags'].most_common()
        return self.stats['negative_tags'].most_common(limit)
    
    def get_statistics_summary(self) -> Dict:
        """Get summary of all statistics"""
        return {
            'total_images_processed': self.stats['total_images_processed'],
            'unique_models': len(self.stats['models']),
            'unique_positive_tags': len(self.stats['positive_tags']),
            'unique_negative_tags': len(self.stats['negative_tags']),
            'top_models': self.get_top_models(10),
            'top_positive_tags': self.get_top_positive_tags(20),
            'top_negative_tags': self.get_top_negative_tags(20),
            'last_update': self.stats.get('last_update')
        }
    
    def consolidate_tags(self):
        """Consolidate existing tags using enhanced normalization"""
        print("Consolidating tags with enhanced normalization...")
        
        # Consolidate positive tags
        new_positive_tags = Counter()
        for old_tag, count in self.stats['positive_tags'].items():
            normalized_tag = self.normalize_tag(old_tag)
            new_positive_tags[normalized_tag] += count
        
        # Consolidate negative tags
        new_negative_tags = Counter()
        for old_tag, count in self.stats['negative_tags'].items():
            normalized_tag = self.normalize_tag(old_tag)
            new_negative_tags[normalized_tag] += count
        
        # Show consolidation results
        pos_before = len(self.stats['positive_tags'])
        neg_before = len(self.stats['negative_tags'])
        
        self.stats['positive_tags'] = new_positive_tags
        self.stats['negative_tags'] = new_negative_tags
        
        pos_after = len(self.stats['positive_tags'])
        neg_after = len(self.stats['negative_tags'])
        
        print(f"Positive tags: {pos_before} -> {pos_after} (reduced by {pos_before - pos_after})")
        print(f"Negative tags: {neg_before} -> {neg_after} (reduced by {neg_before - neg_after})")
        
        # Save consolidated statistics
        import datetime
        self.stats['last_update'] = datetime.datetime.now().isoformat()
        self.save_statistics()
        
        return {
            'positive_before': pos_before,
            'positive_after': pos_after,
            'negative_before': neg_before,
            'negative_after': neg_after
        }
    
    def clear_statistics(self):
        """Clear all statistics (for reset functionality)"""
        self.stats = {
            'processed_images': set(),
            'models': Counter(),
            'positive_tags': Counter(),
            'negative_tags': Counter(),
            'total_images_processed': 0,
            'last_update': None
        }
        self.save_statistics()
    
    def export_statistics(self, export_path: str):
        """Export statistics to a file"""
        summary = self.get_statistics_summary()
        
        if export_path.endswith('.json'):
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        elif export_path.endswith('.csv'):
            import csv
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write summary
                writer.writerow(['Summary'])
                writer.writerow(['Total Images Processed', summary['total_images_processed']])
                writer.writerow(['Unique Models', summary['unique_models']])
                writer.writerow(['Unique Positive Tags', summary['unique_positive_tags']])
                writer.writerow(['Unique Negative Tags', summary['unique_negative_tags']])
                writer.writerow([])
                
                # Write top models
                writer.writerow(['Top Models'])
                writer.writerow(['Model', 'Count'])
                for model, count in summary['top_models']:
                    writer.writerow([model, count])
                writer.writerow([])
                
                # Write top positive tags
                writer.writerow(['Top Positive Tags'])
                writer.writerow(['Tag', 'Count'])
                for tag, count in summary['top_positive_tags']:
                    writer.writerow([tag, count])
                writer.writerow([])
                
                # Write top negative tags
                writer.writerow(['Top Negative Tags'])
                writer.writerow(['Tag', 'Count'])
                for tag, count in summary['top_negative_tags']:
                    writer.writerow([tag, count])

    def apply_custom_consolidation(self, consolidation_rules, blacklists, progress_callback=None):
        """
        Apply custom consolidation rules and blacklists to statistics
        
        Args:
            consolidation_rules (dict): Rules mapping target tags to lists of source tags
            blacklists (dict): Lists of tags to remove for each category
            progress_callback (callable): Optional callback for progress updates
        
        Returns:
            dict: Results summary with counts of consolidated and blacklisted tags
        """
        consolidated_count = 0
        blacklisted_count = 0
        
        try:
            if progress_callback:
                progress_callback(20, "Processing positive tag consolidations...")
            
            # Process positive tag consolidations
            if "positive" in consolidation_rules:
                for target_tag, source_tags in consolidation_rules["positive"].items():
                    total_count = 0
                    
                    # Sum up counts from source tags
                    for source_tag in source_tags:
                        if source_tag in self.stats['positive_tags']:
                            total_count += self.stats['positive_tags'][source_tag]
                            del self.stats['positive_tags'][source_tag]
                            consolidated_count += 1
                    
                    # Add consolidated count to target tag
                    if total_count > 0:
                        if target_tag in self.stats['positive_tags']:
                            self.stats['positive_tags'][target_tag] += total_count
                        else:
                            self.stats['positive_tags'][target_tag] = total_count
            
            if progress_callback:
                progress_callback(40, "Processing negative tag consolidations...")
            
            # Process negative tag consolidations
            if "negative" in consolidation_rules:
                for target_tag, source_tags in consolidation_rules["negative"].items():
                    total_count = 0
                    
                    # Sum up counts from source tags
                    for source_tag in source_tags:
                        if source_tag in self.stats['negative_tags']:
                            total_count += self.stats['negative_tags'][source_tag]
                            del self.stats['negative_tags'][source_tag]
                            consolidated_count += 1
                    
                    # Add consolidated count to target tag
                    if total_count > 0:
                        if target_tag in self.stats['negative_tags']:
                            self.stats['negative_tags'][target_tag] += total_count
                        else:
                            self.stats['negative_tags'][target_tag] = total_count
            
            if progress_callback:
                progress_callback(60, "Applying positive tag blacklists...")
            
            # Apply positive tag blacklist
            if "positive" in blacklists:
                for tag in blacklists["positive"]:
                    if tag in self.stats['positive_tags']:
                        del self.stats['positive_tags'][tag]
                        blacklisted_count += 1
            
            if progress_callback:
                progress_callback(80, "Applying negative tag blacklists...")
            
            # Apply negative tag blacklist
            if "negative" in blacklists:
                for tag in blacklists["negative"]:
                    if tag in self.stats['negative_tags']:
                        del self.stats['negative_tags'][tag]
                        blacklisted_count += 1
            
            if progress_callback:
                progress_callback(90, "Saving updated statistics...")
            
            # Save updated statistics
            self.save_statistics()
            
            if progress_callback:
                progress_callback(100, "Consolidation complete!")
            
            return {
                "consolidated_count": consolidated_count,
                "blacklisted_count": blacklisted_count,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def get_tags_by_pattern(self, pattern, category="positive", case_sensitive=False):
        """
        Get tags matching a pattern
        
        Args:
            pattern (str): Pattern to search for
            category (str): "positive" or "negative"
            case_sensitive (bool): Whether search is case sensitive
        
        Returns:
            list: List of (tag, count) tuples matching the pattern
        """
        tags_dict = self.stats['positive_tags'] if category == "positive" else self.stats['negative_tags']
        
        if not case_sensitive:
            pattern = pattern.lower()
            
        matching_tags = []
        for tag, count in tags_dict.items():
            search_tag = tag if case_sensitive else tag.lower()
            if pattern in search_tag:
                matching_tags.append((tag, count))
        
        # Sort by count descending
        return sorted(matching_tags, key=lambda x: x[1], reverse=True)
    
    def get_similar_tags(self, target_tag, category="positive", threshold=0.7):
        """
        Get tags similar to a target tag using fuzzy matching
        
        Args:
            target_tag (str): Tag to find similar matches for
            category (str): "positive" or "negative"
            threshold (float): Similarity threshold (0.0 to 1.0)
        
        Returns:
            list: List of (tag, count, similarity) tuples
        """
        try:
            from difflib import SequenceMatcher
        except ImportError:
            # Fallback to simple substring matching
            return self.get_tags_by_pattern(target_tag, category, case_sensitive=False)
        
        tags_dict = self.stats['positive_tags'] if category == "positive" else self.stats['negative_tags']
        similar_tags = []
        
        for tag, count in tags_dict.items():
            similarity = SequenceMatcher(None, target_tag.lower(), tag.lower()).ratio()
            if similarity >= threshold and tag.lower() != target_tag.lower():
                similar_tags.append((tag, count, similarity))
        
        # Sort by similarity descending
        return sorted(similar_tags, key=lambda x: x[2], reverse=True)
    
    def get_consolidation_suggestions(self, category="positive", min_count=5):
        """
        Get automatic consolidation suggestions based on tag similarity
        
        Args:
            category (str): "positive" or "negative"
            min_count (int): Minimum tag count to consider for consolidation
        
        Returns:
            dict: Dictionary mapping suggested target tags to lists of similar tags
        """
        tags_dict = self.stats['positive_tags'] if category == "positive" else self.stats['negative_tags']
        suggestions = {}
        processed_tags = set()
        
        # Sort tags by count (descending) to prioritize popular tags as targets
        sorted_tags = sorted(tags_dict.items(), key=lambda x: x[1], reverse=True)
        
        for tag, count in sorted_tags:
            if count < min_count or tag in processed_tags:
                continue
                
            # Find similar tags
            similar_tags = self.get_similar_tags(tag, category, threshold=0.8)
            
            # Filter out already processed tags and low-count tags
            valid_similar = []
            for similar_tag, similar_count, similarity in similar_tags:
                if (similar_tag not in processed_tags and 
                    similar_count >= min_count and 
                    similar_tag != tag):
                    valid_similar.append(similar_tag)
                    processed_tags.add(similar_tag)
            
            if valid_similar:
                suggestions[tag] = valid_similar
                processed_tags.add(tag)
        
        return suggestions
    
    def export_tags_for_consolidation(self, category="positive", output_file=None):
        """
        Export tags to a file for manual consolidation rule creation
        
        Args:
            category (str): "positive" or "negative"
            output_file (str): Output file path (optional)
        
        Returns:
            str: File path where tags were exported
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{category}_tags_for_consolidation_{timestamp}.csv"
        
        tags_dict = self.stats['positive_tags'] if category == "positive" else self.stats['negative_tags']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Tag', 'Count', 'Normalized', 'Suggestions'])
            
            for tag, count in sorted(tags_dict.items(), key=lambda x: x[1], reverse=True):
                normalized = self.normalize_tag(tag)
                suggestions = [s[0] for s in self.get_similar_tags(tag, category, threshold=0.8)[:3]]
                writer.writerow([tag, count, normalized, '; '.join(suggestions)])
        
        return output_file
    
    def fix_misclassified_tags(self):
        """Fix tags that are clearly negative but incorrectly in positive stats"""
        print("Fixing misclassified tags...")
        
        # List of tags that should definitely be in negative stats
        obviously_negative_tags = {
            'blurry', 'bad_anatomy', 'low_quality', 'deformed', 'disfigured', 'cropped', 
            'watermark', 'text', 'signature', 'extra limbs', 'missing limbs', 'bad hands',
            'extra fingers', 'missing fingers', 'poorly drawn', 'worst_quality', 
            'low_res', 'error', 'jpeg artifacts', 'artifacts', 'compression artifacts',
            'bad proportions', 'mutation', 'mutated', 'malformed', 'gross proportions',
            'duplicate', 'morbid', 'mutilated', 'extra heads', 'poorly drawn hands',
            'poorly drawn face', 'mutation', 'bad art', 'beginner', 'amateur',
            'distorted', 'b&w', 'black and white', 'monochrome', 'grayscale',
            'plastic skin', 'oversaturated', 'contrast', 'bad_quality', 'unclear',
            'fuzzy', 'pixelated', 'lowres', 'normal_quality', 'bad face', 'ugly face',
            'asymmetric', 'weird', 'strange', 'odd', 'bizarre', 'distorted face',
            'distorted body', 'bad lighting', 'overexposed', 'underexposed',
            # Additional problematic tags
            'ugly', 'child', 'baby', 'toddler', 'infant', 'kid', 'minor', 'underage',
            'elderly', 'old', 'aged', 'grainy', 'grain', 'noisy', 'noise', 
            'fused fingers', 'fused limbs', 'fused', 'merged fingers', 'webbed fingers',
            'flat chest', 'flat', 'score_4', 'score_3', 'score_2', 'score_1', 'score_0',
            'rating:explicit', 'rating:questionable', 'nsfw', 'nude', 'naked', 'penis',
            'vagina', 'sex', 'porn', 'hentai', 'erotic', 'adult', 'mature content'
        }
        
        moved_count = 0
        moved_tags = []
        
        # Check each tag in positive stats
        for tag in list(self.stats['positive_tags'].keys()):
            tag_lower = tag.lower().replace('_', ' ')
            tag_normalized = tag.lower()
            
            # Check if this tag matches any obviously negative pattern
            is_negative = False
            for neg_pattern in obviously_negative_tags:
                if (neg_pattern in tag_lower or 
                    neg_pattern.replace(' ', '_') in tag_normalized or
                    neg_pattern.replace('_', ' ') in tag_lower):
                    is_negative = True
                    break
            
            # Move tag from positive to negative
            if is_negative:
                count = self.stats['positive_tags'][tag]
                del self.stats['positive_tags'][tag]
                self.stats['negative_tags'][tag] += count
                moved_count += count
                moved_tags.append((tag, count))
                print(f"  Moved '{tag}' ({count} occurrences) from positive to negative")
        
        print(f"Fixed {len(moved_tags)} misclassified tags, affecting {moved_count} total occurrences")
        
        if moved_tags:
            # Save updated statistics
            import datetime
            self.stats['last_update'] = datetime.datetime.now().isoformat()
            self.save_statistics()
            print("Statistics updated and saved.")
        
        return {
            'tags_moved': len(moved_tags),
            'total_occurrences_moved': moved_count,
            'moved_details': moved_tags
        }
    
    def remove_tag(self, tag_name: str, category: str = None) -> Dict:
        """Remove a tag from statistics completely
        
        Args:
            tag_name: The tag to remove
            category: 'positive', 'negative', or None (auto-detect)
        
        Returns:
            dict: Results with removed count and category
        """
        removed_count = 0
        removed_from = []
        
        # Auto-detect category if not specified
        if category is None:
            categories_to_check = ['positive', 'negative']
        else:
            categories_to_check = [category]
        
        for cat in categories_to_check:
            if tag_name in self.stats[f'{cat}_tags']:
                count = self.stats[f'{cat}_tags'][tag_name]
                del self.stats[f'{cat}_tags'][tag_name]
                removed_count += count
                removed_from.append(cat)
        
        if removed_count > 0:
            # Save updated statistics
            import datetime
            self.stats['last_update'] = datetime.datetime.now().isoformat()
            self.save_statistics()
            print(f"Removed tag '{tag_name}' ({removed_count} occurrences) from {', '.join(removed_from)} statistics")
        
        return {
            'removed': removed_count > 0,
            'count': removed_count,
            'categories': removed_from
        }
    
    def remove_model(self, model_name: str) -> Dict:
        """Remove a model from statistics completely
        
        Args:
            model_name: The model to remove
        
        Returns:
            dict: Results with removed count
        """
        removed_count = 0
        
        if model_name in self.stats['models']:
            removed_count = self.stats['models'][model_name]
            del self.stats['models'][model_name]
            
            # Save updated statistics
            import datetime
            self.stats['last_update'] = datetime.datetime.now().isoformat()
            self.save_statistics()
            print(f"Removed model '{model_name}' ({removed_count} occurrences) from statistics")
        
        return {
            'removed': removed_count > 0,
            'count': removed_count
        }
    
    def update_image_metadata_in_statistics(self, image_path: str, old_metadata: Dict, new_metadata: Dict) -> bool:
        """Update statistics when image metadata is edited
        
        Args:
            image_path: Path to the image that was edited
            old_metadata: Previous metadata values
            new_metadata: New metadata values
        
        Returns:
            bool: True if statistics were updated
        """
        try:
            # Get image identifier to check if this image was already processed
            image_id = self.get_image_identifier(image_path, new_metadata)
            
            # Only update if this image was already in our statistics
            if image_id not in self.stats['processed_images']:
                # If not processed before, process it normally
                return self.process_image_metadata(image_path, new_metadata)
            
            # Remove old statistics for this image
            self._remove_image_from_statistics(old_metadata)
            
            # Add new statistics for this image  
            self._add_image_to_statistics(new_metadata)
            
            # Save updated statistics
            import datetime
            self.stats['last_update'] = datetime.datetime.now().isoformat()
            self.save_statistics()
            
            print(f"Updated statistics for edited image: {os.path.basename(image_path)}")
            return True
            
        except Exception as e:
            print(f"Error updating statistics for edited metadata: {e}")
            return False
    
    def _remove_image_from_statistics(self, metadata: Dict):
        """Remove an image's contribution from statistics (internal method)"""
        # Remove model count
        model_name = metadata.get('model_name')
        if model_name and model_name.strip():
            clean_model = model_name.strip()
            if clean_model.lower().startswith('hash:'):
                clean_model = metadata.get('model_hash', clean_model)
            
            normalized_model = self.normalize_model_name(clean_model)
            if normalized_model in self.stats['models']:
                self.stats['models'][normalized_model] -= 1
                if self.stats['models'][normalized_model] <= 0:
                    del self.stats['models'][normalized_model]
        
        # Remove positive tag counts
        positive_prompt = metadata.get('positive_prompt', '')
        if positive_prompt:
            positive_tags = self.extract_tags_from_prompt(positive_prompt)
            for tag in positive_tags:
                if tag in self.stats['positive_tags']:
                    self.stats['positive_tags'][tag] -= 1
                    if self.stats['positive_tags'][tag] <= 0:
                        del self.stats['positive_tags'][tag]
        
        # Remove negative tag counts
        negative_prompt = metadata.get('negative_prompt', '')
        if negative_prompt:
            negative_tags = self.extract_tags_from_prompt(negative_prompt)
            for tag in negative_tags:
                if tag in self.stats['negative_tags']:
                    self.stats['negative_tags'][tag] -= 1
                    if self.stats['negative_tags'][tag] <= 0:
                        del self.stats['negative_tags'][tag]
    
    def _add_image_to_statistics(self, metadata: Dict):
        """Add an image's contribution to statistics (internal method)"""
        # Add model count
        model_name = metadata.get('model_name')
        if model_name and model_name.strip():
            clean_model = model_name.strip()
            if clean_model.lower().startswith('hash:'):
                clean_model = metadata.get('model_hash', clean_model)
            
            normalized_model = self.normalize_model_name(clean_model)
            self.stats['models'][normalized_model] += 1
        
        # Add positive tag counts
        positive_prompt = metadata.get('positive_prompt', '')
        if positive_prompt:
            positive_tags = self.extract_tags_from_prompt(positive_prompt)
            for tag in positive_tags:
                self.stats['positive_tags'][tag] += 1
        
        # Add negative tag counts
        negative_prompt = metadata.get('negative_prompt', '')
        if negative_prompt:
            negative_tags = self.extract_tags_from_prompt(negative_prompt)
            for tag in negative_tags:
                self.stats['negative_tags'][tag] += 1

# Global instance
stats_tracker = StatisticsTracker()

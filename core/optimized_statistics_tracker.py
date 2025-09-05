"""
Optimized Statistics Tracker for MetaPicPick
Enhanced version with caching, performance optimizations, and better error handling.
"""

from utils.common_imports import *
from utils.logger import logger, PerformanceTimer
from config.settings import get_config, get_performance_settings
from functools import lru_cache
from threading import Lock
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class CacheEntry:
    """Cache entry with timestamp for invalidation"""
    
    def __init__(self, data: Any, ttl: int = 300):
        self.data = data
        self.timestamp = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return (time.time() - self.timestamp) > self.ttl
    
    def refresh(self, data: Any):
        """Refresh cache entry with new data"""
        self.data = data
        self.timestamp = time.time()


class OptimizedStatisticsTracker:
    """Enhanced statistics tracker with performance optimizations"""
    
    def __init__(self):
        """Initialize the optimized statistics tracker"""
        self.settings = QSettings('MetaPicPick', 'Statistics')
        self.stats_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 'metapicpick_statistics.json'
        )
        self.model_mapping_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 'model_name_mappings.json'
        )
        
        # Thread safety
        self._lock = Lock()
        self._cache_lock = Lock()
        
        # Performance settings
        self.perf_settings = get_performance_settings()
        
        # Initialize cache
        self._cache = {} if self.perf_settings['cache_enabled'] else None
        self._cache_timeout = self.perf_settings['cache_timeout']
        
        # Load data
        self.stats = self.load_statistics()
        self.model_name_mappings = self.load_model_mappings()
        
        # Track dirty flags for selective updates
        self._dirty_flags = set()
        self._last_save_time = time.time()
        
        # Performance metrics
        self._operation_counts = defaultdict(int)
        self._operation_times = defaultdict(list)
        
        logger.info("OptimizedStatisticsTracker initialized")
    
    def load_statistics(self) -> Dict:
        """Load statistics from file with error handling"""
        with PerformanceTimer("load_statistics"):
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
                    
                    logger.info(f"Loaded statistics: {stats['total_images_processed']} images")
                    return stats
                    
                except Exception as e:
                    logger.error(f"Error loading statistics from {self.stats_file}", e)
            
            # Default empty statistics
            logger.info("Creating new statistics database")
            return {
                'processed_images': set(),
                'models': Counter(),
                'positive_tags': Counter(),
                'negative_tags': Counter(),
                'total_images_processed': 0,
                'last_update': None
            }
    
    def save_statistics(self, force: bool = False):
        """Save statistics to file with throttling"""
        current_time = time.time()
        min_save_interval = get_config('statistics_save_interval', 30)  # seconds
        
        if not force and (current_time - self._last_save_time) < min_save_interval:
            logger.debug("Skipping save due to throttling")
            return
        
        with PerformanceTimer("save_statistics"):
            try:
                with self._lock:
                    # Convert set to list for JSON serialization
                    stats_to_save = self.stats.copy()
                    stats_to_save['processed_images'] = list(self.stats['processed_images'])
                    stats_to_save['models'] = dict(self.stats['models'])
                    stats_to_save['positive_tags'] = dict(self.stats['positive_tags'])
                    stats_to_save['negative_tags'] = dict(self.stats['negative_tags'])
                    stats_to_save['last_update'] = datetime.now().isoformat()
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
                    
                    # Write to temporary file first, then rename (atomic operation)
                    temp_file = self.stats_file + '.tmp'
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(stats_to_save, f, indent=2, ensure_ascii=False)
                    
                    # Atomic rename
                    if os.path.exists(self.stats_file):
                        backup_file = self.stats_file + '.bak'
                        shutil.copy2(self.stats_file, backup_file)
                    
                    shutil.move(temp_file, self.stats_file)
                    
                    self._last_save_time = current_time
                    self._clear_cache()
                    
                    logger.debug("Statistics saved successfully")
                    
            except Exception as e:
                logger.error("Error saving statistics", e)
                raise StatisticsError(f"Failed to save statistics: {e}")
    
    def _clear_cache(self):
        """Clear all cached data"""
        if self._cache is not None:
            with self._cache_lock:
                self._cache.clear()
                logger.debug("Statistics cache cleared")
    
    def _get_cached_or_compute(self, cache_key: str, compute_func, *args, **kwargs):
        """Get cached result or compute if not available"""
        if self._cache is None:
            return compute_func(*args, **kwargs)
        
        with self._cache_lock:
            entry = self._cache.get(cache_key)
            
            if entry is not None and not entry.is_expired():
                logger.debug(f"Cache hit for {cache_key}")
                return entry.data
            
            # Compute new value
            with PerformanceTimer(f"compute_{cache_key}"):
                result = compute_func(*args, **kwargs)
            
            # Cache the result
            self._cache[cache_key] = CacheEntry(result, self._cache_timeout)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
    
    def get_top_models(self, limit: int = 10) -> List[tuple]:
        """Get top models by usage count with caching"""
        cache_key = f"top_models_{limit}"
        
        def compute_top_models():
            if limit == 0:
                return self.stats['models'].most_common()
            return self.stats['models'].most_common(limit)
        
        return self._get_cached_or_compute(cache_key, compute_top_models)
    
    def get_top_positive_tags(self, limit: int = 50) -> List[tuple]:
        """Get top positive prompt tags with caching"""
        cache_key = f"top_positive_tags_{limit}"
        
        def compute_top_positive_tags():
            if limit == 0:
                return self.stats['positive_tags'].most_common()
            return self.stats['positive_tags'].most_common(limit)
        
        return self._get_cached_or_compute(cache_key, compute_top_positive_tags)
    
    def get_top_negative_tags(self, limit: int = 50) -> List[tuple]:
        """Get top negative prompt tags with caching"""
        cache_key = f"top_negative_tags_{limit}"
        
        def compute_top_negative_tags():
            if limit == 0:
                return self.stats['negative_tags'].most_common()
            return self.stats['negative_tags'].most_common(limit)
        
        return self._get_cached_or_compute(cache_key, compute_top_negative_tags)
    
    def get_statistics_summary(self) -> Dict:
        """Get statistics summary with caching"""
        cache_key = "statistics_summary"
        
        def compute_summary():
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
        
        return self._get_cached_or_compute(cache_key, compute_summary)
    
    def process_images_batch(self, image_metadata_pairs: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """
        Process multiple images in batch for better performance
        
        Args:
            image_metadata_pairs: List of (image_path, metadata) tuples
            
        Returns:
            Dictionary with processing results
        """
        with PerformanceTimer("process_images_batch", f"{len(image_metadata_pairs)} images"):
            results = {
                'processed_count': 0,
                'skipped_count': 0,
                'errors': []
            }
            
            # Use thread pool if parallel processing is enabled
            if self.perf_settings['parallel_processing'] and len(image_metadata_pairs) > 10:
                results = self._process_batch_parallel(image_metadata_pairs)
            else:
                results = self._process_batch_sequential(image_metadata_pairs)
            
            # Save statistics after batch processing
            if results['processed_count'] > 0:
                self.save_statistics()
                logger.info(f"Batch processing complete: {results['processed_count']} processed")
            
            return results
    
    def _process_batch_sequential(self, image_metadata_pairs: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """Process images sequentially"""
        results = {'processed_count': 0, 'skipped_count': 0, 'errors': []}
        
        for image_path, metadata in image_metadata_pairs:
            try:
                if self.process_image_metadata(image_path, metadata):
                    results['processed_count'] += 1
                else:
                    results['skipped_count'] += 1
            except Exception as e:
                error_msg = f"Error processing {image_path}: {e}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        return results
    
    def _process_batch_parallel(self, image_metadata_pairs: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """Process images in parallel using thread pool"""
        results = {'processed_count': 0, 'skipped_count': 0, 'errors': []}
        max_workers = self.perf_settings['max_worker_threads']
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_image = {
                executor.submit(self._process_single_image, image_path, metadata): image_path
                for image_path, metadata in image_metadata_pairs
            }
            
            # Collect results
            for future in as_completed(future_to_image):
                image_path = future_to_image[future]
                try:
                    processed = future.result()
                    if processed:
                        results['processed_count'] += 1
                    else:
                        results['skipped_count'] += 1
                except Exception as e:
                    error_msg = f"Error processing {image_path}: {e}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
        
        return results
    
    def _process_single_image(self, image_path: str, metadata: Dict) -> bool:
        """Process a single image (thread-safe)"""
        with self._lock:
            return self.process_image_metadata(image_path, metadata)
    
    def process_image_metadata(self, image_path: str, metadata: Dict) -> bool:
        """Process metadata from an image (optimized version)"""
        with PerformanceTimer("process_image_metadata"):
            # Check if we've already processed this image
            image_id = self.get_image_identifier(image_path, metadata)
            if image_id in self.stats['processed_images']:
                logger.debug(f"Image already processed: {os.path.basename(image_path)}")
                return False
            
            # Mark as processed
            self.stats['processed_images'].add(image_id)
            self.stats['total_images_processed'] += 1
            
            # Extract and count model (optimized)
            self._process_model_metadata(metadata)
            
            # Extract and count tags (optimized)
            self._process_tag_metadata(metadata)
            
            # Mark cache as dirty
            self._clear_cache()
            
            logger.debug(f"Processed metadata for: {os.path.basename(image_path)}")
            return True
    
    def _process_model_metadata(self, metadata: Dict):
        """Process model-related metadata"""
        model_name = metadata.get('model_name')
        if model_name and model_name.strip():
            clean_model = model_name.strip()
            if clean_model.lower().startswith('hash:'):
                clean_model = metadata.get('model_hash', clean_model)
            
            # Use cached normalization if available
            normalized_model = self.normalize_model_name(clean_model)
            self.stats['models'][normalized_model] += 1
    
    def _process_tag_metadata(self, metadata: Dict):
        """Process tag-related metadata"""
        # Process positive prompt tags
        positive_prompt = metadata.get('positive_prompt', '')
        if positive_prompt:
            positive_tags = self.extract_tags_from_prompt(positive_prompt)
            for tag in positive_tags:
                self.stats['positive_tags'][tag] += 1
        
        # Process negative prompt tags
        negative_prompt = metadata.get('negative_prompt', '')
        if negative_prompt:
            negative_tags = self.extract_tags_from_prompt(negative_prompt)
            for tag in negative_tags:
                self.stats['negative_tags'][tag] += 1
    
    @lru_cache(maxsize=1000)
    def normalize_model_name(self, model_path_or_name: str) -> str:
        """Extract and normalize model name (cached)"""
        if not model_path_or_name:
            return "Unknown Model"
        
        # Check custom mappings first
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
        
        # Clean up the name
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
        model_name = ' '.join(model_name.split())
        
        return model_name if model_name else "Unknown Model"
    
    @lru_cache(maxsize=2000)
    def normalize_tag(self, tag: str) -> str:
        """Normalize a tag (cached version)"""
        if not tag:
            return tag
        
        # Convert to lowercase and clean spaces
        normalized = ' '.join(tag.lower().split())
        
        # Use pre-compiled regex for better performance
        if hasattr(self, '_tag_normalizations'):
            return self._tag_normalizations.get(normalized, normalized)
        
        # Initialize tag normalizations on first use
        self._tag_normalizations = {
            # Common variations
            '1 girl': '1girl',
            '2 girls': '2girls',
            'large breast': 'large_breasts',
            'high quality': 'high_quality',
            'long hair': 'long_hair',
            'blue eyes': 'blue_eyes',
            'looking at viewer': 'looking_at_viewer',
            # Add more normalizations as needed
        }
        
        return self._tag_normalizations.get(normalized, normalized)
    
    def extract_tags_from_prompt(self, prompt: str) -> Set[str]:
        """Extract tags from prompt with optimizations"""
        if not prompt:
            return set()
        
        # Cache key for this prompt
        prompt_hash = hash(prompt)
        cache_key = f"prompt_tags_{prompt_hash}"
        
        # Check cache first
        if hasattr(self, '_prompt_cache'):
            cached = self._prompt_cache.get(cache_key)
            if cached is not None:
                return cached
        else:
            self._prompt_cache = {}
        
        # Extract tags
        with PerformanceTimer("extract_tags_from_prompt"):
            # Remove LoRA and weight syntax more efficiently
            cleaned_prompt = re.sub(r'<lora:[^>]+>', '', prompt)
            cleaned_prompt = re.sub(r'\([^)]*:\d*\.?\d*\)', lambda m: m.group(0).split(':')[0][1:], cleaned_prompt)
            cleaned_prompt = re.sub(r'\(([^)]*)\)', r'\1', cleaned_prompt)
            cleaned_prompt = re.sub(r'[<>\[\]{}]', '', cleaned_prompt)
            
            # Split and clean tags
            tags = set()
            for tag in re.split(r'[,\n]+', cleaned_prompt):
                tag = tag.strip()
                if len(tag) >= 3:
                    # Skip common connecting words
                    if tag.lower() not in {'and', 'the', 'with', 'for', 'from', 'very', 'too'}:
                        normalized_tag = self.normalize_tag(tag)
                        tags.add(normalized_tag)
        
        # Cache the result
        if len(self._prompt_cache) < 1000:  # Limit cache size
            self._prompt_cache[cache_key] = tags
        
        return tags
    
    def get_image_identifier(self, image_path: str, metadata: Dict) -> str:
        """Get unique identifier for an image (optimized)"""
        try:
            file_stat = os.stat(image_path)
            file_size = file_stat.st_size
            file_mtime = int(file_stat.st_mtime)
            
            # Use hash of key metadata for efficiency
            seed = metadata.get('seed', '')
            model_hash = metadata.get('model_hash', '')
            
            # Create hash instead of long string
            identifier_string = f"{image_path}|{file_size}|{file_mtime}|{seed}|{model_hash}"
            return str(hash(identifier_string))
        except Exception:
            return str(hash(image_path))
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            'operation_counts': dict(self._operation_counts),
            'average_operation_times': {
                op: sum(times) / len(times) if times else 0
                for op, times in self._operation_times.items()
            },
            'cache_size': len(self._cache) if self._cache else 0,
            'cache_enabled': self._cache is not None,
            'total_processed_images': self.stats['total_images_processed'],
            'last_save_time': self._last_save_time
        }
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        if self._cache is None:
            return
        
        with self._cache_lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    # Import all other methods from original statistics tracker
    def load_model_mappings(self) -> Dict[str, str]:
        """Load custom model name mappings from file"""
        if os.path.exists(self.model_mapping_file):
            try:
                with open(self.model_mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Error loading model mappings", e)
        return {}
    
    def save_model_mappings(self):
        """Save custom model name mappings to file"""
        try:
            os.makedirs(os.path.dirname(self.model_mapping_file), exist_ok=True)
            with open(self.model_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_name_mappings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Error saving model mappings", e)
    
    def consolidate_model_names(self):
        """Apply normalization to all existing model names in statistics"""
        with PerformanceTimer("consolidate_model_names"):
            logger.info("Consolidating model names...")
            
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
            
            logger.info(f"Model consolidation: {models_before} -> {models_after} (reduced by {models_before - models_after})")
            
            # Clear cache after consolidation
            self._clear_cache()
            self.save_statistics(force=True)
            
            return {
                'models_before': models_before,
                'models_after': models_after,
                'changes_made': len(consolidation_log)
            }


# Create optimized global instance
optimized_stats_tracker = OptimizedStatisticsTracker()

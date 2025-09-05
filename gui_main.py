# Enhanced MetaPicPick GUI with integrated utilities
from utils.common_imports import *
from utils.logger import logger, PerformanceTimer
from utils.gui_factory import GUIFactory
from utils.error_handler import handle_errors, ErrorCategory, ErrorSeverity, handle_gui_error
from config.settings import get_config, get_display_settings, get_performance_settings
from utils.metadata_utils import extract_metadata, save_metadata
from utils.plugin_manager import PluginManager
from core.optimized_statistics_tracker import optimized_stats_tracker
from core.statistics_tab import StatisticsTab

class ResizableSplitter(QSplitter):
    """Enhanced splitter with persistence, better defaults, and logging"""
    
    def __init__(self, orientation, settings_key, parent=None):
        super().__init__(orientation, parent)
        self.settings_key = settings_key
        self.settings = QSettings('MetaPicPick', 'Layout')
        
        # Set splitter properties
        self.setChildrenCollapsible(False)
        self.setHandleWidth(6)
        
        logger.debug(f"Created ResizableSplitter with key: {settings_key}")
    
    @handle_errors(ErrorCategory.GUI, "Saving splitter state")
    def save_state(self):
        """Save splitter state to settings with error handling"""
        self.settings.setValue(self.settings_key, self.saveState())
        logger.debug(f"Saved splitter state for: {self.settings_key}")
    
    @handle_errors(ErrorCategory.GUI, "Restoring splitter state")
    def restore_state(self):
        """Restore splitter state from settings with error handling"""
        state = self.settings.value(self.settings_key)
        if state:
            self.restoreState(state)
            logger.debug(f"Restored splitter state for: {self.settings_key}")
        else:
            logger.debug(f"No saved state found for splitter: {self.settings_key}")

class LibraryTab(QWidget):
    """Library tab with folder browser, image list, and metadata preview"""
    
    def __init__(self, plugins, parent=None):
        super().__init__(parent)
        self.plugins = plugins
        self.loaded_images = []
        self.current_image_path = None
        self.gui_factory = GUIFactory()
        
        logger.info("Initializing Library tab")
        self.init_ui()
        logger.debug("Library tab initialized successfully")
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Main horizontal splitter
        main_splitter = ResizableSplitter(Qt.Horizontal, 'library_main_splitter')
        
        # Left panel: Folder tree and filters
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right side: vertical splitter for image list and preview
        right_splitter = ResizableSplitter(Qt.Vertical, 'library_right_splitter')
        
        # Center panel: Image list
        center_panel = self.create_center_panel()
        right_splitter.addWidget(center_panel)
        
        # Bottom right panel: Preview and quick metadata
        preview_panel = self.create_preview_panel()
        right_splitter.addWidget(preview_panel)
        
        # Set initial sizes for right splitter
        right_splitter.setSizes([400, 300])
        
        main_splitter.addWidget(right_splitter)
        
        # Set initial sizes for main splitter  
        main_splitter.setSizes([250, 750])
        
        layout.addWidget(main_splitter)
        
        # Restore saved states
        main_splitter.restore_state()
        right_splitter.restore_state()
        
    @handle_errors(ErrorCategory.GUI, "Creating left panel")
    def create_left_panel(self):
        """Create left panel with controls and filters using GUI factory"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Folder controls using GUI factory
        folder_group = self.gui_factory.create_group_box("Folder")
        folder_layout = folder_group.layout()
        
        load_button = self.gui_factory.create_styled_button(
            "Load Folder", 
            self.load_folder, 
            'primary',
            tooltip="Select a folder containing images to analyze"
        )
        folder_layout.addWidget(load_button)
        
        layout.addWidget(folder_group)
        
        # Filter controls using GUI factory
        filter_group = self.gui_factory.create_group_box("Filters")
        filter_layout = filter_group.layout()
        
        self.search_bar = self.gui_factory.create_line_edit(
            placeholder="Search metadata..."
        )
        self.search_bar.textChanged.connect(self.filter_images)
        filter_layout.addWidget(self.gui_factory.create_label("Search:"))
        filter_layout.addWidget(self.search_bar)
        
        self.filter_model = self.gui_factory.create_combo_box(["All Models"])
        self.filter_model.currentTextChanged.connect(self.filter_images)
        filter_layout.addWidget(self.gui_factory.create_label("Model:"))
        filter_layout.addWidget(self.filter_model)
        
        self.filter_negative_prompt = QCheckBox("Only With Negative Prompt")
        self.filter_negative_prompt.stateChanged.connect(self.filter_images)
        filter_layout.addWidget(self.filter_negative_prompt)
        
        layout.addWidget(filter_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        bulk_rename_btn = QPushButton("Bulk Rename")
        bulk_rename_btn.clicked.connect(self.bulk_rename)
        actions_layout.addWidget(bulk_rename_btn)
        
        create_folder_btn = QPushButton("Create Folder")
        create_folder_btn.clicked.connect(self.create_folder)
        actions_layout.addWidget(create_folder_btn)
        
        move_btn = QPushButton("Move Selected to Folder")
        move_btn.clicked.connect(self.move_to_folder)
        actions_layout.addWidget(move_btn)
        
        export_btn = QPushButton("Export Filtered Metadata")
        export_btn.clicked.connect(self.export_filtered)
        actions_layout.addWidget(export_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        panel.setMinimumWidth(200)
        return panel
        
    def create_center_panel(self):
        """Create center panel with image list"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_label = QLabel("Images")
        header_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(header_label)
        
        # Image list
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.load_selected_image)
        self.image_list.setAlternatingRowColors(True)
        layout.addWidget(self.image_list)
        
        panel.setMinimumHeight(200)
        return panel
        
    def create_preview_panel(self):
        """Create preview panel with image and metadata"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Image preview (left side)
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumSize(200, 200)
        self.image_preview.setStyleSheet("border: 1px solid gray;")
        preview_layout.addWidget(self.image_preview)
        
        layout.addWidget(preview_group)
        
        # Quick metadata (right side)
        metadata_group = QGroupBox("Quick Info")
        metadata_layout = QVBoxLayout(metadata_group)
        
        self.quick_metadata = QTextEdit()
        self.quick_metadata.setMaximumHeight(200)
        self.quick_metadata.setReadOnly(True)
        metadata_layout.addWidget(self.quick_metadata)
        
        layout.addWidget(metadata_group)
        
        panel.setMinimumHeight(150)
        return panel

    def load_folder(self):
        """Load images from selected folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.image_list.clear()
            self.loaded_images = []
            seen_models = set()
            
            for fname in os.listdir(folder):
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    full_path = os.path.join(folder, fname)
                    self.loaded_images.append(full_path)
                    self.image_list.addItem(full_path)
                    
                    # Extract metadata for model filter and statistics
                    meta = extract_metadata(full_path, self.plugins)
                    
                    # Track statistics for this image
                    stats_tracker.process_image_metadata(full_path, meta)
                    
                    model_name = meta.get("model_name")
                    if model_name:
                        seen_models.add(model_name)
                        
            # Update model filter
            self.filter_model.clear()
            self.filter_model.addItem("All Models")
            for model in sorted(seen_models):
                self.filter_model.addItem(model)

    def load_selected_image(self, item):
        """Load and display selected image"""
        self.current_image_path = item.text()
        
        # Update preview
        pixmap = QPixmap(self.current_image_path).scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_preview.setPixmap(pixmap)
        
        # Update quick metadata
        meta = extract_metadata(self.current_image_path, self.plugins)
        metadata_text = ""
        for key, value in meta.items():
            if key.startswith('_'):
                continue
            if key in ['positive_prompt', 'negative_prompt']:
                # Truncate long prompts
                if len(str(value)) > 100:
                    value = str(value)[:100] + "..."
            metadata_text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        self.quick_metadata.setText(metadata_text)

    def filter_images(self):
        """Filter images based on search and model criteria"""
        query = self.search_bar.text().lower()
        model_filter = self.filter_model.currentText()
        neg_prompt = self.filter_negative_prompt.isChecked()
        
        self.image_list.clear()
        for path in self.loaded_images:
            meta = extract_metadata(path, self.plugins)
            match = True
            
            if model_filter != "All Models" and meta.get("model_name") != model_filter:
                match = False
            if neg_prompt and not meta.get("negative_prompt"):
                match = False
            if query and query not in json.dumps(meta).lower():
                match = False
                
            if match:
                self.image_list.addItem(path)

    def bulk_rename(self):
        """Bulk rename selected images"""
        if not self.current_image_path:
            return
        folder = os.path.dirname(self.current_image_path)
        prefix, _ = QFileDialog.getSaveFileName(self, "Enter Prefix", folder)
        if prefix:
            for idx, path in enumerate(self.loaded_images):
                ext = os.path.splitext(path)[1]
                new_path = os.path.join(folder, f"{prefix}_{idx+1}{ext}")
                os.rename(path, new_path)
            self.load_folder()

    def create_folder(self):
        """Create new folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Destination")
        if folder:
            name, _ = QFileDialog.getSaveFileName(self, "New Folder Name", folder)
            if name:
                os.makedirs(name, exist_ok=True)

    def move_to_folder(self):
        """Move selected images to folder"""
        folder = QFileDialog.getExistingDirectory(self, "Move to Folder")
        if folder:
            for item in self.image_list.selectedItems():
                shutil.move(item.text(), os.path.join(folder, os.path.basename(item.text())))
            self.load_folder()

    def export_filtered(self):
        """Export filtered metadata"""
        export_path, _ = QFileDialog.getSaveFileName(self, "Export Metadata", "metadata.json")
        if export_path:
            export_data = []
            for idx in range(self.image_list.count()):
                path = self.image_list.item(idx).text()
                meta = extract_metadata(path, self.plugins)
                meta["filename"] = os.path.basename(path)
                export_data.append(meta)
            
            if export_path.endswith(".csv"):
                keys = sorted({k for row in export_data for k in row.keys()})
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(export_data)
            else:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)

class MetadataTab(QWidget):
    """Enhanced metadata editing tab with integrated utilities"""
    
    def __init__(self, plugins, parent=None):
        super().__init__(parent)
        self.plugins = plugins
        self.current_image_path = None
        self.gui_factory = GUIFactory()
        
        logger.info("Initializing Metadata tab")
        self.init_ui()
        logger.debug("Metadata tab initialized successfully")
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Main splitter
        splitter = ResizableSplitter(Qt.Horizontal, 'metadata_main_splitter')
        
        # Left panel: Field editing
        left_panel = self.create_field_editor()
        splitter.addWidget(left_panel)
        
        # Right panel: Preview and validation
        right_panel = self.create_preview_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        splitter.restore_state()
        
    def create_field_editor(self):
        """Create field editor panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File selection
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout(file_group)
        
        select_file_btn = QPushButton("Select Image File")
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_btn)
        
        self.current_file_label = QLabel("No file selected")
        file_layout.addWidget(self.current_file_label)
        
        layout.addWidget(file_group)
        
        # Metadata fields
        fields_group = QGroupBox("Metadata Fields")
        fields_layout = QVBoxLayout(fields_group)
        
        # Create scrollable area for fields
        scroll = QScrollArea()
        fields_widget = QWidget()
        fields_layout_inner = QVBoxLayout(fields_widget)
        
        # Create enhanced metadata fields
        self.meta_fields = {
            # Basic info
            'source': QLineEdit(),
            'model_name': QLineEdit(),
            'model_hash': QLineEdit(),
            'version': QLineEdit(),
            'software': QLineEdit(),
            
            # Image dimensions
            'width': QLineEdit(),
            'height': QLineEdit(),
            'size': QLineEdit(),
            
            # Generation parameters
            'scheduler': QLineEdit(),
            'sampler': QLineEdit(),
            'cfg_scale': QLineEdit(),
            'steps': QLineEdit(),
            'seed': QLineEdit(),
            'subseed': QLineEdit(),
            'clip_skip': QLineEdit(),
            'eta': QLineEdit(),
            'denoising_strength': QLineEdit(),
            'ensd': QLineEdit(),
            'batch_size': QLineEdit(),
            
            # Prompts
            'positive_prompt': QTextEdit(),
            'negative_prompt': QTextEdit(),
            
            # Advanced features
            'controlnet': QLineEdit(),
            'controlnet_strength': QLineEdit(),
            'lora': QLineEdit(),
            'loras': QTextEdit(),
            'lora_hashes': QTextEdit(),
            'ti_hashes': QTextEdit(),
            'vae': QLineEdit(),
            'hypernetwork': QLineEdit(),
            'face_restoration': QLineEdit(),
            'codeformer_weight': QLineEdit(),
            'upscaler': QLineEdit(),
            
            # Hi-res fix
            'hires_upscale': QLineEdit(),
            'hires_steps': QLineEdit(),
            'hires_upscaler': QLineEdit(),
            'hires_resize_width': QLineEdit(),
            'hires_resize_height': QLineEdit(),
            
            # Variation/seed settings
            'subseed_strength': QLineEdit(),
            'seed_resize_from_width': QLineEdit(),
            'seed_resize_from_height': QLineEdit(),
            
            # NovelAI specific
            'qualifiers': QTextEdit(),
            'sm': QLineEdit(),
            'sm_dyn': QLineEdit(),
            'noise_schedule': QLineEdit(),
            'request_type': QLineEdit(),
            'signed_hash': QLineEdit(),
            
            # Technical details
            'karras': QLineEdit(),
            'rng': QLineEdit(),
            'token_merging_ratio': QLineEdit(),
            'extra_data': QTextEdit(),
            'title': QLineEdit(),
            
            # General/fallback fields
            'description': QTextEdit(),
            'extra': QTextEdit()
        }
        
        # Organize fields into logical groups
        field_groups = {
            'Basic Information': [
                'source', 'model_name', 'model_hash', 'version', 'software'
            ],
            'Image Properties': [
                'width', 'height', 'size'
            ],
            'Generation Parameters': [
                'scheduler', 'sampler', 'cfg_scale', 'steps', 'seed', 'subseed',
                'clip_skip', 'eta', 'denoising_strength', 'ensd', 'batch_size'
            ],
            'Prompts': [
                'positive_prompt', 'negative_prompt'
            ],
            'Advanced Features': [
                'controlnet', 'controlnet_strength', 'lora', 'loras', 'lora_hashes',
                'ti_hashes', 'vae', 'hypernetwork', 'face_restoration', 
                'codeformer_weight', 'upscaler'
            ],
            'Hi-res Fix': [
                'hires_upscale', 'hires_steps', 'hires_upscaler',
                'hires_resize_width', 'hires_resize_height'
            ],
            'Variation/Seed Settings': [
                'subseed_strength', 'seed_resize_from_width', 'seed_resize_from_height'
            ],
            'NovelAI Specific': [
                'qualifiers', 'sm', 'sm_dyn', 'noise_schedule', 'request_type', 'signed_hash'
            ],
            'Technical Details': [
                'karras', 'rng', 'token_merging_ratio', 'extra_data', 'title'
            ],
            'Other': [
                'description', 'extra'
            ]
        }
        
        # Create collapsible groups
        for group_name, field_names in field_groups.items():
            group_box = QGroupBox(group_name)
            group_box.setCheckable(True)
            group_box.setChecked(group_name in ['Basic Information', 'Generation Parameters', 'Prompts'])
            
            group_layout = QFormLayout(group_box)
            
            for field_name in field_names:
                if field_name in self.meta_fields:
                    widget = self.meta_fields[field_name]
                    label = QLabel(field_name.replace('_', ' ').title())
                    if isinstance(widget, QTextEdit):
                        widget.setMaximumHeight(80)
                    group_layout.addRow(label, widget)
            
            fields_layout_inner.addWidget(group_box)
        
        # Add stretch to push groups to top
        fields_layout_inner.addStretch()
        
        scroll.setWidget(fields_widget)
        scroll.setWidgetResizable(True)
        fields_layout.addWidget(scroll)
        
        # Save button
        save_btn = QPushButton("Save Metadata")
        save_btn.clicked.connect(self.save_metadata)
        fields_layout.addWidget(save_btn)
        
        layout.addWidget(fields_group)
        
        panel.setMinimumWidth(400)
        return panel
        
    def create_preview_panel(self):
        """Create preview and validation panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumSize(300, 300)
        self.image_preview.setStyleSheet("border: 1px solid gray;")
        preview_layout.addWidget(self.image_preview)
        
        layout.addWidget(preview_group)
        
        # Raw metadata view
        raw_group = QGroupBox("Raw Metadata")
        raw_layout = QVBoxLayout(raw_group)
        
        self.raw_metadata = QTextEdit()
        self.raw_metadata.setReadOnly(True)
        self.raw_metadata.setFont(QFont("Consolas", 9))
        raw_layout.addWidget(self.raw_metadata)
        
        layout.addWidget(raw_group)
        
        return panel

    def select_file(self):
        """Select image file for metadata editing"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "", 
            "Image Files (*.png *.jpg *.jpeg *.webp)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.current_file_label.setText(os.path.basename(file_path))
            
            # Load image preview
            pixmap = QPixmap(file_path).scaled(
                300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_preview.setPixmap(pixmap)
            
            # Load metadata into fields
            self.load_metadata()

    def load_metadata(self):
        """Load metadata into form fields"""
        if not self.current_image_path:
            return
            
        meta = extract_metadata(self.current_image_path, self.plugins)
        
        # Track statistics for this image
        optimized_stats_tracker.add_image_metadata(self.current_image_path, meta)
        
        # Fill form fields
        for key, widget in self.meta_fields.items():
            value = meta.get(key, "")
            if isinstance(widget, QTextEdit):
                widget.setPlainText(str(value))
            else:
                widget.setText(str(value))
        
        # Show raw metadata
        self.raw_metadata.setPlainText(json.dumps(meta, indent=2))

    def save_metadata(self):
        """Save metadata to image file with enhanced validation and feedback"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "No file selected")
            return
        
        # Collect form data and validate
        meta = {}
        validation_errors = []
        
        for key, widget in self.meta_fields.items():
            if isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()
            else:
                value = widget.text().strip()
            
            # Only include non-empty values
            if value:
                # Validate specific fields
                if key in ['seed', 'steps', 'width', 'height', 'clip_skip', 'batch_size']:
                    try:
                        int(value)
                    except ValueError:
                        validation_errors.append(f"{key.replace('_', ' ').title()} must be a number")
                        continue
                        
                elif key in ['cfg_scale', 'denoising_strength', 'eta', 'hires_upscale', 'subseed_strength']:
                    try:
                        float(value)
                    except ValueError:
                        validation_errors.append(f"{key.replace('_', ' ').title()} must be a decimal number")
                        continue
                
                meta[key] = value
        
        # Show validation errors if any
        if validation_errors:
            QMessageBox.warning(
                self, 
                "Validation Errors", 
                "Please fix the following errors:\n\n" + "\n".join(validation_errors)
            )
            return
        
        # Show what will be saved
        fields_to_save = [key for key, value in meta.items() if value]
        if not fields_to_save:
            QMessageBox.information(
                self,
                "No Changes",
                "No metadata fields have values to save."
            )
            return
        
        # Confirm save with user
        reply = QMessageBox.question(
            self,
            "Save Metadata",
            f"Save metadata to image file?\n\n"
            f"File: {os.path.basename(self.current_image_path)}\n"
            f"Fields to save: {len(fields_to_save)}\n\n"
            f"This will embed the metadata into the image file\n"
            f"in a format that AI tools can read.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Save metadata
        try:
            success = save_metadata(self.current_image_path, meta)
            
            if success:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Metadata saved successfully!\n\n"
                    f"Saved {len(fields_to_save)} fields to:\n"
                    f"{os.path.basename(self.current_image_path)}\n\n"
                    f"The metadata is now embedded in the image\n"
                    f"and can be read by other AI tools."
                )
                
                # Update statistics with new metadata
                optimized_stats_tracker.add_image_metadata(self.current_image_path, meta)
                
                # Refresh raw metadata view
                self.load_metadata()
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Failed to save metadata to:\n{os.path.basename(self.current_image_path)}\n\n"
                    f"Please check that the file is not read-only\n"
                    f"and that you have write permissions."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving metadata:\n\n{str(e)}"
            )

class BatchTab(QWidget):
    """Batch processing tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Placeholder content
        placeholder = QLabel("Batch Processing")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setFont(QFont("Arial", 16))
        layout.addWidget(placeholder)
        
        info_label = QLabel("This tab will contain batch processing tools:\n" +
                           "• Batch rename operations\n" +
                           "• Bulk metadata editing\n" +
                           "• File organization tools\n" +
                           "• Progress tracking")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

class SettingsTab(QWidget):
    """Settings and preferences tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Settings splitter
        splitter = ResizableSplitter(Qt.Horizontal, 'settings_splitter')
        
        # Left: Categories
        categories = QListWidget()
        categories.addItems([
            "General",
            "Display",
            "Metadata",
            "Shortcuts",
            "Plugins",
            "Advanced"
        ])
        categories.setMaximumWidth(200)
        splitter.addWidget(categories)
        
        # Right: Settings content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        settings_label = QLabel("Settings")
        settings_label.setFont(QFont("Arial", 16))
        content_layout.addWidget(settings_label)
        
        info_label = QLabel("Settings panels will be implemented here based on selected category")
        content_layout.addWidget(info_label)
        
        splitter.addWidget(content)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        
        splitter.restore_state()

class MetaPicPickTabbed(QMainWindow):
    """Enhanced main application with integrated utilities and configuration"""
    
    def __init__(self):
        super().__init__()
        
        # Get display settings from configuration
        display_settings = get_display_settings()
        
        self.setWindowTitle("MetaPicPick - Enhanced v2.0")
        self.setGeometry(
            100, 100, 
            display_settings['window_width'], 
            display_settings['window_height']
        )
        
        # Initialize components with error handling
        try:
            logger.info("Initializing plugin manager...")
            self.plugin_manager = PluginManager("parsers")
            logger.info(f"Loaded {len(self.plugin_manager.plugins)} parser plugins")
        except Exception as e:
            handle_gui_error(e, "PluginManager", "initialization")
            self.plugin_manager = None
        
        logger.info("Initializing main application window...")
        self.init_ui()
        self.restore_window_state()
        logger.info("Main application window initialized successfully")
        
    def init_ui(self):
        """Initialize the tabbed user interface"""
        # Create central tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create tabs with error handling
        try:
            plugins = self.plugin_manager.plugins if self.plugin_manager else []
            
            logger.debug("Creating Library tab...")
            self.library_tab = LibraryTab(plugins)
            
            logger.debug("Creating Metadata tab...")
            self.metadata_tab = MetadataTab(plugins)
            
            logger.debug("Creating Batch tab...")
            self.batch_tab = BatchTab()
            
            logger.debug("Creating Statistics tab...")
            self.statistics_tab = StatisticsTab()
            
            logger.debug("Creating Settings tab...")
            self.settings_tab = SettingsTab()
            
            logger.debug("All tabs created successfully")
        except Exception as e:
            handle_gui_error(e, "MainWindow", "creating tabs")
        
        # Add tabs to widget
        self.tab_widget.addTab(self.library_tab, "📁 Library")
        self.tab_widget.addTab(self.metadata_tab, "📝 Metadata")
        self.tab_widget.addTab(self.batch_tab, "⚡ Batch")
        self.tab_widget.addTab(self.statistics_tab, "📊 Statistics")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
        # Connect tab change to save current tab and handle statistics tab visibility
        self.tab_widget.currentChanged.connect(self.save_current_tab)
        self.tab_widget.currentChanged.connect(self.statistics_tab.on_tab_changed)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Enhanced parsers loaded")
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Load Folder', self.library_tab.load_folder)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # View menu
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Reset Layout', self.reset_layout)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
    
    def save_current_tab(self, index):
        """Save current tab preference"""
        settings = QSettings('MetaPicPick', 'Layout')
        settings.setValue('current_tab', index)
    
    def restore_window_state(self):
        """Restore window state and current tab"""
        settings = QSettings('MetaPicPick', 'Layout')
        
        # Restore window geometry
        geometry = settings.value('window_geometry')
        if geometry:
            self.restoreGeometry(geometry)
            
        # Restore current tab
        current_tab = settings.value('current_tab', 0, type=int)
        if current_tab < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(current_tab)
    
    def reset_layout(self):
        """Reset all layouts to defaults"""
        reply = QMessageBox.question(
            self, 'Reset Layout',
            'Reset all panel layouts to defaults?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            settings = QSettings('MetaPicPick', 'Layout')
            settings.clear()
            QMessageBox.information(self, 'Layout Reset', 'Please restart the application to see changes.')
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 'About MetaPicPick',
            'MetaPicPick - Enhanced Metadata Manager\n\n' +
            'A unified GUI for extracting and managing AI image metadata.\n' +
            'Version 1.2 - Enhanced Parsers with Tabbed Interface'
        )
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Save window geometry
        settings = QSettings('MetaPicPick', 'Layout')
        settings.setValue('window_geometry', self.saveGeometry())
        
        # Save splitter states
        for splitter in self.findChildren(ResizableSplitter):
            splitter.save_state()
            
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application properties for settings
    app.setOrganizationName("MetaPicPick")
    app.setApplicationName("MetaPicPick")
    
    window = MetaPicPickTabbed()
    window.show()
    
    sys.exit(app.exec_())

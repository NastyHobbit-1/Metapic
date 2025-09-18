#!/usr/bin/env python3
"""
MetaPic Enhanced GUI - Comprehensive tabbed interface
Integrates advanced features from H:\Metapic with modern architecture
"""

from __future__ import annotations
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from collections import defaultdict, Counter

# Modern imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget,
    QListWidgetItem, QTextEdit, QLineEdit, QPushButton, QLabel,
    QFileDialog, QMessageBox, QProgressBar, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMenu, QAction, QStatusBar
)
from PySide6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PySide6.QtGui import QPixmap, QFont, QIcon, QAction

# Import from existing modern architecture
from ..models import ImageMeta
from ..extract import exiftool_batch
from ..normalize import Normalizer
from ..utils import iter_images
from ..plugins import run_parse_chain
from ..bulk import plan_rename

class PerformanceTimer:
    """Simple performance timer for GUI operations"""
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = __import__('time').time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = __import__('time').time() - self.start_time
            print(f"[PERF] {self.operation_name}: {duration:.3f}s")

class ResizableSplitter(QSplitter):
    """Enhanced splitter with persistence and better defaults"""
    
    def __init__(self, orientation, settings_key: str, parent=None):
        super().__init__(orientation, parent)
        self.settings_key = settings_key
        self.settings = QSettings('MetaPic', 'Layout')
        
        # Set splitter properties
        self.setChildrenCollapsible(False)
        self.setHandleWidth(6)
    
    def save_state(self):
        """Save splitter state to settings"""
        try:
            self.settings.setValue(self.settings_key, self.saveState())
        except Exception as e:
            print(f"Error saving splitter state: {e}")
    
    def restore_state(self):
        """Restore splitter state from settings"""
        try:
            state = self.settings.value(self.settings_key)
            if state:
                self.restoreState(state)
        except Exception as e:
            print(f"Error restoring splitter state: {e}")

class LibraryTab(QWidget):
    """Library tab with folder browser, image list, and metadata preview"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loaded_images: List[ImageMeta] = []
        self.current_image_path: Optional[str] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the library tab interface"""
        layout = QVBoxLayout(self)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        self.load_folder_btn = QPushButton("Load Folder")
        self.load_folder_btn.clicked.connect(self.load_folder)
        controls_layout.addWidget(self.load_folder_btn)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search images...")
        self.search_edit.textChanged.connect(self.filter_images)
        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_edit)
        
        self.model_filter = QComboBox()
        self.model_filter.addItem("All Models")
        self.model_filter.currentTextChanged.connect(self.filter_images)
        controls_layout.addWidget(QLabel("Model:"))
        controls_layout.addWidget(self.model_filter)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Main content area
        main_splitter = ResizableSplitter(Qt.Horizontal, "library_main", self)
        
        # Left panel - Image list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.on_image_selected)
        left_layout.addWidget(QLabel("Images:"))
        left_layout.addWidget(self.image_list)
        
        # Image count label
        self.image_count_label = QLabel("No images loaded")
        left_layout.addWidget(self.image_count_label)
        
        main_splitter.addWidget(left_panel)
        
        # Right panel - Metadata preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.metadata_preview = QTextEdit()
        self.metadata_preview.setReadOnly(True)
        self.metadata_preview.setFont(QFont("Consolas", 9))
        right_layout.addWidget(QLabel("Metadata Preview:"))
        right_layout.addWidget(self.metadata_preview)
        
        main_splitter.addWidget(right_panel)
        
        # Set initial splitter proportions
        main_splitter.setSizes([400, 600])
        
        layout.addWidget(main_splitter)
    
    def load_folder(self):
        """Load images from selected folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not folder:
            return
        
        try:
            with PerformanceTimer("load_folder"):
                # Get image files
                image_files = list(iter_images([folder]))
                if not image_files:
                    QMessageBox.information(self, "No Images", "No supported images found in the selected folder.")
                    return
                
                # Extract metadata
                raw_metadata = exiftool_batch(image_files)
                normalizer = Normalizer()
                
                self.loaded_images = []
                for image_file in image_files:
                    raw = raw_metadata.get(str(image_file), {})
                    parsed = run_parse_chain(raw)
                    parsed.update(normalizer.parse_text_block(parsed.get("prompt", "")))
                    
                    # Create ImageMeta object
                    meta = ImageMeta(
                        path=str(image_file),
                        metadata_raw=raw,
                        parsed_raw=parsed,
                        **{k: v for k, v in parsed.items() if k in ImageMeta.model_fields and v is not None}
                    )
                    self.loaded_images.append(meta)
                
                self.populate_image_list()
                self.update_model_filter()
                self.image_count_label.setText(f"Loaded {len(self.loaded_images)} images")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load folder: {e}")
    
    def populate_image_list(self):
        """Populate the image list widget"""
        self.image_list.clear()
        
        for meta in self.loaded_images:
            item = QListWidgetItem()
            item.setText(f"{Path(meta.path).name}")
            item.setData(Qt.UserRole, meta.path)
            
            # Add metadata info to display
            info_parts = []
            if meta.model:
                info_parts.append(f"Model: {meta.model}")
            if meta.steps:
                info_parts.append(f"Steps: {meta.steps}")
            if meta.cfg:
                info_parts.append(f"CFG: {meta.cfg}")
            
            if info_parts:
                item.setToolTip("\n".join(info_parts))
            
            self.image_list.addItem(item)
    
    def update_model_filter(self):
        """Update the model filter dropdown"""
        models = set()
        for meta in self.loaded_images:
            if meta.model:
                models.add(meta.model)
        
        current_text = self.model_filter.currentText()
        self.model_filter.clear()
        self.model_filter.addItem("All Models")
        
        for model in sorted(models):
            self.model_filter.addItem(model)
        
        # Restore selection if possible
        index = self.model_filter.findText(current_text)
        if index >= 0:
            self.model_filter.setCurrentIndex(index)
    
    def filter_images(self):
        """Filter images based on search and model criteria"""
        search_text = self.search_edit.text().lower()
        selected_model = self.model_filter.currentText()
        
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            image_path = item.data(Qt.UserRole)
            
            # Find corresponding metadata
            meta = next((m for m in self.loaded_images if m.path == image_path), None)
            if not meta:
                continue
            
            # Check search criteria
            matches_search = (
                search_text in Path(image_path).name.lower() or
                (meta.prompt and search_text in meta.prompt.lower()) or
                (meta.model and search_text in meta.model.lower())
            )
            
            # Check model filter
            matches_model = (
                selected_model == "All Models" or
                (meta.model and meta.model == selected_model)
            )
            
            item.setHidden(not (matches_search and matches_model))
    
    def on_image_selected(self, item: QListWidgetItem):
        """Handle image selection"""
        image_path = item.data(Qt.UserRole)
        self.current_image_path = image_path
        
        # Find metadata for selected image
        meta = next((m for m in self.loaded_images if m.path == image_path), None)
        if meta:
            self.show_metadata_preview(meta)
    
    def show_metadata_preview(self, meta: ImageMeta):
        """Show metadata preview for selected image"""
        preview_text = f"File: {Path(meta.path).name}\n"
        preview_text += f"Path: {meta.path}\n"
        preview_text += f"Size: {meta.width}x{meta.height}\n" if meta.width and meta.height else ""
        preview_text += f"Format: {meta.format}\n" if meta.format else ""
        preview_text += f"Size: {meta.size_bytes} bytes\n" if meta.size_bytes else ""
        preview_text += "\n"
        
        if meta.model:
            preview_text += f"Model: {meta.model}\n"
        if meta.base_model:
            preview_text += f"Base Model: {meta.base_model}\n"
        if meta.sampler:
            preview_text += f"Sampler: {meta.sampler}\n"
        if meta.steps:
            preview_text += f"Steps: {meta.steps}\n"
        if meta.cfg:
            preview_text += f"CFG Scale: {meta.cfg}\n"
        if meta.seed:
            preview_text += f"Seed: {meta.seed}\n"
        if meta.prompt:
            preview_text += f"\nPrompt:\n{meta.prompt}\n"
        if meta.negative_prompt:
            preview_text += f"\nNegative Prompt:\n{meta.negative_prompt}\n"
        
        self.metadata_preview.setText(preview_text)

class StatisticsTab(QWidget):
    """Statistics tab with model and tag analysis"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_data: Dict[str, Any] = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the statistics tab interface"""
        layout = QVBoxLayout(self)
        
        # Statistics summary
        summary_group = QGroupBox("Summary")
        summary_layout = QFormLayout(summary_group)
        
        self.total_images_label = QLabel("0")
        self.total_models_label = QLabel("0")
        self.total_tags_label = QLabel("0")
        
        summary_layout.addRow("Total Images:", self.total_images_label)
        summary_layout.addRow("Unique Models:", self.total_models_label)
        summary_layout.addRow("Unique Tags:", self.total_tags_label)
        
        layout.addWidget(summary_group)
        
        # Models table
        models_group = QGroupBox("Models")
        models_layout = QVBoxLayout(models_group)
        
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(2)
        self.models_table.setHorizontalHeaderLabels(["Model", "Count"])
        self.models_table.horizontalHeader().setStretchLastSection(True)
        
        models_layout.addWidget(self.models_table)
        layout.addWidget(models_group)
        
        # Tags table
        tags_group = QGroupBox("Top Tags")
        tags_layout = QVBoxLayout(tags_group)
        
        self.tags_table = QTableWidget()
        self.tags_table.setColumnCount(2)
        self.tags_table.setHorizontalHeaderLabels(["Tag", "Count"])
        self.tags_table.horizontalHeader().setStretchLastSection(True)
        
        tags_layout.addWidget(self.tags_table)
        layout.addWidget(tags_group)
    
    def update_statistics(self, images: List[ImageMeta]):
        """Update statistics with new image data"""
        if not images:
            self.clear_statistics()
            return
        
        # Calculate statistics
        models = Counter()
        positive_tags = Counter()
        negative_tags = Counter()
        
        for meta in images:
            if meta.model:
                models[meta.model] += 1
            
            # Extract tags from prompts
            if meta.prompt:
                tags = [tag.strip() for tag in meta.prompt.split(',') if tag.strip()]
                for tag in tags:
                    positive_tags[tag] += 1
            
            if meta.negative_prompt:
                tags = [tag.strip() for tag in meta.negative_prompt.split(',') if tag.strip()]
                for tag in tags:
                    negative_tags[tag] += 1
        
        # Update summary
        self.total_images_label.setText(str(len(images)))
        self.total_models_label.setText(str(len(models)))
        self.total_tags_label.setText(str(len(positive_tags) + len(negative_tags)))
        
        # Update models table
        self.populate_table(self.models_table, models.most_common(20))
        
        # Update tags table (combine positive and negative)
        all_tags = positive_tags + negative_tags
        self.populate_table(self.tags_table, all_tags.most_common(50))
    
    def populate_table(self, table: QTableWidget, data: List[tuple]):
        """Populate a table with data"""
        table.setRowCount(len(data))
        
        for row, (name, count) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(str(name)))
            table.setItem(row, 1, QTableWidgetItem(str(count)))
    
    def clear_statistics(self):
        """Clear all statistics"""
        self.total_images_label.setText("0")
        self.total_models_label.setText("0")
        self.total_tags_label.setText("0")
        self.models_table.setRowCount(0)
        self.tags_table.setRowCount(0)

class MetadataTab(QWidget):
    """Metadata editing tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_meta: Optional[ImageMeta] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the metadata editing interface"""
        layout = QVBoxLayout(self)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.file_edit)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        layout.addLayout(file_layout)
        
        # Metadata editing form
        form_group = QGroupBox("Metadata")
        form_layout = QFormLayout(form_group)
        
        self.model_edit = QLineEdit()
        self.base_model_edit = QLineEdit()
        self.sampler_edit = QLineEdit()
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 1000)
        self.cfg_spin = QDoubleSpinBox()
        self.cfg_spin.setRange(0.1, 50.0)
        self.cfg_spin.setDecimals(1)
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2**32-1)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMaximumHeight(100)
        self.negative_prompt_edit = QTextEdit()
        self.negative_prompt_edit.setMaximumHeight(100)
        
        form_layout.addRow("Model:", self.model_edit)
        form_layout.addRow("Base Model:", self.base_model_edit)
        form_layout.addRow("Sampler:", self.sampler_edit)
        form_layout.addRow("Steps:", self.steps_spin)
        form_layout.addRow("CFG Scale:", self.cfg_spin)
        form_layout.addRow("Seed:", self.seed_spin)
        form_layout.addRow("Prompt:", self.prompt_edit)
        form_layout.addRow("Negative Prompt:", self.negative_prompt_edit)
        
        layout.addWidget(form_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load Metadata")
        self.load_btn.clicked.connect(self.load_metadata)
        self.load_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Save Metadata")
        self.save_btn.clicked.connect(self.save_metadata)
        self.save_btn.setEnabled(False)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def browse_file(self):
        """Browse for image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "",
            "Image Files (*.png *.jpg *.jpeg *.webp *.tiff *.tif)"
        )
        
        if file_path:
            self.file_edit.setText(file_path)
            self.load_btn.setEnabled(True)
            self.current_meta = None
    
    def load_metadata(self):
        """Load metadata from selected file"""
        file_path = self.file_edit.text()
        if not file_path:
            return
        
        try:
            # Extract metadata using existing system
            image_files = [Path(file_path)]
            raw_metadata = exiftool_batch(image_files)
            normalizer = Normalizer()
            
            raw = raw_metadata.get(file_path, {})
            parsed = run_parse_chain(raw)
            parsed.update(normalizer.parse_text_block(parsed.get("prompt", "")))
            
            # Create ImageMeta object
            self.current_meta = ImageMeta(
                path=file_path,
                metadata_raw=raw,
                parsed_raw=parsed,
                **{k: v for k, v in parsed.items() if k in ImageMeta.model_fields and v is not None}
            )
            
            # Populate form
            self.populate_form()
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load metadata: {e}")
    
    def populate_form(self):
        """Populate form with current metadata"""
        if not self.current_meta:
            return
        
        meta = self.current_meta
        
        self.model_edit.setText(meta.model or "")
        self.base_model_edit.setText(meta.base_model or "")
        self.sampler_edit.setText(meta.sampler or "")
        self.steps_spin.setValue(meta.steps or 20)
        self.cfg_spin.setValue(meta.cfg or 7.0)
        self.seed_spin.setValue(meta.seed or 0)
        self.prompt_edit.setPlainText(meta.prompt or "")
        self.negative_prompt_edit.setPlainText(meta.negative_prompt or "")
    
    def save_metadata(self):
        """Save metadata to file"""
        if not self.current_meta:
            return
        
        # TODO: Implement metadata saving
        QMessageBox.information(self, "Save", "Metadata saving not yet implemented")

class MetaPicEnhancedGUI(QMainWindow):
    """Enhanced MetaPic GUI with comprehensive tabbed interface"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaPic Enhanced")
        self.setGeometry(100, 100, 1400, 900)
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Load settings
        self.load_settings()
    
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.library_tab = LibraryTab()
        self.statistics_tab = StatisticsTab()
        self.metadata_tab = MetadataTab()
        
        self.tab_widget.addTab(self.library_tab, "Library")
        self.tab_widget.addTab(self.statistics_tab, "Statistics")
        self.tab_widget.addTab(self.metadata_tab, "Metadata")
        
        layout.addWidget(self.tab_widget)
        
        # Connect tab changes to update statistics
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        load_action = QAction("Load Folder", self)
        load_action.triggered.connect(self.library_tab.load_folder)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def on_tab_changed(self, index: int):
        """Handle tab change events"""
        if index == 1:  # Statistics tab
            # Update statistics with current library data
            self.statistics_tab.update_statistics(self.library_tab.loaded_images)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About MetaPic Enhanced", 
                         "MetaPic Enhanced v2.0\n\n"
                         "A comprehensive AI image metadata management tool\n"
                         "Built with modern Python and PySide6")
    
    def load_settings(self):
        """Load application settings"""
        settings = QSettings('MetaPic', 'Enhanced')
        
        # Restore window geometry
        geometry = settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore window state
        state = settings.value('windowState')
        if state:
            self.restoreState(state)
    
    def save_settings(self):
        """Save application settings"""
        settings = QSettings('MetaPic', 'Enhanced')
        
        # Save window geometry and state
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.save_settings()
        event.accept()

def main():
    """Main entry point for the enhanced GUI"""
    app = QApplication(sys.argv)
    app.setApplicationName("MetaPic Enhanced")
    app.setOrganizationName("MetaPic")
    app.setApplicationVersion("2.0")
    
    window = MetaPicEnhancedGUI()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())

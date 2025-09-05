#!/usr/bin/env python3
"""
Model Name Manager Dialog
Provides interface for viewing and editing model name mappings
"""

import os
import json
from collections import Counter
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QTextEdit,
    QMessageBox, QSplitter, QGroupBox, QFormLayout, QComboBox,
    QAbstractItemView, QProgressBar, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

class ModelConsolidationWorker(QThread):
    """Worker thread for model name consolidation"""
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    
    def __init__(self, stats_tracker):
        super().__init__()
        self.stats_tracker = stats_tracker
        
    def run(self):
        try:
            self.progress_updated.emit(20, "Analyzing current model names...")
            result = self.stats_tracker.consolidate_model_names()
            self.progress_updated.emit(100, "Model consolidation complete!")
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"error": str(e)})

class ModelNameManagerDialog(QDialog):
    """Dialog for managing model name mappings and normalization"""
    
    def __init__(self, stats_tracker, parent=None):
        super().__init__(parent)
        self.stats_tracker = stats_tracker
        self.setWindowTitle("Model Name Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Tab 1: Current Models
        models_tab = self.create_models_tab()
        tab_widget.addTab(models_tab, "Current Models")
        
        # Tab 2: Custom Mappings
        mappings_tab = self.create_mappings_tab()
        tab_widget.addTab(mappings_tab, "Custom Mappings")
        
        # Tab 3: Normalization Rules
        rules_tab = self.create_rules_tab()
        tab_widget.addTab(rules_tab, "Normalization Rules")
        
        layout.addWidget(tab_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.consolidate_button = QPushButton("Consolidate Model Names")
        self.consolidate_button.clicked.connect(self.consolidate_models)
        self.consolidate_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.consolidate_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_models_tab(self):
        """Create the current models tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header info
        info_layout = QFormLayout()
        self.total_models_label = QLabel("0")
        self.total_usage_label = QLabel("0")
        info_layout.addRow("Total Model Names:", self.total_models_label)
        info_layout.addRow("Total Model Usage:", self.total_usage_label)
        layout.addLayout(info_layout)
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search model names...")
        self.search_box.textChanged.connect(self.filter_models)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_box)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Models table
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(4)
        self.models_table.setHorizontalHeaderLabels(["Original Model Name", "Normalized Name", "Usage Count", "Actions"])
        
        # Configure table
        header = self.models_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Original name
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Normalized name  
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Count
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Actions
        
        self.models_table.setAlternatingRowColors(True)
        self.models_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        layout.addWidget(self.models_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_mappings_tab(self):
        """Create the custom mappings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Add new mapping section
        mapping_group = QGroupBox("Add Custom Mapping")
        mapping_layout = QFormLayout()
        
        self.original_name_input = QLineEdit()
        self.original_name_input.setPlaceholderText("Enter original model name/path...")
        
        self.custom_name_input = QLineEdit()
        self.custom_name_input.setPlaceholderText("Enter display name...")
        
        add_mapping_button = QPushButton("Add Mapping")
        add_mapping_button.clicked.connect(self.add_custom_mapping)
        
        mapping_layout.addRow("Original Name:", self.original_name_input)
        mapping_layout.addRow("Display Name:", self.custom_name_input)
        mapping_layout.addWidget(add_mapping_button)
        
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Custom mappings table
        mappings_group = QGroupBox("Current Custom Mappings")
        mappings_layout = QVBoxLayout()
        
        self.mappings_table = QTableWidget()
        self.mappings_table.setColumnCount(3)
        self.mappings_table.setHorizontalHeaderLabels(["Original Name", "Custom Display Name", "Actions"])
        
        header = self.mappings_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.mappings_table.setAlternatingRowColors(True)
        
        mappings_layout.addWidget(self.mappings_table)
        mappings_group.setLayout(mappings_layout)
        layout.addWidget(mappings_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_rules_tab(self):
        """Create the normalization rules tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Rules info
        info_text = QTextEdit()
        info_text.setMaximumHeight(300)
        info_text.setReadOnly(True)
        
        rules_info = """
Model Name Normalization Rules:

1. Extract filename from full path
   Example: "Checkpoints\\Z\\PDXL\\WIP\\Fucktastic_2.5D_v2.2_PDXL.safetensors"
   → "Fucktastic_2.5D_v2.2_PDXL.safetensors"

2. Remove file extensions
   Extensions removed: .safetensors, .ckpt, .pt, .pth, .bin
   Example: "Fucktastic_2.5D_v2.2_PDXL.safetensors" → "Fucktastic_2.5D_v2.2_PDXL"

3. Remove common prefixes
   Prefixes removed: checkpoint_, model_, final_
   Example: "model_Fucktastic_2.5D_v2.2_PDXL" → "Fucktastic_2.5D_v2.2_PDXL"

4. Remove common suffixes  
   Suffixes removed: _final, _checkpoint, _model, _v1, _v2, _v3, _epoch
   Example: "Fucktastic_2.5D_v2.2_PDXL_final" → "Fucktastic_2.5D_v2.2_PDXL"

5. Clean up formatting
   Replace underscores with spaces and remove extra whitespace
   Example: "Fucktastic_2.5D_v2.2_PDXL" → "Fucktastic 2.5D v2.2 PDXL"

Custom mappings override automatic normalization rules.
        """
        
        info_text.setPlainText(rules_info.strip())
        layout.addWidget(info_text)
        
        # Test normalization
        test_group = QGroupBox("Test Normalization")
        test_layout = QFormLayout()
        
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Enter model path or name to test...")
        self.test_input.textChanged.connect(self.update_test_result)
        
        self.test_result = QLineEdit()
        self.test_result.setReadOnly(True)
        self.test_result.setStyleSheet("background-color: #f0f0f0;")
        
        test_layout.addRow("Input:", self.test_input)
        test_layout.addRow("Result:", self.test_result)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        widget.setLayout(layout)
        return widget
    
    def load_data(self):
        """Load current model data and mappings"""
        # Load models
        models = self.stats_tracker.get_top_models(0)  # Get all models
        self.total_models_label.setText(str(len(models)))
        
        total_usage = sum(count for _, count in models)
        self.total_usage_label.setText(str(total_usage))
        
        # Load model table
        self.models_table.setRowCount(len(models))
        
        for row, (model_name, count) in enumerate(models):
            # Original name
            original_item = QTableWidgetItem(model_name)
            self.models_table.setItem(row, 0, original_item)
            
            # Normalized name (what it would become)
            normalized = self.stats_tracker.normalize_model_name(model_name)
            normalized_item = QTableWidgetItem(normalized)
            if normalized != model_name:
                normalized_item.setBackground(QColor(255, 255, 204))  # Light yellow highlight
            self.models_table.setItem(row, 1, normalized_item)
            
            # Usage count
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.models_table.setItem(row, 2, count_item)
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            
            mapping_button = QPushButton("Create Mapping")
            mapping_button.clicked.connect(lambda checked, orig=model_name: self.create_mapping_for_model(orig))
            mapping_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
            action_layout.addWidget(mapping_button)
            
            remove_button = QPushButton("🗑️")
            remove_button.clicked.connect(lambda checked, orig=model_name, cnt=count: self.remove_model(orig, cnt))
            remove_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
            remove_button.setToolTip("Remove this model from statistics")
            action_layout.addWidget(remove_button)
            
            self.models_table.setCellWidget(row, 3, action_widget)
        
        # Load mappings table
        self.load_mappings_table()
    
    def load_mappings_table(self):
        """Load the custom mappings table"""
        mappings = self.stats_tracker.get_all_model_mappings()
        self.mappings_table.setRowCount(len(mappings))
        
        for row, (original, custom) in enumerate(mappings.items()):
            # Original name
            original_item = QTableWidgetItem(original)
            self.mappings_table.setItem(row, 0, original_item)
            
            # Custom name
            custom_item = QTableWidgetItem(custom)
            self.mappings_table.setItem(row, 1, custom_item)
            
            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, orig=original: self.remove_mapping(orig))
            delete_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
            self.mappings_table.setCellWidget(row, 2, delete_button)
    
    def filter_models(self):
        """Filter models table based on search text"""
        search_text = self.search_box.text().lower()
        
        for row in range(self.models_table.rowCount()):
            original_item = self.models_table.item(row, 0)
            normalized_item = self.models_table.item(row, 1)
            
            original_text = original_item.text().lower() if original_item else ""
            normalized_text = normalized_item.text().lower() if normalized_item else ""
            
            visible = (search_text in original_text or search_text in normalized_text) if search_text else True
            self.models_table.setRowHidden(row, not visible)
    
    def create_mapping_for_model(self, original_name):
        """Pre-fill the mapping form for a specific model"""
        self.original_name_input.setText(original_name)
        self.custom_name_input.setFocus()
        
        # Switch to mappings tab
        parent_widget = self.parent()
        if hasattr(parent_widget, 'setCurrentIndex'):
            parent_widget.setCurrentIndex(1)
    
    def add_custom_mapping(self):
        """Add a new custom model mapping"""
        original = self.original_name_input.text().strip()
        custom = self.custom_name_input.text().strip()
        
        if not original or not custom:
            QMessageBox.warning(self, "Invalid Input", "Both original and custom names are required.")
            return
        
        self.stats_tracker.set_model_name_mapping(original, custom)
        
        # Clear inputs
        self.original_name_input.clear()
        self.custom_name_input.clear()
        
        # Reload data
        self.load_mappings_table()
        self.load_data()  # Refresh models table to show updated mappings
        
        QMessageBox.information(self, "Mapping Added", f"Created mapping: {original} → {custom}")
    
    def remove_mapping(self, original_name):
        """Remove a custom model mapping"""
        reply = QMessageBox.question(
            self, "Remove Mapping",
            f"Remove custom mapping for '{original_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stats_tracker.remove_model_name_mapping(original_name)
            self.load_mappings_table()
            self.load_data()  # Refresh models table
            QMessageBox.information(self, "Mapping Removed", f"Removed mapping for '{original_name}'")
    
    def update_test_result(self):
        """Update the test result when input changes"""
        test_input = self.test_input.text().strip()
        if test_input:
            result = self.stats_tracker.normalize_model_name(test_input)
            self.test_result.setText(result)
        else:
            self.test_result.clear()
    
    def consolidate_models(self):
        """Apply model name consolidation"""
        reply = QMessageBox.question(
            self, "Consolidate Model Names",
            "This will apply normalization rules to all model names in your statistics. " +
            "Model names with the same normalized form will be combined. " +
            "This action cannot be undone.\\n\\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        
        # Start worker thread
        self.worker = ModelConsolidationWorker(self.stats_tracker)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.consolidation_finished)
        self.worker.start()
        
        # Disable button during operation
        self.consolidate_button.setEnabled(False)
    
    def update_progress(self, percent, message):
        """Update progress bar and label"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)
    
    def consolidation_finished(self, results):
        """Handle consolidation completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.consolidate_button.setEnabled(True)
        
        if "error" in results:
            QMessageBox.critical(self, "Error", f"Model consolidation failed: {results['error']}")
            return
        
        # Show results
        message = f"Model consolidation completed!\\n\\n"
        message += f"Models before: {results.get('models_before', 0)}\\n"
        message += f"Models after: {results.get('models_after', 0)}\\n"
        message += f"Names changed: {results.get('changes_made', 0)}"
        
        QMessageBox.information(self, "Consolidation Complete", message)
        
        # Reload data
        self.load_data()
    
    def remove_model(self, model_name, count):
        """Remove a model from statistics entirely"""
        reply = QMessageBox.question(
            self, "Remove Model Permanently",
            f"Permanently remove model '{model_name}' from statistics?\n\n" +
            f"This will remove {count} occurrences of this model.\n\n" +
            "⚠️ This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.stats_tracker.remove_model(model_name)
                
                if result['removed']:
                    # Reload data
                    self.load_data()
                    
                    QMessageBox.information(
                        self, "Model Removed",
                        f"Successfully removed model '{model_name}' ({result['count']} occurrences) from statistics."
                    )
                else:
                    QMessageBox.warning(
                        self, "Model Not Found",
                        f"Model '{model_name}' was not found in statistics."
                    )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove model: {str(e)}")

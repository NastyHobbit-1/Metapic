#!/usr/bin/env python3
"""
Advanced Tag Consolidation Dialog
Provides interactive tag consolidation with custom rules and blacklisting
"""

import json
import os
import datetime
from collections import defaultdict
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit, QLabel,
    QTextEdit, QComboBox, QCheckBox, QMessageBox, QProgressBar,
    QSplitter, QGroupBox, QFormLayout, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class TagConsolidationWorker(QThread):
    """Worker thread for tag consolidation operations"""
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    
    def __init__(self, stats_tracker, consolidation_rules, blacklists):
        super().__init__()
        self.stats_tracker = stats_tracker
        self.consolidation_rules = consolidation_rules
        self.blacklists = blacklists
        
    def run(self):
        try:
            self.progress_updated.emit(10, "Loading current statistics...")
            
            # Apply consolidation rules and blacklists
            results = self.stats_tracker.apply_custom_consolidation(
                self.consolidation_rules, 
                self.blacklists,
                progress_callback=self.update_progress
            )
            
            self.progress_updated.emit(100, "Consolidation complete!")
            self.finished.emit(results)
            
        except Exception as e:
            self.finished.emit({"error": str(e)})
    
    def update_progress(self, percent, message):
        self.progress_updated.emit(percent, message)

class AdvancedTagConsolidationDialog(QDialog):
    """Advanced dialog for tag consolidation with custom rules and blacklisting"""
    
    def __init__(self, stats_tracker, parent=None):
        super().__init__(parent)
        self.stats_tracker = stats_tracker
        self.setWindowTitle("Advanced Tag Consolidation")
        self.setGeometry(100, 100, 1200, 800)
        
        # Load existing rules and blacklists
        self.consolidation_rules_file = "tag_consolidation_rules.json"
        self.blacklists_file = "tag_blacklists.json"
        
        self.consolidation_rules = self.load_consolidation_rules()
        self.blacklists = self.load_blacklists()
        
        self.setup_ui()
        self.load_current_tags()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Tab 1: Tag Consolidation
        consolidation_tab = self.create_consolidation_tab()
        tab_widget.addTab(consolidation_tab, "Tag Consolidation")
        
        # Tab 2: Blacklists
        blacklist_tab = self.create_blacklist_tab()
        tab_widget.addTab(blacklist_tab, "Blacklists")
        
        # Tab 3: Category Management
        category_tab = self.create_category_management_tab()
        tab_widget.addTab(category_tab, "Category Management")
        
        # Tab 4: Rules Management
        rules_tab = self.create_rules_tab()
        tab_widget.addTab(rules_tab, "Rules & History")
        
        layout.addWidget(tab_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("Preview Changes")
        self.preview_button.clicked.connect(self.preview_changes)
        
        self.apply_button = QPushButton("Apply Consolidation")
        self.apply_button.clicked.connect(self.apply_consolidation)
        
        self.save_rules_button = QPushButton("Save Rules")
        self.save_rules_button.clicked.connect(self.save_rules)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_rules_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_consolidation_tab(self):
        """Create the tag consolidation tab"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Left side - Available tags
        left_group = QGroupBox("Available Tags")
        left_layout = QVBoxLayout()
        
        # Category selection
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Positive Tags", "Negative Tags"])
        self.category_combo.currentTextChanged.connect(self.load_category_tags)
        left_layout.addWidget(self.category_combo)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tags...")
        self.search_box.textChanged.connect(self.filter_tags)
        left_layout.addWidget(self.search_box)
        
        # Tags list with counts
        self.tags_list = QListWidget()
        self.tags_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        left_layout.addWidget(self.tags_list)
        
        # Selection info
        self.selection_info = QLabel("No tags selected")
        left_layout.addWidget(self.selection_info)
        
        left_group.setLayout(left_layout)
        layout.addWidget(left_group)
        
        # Middle - Actions
        middle_layout = QVBoxLayout()
        
        self.add_to_rule_button = QPushButton("→ Add to Rule →")
        self.add_to_rule_button.clicked.connect(self.add_selected_to_rule)
        
        self.add_to_blacklist_button = QPushButton("→ Add to Blacklist →")
        self.add_to_blacklist_button.clicked.connect(self.add_selected_to_blacklist)
        
        self.remove_from_rule_button = QPushButton("← Remove from Rule ←")
        self.remove_from_rule_button.clicked.connect(self.remove_from_rule)
        
        middle_layout.addStretch()
        middle_layout.addWidget(self.add_to_rule_button)
        middle_layout.addWidget(self.add_to_blacklist_button)
        middle_layout.addWidget(self.remove_from_rule_button)
        middle_layout.addStretch()
        
        layout.addLayout(middle_layout)
        
        # Right side - Consolidation rules
        right_group = QGroupBox("Consolidation Rules")
        right_layout = QVBoxLayout()
        
        # Target tag input
        target_layout = QFormLayout()
        self.target_tag_input = QLineEdit()
        self.target_tag_input.setPlaceholderText("Enter target tag name...")
        target_layout.addRow("Consolidate to:", self.target_tag_input)
        right_layout.addLayout(target_layout)
        
        # Current rule tags
        self.rule_tags_list = QListWidget()
        self.rule_tags_list.setMaximumHeight(200)
        right_layout.addWidget(QLabel("Tags to consolidate:"))
        right_layout.addWidget(self.rule_tags_list)
        
        # Create rule button
        self.create_rule_button = QPushButton("Create Consolidation Rule")
        self.create_rule_button.clicked.connect(self.create_consolidation_rule)
        right_layout.addWidget(self.create_rule_button)
        
        # Existing rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Target Tag", "Source Tags", "Actions"])
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(QLabel("Existing Rules:"))
        right_layout.addWidget(self.rules_table)
        
        right_group.setLayout(right_layout)
        layout.addWidget(right_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_blacklist_tab(self):
        """Create the blacklist management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Category tabs for blacklists
        blacklist_tabs = QTabWidget()
        
        # Positive tags blacklist
        pos_widget = QWidget()
        pos_layout = QVBoxLayout()
        
        pos_layout.addWidget(QLabel("Blacklisted Positive Tags:"))
        self.pos_blacklist = QListWidget()
        pos_layout.addWidget(self.pos_blacklist)
        
        pos_buttons = QHBoxLayout()
        self.remove_pos_blacklist = QPushButton("Remove Selected")
        self.remove_pos_blacklist.clicked.connect(lambda: self.remove_from_blacklist("positive"))
        self.clear_pos_blacklist = QPushButton("Clear All")
        self.clear_pos_blacklist.clicked.connect(lambda: self.clear_blacklist("positive"))
        pos_buttons.addWidget(self.remove_pos_blacklist)
        pos_buttons.addWidget(self.clear_pos_blacklist)
        pos_buttons.addStretch()
        pos_layout.addLayout(pos_buttons)
        
        pos_widget.setLayout(pos_layout)
        blacklist_tabs.addTab(pos_widget, "Positive Tags")
        
        # Negative tags blacklist
        neg_widget = QWidget()
        neg_layout = QVBoxLayout()
        
        neg_layout.addWidget(QLabel("Blacklisted Negative Tags:"))
        self.neg_blacklist = QListWidget()
        neg_layout.addWidget(self.neg_blacklist)
        
        neg_buttons = QHBoxLayout()
        self.remove_neg_blacklist = QPushButton("Remove Selected")
        self.remove_neg_blacklist.clicked.connect(lambda: self.remove_from_blacklist("negative"))
        self.clear_neg_blacklist = QPushButton("Clear All")
        self.clear_neg_blacklist.clicked.connect(lambda: self.clear_blacklist("negative"))
        neg_buttons.addWidget(self.remove_neg_blacklist)
        neg_buttons.addWidget(self.clear_neg_blacklist)
        neg_buttons.addStretch()
        neg_layout.addLayout(neg_buttons)
        
        neg_widget.setLayout(neg_layout)
        blacklist_tabs.addTab(neg_widget, "Negative Tags")
        
        layout.addWidget(blacklist_tabs)
        
        widget.setLayout(layout)
        return widget
    
    def create_rules_tab(self):
        """Create the rules management and history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Import/Export section
        io_group = QGroupBox("Import/Export Rules")
        io_layout = QHBoxLayout()
        
        self.export_rules_button = QPushButton("Export Rules")
        self.export_rules_button.clicked.connect(self.export_rules)
        
        self.import_rules_button = QPushButton("Import Rules")
        self.import_rules_button.clicked.connect(self.import_rules)
        
        self.reset_rules_button = QPushButton("Reset All Rules")
        self.reset_rules_button.clicked.connect(self.reset_all_rules)
        
        io_layout.addWidget(self.export_rules_button)
        io_layout.addWidget(self.import_rules_button)
        io_layout.addStretch()
        io_layout.addWidget(self.reset_rules_button)
        
        io_group.setLayout(io_layout)
        layout.addWidget(io_group)
        
        # History section
        history_group = QGroupBox("Consolidation History")
        history_layout = QVBoxLayout()
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(200)
        history_layout.addWidget(self.history_text)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Statistics section
        stats_group = QGroupBox("Current Statistics")
        stats_layout = QFormLayout()
        
        self.total_pos_tags_label = QLabel("0")
        self.total_neg_tags_label = QLabel("0")
        self.blacklisted_pos_label = QLabel("0")
        self.blacklisted_neg_label = QLabel("0")
        self.consolidation_rules_label = QLabel("0")
        
        stats_layout.addRow("Total Positive Tags:", self.total_pos_tags_label)
        stats_layout.addRow("Total Negative Tags:", self.total_neg_tags_label)
        stats_layout.addRow("Blacklisted Positive:", self.blacklisted_pos_label)
        stats_layout.addRow("Blacklisted Negative:", self.blacklisted_neg_label)
        stats_layout.addRow("Consolidation Rules:", self.consolidation_rules_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_category_management_tab(self):
        """Create the category management tab for moving tags between positive and negative"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Left side - Positive tags
        left_group = QGroupBox("Positive Tags")
        left_layout = QVBoxLayout()
        
        # Search for positive tags
        self.pos_search_box = QLineEdit()
        self.pos_search_box.setPlaceholderText("Search positive tags...")
        self.pos_search_box.textChanged.connect(self.filter_positive_category_tags)
        left_layout.addWidget(self.pos_search_box)
        
        # Positive tags list
        self.positive_category_list = QListWidget()
        self.positive_category_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        left_layout.addWidget(self.positive_category_list)
        
        # Move to negative button
        self.move_to_negative_button = QPushButton("Move to Negative →")
        self.move_to_negative_button.clicked.connect(self.move_tags_to_negative)
        self.move_to_negative_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        left_layout.addWidget(self.move_to_negative_button)
        
        # Remove positive tags button
        self.remove_positive_button = QPushButton("🗑️ Remove Tags")
        self.remove_positive_button.clicked.connect(self.remove_positive_tags)
        self.remove_positive_button.setStyleSheet("QPushButton { background-color: #9E9E9E; color: white; font-weight: bold; }")
        left_layout.addWidget(self.remove_positive_button)
        
        left_group.setLayout(left_layout)
        layout.addWidget(left_group)
        
        # Middle - Info and actions
        middle_layout = QVBoxLayout()
        
        # Instructions
        info_label = QLabel(
            "Category Management\n\n"
            "Use this tab to move tags between\n"
            "positive and negative categories.\n\n"
            "Select tags from either list and\n"
            "click the appropriate button to move them."
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("QLabel { font-weight: bold; padding: 20px; background-color: #e3f2fd; border-radius: 10px; }")
        
        middle_layout.addStretch()
        middle_layout.addWidget(info_label)
        
        # Bulk operations
        bulk_group = QGroupBox("Bulk Operations")
        bulk_layout = QVBoxLayout()
        
        self.auto_fix_button = QPushButton("Auto-Fix Misclassified Tags")
        self.auto_fix_button.clicked.connect(self.auto_fix_categories)
        self.auto_fix_button.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; }")
        bulk_layout.addWidget(self.auto_fix_button)
        
        bulk_group.setLayout(bulk_layout)
        middle_layout.addWidget(bulk_group)
        middle_layout.addStretch()
        
        layout.addLayout(middle_layout)
        
        # Right side - Negative tags
        right_group = QGroupBox("Negative Tags")
        right_layout = QVBoxLayout()
        
        # Search for negative tags
        self.neg_search_box = QLineEdit()
        self.neg_search_box.setPlaceholderText("Search negative tags...")
        self.neg_search_box.textChanged.connect(self.filter_negative_category_tags)
        right_layout.addWidget(self.neg_search_box)
        
        # Negative tags list
        self.negative_category_list = QListWidget()
        self.negative_category_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        right_layout.addWidget(self.negative_category_list)
        
        # Move to positive button
        self.move_to_positive_button = QPushButton("← Move to Positive")
        self.move_to_positive_button.clicked.connect(self.move_tags_to_positive)
        self.move_to_positive_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        right_layout.addWidget(self.move_to_positive_button)
        
        # Remove negative tags button
        self.remove_negative_button = QPushButton("🗑️ Remove Tags")
        self.remove_negative_button.clicked.connect(self.remove_negative_tags)
        self.remove_negative_button.setStyleSheet("QPushButton { background-color: #9E9E9E; color: white; font-weight: bold; }")
        right_layout.addWidget(self.remove_negative_button)
        
        right_group.setLayout(right_layout)
        layout.addWidget(right_group)
        
        widget.setLayout(layout)
        return widget
    
    def load_current_tags(self):
        """Load current tags from statistics tracker"""
        try:
            # Load positive tags
            self.positive_tags = self.stats_tracker.get_top_positive_tags(0)  # Get all
            # Load negative tags  
            self.negative_tags = self.stats_tracker.get_top_negative_tags(0)  # Get all
            
            self.load_category_tags()
            self.load_category_management_lists()
            self.update_blacklists_display()
            self.update_rules_display()
            self.update_statistics_display()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load tags: {str(e)}")
    
    def load_category_tags(self):
        """Load tags for selected category"""
        self.tags_list.clear()
        
        if self.category_combo.currentText() == "Positive Tags":
            tags = self.positive_tags
        else:
            tags = self.negative_tags
        
        for tag, count in tags:
            item = QListWidgetItem(f"{tag} ({count})")
            item.setData(Qt.UserRole, tag)
            self.tags_list.addItem(item)
    
    def filter_tags(self):
        """Filter tags based on search text"""
        search_text = self.search_box.text().lower()
        
        for i in range(self.tags_list.count()):
            item = self.tags_list.item(i)
            tag = item.data(Qt.UserRole)
            visible = search_text in tag.lower() if search_text else True
            item.setHidden(not visible)
    
    def add_selected_to_rule(self):
        """Add selected tags to current rule"""
        selected_items = self.tags_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select tags to add to the rule.")
            return
        
        for item in selected_items:
            tag = item.data(Qt.UserRole)
            # Check if tag is already in rule
            existing = False
            for i in range(self.rule_tags_list.count()):
                if self.rule_tags_list.item(i).data(Qt.UserRole) == tag:
                    existing = True
                    break
            
            if not existing:
                rule_item = QListWidgetItem(tag)
                rule_item.setData(Qt.UserRole, tag)
                self.rule_tags_list.addItem(rule_item)
        
        self.update_selection_info()
    
    def add_selected_to_blacklist(self):
        """Add selected tags to blacklist"""
        selected_items = self.tags_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select tags to blacklist.")
            return
        
        category = "positive" if self.category_combo.currentText() == "Positive Tags" else "negative"
        
        for item in selected_items:
            tag = item.data(Qt.UserRole)
            if tag not in self.blacklists[category]:
                self.blacklists[category].append(tag)
        
        self.update_blacklists_display()
        self.update_selection_info()
    
    def remove_from_rule(self):
        """Remove selected tags from current rule"""
        selected_items = self.rule_tags_list.selectedItems()
        for item in selected_items:
            self.rule_tags_list.takeItem(self.rule_tags_list.row(item))
    
    def create_consolidation_rule(self):
        """Create a new consolidation rule"""
        target_tag = self.target_tag_input.text().strip()
        if not target_tag:
            QMessageBox.warning(self, "Invalid Target", "Please enter a target tag name.")
            return
        
        if self.rule_tags_list.count() == 0:
            QMessageBox.warning(self, "No Tags", "Please add tags to consolidate.")
            return
        
        # Get source tags
        source_tags = []
        for i in range(self.rule_tags_list.count()):
            source_tags.append(self.rule_tags_list.item(i).data(Qt.UserRole))
        
        # Add rule
        category = "positive" if self.category_combo.currentText() == "Positive Tags" else "negative"
        
        if category not in self.consolidation_rules:
            self.consolidation_rules[category] = {}
        
        self.consolidation_rules[category][target_tag] = source_tags
        
        # Clear inputs
        self.target_tag_input.clear()
        self.rule_tags_list.clear()
        
        self.update_rules_display()
        QMessageBox.information(self, "Rule Created", f"Consolidation rule created: {', '.join(source_tags)} → {target_tag}")
    
    def update_rules_display(self):
        """Update the rules table display"""
        self.rules_table.setRowCount(0)
        
        row = 0
        for category in ["positive", "negative"]:
            if category in self.consolidation_rules:
                for target_tag, source_tags in self.consolidation_rules[category].items():
                    self.rules_table.insertRow(row)
                    
                    # Target tag
                    target_item = QTableWidgetItem(f"[{category.title()}] {target_tag}")
                    self.rules_table.setItem(row, 0, target_item)
                    
                    # Source tags
                    source_item = QTableWidgetItem(", ".join(source_tags))
                    self.rules_table.setItem(row, 1, source_item)
                    
                    # Delete button
                    delete_button = QPushButton("Delete")
                    delete_button.clicked.connect(lambda checked, cat=category, tgt=target_tag: self.delete_rule(cat, tgt))
                    self.rules_table.setCellWidget(row, 2, delete_button)
                    
                    row += 1
    
    def delete_rule(self, category, target_tag):
        """Delete a consolidation rule"""
        if category in self.consolidation_rules and target_tag in self.consolidation_rules[category]:
            del self.consolidation_rules[category][target_tag]
            self.update_rules_display()
            QMessageBox.information(self, "Rule Deleted", f"Deleted rule for '{target_tag}'")
    
    def update_blacklists_display(self):
        """Update blacklist displays"""
        self.pos_blacklist.clear()
        self.neg_blacklist.clear()
        
        for tag in self.blacklists["positive"]:
            self.pos_blacklist.addItem(tag)
        
        for tag in self.blacklists["negative"]:
            self.neg_blacklist.addItem(tag)
    
    def update_statistics_display(self):
        """Update statistics labels"""
        self.total_pos_tags_label.setText(str(len(self.positive_tags)))
        self.total_neg_tags_label.setText(str(len(self.negative_tags)))
        self.blacklisted_pos_label.setText(str(len(self.blacklists["positive"])))
        self.blacklisted_neg_label.setText(str(len(self.blacklists["negative"])))
        
        total_rules = sum(len(rules) for rules in self.consolidation_rules.values())
        self.consolidation_rules_label.setText(str(total_rules))
    
    def update_selection_info(self):
        """Update selection info label"""
        selected_count = len(self.tags_list.selectedItems())
        self.selection_info.setText(f"{selected_count} tags selected")
    
    def remove_from_blacklist(self, category):
        """Remove selected items from blacklist"""
        if category == "positive":
            list_widget = self.pos_blacklist
        else:
            list_widget = self.neg_blacklist
        
        selected_items = list_widget.selectedItems()
        for item in selected_items:
            tag = item.text()
            if tag in self.blacklists[category]:
                self.blacklists[category].remove(tag)
            list_widget.takeItem(list_widget.row(item))
    
    def clear_blacklist(self, category):
        """Clear entire blacklist for category"""
        reply = QMessageBox.question(
            self, "Clear Blacklist", 
            f"Are you sure you want to clear all {category} blacklisted tags?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.blacklists[category].clear()
            self.update_blacklists_display()
    
    def preview_changes(self):
        """Preview consolidation changes"""
        if not self.consolidation_rules and not any(self.blacklists.values()):
            QMessageBox.information(self, "No Changes", "No consolidation rules or blacklisted tags to preview.")
            return
        
        # Create preview dialog
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Preview Consolidation Changes")
        preview_dialog.setGeometry(150, 150, 800, 600)
        
        layout = QVBoxLayout()
        
        preview_text = QTextEdit()
        preview_text.setReadOnly(True)
        
        # Generate preview content
        preview_content = self.generate_preview_content()
        preview_text.setPlainText(preview_content)
        
        layout.addWidget(preview_text)
        
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(preview_dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        preview_dialog.setLayout(layout)
        preview_dialog.exec_()
    
    def generate_preview_content(self):
        """Generate preview content for changes"""
        content = []
        content.append("CONSOLIDATION PREVIEW")
        content.append("=" * 50)
        content.append("")
        
        # Consolidation rules
        if any(self.consolidation_rules.values()):
            content.append("CONSOLIDATION RULES:")
            content.append("-" * 30)
            
            for category in ["positive", "negative"]:
                if category in self.consolidation_rules and self.consolidation_rules[category]:
                    content.append(f"\n{category.title()} Tags:")
                    for target_tag, source_tags in self.consolidation_rules[category].items():
                        # Calculate total count that will be consolidated
                        total_count = 0
                        current_tags = self.positive_tags if category == "positive" else self.negative_tags
                        tag_dict = dict(current_tags)
                        
                        for source_tag in source_tags:
                            total_count += tag_dict.get(source_tag, 0)
                        
                        content.append(f"  • {', '.join(source_tags)} → {target_tag} (Total: {total_count})")
        
        # Blacklisted tags
        if any(self.blacklists.values()):
            content.append("\n\nBLACKLISTED TAGS (will be removed):")
            content.append("-" * 40)
            
            for category in ["positive", "negative"]:
                if self.blacklists[category]:
                    content.append(f"\n{category.title()} Tags:")
                    for tag in self.blacklists[category]:
                        content.append(f"  • {tag}")
        
        if not any(self.consolidation_rules.values()) and not any(self.blacklists.values()):
            content.append("No changes to preview.")
        
        return "\n".join(content)
    
    def apply_consolidation(self):
        """Apply consolidation rules and blacklists"""
        if not self.consolidation_rules and not any(self.blacklists.values()):
            QMessageBox.information(self, "No Changes", "No consolidation rules or blacklisted tags to apply.")
            return
        
        reply = QMessageBox.question(
            self, "Apply Consolidation",
            "Are you sure you want to apply these consolidation changes? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        
        # Start worker thread
        self.worker = TagConsolidationWorker(self.stats_tracker, self.consolidation_rules, self.blacklists)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.consolidation_finished)
        self.worker.start()
        
        # Disable buttons during operation
        self.apply_button.setEnabled(False)
        self.preview_button.setEnabled(False)
    
    def update_progress(self, percent, message):
        """Update progress bar and label"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)
    
    def consolidation_finished(self, results):
        """Handle consolidation completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.apply_button.setEnabled(True)
        self.preview_button.setEnabled(True)
        
        if "error" in results:
            QMessageBox.critical(self, "Error", f"Consolidation failed: {results['error']}")
            return
        
        # Show results
        message = f"Consolidation completed successfully!\n\n"
        message += f"Tags consolidated: {results.get('consolidated_count', 0)}\n"
        message += f"Tags blacklisted: {results.get('blacklisted_count', 0)}\n"
        
        QMessageBox.information(self, "Consolidation Complete", message)
        
        # Update history
        self.add_to_history(results)
        
        # Reload tags
        self.load_current_tags()
    
    def add_to_history(self, results):
        """Add consolidation to history"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        history_entry = f"\n[{timestamp}] Consolidation Applied:\n"
        history_entry += f"  • Tags consolidated: {results.get('consolidated_count', 0)}\n"
        history_entry += f"  • Tags blacklisted: {results.get('blacklisted_count', 0)}\n"
        
        current_text = self.history_text.toPlainText()
        self.history_text.setPlainText(current_text + history_entry)
    
    def load_consolidation_rules(self):
        """Load consolidation rules from file"""
        try:
            if os.path.exists(self.consolidation_rules_file):
                with open(self.consolidation_rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading consolidation rules: {e}")
        
        return {"positive": {}, "negative": {}}
    
    def load_blacklists(self):
        """Load blacklists from file"""
        try:
            if os.path.exists(self.blacklists_file):
                with open(self.blacklists_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading blacklists: {e}")
        
        return {"positive": [], "negative": []}
    
    def save_rules(self):
        """Save consolidation rules and blacklists"""
        try:
            # Save consolidation rules
            with open(self.consolidation_rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.consolidation_rules, f, indent=2, ensure_ascii=False)
            
            # Save blacklists
            with open(self.blacklists_file, 'w', encoding='utf-8') as f:
                json.dump(self.blacklists, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Saved", "Rules and blacklists saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save rules: {str(e)}")
    
    def export_rules(self):
        """Export rules and blacklists to file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Rules", "tag_consolidation_rules.json", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                export_data = {
                    "consolidation_rules": self.consolidation_rules,
                    "blacklists": self.blacklists,
                    "export_timestamp": str(datetime.datetime.now())
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Exported", f"Rules exported to: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export rules: {str(e)}")
    
    def import_rules(self):
        """Import rules and blacklists from file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Rules", "", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                if "consolidation_rules" in import_data:
                    self.consolidation_rules = import_data["consolidation_rules"]
                
                if "blacklists" in import_data:
                    self.blacklists = import_data["blacklists"]
                
                self.update_rules_display()
                self.update_blacklists_display()
                self.update_statistics_display()
                
                QMessageBox.information(self, "Imported", f"Rules imported from: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import rules: {str(e)}")
    
    def reset_all_rules(self):
        """Reset all consolidation rules and blacklists"""
        reply = QMessageBox.question(
            self, "Reset Rules",
            "Are you sure you want to reset all consolidation rules and blacklists? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.consolidation_rules = {"positive": {}, "negative": {}}
            self.blacklists = {"positive": [], "negative": []}
            
            self.update_rules_display()
            self.update_blacklists_display()
            self.update_statistics_display()
            
            QMessageBox.information(self, "Reset Complete", "All rules and blacklists have been cleared.")
    
    def load_category_management_lists(self):
        """Load tags into the category management lists"""
        # Clear existing items
        if hasattr(self, 'positive_category_list'):
            self.positive_category_list.clear()
            self.negative_category_list.clear()
            
            # Load positive tags
            for tag, count in self.positive_tags:
                item = QListWidgetItem(f"{tag} ({count})")
                item.setData(Qt.UserRole, (tag, count, "positive"))
                self.positive_category_list.addItem(item)
            
            # Load negative tags
            for tag, count in self.negative_tags:
                item = QListWidgetItem(f"{tag} ({count})")
                item.setData(Qt.UserRole, (tag, count, "negative"))
                self.negative_category_list.addItem(item)
    
    def filter_positive_category_tags(self):
        """Filter positive category tags based on search text"""
        if not hasattr(self, 'positive_category_list'):
            return
            
        search_text = self.pos_search_box.text().lower()
        
        for i in range(self.positive_category_list.count()):
            item = self.positive_category_list.item(i)
            tag_data = item.data(Qt.UserRole)
            if tag_data:
                tag = tag_data[0]
                visible = search_text in tag.lower() if search_text else True
                item.setHidden(not visible)
    
    def filter_negative_category_tags(self):
        """Filter negative category tags based on search text"""
        if not hasattr(self, 'negative_category_list'):
            return
            
        search_text = self.neg_search_box.text().lower()
        
        for i in range(self.negative_category_list.count()):
            item = self.negative_category_list.item(i)
            tag_data = item.data(Qt.UserRole)
            if tag_data:
                tag = tag_data[0]
                visible = search_text in tag.lower() if search_text else True
                item.setHidden(not visible)
    
    def move_tags_to_negative(self):
        """Move selected positive tags to negative category"""
        selected_items = self.positive_category_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select positive tags to move to negative category.")
            return
        
        # Get tag names and counts
        tags_to_move = []
        for item in selected_items:
            tag_data = item.data(Qt.UserRole)
            if tag_data:
                tag, count, _ = tag_data
                tags_to_move.append((tag, count))
        
        if not tags_to_move:
            return
        
        # Confirm the operation
        tag_names = [tag for tag, count in tags_to_move]
        reply = QMessageBox.question(
            self, "Move Tags to Negative",
            f"Move {len(tag_names)} tag(s) from positive to negative category?\n\n" +
            f"Tags to move: {', '.join(tag_names[:5])}" +
            (f" and {len(tag_names) - 5} more..." if len(tag_names) > 5 else "") +
            "\n\nThis action will update your statistics.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Move tags in statistics
                for tag, count in tags_to_move:
                    # Remove from positive
                    if tag in self.stats_tracker.stats['positive_tags']:
                        del self.stats_tracker.stats['positive_tags'][tag]
                    
                    # Add to negative
                    self.stats_tracker.stats['negative_tags'][tag] += count
                
                # Save statistics
                import datetime
                self.stats_tracker.stats['last_update'] = datetime.datetime.now().isoformat()
                self.stats_tracker.save_statistics()
                
                # Reload data
                self.load_current_tags()
                
                QMessageBox.information(
                    self, "Tags Moved",
                    f"Successfully moved {len(tags_to_move)} tag(s) from positive to negative category."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to move tags: {str(e)}")
    
    def move_tags_to_positive(self):
        """Move selected negative tags to positive category"""
        selected_items = self.negative_category_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select negative tags to move to positive category.")
            return
        
        # Get tag names and counts
        tags_to_move = []
        for item in selected_items:
            tag_data = item.data(Qt.UserRole)
            if tag_data:
                tag, count, _ = tag_data
                tags_to_move.append((tag, count))
        
        if not tags_to_move:
            return
        
        # Confirm the operation
        tag_names = [tag for tag, count in tags_to_move]
        reply = QMessageBox.question(
            self, "Move Tags to Positive",
            f"Move {len(tag_names)} tag(s) from negative to positive category?\n\n" +
            f"Tags to move: {', '.join(tag_names[:5])}" +
            (f" and {len(tag_names) - 5} more..." if len(tag_names) > 5 else "") +
            "\n\nThis action will update your statistics.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Move tags in statistics
                for tag, count in tags_to_move:
                    # Remove from negative
                    if tag in self.stats_tracker.stats['negative_tags']:
                        del self.stats_tracker.stats['negative_tags'][tag]
                    
                    # Add to positive
                    self.stats_tracker.stats['positive_tags'][tag] += count
                
                # Save statistics
                import datetime
                self.stats_tracker.stats['last_update'] = datetime.datetime.now().isoformat()
                self.stats_tracker.save_statistics()
                
                # Reload data
                self.load_current_tags()
                
                QMessageBox.information(
                    self, "Tags Moved",
                    f"Successfully moved {len(tags_to_move)} tag(s) from negative to positive category."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to move tags: {str(e)}")
    
    def auto_fix_categories(self):
        """Use the automatic fix to correct misclassified tags"""
        reply = QMessageBox.question(
            self, "Auto-Fix Misclassified Tags",
            "This will automatically move obviously negative tags (like 'blurry', 'bad anatomy', etc.) " +
            "from positive to negative statistics.\n\n" +
            "This is the same fix available in the main Statistics tab.\n\n" +
            "Continue with the auto-fix?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.stats_tracker.fix_misclassified_tags()
                
                # Reload data
                self.load_current_tags()
                
                if result['tags_moved'] > 0:
                    message = f"Auto-fix completed!\n\n"
                    message += f"Tags moved: {result['tags_moved']}\n"
                    message += f"Total occurrences moved: {result['total_occurrences_moved']}\n\n"
                    message += "Your tag categories are now more accurate!"
                else:
                    message = "No misclassified tags found. Your categories are already correct!"
                
                QMessageBox.information(self, "Auto-Fix Complete", message)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Auto-fix failed: {str(e)}")
    
    def remove_positive_tags(self):
        """Remove selected positive tags from statistics entirely"""
        selected_items = self.positive_category_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select positive tags to remove from statistics.")
            return
        
        # Get tag names and counts
        tags_to_remove = []
        for item in selected_items:
            tag_data = item.data(Qt.UserRole)
            if tag_data:
                tag, count, _ = tag_data
                tags_to_remove.append((tag, count))
        
        if not tags_to_remove:
            return
        
        # Confirm the operation
        tag_names = [tag for tag, count in tags_to_remove]
        total_occurrences = sum(count for tag, count in tags_to_remove)
        
        reply = QMessageBox.question(
            self, "Remove Tags Permanently",
            f"Permanently remove {len(tag_names)} tag(s) from statistics?\n\n" +
            f"Tags to remove: {', '.join(tag_names[:5])}" +
            (f" and {len(tag_names) - 5} more..." if len(tag_names) > 5 else "") +
            f"\n\nTotal occurrences: {total_occurrences}\n" +
            "\n⚠️ This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                removed_count = 0
                for tag, count in tags_to_remove:
                    result = self.stats_tracker.remove_tag(tag, "positive")
                    if result['removed']:
                        removed_count += result['count']
                
                # Reload data
                self.load_current_tags()
                
                QMessageBox.information(
                    self, "Tags Removed",
                    f"Successfully removed {len(tags_to_remove)} tag(s) with {removed_count} total occurrences from statistics."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove tags: {str(e)}")
    
    def remove_negative_tags(self):
        """Remove selected negative tags from statistics entirely"""
        selected_items = self.negative_category_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select negative tags to remove from statistics.")
            return
        
        # Get tag names and counts
        tags_to_remove = []
        for item in selected_items:
            tag_data = item.data(Qt.UserRole)
            if tag_data:
                tag, count, _ = tag_data
                tags_to_remove.append((tag, count))
        
        if not tags_to_remove:
            return
        
        # Confirm the operation
        tag_names = [tag for tag, count in tags_to_remove]
        total_occurrences = sum(count for tag, count in tags_to_remove)
        
        reply = QMessageBox.question(
            self, "Remove Tags Permanently",
            f"Permanently remove {len(tag_names)} tag(s) from statistics?\n\n" +
            f"Tags to remove: {', '.join(tag_names[:5])}" +
            (f" and {len(tag_names) - 5} more..." if len(tag_names) > 5 else "") +
            f"\n\nTotal occurrences: {total_occurrences}\n" +
            "\n⚠️ This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                removed_count = 0
                for tag, count in tags_to_remove:
                    result = self.stats_tracker.remove_tag(tag, "negative")
                    if result['removed']:
                        removed_count += result['count']
                
                # Reload data
                self.load_current_tags()
                
                QMessageBox.information(
                    self, "Tags Removed",
                    f"Successfully removed {len(tags_to_remove)} tag(s) with {removed_count} total occurrences from statistics."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove tags: {str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Mock stats tracker for testing
    class MockStatsTracker:
        def get_top_positive_tags(self, limit):
            return [("1girl", 100), ("blue eyes", 80), ("long hair", 60)]
        
        def get_top_negative_tags(self, limit):
            return [("worst quality", 50), ("blurry", 30)]
        
        def apply_custom_consolidation(self, rules, blacklists, progress_callback=None):
            return {"consolidated_count": 5, "blacklisted_count": 2}
    
    mock_tracker = MockStatsTracker()
    dialog = AdvancedTagConsolidationDialog(mock_tracker)
    dialog.show()
    
    sys.exit(app.exec_())

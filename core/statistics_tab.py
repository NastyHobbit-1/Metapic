# Enhanced Statistics Tab with integrated utilities
from utils.common_imports import *
from utils.logger import logger, PerformanceTimer
from utils.gui_factory import GUIFactory
from utils.error_handler import handle_errors, ErrorCategory, ErrorSeverity
from config.settings import get_config
from .optimized_statistics_tracker import optimized_stats_tracker
from .model_name_manager import ModelNameManagerDialog

class StatisticsTab(QWidget):
    """Enhanced statistics display tab with optimized performance and utilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gui_factory = GUIFactory()
        
        # Get refresh interval from configuration
        self.refresh_interval = get_config('auto_refresh_interval', 5000)
        
        logger.info("Initializing Statistics tab")
        self.init_ui()
        
        # Set up auto-refresh timer with configured interval (but don't start it yet)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_statistics)
        # Don't start timer during initialization to prevent UI blocking
        # self.refresh_timer.start(self.refresh_interval)
        
        logger.debug(f"Statistics tab initialized with {self.refresh_interval}ms refresh interval")
    
    def start_auto_refresh(self):
        """Start the auto-refresh timer (called when tab becomes visible)"""
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(self.refresh_interval)
            logger.debug(f"Started auto-refresh timer with {self.refresh_interval}ms interval")
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with summary
        header_layout = QVBoxLayout()
        
        self.title_label = QLabel("Usage Statistics")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title_label)
        
        # Summary info using GUI factory
        self.summary_widget = self.gui_factory.create_statistics_summary_widget()
        header_layout.addWidget(self.summary_widget)
        
        # Extract labels from summary widget for later updates
        summary_layout = self.summary_widget.layout()
        self.summary_labels = []
        if summary_layout:
            for i in range(summary_layout.count()):
                widget = summary_layout.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    self.summary_labels.append(widget)
        
        # Note: summary_widget already has its layout, don't add it again
        
        # Control buttons using GUI factory
        button_layout = QHBoxLayout()
        
        refresh_btn = self.gui_factory.create_styled_button(
            "Refresh", self.manual_refresh, 'primary',
            tooltip="Refresh statistics display"
        )
        button_layout.addWidget(refresh_btn)
        
        export_btn = self.gui_factory.create_styled_button(
            "Export Statistics", self.export_statistics, 'secondary',
            tooltip="Export statistics to file"
        )
        button_layout.addWidget(export_btn)
        
        model_manager_btn = self.gui_factory.create_styled_button(
            "Model Name Manager", self.open_model_manager, 'primary',
            tooltip="Manage model name mappings and normalization"
        )
        button_layout.addWidget(model_manager_btn)
        
        consolidate_btn = self.gui_factory.create_styled_button(
            "Simple Consolidation", self.consolidate_tags, 'secondary',
            tooltip="Apply basic tag and model consolidation"
        )
        button_layout.addWidget(consolidate_btn)
        
        advanced_consolidate_btn = self.gui_factory.create_styled_button(
            "Advanced Consolidation", self.advanced_consolidation, 'secondary',
            tooltip="Open advanced consolidation dialog"
        )
        button_layout.addWidget(advanced_consolidate_btn)
        
        suggestions_btn = self.gui_factory.create_styled_button(
            "Auto Suggestions", self.show_consolidation_suggestions, 'secondary',
            tooltip="Get automatic consolidation suggestions"
        )
        button_layout.addWidget(suggestions_btn)
        
        fix_tags_btn = self.gui_factory.create_styled_button(
            "Fix Misclassified Tags", self.fix_misclassified_tags, 'warning',
            tooltip="Move negative tags from positive statistics"
        )
        button_layout.addWidget(fix_tags_btn)
        
        clear_btn = self.gui_factory.create_styled_button(
            "Clear Statistics", self.clear_statistics, 'warning',
            tooltip="Clear all statistics data (cannot be undone)"
        )
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        header_layout.addLayout(button_layout)
        
        layout.addLayout(header_layout)
        
        # Main content with tabs
        self.content_tabs = QTabWidget()
        
        # Models tab
        self.models_tab = self.create_models_tab()
        self.content_tabs.addTab(self.models_tab, "📊 Models")
        
        # Positive tags tab  
        self.positive_tags_tab = self.create_positive_tags_tab()
        self.content_tabs.addTab(self.positive_tags_tab, "✅ Positive Tags")
        
        # Negative tags tab
        self.negative_tags_tab = self.create_negative_tags_tab()
        self.content_tabs.addTab(self.negative_tags_tab, "❌ Negative Tags")
        
        layout.addWidget(self.content_tabs)
        
        # Load statistics asynchronously on first show
        self.statistics_loaded = False
        
        # Initial placeholder message
        self.show_loading_message()
    
    def create_models_tab(self):
        """Create the models statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Models table using GUI factory
        self.models_table = self.gui_factory.create_table_with_headers(["Model Name", "Usage Count"])
        
        layout.addWidget(self.models_table)
        
        return tab
    
    def create_positive_tags_tab(self):
        """Create the positive tags statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Positive tags table using GUI factory
        self.positive_tags_table = self.gui_factory.create_table_with_headers(["Tag", "Usage Count"])
        
        layout.addWidget(self.positive_tags_table)
        
        return tab
    
    def create_negative_tags_tab(self):
        """Create the negative tags statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Negative tags table using GUI factory
        self.negative_tags_table = self.gui_factory.create_table_with_headers(["Tag", "Usage Count"])
        
        layout.addWidget(self.negative_tags_table)
        
        return tab
    
    @handle_errors(ErrorCategory.STATISTICS, "Refreshing statistics display")
    def refresh_statistics(self):
        """Refresh all statistics displays using optimized tracker"""
        with PerformanceTimer("refresh_statistics_display"):
            summary = optimized_stats_tracker.get_statistics_summary()
            
            # Update summary widget labels directly instead of recreating
            try:
                # Get labels and update them directly
                layout = self.summary_widget.layout()
                if layout and layout.count() >= 4:
                    for i in range(layout.count()):
                        item = layout.itemAt(i)
                        if item and item.widget():
                            label = item.widget()
                            if isinstance(label, QLabel):
                                if i == 0:
                                    label.setText(f"Images Processed: {summary['total_images_processed']}")
                                elif i == 1:
                                    label.setText(f"Unique Models: {summary['unique_models']}")
                                elif i == 2:
                                    label.setText(f"Positive Tags: {summary['unique_positive_tags']}")
                                elif i == 3:
                                    label.setText(f"Negative Tags: {summary['unique_negative_tags']}")
            except Exception as e:
                logger.warning(f"Could not update summary labels: {e}")
            
            # Get display limit from configuration
            max_display = get_config('max_tags_display', 1000)
            
            # Update models table
            all_models = optimized_stats_tracker.get_top_models(max_display)
            self.update_table(self.models_table, all_models)
            
            # Update positive tags table
            all_positive = optimized_stats_tracker.get_top_positive_tags(max_display)
            self.update_table(self.positive_tags_table, all_positive)
            
            # Update negative tags table
            all_negative = optimized_stats_tracker.get_top_negative_tags(max_display)
            self.update_table(self.negative_tags_table, all_negative)
            
            logger.debug(f"Statistics refreshed: {summary['total_images_processed']} images, "
                        f"{summary['unique_models']} models, "
                        f"{summary['unique_positive_tags']} positive tags, "
                        f"{summary['unique_negative_tags']} negative tags")
    
    def on_tab_changed(self, index):
        """Handle tab change to implement lazy loading"""
        # Check if this is the statistics tab (index 3 based on tab order)
        if index == 3 and not self.statistics_loaded:
            logger.info("Statistics tab became visible, loading data...")
            self.start_auto_refresh()
            self.load_statistics_async()
    
    def show_loading_message(self):
        """Show a loading message in the statistics tables"""
        try:
            # Set placeholder text in tables
            for table, message in [
                (self.models_table, "Click 'Refresh' to load model statistics..."),
                (self.positive_tags_table, "Click 'Refresh' to load positive tag statistics..."),
                (self.negative_tags_table, "Click 'Refresh' to load negative tag statistics...")
            ]:
                table.setRowCount(1)
                placeholder = QTableWidgetItem(message)
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEditable)
                table.setItem(0, 0, placeholder)
                table.setSpan(0, 0, 1, table.columnCount())
        except Exception as e:
            logger.warning(f"Error showing loading message: {e}")
    
    def load_statistics_async(self):
        """Load statistics asynchronously using QTimer to avoid blocking UI"""
        if self.statistics_loaded:
            return
            
        # Use QTimer to defer the loading to the next event loop iteration
        QTimer.singleShot(100, self.perform_statistics_refresh)
    
    def perform_statistics_refresh(self):
        """Perform the actual statistics refresh"""
        try:
            self.refresh_statistics()
            self.statistics_loaded = True
            logger.info("Statistics loaded successfully")
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
    
    def manual_refresh(self):
        """Handle manual refresh button click"""
        logger.info("Manual statistics refresh requested")
        self.statistics_loaded = False  # Force reload
        self.load_statistics_async()
    
    def update_table(self, table: QTableWidget, data: list):
        """Update a table with data"""
        table.setRowCount(len(data))
        
        for row, (item, count) in enumerate(data):
            # Item name
            item_widget = QTableWidgetItem(str(item))
            item_widget.setFlags(item_widget.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 0, item_widget)
            
            # Count
            count_widget = QTableWidgetItem(str(count))
            count_widget.setFlags(count_widget.flags() & ~Qt.ItemIsEditable)
            count_widget.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 1, count_widget)
        
        # Sort by count descending by default
        table.sortItems(1, Qt.DescendingOrder)
    
    def export_statistics(self):
        """Export statistics to file"""
        file_path, file_filter = QFileDialog.getSaveFileName(
            self, 
            "Export Statistics", 
            "metapicpick_statistics.json",
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                stats_tracker.export_statistics(file_path)
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Statistics exported successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export statistics:\n{str(e)}"
                )
    
    def open_model_manager(self):
        """Open the model name manager dialog"""
        try:
            dialog = ModelNameManagerDialog(stats_tracker, self)
            result = dialog.exec_()
            
            if result == dialog.Accepted:
                # Refresh statistics after any model changes
                self.refresh_statistics()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                    f"Failed to open model name manager:\n\n{str(e)}"
            )
    
    def fix_misclassified_tags(self):
        """Fix tags that are clearly negative but appearing in positive stats"""
        reply = QMessageBox.question(
            self,
            "Fix Misclassified Tags",
            "This will move obviously negative tags (like 'blurry', 'bad anatomy', etc.) " +
            "from positive to negative statistics.\n\n" +
            "This fixes data corruption where negative quality terms " +
            "incorrectly appear in positive tag statistics.\n\n" +
            "Continue with the fix?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = stats_tracker.fix_misclassified_tags()
                self.refresh_statistics()
                
                if result['tags_moved'] > 0:
                    message = f"Tag classification fix completed!\n\n"
                    message += f"Tags moved: {result['tags_moved']}\n"
                    message += f"Total occurrences moved: {result['total_occurrences_moved']}\n\n"
                    message += "The most common fixes:\n"
                    
                    # Show top 10 moved tags
                    for tag, count in sorted(result['moved_details'], key=lambda x: x[1], reverse=True)[:10]:
                        message += f"• {tag}: {count} occurrences\n"
                    
                    if len(result['moved_details']) > 10:
                        message += f"... and {len(result['moved_details']) - 10} more\n\n"
                    
                    message += "Your statistics are now more accurate!"
                else:
                    message = "No misclassified tags found. Your statistics are already correct!"
                
                QMessageBox.information(
                    self,
                    "Tags Fixed",
                    message
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Fix Error",
                    f"Failed to fix misclassified tags:\n\n{str(e)}"
                )
    
    def consolidate_tags(self):
        """Consolidate similar tags using enhanced normalization"""
        reply = QMessageBox.question(
            self,
            "Consolidate Tags",
            "Consolidate similar tags to reduce duplicates?\n\n"
            "This will merge tags like:\n"
            "• '1 girl' → '1girl'\n"
            "• 'blue eyes' → 'blue_eyes'\n"
            "• 'large breast' → 'large_breasts'\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = stats_tracker.consolidate_tags()
                self.refresh_statistics()
                
                pos_reduced = result['positive_before'] - result['positive_after']
                neg_reduced = result['negative_before'] - result['negative_after']
                
                QMessageBox.information(
                    self,
                    "Tags Consolidated",
                    f"Tag consolidation completed successfully!\n\n"
                    f"Positive tags: {result['positive_before']} → {result['positive_after']} "
                    f"(reduced by {pos_reduced})\n"
                    f"Negative tags: {result['negative_before']} → {result['negative_after']} "
                    f"(reduced by {neg_reduced})\n\n"
                    f"Similar tags have been merged together."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Consolidation Error",
                    f"Failed to consolidate tags:\n\n{str(e)}"
                )
    
    def clear_statistics(self):
        """Clear all statistics with confirmation"""
        reply = QMessageBox.question(
            self,
            "Clear Statistics",
            "Are you sure you want to clear all statistics?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            stats_tracker.clear_statistics()
            self.refresh_statistics()
            QMessageBox.information(
                self,
                "Statistics Cleared",
                "All statistics have been cleared."
            )
    
    def advanced_consolidation(self):
        """Open advanced tag consolidation dialog"""
        try:
            from .advanced_tag_consolidation import AdvancedTagConsolidationDialog
            
            dialog = AdvancedTagConsolidationDialog(stats_tracker, self)
            result = dialog.exec_()
            
            if result == dialog.Accepted:
                # Refresh statistics after consolidation
                self.refresh_statistics()
                
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to load advanced consolidation dialog:\n\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open advanced consolidation:\n\n{str(e)}"
            )
    
    def show_consolidation_suggestions(self):
        """Show automatic consolidation suggestions"""
        try:
            # Get suggestions for both positive and negative tags
            pos_suggestions = stats_tracker.get_consolidation_suggestions("positive", min_count=3)
            neg_suggestions = stats_tracker.get_consolidation_suggestions("negative", min_count=2)
            
            if not pos_suggestions and not neg_suggestions:
                QMessageBox.information(
                    self,
                    "No Suggestions",
                    "No consolidation suggestions found. Try loading more images or lowering the minimum count threshold."
                )
                return
            
            # Create suggestions dialog
            suggestions_dialog = QDialog(self)
            suggestions_dialog.setWindowTitle("Consolidation Suggestions")
            suggestions_dialog.setGeometry(100, 100, 600, 400)
            
            layout = QVBoxLayout()
            
            # Instructions
            instructions = QLabel(
                "These are automatic suggestions based on tag similarity.\n"
                "Review and use the Advanced Consolidation dialog to apply specific rules."
            )
            instructions.setWordWrap(True)
            layout.addWidget(instructions)
            
            # Suggestions text
            suggestions_text = QTextEdit()
            suggestions_text.setReadOnly(True)
            
            content = []
            
            if pos_suggestions:
                content.append("POSITIVE TAG SUGGESTIONS:")
                content.append("-" * 30)
                for target_tag, similar_tags in pos_suggestions.items():
                    content.append(f"• Consolidate to '{target_tag}': {', '.join(similar_tags)}")
                content.append("")
            
            if neg_suggestions:
                content.append("NEGATIVE TAG SUGGESTIONS:")
                content.append("-" * 30)
                for target_tag, similar_tags in neg_suggestions.items():
                    content.append(f"• Consolidate to '{target_tag}': {', '.join(similar_tags)}")
            
            suggestions_text.setPlainText("\n".join(content))
            layout.addWidget(suggestions_text)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            export_btn = QPushButton("Export Suggestions")
            export_btn.clicked.connect(lambda: self.export_suggestions(pos_suggestions, neg_suggestions))
            button_layout.addWidget(export_btn)
            
            advanced_btn = QPushButton("Open Advanced Consolidation")
            advanced_btn.clicked.connect(lambda: [suggestions_dialog.accept(), self.advanced_consolidation()])
            button_layout.addWidget(advanced_btn)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(suggestions_dialog.accept)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            suggestions_dialog.setLayout(layout)
            suggestions_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate consolidation suggestions:\n\n{str(e)}"
            )
    
    def export_suggestions(self, pos_suggestions, neg_suggestions):
        """Export consolidation suggestions to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Consolidation Suggestions",
            "consolidation_suggestions.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("METAPICPICK CONSOLIDATION SUGGESTIONS\n")
                    f.write("=" * 50 + "\n\n")
                    
                    if pos_suggestions:
                        f.write("POSITIVE TAG SUGGESTIONS:\n")
                        f.write("-" * 30 + "\n")
                        for target_tag, similar_tags in pos_suggestions.items():
                            f.write(f"• Consolidate to '{target_tag}': {', '.join(similar_tags)}\n")
                        f.write("\n")
                    
                    if neg_suggestions:
                        f.write("NEGATIVE TAG SUGGESTIONS:\n")
                        f.write("-" * 30 + "\n")
                        for target_tag, similar_tags in neg_suggestions.items():
                            f.write(f"• Consolidate to '{target_tag}': {', '.join(similar_tags)}\n")
                
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Suggestions exported to: {file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export suggestions: {str(e)}"
                )

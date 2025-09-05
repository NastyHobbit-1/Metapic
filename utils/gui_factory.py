"""
GUI Component Factory for MetaPicPick
Provides standardized creation of common GUI components with consistent styling.
"""

from .common_imports import *
from .logger import logger, PerformanceTimer


class GUIFactory:
    """Factory class for creating standardized GUI components"""
    
    def __init__(self):
        """Initialize the GUI factory"""
        logger.debug("Initializing GUIFactory")
    
    @staticmethod
    def create_styled_button(text: str, 
                           callback=None, 
                           style_class: str = 'primary',
                           tooltip: str = None,
                           enabled: bool = True,
                           min_width: int = None,
                           icon: QIcon = None) -> QPushButton:
        """
        Create a styled button with consistent appearance
        
        Args:
            text: Button text
            callback: Click callback function
            style_class: Style class ('primary', 'secondary', 'success', 'warning')
            tooltip: Tooltip text
            enabled: Whether button is enabled
            min_width: Minimum button width
            icon: Button icon
            
        Returns:
            Configured QPushButton
        """
        button = QPushButton(text)
        
        if callback:
            button.clicked.connect(callback)
        
        if style_class in BUTTON_STYLES:
            button.setStyleSheet(BUTTON_STYLES[style_class])
        
        if tooltip:
            button.setToolTip(tooltip)
        
        button.setEnabled(enabled)
        button.setMinimumHeight(DEFAULT_BUTTON_HEIGHT)
        
        if min_width:
            button.setMinimumWidth(min_width)
        
        if icon:
            button.setIcon(icon)
        
        logger.debug(f"Created styled button: '{text}' with style '{style_class}'")
        return button
    
    @staticmethod
    def create_table_with_headers(headers: List[str],
                                sortable: bool = True,
                                alternating_rows: bool = True,
                                selection_behavior: QTableWidget.SelectionBehavior = QTableWidget.SelectRows,
                                resize_mode: QHeaderView.ResizeMode = QHeaderView.Stretch,
                                context_menu: bool = True) -> QTableWidget:
        """
        Create a standardized table widget
        
        Args:
            headers: List of column headers
            sortable: Whether to enable sorting
            alternating_rows: Whether to show alternating row colors
            selection_behavior: Selection behavior
            resize_mode: Column resize mode
            context_menu: Whether to enable context menu
            
        Returns:
            Configured QTableWidget
        """
        with PerformanceTimer("create_table_widget"):
            table = QTableWidget()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            if sortable:
                table.setSortingEnabled(True)
            
            table.setAlternatingRowColors(alternating_rows)
            table.setSelectionBehavior(selection_behavior)
            table.setStyleSheet(TABLE_STYLE)
            
            # Configure header
            header = table.horizontalHeader()
            for i in range(len(headers)):
                if i == len(headers) - 1:  # Last column
                    header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
                else:
                    header.setSectionResizeMode(i, resize_mode)
            
            # Set row height
            table.verticalHeader().setDefaultSectionSize(DEFAULT_TABLE_ROW_HEIGHT)
            
            if context_menu:
                table.setContextMenuPolicy(Qt.CustomContextMenu)
            
            logger.debug(f"Created table with {len(headers)} columns: {headers}")
            return table
    
    @staticmethod
    def create_group_box(title: str, 
                        layout_type: str = 'vertical',
                        checkable: bool = False,
                        checked: bool = True) -> QGroupBox:
        """
        Create a styled group box
        
        Args:
            title: Group box title
            layout_type: 'vertical', 'horizontal', 'grid', or 'form'
            checkable: Whether group box is checkable
            checked: Initial checked state if checkable
            
        Returns:
            Configured QGroupBox
        """
        group_box = QGroupBox(title)
        group_box.setStyleSheet(GROUPBOX_STYLE)
        
        if checkable:
            group_box.setCheckable(True)
            group_box.setChecked(checked)
        
        # Create appropriate layout
        if layout_type == 'horizontal':
            layout = QHBoxLayout(group_box)
        elif layout_type == 'grid':
            layout = QGridLayout(group_box)
        elif layout_type == 'form':
            layout = QFormLayout(group_box)
        else:  # vertical
            layout = QVBoxLayout(group_box)
        
        group_box.setLayout(layout)
        
        logger.debug(f"Created group box: '{title}' with {layout_type} layout")
        return group_box
    
    @staticmethod
    def create_label(text: str,
                    font_size: int = DEFAULT_FONT_SIZE,
                    bold: bool = False,
                    alignment: Qt.AlignmentFlag = Qt.AlignLeft,
                    word_wrap: bool = False,
                    color: str = None) -> QLabel:
        """
        Create a standardized label
        
        Args:
            text: Label text
            font_size: Font size
            bold: Whether text is bold
            alignment: Text alignment
            word_wrap: Whether to enable word wrap
            color: Text color (hex string)
            
        Returns:
            Configured QLabel
        """
        label = QLabel(text)
        
        font = QFont()
        font.setPointSize(font_size)
        if bold:
            font.setBold(True)
        label.setFont(font)
        
        label.setAlignment(alignment)
        label.setWordWrap(word_wrap)
        
        if color:
            label.setStyleSheet(f"color: {color};")
        
        return label
    
    @staticmethod
    def create_line_edit(placeholder: str = "",
                        max_length: int = None,
                        read_only: bool = False,
                        password: bool = False,
                        validator=None) -> QLineEdit:
        """
        Create a standardized line edit
        
        Args:
            placeholder: Placeholder text
            max_length: Maximum text length
            read_only: Whether widget is read-only
            password: Whether this is a password field
            validator: Input validator
            
        Returns:
            Configured QLineEdit
        """
        line_edit = QLineEdit()
        
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        
        if max_length:
            line_edit.setMaxLength(max_length)
        
        line_edit.setReadOnly(read_only)
        
        if password:
            line_edit.setEchoMode(QLineEdit.Password)
        
        if validator:
            line_edit.setValidator(validator)
        
        return line_edit
    
    @staticmethod
    def create_text_edit(read_only: bool = False,
                        font_family: str = "Consolas",
                        font_size: int = 9,
                        max_height: int = None,
                        placeholder: str = "") -> QTextEdit:
        """
        Create a standardized text edit widget
        
        Args:
            read_only: Whether widget is read-only
            font_family: Font family name
            font_size: Font size
            max_height: Maximum height
            placeholder: Placeholder text
            
        Returns:
            Configured QTextEdit
        """
        text_edit = QTextEdit()
        text_edit.setReadOnly(read_only)
        
        font = QFont(font_family, font_size)
        text_edit.setFont(font)
        
        if max_height:
            text_edit.setMaximumHeight(max_height)
        
        if placeholder:
            text_edit.setPlaceholderText(placeholder)
        
        return text_edit
    
    @staticmethod
    def create_progress_bar(minimum: int = 0,
                          maximum: int = 100,
                          value: int = 0,
                          text_visible: bool = True,
                          format_string: str = "%p%") -> QProgressBar:
        """
        Create a standardized progress bar
        
        Args:
            minimum: Minimum value
            maximum: Maximum value
            value: Initial value
            text_visible: Whether to show percentage text
            format_string: Format string for text
            
        Returns:
            Configured QProgressBar
        """
        progress_bar = QProgressBar()
        progress_bar.setMinimum(minimum)
        progress_bar.setMaximum(maximum)
        progress_bar.setValue(value)
        progress_bar.setTextVisible(text_visible)
        progress_bar.setFormat(format_string)
        
        return progress_bar
    
    @staticmethod
    def create_splitter(orientation: Qt.Orientation,
                       settings_key: str = None,
                       collapsible: bool = False,
                       handle_width: int = 6) -> QSplitter:
        """
        Create a standardized splitter
        
        Args:
            orientation: Splitter orientation
            settings_key: Settings key for persistence
            collapsible: Whether children can be collapsed
            handle_width: Handle width in pixels
            
        Returns:
            Configured QSplitter
        """
        if settings_key:
            # Use existing ResizableSplitter if settings key provided
            from gui_main import ResizableSplitter
            splitter = ResizableSplitter(orientation, settings_key)
        else:
            splitter = QSplitter(orientation)
            splitter.setChildrenCollapsible(collapsible)
            splitter.setHandleWidth(handle_width)
        
        return splitter
    
    @staticmethod
    def create_combo_box(items: List[str] = None,
                        editable: bool = False,
                        current_text: str = None) -> QComboBox:
        """
        Create a standardized combo box
        
        Args:
            items: List of items to add
            editable: Whether combo box is editable
            current_text: Initial selected text
            
        Returns:
            Configured QComboBox
        """
        combo_box = QComboBox()
        combo_box.setEditable(editable)
        
        if items:
            combo_box.addItems(items)
        
        if current_text and current_text in items:
            combo_box.setCurrentText(current_text)
        
        return combo_box
    
    @staticmethod
    def create_spin_box(minimum: int = 0,
                       maximum: int = 100,
                       value: int = 0,
                       suffix: str = "",
                       single_step: int = 1) -> QSpinBox:
        """
        Create a standardized spin box
        
        Args:
            minimum: Minimum value
            maximum: Maximum value
            value: Initial value
            suffix: Value suffix
            single_step: Step size
            
        Returns:
            Configured QSpinBox
        """
        spin_box = QSpinBox()
        spin_box.setMinimum(minimum)
        spin_box.setMaximum(maximum)
        spin_box.setValue(value)
        spin_box.setSingleStep(single_step)
        
        if suffix:
            spin_box.setSuffix(suffix)
        
        return spin_box
    
    @staticmethod
    def create_dialog(title: str,
                     parent: QWidget = None,
                     modal: bool = True,
                     size: Tuple[int, int] = (600, 400)) -> QDialog:
        """
        Create a standardized dialog
        
        Args:
            title: Dialog title
            parent: Parent widget
            modal: Whether dialog is modal
            size: Dialog size as (width, height)
            
        Returns:
            Configured QDialog
        """
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setModal(modal)
        dialog.resize(size[0], size[1])
        
        # Center on parent if available
        if parent:
            dialog.move(
                parent.geometry().center() - dialog.rect().center()
            )
        
        return dialog
    
    @staticmethod
    def create_button_box(buttons: QDialogButtonBox.StandardButton = QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                         orientation: Qt.Orientation = Qt.Horizontal) -> QDialogButtonBox:
        """
        Create a standardized dialog button box
        
        Args:
            buttons: Standard buttons to include
            orientation: Button orientation
            
        Returns:
            Configured QDialogButtonBox
        """
        button_box = QDialogButtonBox(buttons, orientation)
        return button_box
    
    def create_statistics_summary_widget(self, 
                                       total_images: int = 0,
                                       unique_models: int = 0,
                                       positive_tags: int = 0,
                                       negative_tags: int = 0) -> QWidget:
        """
        Create a statistics summary widget with consistent layout
        
        Args:
            total_images: Total number of processed images
            unique_models: Number of unique models
            positive_tags: Number of positive tags
            negative_tags: Number of negative tags
            
        Returns:
            Widget containing statistics summary
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Create summary labels
        labels = [
            ("Images Processed", total_images),
            ("Unique Models", unique_models),
            ("Positive Tags", positive_tags),
            ("Negative Tags", negative_tags)
        ]
        
        for label_text, value in labels:
            label = self.create_label(
                f"{label_text}: {value}",
                font_size=12,
                bold=False
            )
            layout.addWidget(label)
        
        layout.addStretch()
        return widget

"""
Common imports module for MetaPicPick
Centralizes frequently used imports to reduce duplication across modules.
"""

# Standard library imports
import os
import sys
import json
import csv
import re
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QTextEdit, QLineEdit, QMessageBox,
    QComboBox, QCheckBox, QTabWidget, QSplitter, QGroupBox, QFormLayout,
    QScrollArea, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QSlider,
    QProgressDialog, QFrame, QSizePolicy, QGridLayout, QTreeWidget,
    QTreeWidgetItem, QStatusBar, QMenuBar, QAction
)

from PyQt5.QtGui import (
    QPixmap, QFont, QColor, QPalette, QIcon, QPainter, QBrush, QPen,
    QFontMetrics, QTextCursor, QTextCharFormat, QSyntaxHighlighter
)

from PyQt5.QtCore import (
    Qt, QSettings, QTimer, QThread, pyqtSignal, QObject, QSize, QRect,
    QPoint, QUrl, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QVariantAnimation, QAbstractAnimation
)

# Common exceptions for standardized error handling
class MetaPicPickError(Exception):
    """Base exception for MetaPicPick application"""
    pass

class MetadataError(MetaPicPickError):
    """Exception for metadata-related errors"""
    pass

class ParserError(MetaPicPickError):
    """Exception for parser-related errors"""
    pass

class StatisticsError(MetaPicPickError):
    """Exception for statistics-related errors"""
    pass

class ConfigurationError(MetaPicPickError):
    """Exception for configuration-related errors"""
    pass

# Common constants
DEFAULT_FONT_SIZE = 10
DEFAULT_BUTTON_HEIGHT = 30
DEFAULT_TABLE_ROW_HEIGHT = 25
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900

# Common color scheme
COLORS = {
    'primary': '#2196F3',
    'secondary': '#FF9800', 
    'success': '#4CAF50',
    'warning': '#FF5722',
    'error': '#F44336',
    'background': '#FAFAFA',
    'surface': '#FFFFFF',
    'text_primary': '#212121',
    'text_secondary': '#757575'
}

# Common styles
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            font-weight: bold;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #1976D2;
        }}
        QPushButton:pressed {{
            background-color: #0D47A1;
        }}
    """,
    'secondary': f"""
        QPushButton {{
            background-color: {COLORS['secondary']};
            color: white;
            font-weight: bold;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #F57C00;
        }}
        QPushButton:pressed {{
            background-color: #E65100;
        }}
    """,
    'success': f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: white;
            font-weight: bold;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #388E3C;
        }}
        QPushButton:pressed {{
            background-color: #1B5E20;
        }}
    """,
    'warning': f"""
        QPushButton {{
            background-color: {COLORS['warning']};
            color: white;
            font-weight: bold;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #D84315;
        }}
        QPushButton:pressed {{
            background-color: #BF360C;
        }}
    """
}

TABLE_STYLE = """
    QTableWidget {
        gridline-color: #E0E0E0;
        background-color: white;
        alternate-background-color: #F5F5F5;
        selection-background-color: #E3F2FD;
    }
    QTableWidget::item {
        padding: 4px;
        border-bottom: 1px solid #E0E0E0;
    }
    QHeaderView::section {
        background-color: #F0F0F0;
        padding: 6px;
        border: 1px solid #D0D0D0;
        font-weight: bold;
    }
"""

GROUPBOX_STYLE = """
    QGroupBox {
        font-weight: bold;
        border: 2px solid #CCCCCC;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 5px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
"""

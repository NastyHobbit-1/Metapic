#!/usr/bin/env python
"""Validate the codebase structure without requiring all dependencies"""

import os
import ast
import sys

def check_file_exists(filepath, description=""):
    """Check if a file exists and report"""
    if os.path.exists(filepath):
        print(f"✓ {description or os.path.basename(filepath)} exists")
        return True
    else:
        print(f"✗ {description or os.path.basename(filepath)} missing")
        return False

def check_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print(f"✓ {os.path.basename(filepath)} has valid syntax")
        return True
    except SyntaxError as e:
        print(f"✗ {os.path.basename(filepath)} has syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ {os.path.basename(filepath)} error: {e}")
        return False

def check_imports(filepath):
    """Check what modules a file imports"""
    imports = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                    
        return imports
    except Exception as e:
        print(f"  Warning: Could not parse imports from {filepath}: {e}")
        return []

def check_class_methods(filepath, required_methods):
    """Check if classes in a file have required methods"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        classes_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods_found = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                
                missing_methods = [m for m in required_methods if m not in methods_found]
                if missing_methods:
                    print(f"  ✗ Class {class_name} missing methods: {missing_methods}")
                    return False
                else:
                    print(f"  ✓ Class {class_name} has required methods: {required_methods}")
                    classes_found.append(class_name)
                    
        return len(classes_found) > 0
        
    except Exception as e:
        print(f"  Error checking class methods in {filepath}: {e}")
        return False

def validate_codebase():
    """Validate the overall codebase structure"""
    print("MetaPicPick Codebase Structure Validation")
    print("=" * 50)
    
    all_good = True
    
    # Check main files exist
    main_files = {
        "gui_main.py": "Main GUI application",
        "plugin_manager.py": "Plugin manager",  
        "parser_plugin_interface.py": "Parser interface",
        "metadata_utils.py": "Metadata utilities",
        "raw_metadata_loader.py": "Raw metadata loader",
        "requirements.txt": "Dependencies list",
        "MetaPicPick.spec": "PyInstaller spec file",
        "build.bat": "Build script",
        "package.bat": "Package script"
    }
    
    print("\\n1. Checking main files...")
    for filepath, description in main_files.items():
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Check parsers directory
    print("\\n2. Checking parsers directory...")
    parsers_dir = "parsers"
    if check_file_exists(parsers_dir, "Parsers directory"):
        parser_files = [
            "parsers/__init__.py",
            "parsers/automatic1111_parser.py", 
            "parsers/comfyui_parser.py",
            "parsers/novelai_parser.py"
        ]
        
        for parser_file in parser_files:
            if not check_file_exists(parser_file):
                all_good = False
    else:
        all_good = False
    
    # Check syntax of Python files
    print("\\n3. Checking Python file syntax...")
    python_files = [
        "gui_main.py",
        "plugin_manager.py", 
        "parser_plugin_interface.py",
        "metadata_utils.py",
        "raw_metadata_loader.py",
        "parsers/__init__.py",
        "parsers/automatic1111_parser.py",
        "parsers/comfyui_parser.py", 
        "parsers/novelai_parser.py"
    ]
    
    for py_file in python_files:
        if os.path.exists(py_file):
            if not check_syntax(py_file):
                all_good = False
                
    # Check parser classes have required methods
    print("\\n4. Checking parser classes...")
    parser_files = [
        "parsers/automatic1111_parser.py",
        "parsers/comfyui_parser.py",
        "parsers/novelai_parser.py"
    ]
    
    for parser_file in parser_files:
        if os.path.exists(parser_file):
            print(f"  Checking {os.path.basename(parser_file)}...")
            if not check_class_methods(parser_file, ['detect', 'parse']):
                all_good = False
    
    # Check imports consistency  
    print("\\n5. Checking import consistency...")
    
    # Check that gui_main.py imports exist
    if os.path.exists("gui_main.py"):
        imports = check_imports("gui_main.py")
        required_imports = ["metadata_utils", "plugin_manager"]
        missing = [imp for imp in required_imports if imp not in imports]
        if missing:
            print(f"  ✗ gui_main.py missing imports: {missing}")
            all_good = False
        else:
            print("  ✓ gui_main.py has required imports")
            
    print("\\n" + "=" * 50)
    if all_good:
        print("✓ All structural checks passed!")
        print("\\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test the application: python gui_main.py") 
        print("3. Build executable: python -m PyInstaller MetaPicPick.spec")
    else:
        print("✗ Some structural issues found. Please fix the errors above.")
        
    return all_good

if __name__ == "__main__":
    validate_codebase()

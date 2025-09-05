# MetaPicPick Tabbed Interface Guide

## 🎉 **New Tabbed Interface Available!**

Your MetaPicPick now has a modern, organized tabbed interface that addresses the crowding issues and makes sections fully resizable!

## 🚀 **How to Use the New Interface**

### **Starting the Tabbed Version**
```bash
# Activate virtual environment first
metapicpick_env\Scripts\Activate.ps1

# Then run the tabbed version
python gui_main_tabbed.py

# Or use the shortcut
run_tabbed.bat
```

## 📑 **Tab Overview**

### **📁 Library Tab** - Main Workspace
**Layout**: Three resizable sections with persistent sizing

1. **Left Panel** (Resizable):
   - **Folder Controls**: Load folder button
   - **Filters Section**: 
     - Search bar (real-time filtering)
     - Model dropdown filter
     - "Only with negative prompt" checkbox
   - **Actions Section**:
     - Bulk rename operations
     - Create folder
     - Move files to folder
     - Export filtered metadata

2. **Center Panel** (Resizable):
   - Image list with filenames
   - Click any image to preview
   - Shows filtered results in real-time

3. **Bottom Preview Panel** (Resizable):
   - **Left**: Image preview (auto-scaled)
   - **Right**: Quick metadata viewer
   - Truncates long prompts for readability

### **📝 Metadata Tab** - Detailed Editing
**Layout**: Two main resizable sections

1. **Left Panel** (Form Editor):
   - File selection button
   - Scrollable metadata form with all fields:
     - Model info (name, base model)
     - Generation params (steps, CFG, seed, scheduler, sampler)
     - Dimensions (width, height, size, format)
     - Prompts (positive, negative)
     - Extra metadata
   - Save metadata button

2. **Right Panel** (Preview & Validation):
   - **Top**: Live image preview
   - **Bottom**: Raw metadata viewer (JSON format, monospace font)
   - Updates automatically when loading files

### **⚡ Batch Tab** - Future Features
- Placeholder for batch processing tools
- Will include bulk operations, progress tracking
- Organized layout ready for implementation

### **⚙️ Settings Tab** - Preferences
- **Left**: Settings categories list
- **Right**: Settings content area
- Resizable layout ready for preferences

## 🔧 **Resizing Features**

### **How to Resize Panels**
- **Drag splitter handles** between sections
- All splitters are **6px wide** for easy grabbing
- **Minimum sizes** prevent panels from becoming unusable
- **Smooth resizing** with no content jumping

### **Layout Persistence**
- **All panel sizes are automatically saved**
- **Window position and size remembered**
- **Current tab selection restored** on restart
- Each splitter has its own save key for independent sizing

### **Reset Layout**
- **View Menu → Reset Layout** clears all saved sizes
- Returns to default proportions
- Requires restart to take effect

## 📊 **Default Panel Ratios**

### Library Tab:
- **Left panel**: 250px (filters & actions)
- **Right area**: 750px (split into center + preview)
- **Center vs Preview**: 400px : 300px

### Metadata Tab:
- **Form editor**: 600px
- **Preview area**: 400px

## 🎯 **Key Benefits**

### **✅ Solved Crowding Issues**
- Content organized into logical tabs
- Each section has dedicated space
- No more cramped interface

### **✅ Fully Resizable**
- Every section can be resized to your preference
- Layouts persist between sessions
- Professional splitter controls

### **✅ Enhanced Productivity**
- Library tab for browsing and quick operations
- Metadata tab for detailed editing
- Clear separation of concerns

### **✅ Future-Ready**
- Batch and Settings tabs ready for expansion
- Modular architecture for easy feature addition
- Professional UI framework

## 🔄 **Switching Between Versions**

You now have **two interface options**:

### **Original Interface** (`gui_main.py`)
- Single-window with all controls visible
- Good for simple, quick tasks
- More compact but can feel crowded

### **Tabbed Interface** (`gui_main_tabbed.py`) ⭐ **Recommended**
- Modern tabbed organization
- Resizable sections with persistence
- Better for complex workflows
- Professional appearance

## 🛠️ **Building Executables**

The build system now supports both versions:

```bash
# Run build script
build.bat

# Choose version when prompted:
# 1 = Original version → MetaPicPick.exe
# 2 = Tabbed version → MetaPicPick_Tabbed.exe
```

## 💡 **Tips for Best Experience**

1. **Start with Library Tab** - Load your image folder here first
2. **Adjust panels** to your screen size and preference
3. **Use search and filters** to quickly find specific images
4. **Switch to Metadata Tab** for detailed editing of individual files
5. **Layout will remember** your preferences automatically

## 🎊 **What's Delivered**

✅ **Tabbed interface** - No more crowded single window  
✅ **Resizable sections** - Every panel can be adjusted  
✅ **Persistent layouts** - Your sizes are remembered  
✅ **All original features** - Nothing lost in transition  
✅ **Professional design** - Modern, organized interface  
✅ **Easy switching** - Keep both versions available  

Your MetaPicPick is now much more organized and user-friendly! 🎉

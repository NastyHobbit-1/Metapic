# Enhanced Metadata Parsers

This directory contains enhanced versions of the metadata parsers that extract significantly more information from AI-generated images compared to the original parsers.

## Enhanced Parsers

### 1. Enhanced Automatic1111 Parser (`enhanced_automatic1111_parser.py`)
Extracts more comprehensive metadata from Stable Diffusion images generated with Automatic1111 WebUI:

**New Fields Extracted:**
- `model_hash` - Model checkpoint hash
- `scheduler` - Scheduler/schedule type  
- `clip_skip` - CLIP skip value
- `ensd` - ENSD parameter
- `eta` - Eta parameter
- `denoising_strength` - Denoising strength for img2img
- `face_restoration` - Face restoration method
- `codeformer_weight` - CodeFormer weight
- `hires_upscale` - Hi-res fix upscale factor
- `hires_steps` - Hi-res fix steps
- `hires_upscaler` - Hi-res fix upscaler method
- `hires_resize_width/height` - Hi-res fix target dimensions
- `subseed` - Variation seed
- `subseed_strength` - Variation seed strength
- `seed_resize_from_width/height` - Seed resize dimensions
- `controlnet` - ControlNet information
- `version` - Software version
- `karras` - Karras scheduler flag
- `rng` - RNG type
- `token_merging_ratio` - Token merging ratio
- `ti_hashes` - Textual inversion hashes
- `lora_hashes` - LoRA hashes

### 2. Enhanced ComfyUI Parser (`enhanced_comfyui_parser.py`)
Better parsing of ComfyUI workflow JSON data:

**New Features:**
- Extracts parameters from workflow node data
- Identifies model loaders, samplers, encoders automatically
- Extracts LoRA information with strengths
- Processes VAE and ControlNet nodes
- Fallback parameter string parsing
- Better prompt extraction from text encode nodes

**New Fields:**
- `vae` - VAE model name
- `controlnet_strength` - ControlNet strength
- `loras` - Array of LoRA information with strengths
- `extra_data` - Additional ComfyUI metadata

### 3. Enhanced NovelAI Parser (`enhanced_novelai_parser.py`)
Improved NovelAI metadata extraction with base64 decoding:

**New Features:**
- Decodes base64 JSON metadata from PNG comments
- Maps NovelAI-specific field names to standard names
- Extracts qualifiers and advanced parameters
- Better prompt extraction

**New Fields:**
- `qualifiers` - NovelAI booru qualifiers
- `sm`, `sm_dyn` - NovelAI-specific parameters
- `noise_schedule` - Noise scheduling
- `request_type` - Request type
- `signed_hash` - Signed hash

### 4. Enhanced General AI Parser (`enhanced_general_ai_parser.py`)
New general-purpose parser that detects and parses metadata from various AI tools:

**Supported Tools:**
- Stable Diffusion
- Midjourney  
- DALL-E / DALL-E 2
- Leonardo AI
- CivitAI
- Runway ML
- Artbreeder
- DreamStudio
- Adobe Firefly

**Features:**
- Multiple regex patterns for each parameter
- JSON structure parsing
- Robust prompt extraction
- Version information extraction
- Technical parameter detection

## Usage

### Automatic Usage
The enhanced parsers are automatically loaded by the plugin manager and used by the main application. No code changes needed.

### Manual Testing
Use the diagnostic scripts to test the parsers:

```bash
# Compare original vs enhanced parsers
python test_enhanced_parsers.py path/to/image.png

# Demonstrate enhanced extraction
python example_enhanced_usage.py path/to/image.png
```

### In Code
```python
from metadata_utils import extract_metadata

# This automatically uses enhanced parsers
metadata = extract_metadata("image.png")
print(f"Detected: {metadata.get('source')}")
print(f"Fields: {len(metadata)}")
```

## Benefits

1. **More Fields**: Extract 3-5x more metadata fields than original parsers
2. **Better Detection**: Improved detection of AI-generated images
3. **Robust Parsing**: Better handling of various metadata formats
4. **Extended Support**: Support for more AI tools and platforms
5. **Backwards Compatible**: Works with existing code without changes

## Field Mapping

The enhanced parsers standardize field names across different AI tools:

| Standard Name | Automatic1111 | ComfyUI | NovelAI |
|---------------|---------------|---------|---------|
| `cfg_scale` | CFG scale | cfg | scale |
| `denoising_strength` | Denoising strength | denoise | strength |
| `negative_prompt` | Negative prompt | (text encode) | uc |
| `model_name` | Model | ckpt_name | model |

## Installation

The enhanced parsers are already included in your MetaPicPick installation. They will be automatically loaded when you run the application.

## Testing

To verify the enhanced parsers are working:

1. Run the GUI application
2. Load a folder with AI-generated images
3. Select an image and check the metadata fields
4. You should see many more fields populated compared to before

## Troubleshooting

If enhanced parsers are not loading:
1. Check that all files are in the `parsers/` directory
2. Ensure the `parsers/` directory has an `__init__.py` file
3. Check console output for import errors
4. Verify that required dependencies are installed

The system will gracefully fall back to original parsers if enhanced ones fail to load.

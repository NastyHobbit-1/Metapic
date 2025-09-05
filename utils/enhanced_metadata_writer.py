import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any
from PIL import Image, PngImagePlugin, ExifTags
import piexif
import json

class EnhancedMetadataWriter:
    """Enhanced metadata writer that saves metadata in formats compatible with AI tools"""
    
    def __init__(self):
        pass
    
    def save_metadata(self, image_path: str, metadata: Dict[str, Any]) -> bool:
        """Save metadata to image file in appropriate format"""
        try:
            ext = os.path.splitext(image_path)[1].lower()
            
            if ext == ".png":
                return self.save_png_metadata(image_path, metadata)
            elif ext in [".jpg", ".jpeg"]:
                return self.save_jpeg_metadata(image_path, metadata)
            elif ext == ".webp":
                return self.save_webp_metadata(image_path, metadata)
            else:
                print(f"Unsupported format: {ext}")
                return False
                
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return False
    
    def save_png_metadata(self, image_path: str, metadata: Dict[str, Any]) -> bool:
        """Save metadata to PNG file using proper AI tool format"""
        try:
            img = Image.open(image_path)
            
            # Create PNG info object
            pnginfo = PngImagePlugin.PngInfo()
            
            # Build Automatic1111-style parameters string
            parameters_string = self.build_parameters_string(metadata)
            
            # Save in the standard 'parameters' field that AI tools expect
            if parameters_string:
                pnginfo.add_text("parameters", parameters_string)
            
            # Also save individual fields for other tools
            for key, value in metadata.items():
                if key.startswith('_') or not value:
                    continue  # Skip internal fields and empty values
                
                # Convert value to string
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value)
                else:
                    value_str = str(value)
                
                # Add individual metadata fields
                pnginfo.add_text(key, value_str)
            
            # Save the image with metadata
            img.save(image_path, "PNG", pnginfo=pnginfo)
            return True
            
        except Exception as e:
            print(f"Error saving PNG metadata: {e}")
            return False
    
    def save_jpeg_metadata(self, image_path: str, metadata: Dict[str, Any]) -> bool:
        """Save metadata to JPEG file using EXIF"""
        try:
            # Build parameters string
            parameters_string = self.build_parameters_string(metadata)
            
            # Create EXIF dictionary
            exif_dict = {"0th": {}, "Exif": {}, "1st": {}, "thumbnail": None}
            
            # Save parameters in ImageDescription (this is what most tools read)
            if parameters_string:
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = parameters_string.encode("utf-8")
            
            # Save additional metadata in UserComment
            additional_metadata = {}
            for key, value in metadata.items():
                if key.startswith('_') or not value:
                    continue
                if isinstance(value, (dict, list)):
                    additional_metadata[key] = json.dumps(value)
                else:
                    additional_metadata[key] = str(value)
            
            if additional_metadata:
                user_comment = json.dumps(additional_metadata)
                # EXIF UserComment has a specific format
                user_comment_bytes = b"UNICODE\x00" + user_comment.encode("utf-8")
                exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment_bytes
            
            # Generate EXIF bytes
            exif_bytes = piexif.dump(exif_dict)
            
            # Save image with EXIF data
            img = Image.open(image_path)
            img.save(image_path, "JPEG", exif=exif_bytes)
            return True
            
        except Exception as e:
            print(f"Error saving JPEG metadata: {e}")
            return False
    
    def save_webp_metadata(self, image_path: str, metadata: Dict[str, Any]) -> bool:
        """Save metadata to WebP file using XMP"""
        try:
            # Build parameters string
            parameters_string = self.build_parameters_string(metadata)
            
            # Create temporary XMP file
            temp_dir = tempfile.mkdtemp()
            xmp_path = os.path.join(temp_dir, "metadata.xmp")
            
            try:
                # Build XMP content
                xmp_content = self.build_xmp_content(metadata, parameters_string)
                
                with open(xmp_path, "w", encoding="utf-8") as f:
                    f.write(xmp_content)
                
                # Use webpmux to embed XMP (if available)
                webpmux_paths = [
                    "webpmux.exe",
                    "webpmux",
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "webpmux.exe")
                ]
                
                webpmux_path = None
                for path in webpmux_paths:
                    if shutil.which(path) or os.path.isfile(path):
                        webpmux_path = path
                        break
                
                if webpmux_path:
                    temp_output = image_path + ".temp.webp"
                    result = subprocess.run([
                        webpmux_path, "-set", "xmp", xmp_path, 
                        image_path, "-o", temp_output
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        os.replace(temp_output, image_path)
                        return True
                    else:
                        print(f"webpmux failed: {result.stderr}")
                        return False
                else:
                    # Fallback: try to save using PIL with limited metadata support
                    print("webpmux not found, using PIL fallback (limited metadata support)")
                    img = Image.open(image_path)
                    
                    # Save parameters in EXIF if possible
                    if parameters_string:
                        exif_dict = {"0th": {piexif.ImageIFD.ImageDescription: parameters_string.encode("utf-8")}}
                        exif_bytes = piexif.dump(exif_dict)
                        img.save(image_path, "WebP", exif=exif_bytes)
                    else:
                        img.save(image_path, "WebP")
                    return True
                    
            finally:
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            print(f"Error saving WebP metadata: {e}")
            return False
    
    def build_parameters_string(self, metadata: Dict[str, Any]) -> str:
        """Build Automatic1111-style parameters string that AI tools can read"""
        
        # Get the main components
        positive_prompt = metadata.get('positive_prompt', '').strip()
        negative_prompt = metadata.get('negative_prompt', '').strip()
        
        # Build the parameters string
        parameters_parts = []
        
        # Add positive prompt
        if positive_prompt:
            parameters_parts.append(positive_prompt)
        
        # Add negative prompt
        if negative_prompt:
            parameters_parts.append(f"Negative prompt: {negative_prompt}")
        
        # Build parameter list
        param_items = []
        
        # Standard parameters in expected order
        param_mapping = [
            ('steps', 'Steps'),
            ('sampler', 'Sampler'),
            ('cfg_scale', 'CFG scale'),
            ('seed', 'Seed'),
            ('width', 'Size', lambda w, h: f"{w}x{h}" if metadata.get('height') else None),
            ('model_hash', 'Model hash'),
            ('model_name', 'Model'),
            ('vae_hash', 'VAE hash'),
            ('vae', 'VAE'),
            ('denoising_strength', 'Denoising strength'),
            ('clip_skip', 'Clip skip'),
            ('ensd', 'ENSD'),
            ('eta', 'Eta'),
            ('hires_upscale', 'Hires upscale'),
            ('hires_steps', 'Hires steps'),
            ('hires_upscaler', 'Hires upscaler'),
            ('subseed', 'Variation seed'),
            ('subseed_strength', 'Variation seed strength'),
            ('version', 'Version'),
            ('lora_hashes', 'Lora hashes'),
            ('ti_hashes', 'TI hashes')
        ]
        
        for mapping in param_mapping:
            if len(mapping) == 2:
                field_name, param_name = mapping
                value = metadata.get(field_name)
                if value:
                    param_items.append(f"{param_name}: {value}")
            elif len(mapping) == 3:
                field_name, param_name, formatter = mapping
                if field_name == 'width' and metadata.get('width') and metadata.get('height'):
                    size_str = formatter(metadata['width'], metadata['height'])
                    if size_str:
                        param_items.append(f"Size: {size_str}")
        
        # Add any additional parameters that weren't handled above
        handled_fields = {item[0] for item in param_mapping}
        handled_fields.update(['positive_prompt', 'negative_prompt', 'height', 'size'])
        
        for key, value in metadata.items():
            if (key not in handled_fields and 
                not key.startswith('_') and 
                value and 
                key not in ['source', 'extra', 'description']):
                
                # Convert key to readable format
                readable_key = key.replace('_', ' ').title()
                param_items.append(f"{readable_key}: {value}")
        
        # Join parameters
        if param_items:
            parameters_parts.append(", ".join(param_items))
        
        return "\n".join(parameters_parts)
    
    def build_xmp_content(self, metadata: Dict[str, Any], parameters_string: str) -> str:
        """Build XMP content for WebP files"""
        
        xmp_template = '''<?xpacket begin='﻿' id='W5M0MpCehiHzreSzNTczkc9d'?>
<x:xmpmeta xmlns:x='adobe:ns:meta/'>
  <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
    <rdf:Description rdf:about=''
        xmlns:exif='http://ns.adobe.com/exif/1.0/'
        xmlns:tiff='http://ns.adobe.com/tiff/1.0/'
        xmlns:dc='http://purl.org/dc/elements/1.1/'>
{content}
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end='w'?>'''
        
        content_parts = []
        
        # Add parameters string as description
        if parameters_string:
            escaped_params = parameters_string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            content_parts.append(f'      <dc:description>{escaped_params}</dc:description>')
        
        # Add individual metadata fields
        for key, value in metadata.items():
            if key.startswith('_') or not value:
                continue
                
            # Convert value to string and escape XML
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            escaped_value = value_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            safe_key = key.replace(' ', '_').replace(':', '_')
            content_parts.append(f'      <exif:{safe_key}>{escaped_value}</exif:{safe_key}>')
        
        content = '\n'.join(content_parts)
        return xmp_template.format(content=content)


# Create global instance
enhanced_metadata_writer = EnhancedMetadataWriter()

# Maintain backward compatibility
def save_metadata(image_path: str, metadata: Dict[str, Any]) -> bool:
    """Backward compatible save_metadata function"""
    return enhanced_metadata_writer.save_metadata(image_path, metadata)

from .out_request import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import server
import glob
from PIL import Image
from pathlib import Path

COMPRESSED_DIR = Path('compressed_images')
COMPRESSED_DIR.mkdir(exist_ok=True)

# Function to create a compressed version of the image
def create_compressed_image(image_path, compressed_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail((800, 800), Image.ANTIALIAS)  # Resize the image to a maximum of 800x800
        img.save(compressed_path, "JPEG", quality=50)  # Save as JPEG with 70% quality

def delete_image_file(directory, filename):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']
    for ext in image_extensions:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    return False
def list_image_files(directory):
    # List of common image file extensions
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.tif', '*.webp']
    
    # Initialize an empty list to store image file paths
    image_files = []

    # Loop through each extension and use glob to find matching files
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, extension)))
    
    # Sort files by modification time, newest first
    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Extract just the file names
    image_file_names = [os.path.basename(file) for file in image_files]

    return image_file_names
from aiohttp import web
@server.PromptServer.instance.routes.get("/outputs")
async def get_outputs_img_name(request):
    return web.json_response(list_image_files("output"))
@server.PromptServer.instance.routes.delete("/outputs/{filename}")
async def delete_output_img_name(request):
    filename = request.match_info['filename']
    if delete_image_file("output", filename):
        return web.json_response({'status': 'success', 'message': f'File {filename} deleted successfully.'})
    else:
        return web.json_response({'status': 'error', 'message': f'File {filename} not found.'}, status=404)

# Endpoint to serve compressed image
@server.PromptServer.instance.routes.get("/compressed/{filename}")
async def serve_compressed_image(request):
    filename = request.match_info['filename']
    image_path = Path('output') / filename
    compressed_path = COMPRESSED_DIR / filename

    if not compressed_path.exists():
        if image_path.exists():
            create_compressed_image(image_path, compressed_path)
        else:
            return web.json_response({'status': 'error', 'message': f'File {filename} not found.'}, status=404)

    return web.FileResponse(compressed_path)
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
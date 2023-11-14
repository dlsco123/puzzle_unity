import bpy
from pathlib import Path
from PIL import Image
import sys

# Get the command-line arguments
args = sys.argv[sys.argv.index("--") + 1:]
input_image_path = args[0]
size = int(args[1])  # Number of rows and columns
output_dir = Path(args[2]).resolve()

# Ensure the output directory exists
output_dir.mkdir(parents=True, exist_ok=True)

# Function to split the image and create textured planes
def create_textured_planes(image_path, size, output_dir):
    with Image.open(image_path) as img:
        width, height = img.size

        # Adjust the size of each piece based on the puzzle size
        if size == 2:
            piece_width = width // 2
            piece_height = height // 2
        elif size == 3:
            piece_width = width // 3
            piece_height = height // 3
        elif size == 4:
            piece_width = width // 4
            piece_height = height // 4
        else:
            print("Unsupported puzzle size.")
            return

        piece_count = 0
        for i in range(size):
            for j in range(size):
                piece_name = f"piece_{piece_count}"
                # Calculate the piece's coordinates (left, upper, right, lower)
                piece_coords = (
                    j * piece_width,
                    i * piece_height,
                    (j + 1) * piece_width,
                    (i + 1) * piece_height
                )

                # Crop the image and save the texture
                cropped = img.crop((
                    piece_coords[0], 
                    height - piece_coords[3], 
                    piece_coords[2], 
                    height - piece_coords[1]
                ))
                texture_path = output_dir / f"{piece_name}.png"
                cropped.save(texture_path)

                # Create plane and texture
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
                plane = bpy.context.active_object
                plane.name = piece_name

                # Create material with texture
                mat = bpy.data.materials.new(name=f"Mat_{piece_name}")
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image.image = bpy.data.images.load(str(texture_path))
                mat.node_tree.links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
                plane.data.materials.append(mat)

                # Set plane location relative to the size of the grid
                plane.location.x = (j - size / 2 + 0.5) * piece_width
                plane.location.y = (i - size / 2 + 0.5) * piece_height
                plane.location.z = 0

                piece_count += 1

        # Ensure all pieces are selected for export
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.select_set(True)

# Clear the current scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create the puzzle pieces and textured planes
create_textured_planes(input_image_path, size, output_dir)

# Save the scene as an FBX file
output_fbx_path = output_dir / f"puzzle_{size}x{size}.fbx"
bpy.ops.export_scene.fbx(filepath=str(output_fbx_path), use_selection=True)

print(f"FBX saved at: {output_fbx_path}")
print(f"Textures saved at: {output_dir}")

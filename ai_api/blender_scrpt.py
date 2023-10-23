import bpy
import sys
import os

def create_puzzle_plane(image_path, piece_coords, plane_name):
    # 새로운 플레인 생성
    bpy.ops.mesh.primitive_plane_add(size=1)
    plane = bpy.context.active_object
    plane.name = plane_name

    # 이미지 텍스처를 플레인에 할당
    mat = bpy.data.materials.new(name=plane_name)
    mat.use_nodes = True
    plane.data.materials.append(mat)

    shader_nodes = mat.node_tree.nodes

    # 새 이미지 텍스처 노드 생성
    tex_image = shader_nodes.new('ShaderNodeTexImage')
    tex_image.image = bpy.data.images.load(image_path)
    
    shader_nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 1, 1, 1)

    # 이미지 분할 좌표 설정
    tex_image.extension = 'CLIP'
    tex_image.image_user.min_x = piece_coords[0]
    tex_image.image_user.min_y = piece_coords[1]
    tex_image.image_user.max_x = piece_coords[2]
    tex_image.image_user.max_y = piece_coords[3]

    # 연결 설정
    mat.node_tree.links.new(shader_nodes['Principled BSDF'].inputs['Base Color'], tex_image.outputs['Color'])
    
    return plane


def split_and_map_image(image_path, rows, cols):
    # 이미지의 크기 및 정보 로딩
    image = bpy.data.images.load(image_path)
    width, height = image.size
    piece_width = width / cols
    piece_height = height / rows
    
    for i in range(rows):
        for j in range(cols):
            piece_name = f"Piece_{i}_{j}"
            piece_coords = (
                j / cols, 
                (rows - i - 1) / rows, 
                (j + 1) / cols, 
                (rows - i) / rows
            )
            plane = create_puzzle_plane(image_path, piece_coords, piece_name)
            plane.location.x = j
            plane.location.y = i
            plane.rotation_euler.z = 0


# 인자 처리하기 (sys.argv는 Blender에 특정 인자를 전달하기 위해 사용됩니다.)
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # 이 부분은 Blender 인자와 사용자 인자를 분리합니다.
input_image_path = argv[0]
output_fbx_path = argv[1]

# 기존 모든 오브젝트 삭제 (선택적)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 이미지 분할 및 매핑
split_and_map_image(input_image_path, 4, 4)

# 결과를 FBX 파일로 저장
bpy.ops.export_scene.fbx(filepath=output_fbx_path)
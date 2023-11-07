import bpy
import sys
import os
from PIL import Image

def create_puzzle_plane(image_path, piece_coords, plane_name, rows, cols):
    # 새로운 플레인 생성
    bpy.ops.mesh.primitive_plane_add(size=1)
    plane = bpy.context.active_object
    plane.name = plane_name

    # 이미지 텍스처를 플레인에 할당
    mat = bpy.data.materials.new(name=plane_name)
    mat.use_nodes = True
    plane.data.materials.append(mat)

    shader_nodes = mat.node_tree.nodes
    shader_nodes.clear()  # 기존 노드를 모두 제거

    # "Principled BSDF" 및 "Material Output" 노드 생성
    principled_node = shader_nodes.new('ShaderNodeBsdfPrincipled')
    output_node = shader_nodes.new('ShaderNodeOutputMaterial')
    # "Principled BSDF" 및 "Material Output" 노드 생성 부분 아래에 다음 코드 추가
    mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

    # 새 이미지 텍스처 노드 생성
    tex_image = shader_nodes.new('ShaderNodeTexImage')
    
    # 이미지 분할 처리
    with Image.open(image_path) as im:
        cropped = im.crop(piece_coords)
        output_texture_path = os.path.join(os.path.dirname(os.path.dirname(image_path)), "result", f"{plane_name}.png")
        cropped.save(output_texture_path)
    
    tex_image.image = bpy.data.images.load(output_texture_path)
    
    # Texture Coordinate 및 Mapping 노드 추가
    tex_coord = shader_nodes.new('ShaderNodeTexCoord')
    tex_mapping = shader_nodes.new('ShaderNodeMapping')
    tex_mapping.vector_type = 'TEXTURE'
    
    # Translation (이동) 값 설정
    tex_mapping.inputs['Location'].default_value[0] = -piece_coords[0] * cols  # x offset
    tex_mapping.inputs['Location'].default_value[1] = -piece_coords[1] * rows  # y offset
    
    # Scale (확대/축소) 값 설정
    # tex_mapping.inputs['Scale'].default_value[0] = cols  # x scale
    # tex_mapping.inputs['Scale'].default_value[1] = rows  # y scale
    # Scale (확대/축소) 값 설정
    tex_mapping.inputs['Scale'].default_value[0] = 1 / cols  # x scale for one piece
    tex_mapping.inputs['Scale'].default_value[1] = 1 / rows  # y scale for one piece

    
    # 연결 설정
    mat.node_tree.links.new(tex_coord.outputs['UV'], tex_mapping.inputs['Vector'])
    mat.node_tree.links.new(tex_mapping.outputs['Vector'], tex_image.inputs['Vector'])
    mat.node_tree.links.new(principled_node.inputs['Base Color'], tex_image.outputs['Color'])  # Color 연결 변경

    # 텍스처 이미지를 부모 디렉토리의 'result' 폴더에 저장
    parent_dir = os.path.dirname(os.path.dirname(image_path))
    result_dir = os.path.join(parent_dir, "result")
    if not os.path.exists(result_dir):  # 'result' 폴더가 없으면 생성
        os.makedirs(result_dir)
    output_texture_path = os.path.join(result_dir, f"{plane_name}.png")
    tex_image.image.save_render(output_texture_path)

    return plane, output_texture_path  # 플레인과 텍스처 이미지 경로를 반환

piece_count = 0  # 퍼즐 조각에 대한 일련번호를 저장할 전역 변수

def split_and_map_image(image_path, rows, cols):
    global piece_count
    # 이미지의 크기 및 정보 로딩
    image = bpy.data.images.load(image_path)
    width, height = image.size
    piece_width = width / cols
    piece_height = height / rows
    
    texture_paths = []

    for i in range(rows):
        for j in range(cols):
            piece_name = f"Piece_{piece_count}" 
            piece_coords = (
                j * piece_width, 
                height - (i + 1) * piece_height,
                (j + 1) * piece_width,
                height - i * piece_height
            )
            plane, texture_path = create_puzzle_plane(image_path, piece_coords, piece_name, rows, cols)
            plane.location.x = j - cols/2 + 0.5
            plane.location.y = i - rows/2 + 0.5
            plane.rotation_euler.z = 0
            texture_paths.append(texture_path)
            piece_count += 1

    return texture_paths
            

# 인자 처리하기
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # Blender 인자와 사용자 인자 분리
input_image_path = argv[0]
output_fbx_name = os.path.splitext(os.path.basename(argv[1]))[0] + ".fbx"

# output_fbx_name = os.path.basename(argv[1])  # FBX 파일의 이름만 추출
parent_dir = os.path.dirname(os.path.dirname(input_image_path))
output_fbx_path = os.path.join(parent_dir, "result", output_fbx_name)  # 부모 디렉토리의 'result' 폴더로 경로 설정

# 기존 모든 오브젝트 삭제 (선택적)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 이미지 분할 및 매핑
texture_paths = split_and_map_image(input_image_path, 4, 4)
# FBX 저장하기
bpy.ops.export_scene.fbx(filepath=output_fbx_path)


# 결과를 출력
print("FBX:", output_fbx_path)
for path in texture_paths:
    print("PNG:", path)
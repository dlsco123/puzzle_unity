from fastapi import APIRouter, File, UploadFile
import subprocess
import os
from datetime import datetime

router = APIRouter()

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()

    # 지정된 경로에 이미지 저장
    os.makedirs("ai_api/uploads", exist_ok=True)
    
    # 타임스탬프를 이용해 고유한 파일 이름 생성
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    save_path = f"ai_api/uploads/temp_image_{timestamp}.png"

    with open(save_path, "wb") as f:
        f.write(contents)

    # subprocess를 사용하여 Blender 스크립트 실행
    subprocess.run(
        [
            "/path_to_blender_executable/blender", 
            "--background", 
            "--python", "blender_script.py", 
            "--", save_path, f"output_{timestamp}.fbx"
        ], 
        check=True
    )
    
    return {"message": "Image received and processed!"}

from fastapi import APIRouter, File, UploadFile
import subprocess
import os
import uuid

router = APIRouter()

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()

    # 지정된 경로에 이미지 저장
    os.makedirs("uploads", exist_ok=True)
    unique_filename = f"temp_image_{uuid.uuid4().hex}.png"
    save_path = os.path.abspath(os.path.join("uploads", unique_filename))
    with open(save_path, "wb") as f:
        f.write(contents)
    
    # subprocess를 사용하여 Blender 스크립트 실행
    subprocess.run(
        [
            "D:\\blender.exe", 
            "--background", 
            "--python", "D:\\final_unity\\ai_api\\blender_scrpt.py", 
            "--", save_path, f"output_{uuid.uuid4().hex}.fbx"
        ], 
        check=True
    )
    
    return {"message": f"Image received and processed! Saved as {unique_filename}"}

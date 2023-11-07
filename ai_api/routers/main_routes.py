from fastapi import APIRouter, File, UploadFile, HTTPException
import subprocess
import os
import uuid
from fastapi.responses import FileResponse
import zipfile

router = APIRouter()

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()

    # 지정된 경로에 이미지 저장
    os.makedirs("uploads", exist_ok=True)
    unique_filename = f"temp_image_{uuid.uuid4().hex}.png"
    save_path = os.path.abspath(os.path.join("uploads", unique_filename))
    with open(save_path, "wb") as f:
        f.write(contents)
    
    try:
        # subprocess를 사용하여 Blender 스크립트 실행
        subprocess.run(
            [
                "D:\\blender.exe", 
                "--background", 
                "--python", "D:\\final_unity\\ai_api\\blender_scrpt.py", 
                "--", save_path, unique_filename 
            ], 
            check=True
        )
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error while processing the image with Blender.")

    # Blender 스크립트에서 생성된 파일들을 ZIP 파일로 압축
    result_dir = os.path.abspath("result")
    zip_path = os.path.abspath(os.path.join("result", f"{uuid.uuid4().hex}.zip"))

    if os.path.exists(result_dir):
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(result_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not file_path.endswith(".zip"):  # ZIP 파일 제외
                        zipf.write(file_path, os.path.basename(file_path))
    else:
        raise HTTPException(status_code=500, detail="Result directory not found.")


    # 임시 파일 및 디렉터리 정리 (선택적)
    os.remove(save_path)
    for file in os.listdir(result_dir):
        file_path = os.path.join(result_dir, file)
        if file_path != zip_path:  # ZIP 파일은 삭제하지 않도록 예외 처리
            os.remove(file_path)

    # 생성된 ZIP 파일을 반환
    return FileResponse(zip_path, media_type="application/octet-stream", filename="output_files.zip")

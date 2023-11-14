from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import firebase_admin
from firebase_admin import credentials, storage
import subprocess
import os
import uuid
import zipfile
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수로부터 Firebase 설정 읽기
firebase_key_path = os.getenv('FIREBASE_KEY_PATH')
firebase_storage_bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET').replace('gs://', '')

# Firebase Admin 초기화
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {'storageBucket': firebase_storage_bucket_name})

router = APIRouter()

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), size: int = 2):
    print("Size received in FastAPI:", size)
    if size not in [2, 3, 4]:
        raise HTTPException(status_code=400, detail="Size must be 2, 3, or 4.")

    contents = await file.read()

    # 지정된 경로에 이미지 저장
    os.makedirs("uploads", exist_ok=True)
    unique_filename = f"temp_image_{uuid.uuid4().hex}.png"
    save_path = os.path.abspath(os.path.join("uploads", unique_filename))
    with open(save_path, "wb") as f:
        f.write(contents)
    
    try:
        subprocess.run(
            [
                "D:/blender.exe", 
                "--background", 
                "--python", "D:/final_unity/ai_api/blender_scrpt.py", 
                "--", save_path, str(size), "result"
            ], 
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Blender error: {e.stderr.decode()}")

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

    # Firebase Storage에 업로드
    bucket = storage.bucket()
    blob = bucket.blob(f"output_files/{uuid.uuid4().hex}.zip")
    blob.upload_from_filename(zip_path)

    # 업로드된 파일의 URL 반환
    return {"url": blob.public_url}
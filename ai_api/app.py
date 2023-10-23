from typing import List
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
import base64


app = FastAPI()

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    
    pieces = split_image(img, rows=3, cols=3)

    # 이미지 조각을 바이트로 변환하여 응답 목록으로 저장
    byte_io_list = []
    for piece in pieces:
        byte_io = io.BytesIO()
        piece.save(byte_io, format="PNG")
        byte_io_list.append(byte_io.getvalue())

    return {
        "message": "Image received and splitted!",
        "number_of_pieces": len(byte_io_list),
        # 이 부분은 이미지 데이터를 실제로 반환하는 예제이며, 필요에 따라 제거하거나 수정할 수 있습니다.
        "pieces": [piece.decode("utf-8") for piece in map(base64.b64encode, byte_io_list)]
    }

def split_image(image, rows, cols):
    width, height = image.size
    tile_width = width // cols
    tile_height = height // rows

    pieces = []
    for i in range(0, rows):
        for j in range(0, cols):
            left = j * tile_width
            upper = i * tile_height
            right = left + tile_width
            bottom = upper + tile_height
            piece = image.crop((left, upper, right, bottom))
            pieces.append(piece)
    return pieces

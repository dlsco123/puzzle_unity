import socket
from PIL import Image
import io
import struct

def split_image(image_path, rows, cols):
    img = Image.open(image_path)
    width, height = img.size

    tile_width = width // cols
    tile_height = height // rows

    pieces = []
    for i in range(0, rows):
        for j in range(0, cols):
            left = j * tile_width
            upper = i * tile_height
            right = left + tile_width
            bottom = upper + tile_height
            piece = img.crop((left, upper, right, bottom))
            pieces.append(piece)
    return pieces

def create_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)
    print('Server is listening...')
    
    while True:
        client_socket, addr = server_socket.accept()
        print('Got connection from', addr)
        
        # 데이터 길이(4바이트) 수신
        data_length = client_socket.recv(4)
        data_length = struct.unpack('!I', data_length)[0]

        # 이미지 데이터 수신
        img_data = client_socket.recv(data_length)
        img = Image.open(io.BytesIO(img_data))
        
        # 이미지 분할
        pieces = split_image(img, rows=3, cols=3)
        # pieces = split_image("your_image_path.png", 4, 4)

        # 추가적인 처리
        
        client_socket.close()

    
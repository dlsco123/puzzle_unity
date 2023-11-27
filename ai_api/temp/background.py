import cv2
import numpy as np
from pathlib import Path

def process_image(input_image_path, output_image_path):
    # 이미지 로드
    image = cv2.imread(input_image_path)

    # 노이즈 제거
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # 그레이스케일로 변환
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # 대비 향상
    equalized = cv2.equalizeHist(gray)

    # 이진화
    _, binary = cv2.threshold(equalized, 127, 255, cv2.THRESH_BINARY_INV)

    # 선 연결을 위한 팽창(dilation)
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)

    # 선 강화를 위해 캐니 에지 디텍터 사용
    edges = cv2.Canny(dilated, threshold1=30, threshold2=100)

    # 컨투어 확장
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(edges)
    cv2.drawContours(mask, contours, -1, color=255, thickness=cv2.FILLED)

    # 결과 이미지를 확인하기 위한 부분
    result = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow('Result', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 마스크 반전
    inverted_mask = cv2.bitwise_not(mask)

    # 이미지와 반전된 마스크 결합
    bg_removed = cv2.bitwise_and(image, image, mask=inverted_mask)

    # 알파 채널(투명도) 추가
    b, g, r = cv2.split(bg_removed)
    alpha_channel = np.ones(b.shape, dtype=b.dtype) * 255 # 투명도 채널 생성, 모든 픽셀을 완전 불투명으로 설정
    bg_removed = cv2.merge((b, g, r, alpha_channel))

    # 이미지 저장
    cv2.imwrite(output_image_path, bg_removed)

# 이미지 처리 실행
input_path = 'input.png'
output_path = 'background_removed.png'
process_image(input_path, output_path)

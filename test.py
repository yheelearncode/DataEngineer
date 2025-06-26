import easyocr

reader = easyocr.Reader(['en', 'ko'], gpu=False)
image_path = "stock_data2.png"
result = reader.readtext(image_path)

# 인식된 모든 텍스트 출력
for i, detection in enumerate(result):
    print(f"Detection {i}: {detection[1]} (좌표: {detection[0][0]})")
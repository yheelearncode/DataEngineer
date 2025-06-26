import easyocr

reader = easyocr.Reader(['en','ko'], gpu=False)

image_path = "stock_data2.png"
result  = reader.readtext(image_path)
result.sort(key=lambda x: (x[0][0][1], x[0][0][0]))  # y좌표, x좌표 순으로 정렬
row = []
for detection in result:
    text = detection[1]
    row.append(text)
    if len(row) == 4:  # 5개 셀이 한 행
        try:
            name = row[0]
            trade_type= row[1]
            price = row[2]
            quantity= row[3]
          

            print(f"종목: {name}, 매수매도: {trade_type}, 가격: {price}, 거래량: {quantity}\n")
            row = []  # row 초기화
        except Exception as e:
            print(f"행 처리 중 오류: {row}, 오류: {e}")
            row = []  # 오류 발생 시에도 초기화









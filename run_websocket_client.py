import websocket
import json

TOKEN = "d0iaal9r01qrfsaeu1j0d0iaal9r01qrfsaeu1jg"

def on_message(ws, message):
    data = json.loads(message)
    print(data)

def on_open(ws):
    ws.send(json.dumps({
        "type": "subscribe",
        "symbol": "AAPL"
    }))

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

socket_url = f"wss://ws.finnhub.io?token={TOKEN}"
ws = websocket.WebSocketApp(socket_url,
                             on_open=on_open,
                             on_message=on_message,
                             on_close=on_close)
ws.run_forever()

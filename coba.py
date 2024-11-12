import asyncio
from model.request_controller import IncomingCommand, RequestPacket, ResponsePacketRecentReportHour
import json

async def send_request():
    reader, writer = await asyncio.open_connection('localhost', 50011)

    # Membuat RequestPacket dan mengirimkannya sebagai JSON
    request_packet = RequestPacket(command=IncomingCommand.GET_RECENT_HOUR, payload={"vehicle_id": 1})
    writer.write(request_packet.model_dump_json().encode("utf-8"))
    await writer.drain()
    print("Request sent to server.")

    # Penerimaan bertahap hingga seluruh data JSON diterima
    response_data = b""
    while True:
        chunk = await reader.read(1024)  # Terima data per 1024 byte
        if not chunk:
            break
        response_data += chunk

    response_json = response_data.decode("utf-8")

    # Memproses respons JSON
    try:
        response_packet = ResponsePacketRecentReportHour.model_validate_json(response_json)
        print("Response from server:", response_packet)
    except Exception as e:
        print("Error processing server response:", e)

    writer.close()
    await writer.wait_closed()

# Jalankan klien
asyncio.run(send_request())

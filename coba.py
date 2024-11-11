import asyncio
import json
from model.request_controller import RequestPacket, IncomingCommand, ResponsePacketRecentReportHour

async def send_request():
    reader, writer = await asyncio.open_connection('127.0.0.1', 50011)  # Ganti dengan host dan port yang sesuai

    # Buat instance RequestPacket
    request_packet = RequestPacket(
        command=IncomingCommand.GET_RECENT_HOUR,
        payload={"vehicle_id": 1}  # Payload sesuai dengan struktur yang diinginkan
    )
    
    # Serialize dan kirim data ke server
    data = request_packet.model_dump_json().encode('utf-8')
    writer.write(data)
    await writer.drain()
    print("Request sent to server.")

    # Terima respons dari server
    response_data = await reader.read(1000)  # Batasan buffer disesuaikan
    response_json = response_data.decode('utf-8')
    
    # Parse respons ke model
    response_packet = ResponsePacketRecentReportHour.model_validate_json(response_json)
    print("Response received from server:", response_packet)

    writer.close()
    await writer.wait_closed()

# Jalankan fungsi async untuk mengirim permintaan
asyncio.run(send_request())

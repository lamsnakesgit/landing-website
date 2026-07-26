import asyncio
import json
import ssl
import sys
import websockets
from pykalkan.adapter import Adapter
from pykalkan.enums import StorageType

KEY_PATH = '/opt/ai_lawyer/keys/GOST.p12'
KEY_PASSWORD = 'D8.891A6QzG6'

def sign_xml(xml_data):
    # Pass the shared library path
    kalkan = Adapter('/opt/ai_lawyer/scripts/libkalkancryptwr-64.so')
    try:
        kalkan.init()
        # args: cert_path, cert_password, store_type, alias
        kalkan.load_key_store(
            KEY_PATH,
            KEY_PASSWORD,
            StorageType.KCST_PKCS12.value
        )
        # Sign XML
        signed_xml = kalkan.sign_xml(
            xml_data,
            0, # flag
            "", # signNodeId
            "", # parentSignNode
            ""  # parentNameSpace
        )
        kalkan.finalize()
        return signed_xml
    except Exception as e:
        print(f"Kalkan Error: {e}")
        kalkan.finalize()
        return None

async def handler(websocket):
    print(f"[WS] Client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"[WS] RECEIVED: {message}")
            if message == '--heartbeat--':
                await websocket.send('--heartbeat--')
                continue
            
            try:
                data = json.loads(message)
                if data.get('module') == 'kz.gov.pki.knca.basics' and data.get('method') == 'sign':
                    xml_to_sign = data['args']['data']
                    print("[WS] Signing XML...")
                    signed = sign_xml(xml_to_sign)
                    if signed:
                        resp = {
                            "code": "200",
                            "responseObject": signed
                        }
                        print("[WS] Successfully signed!")
                    else:
                        resp = {
                            "code": "500",
                            "message": "Signature failed"
                        }
                    await websocket.send(json.dumps(resp))
                else:
                    await websocket.send('{"code":"500","message":"Method not implemented"}')
            except json.JSONDecodeError:
                print("[WS] Invalid JSON")
    except Exception as e:
        print(f"[WS] Error: {e}")

async def start_ws_server():
    print("[WS] Starting server on wss://127.0.0.1:13579")
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('/opt/ai_lawyer/scripts/cert.pem', '/opt/ai_lawyer/scripts/key.pem')
    server = await websockets.serve(handler, '127.0.0.1', 13579, ssl=ssl_context)
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(start_ws_server())

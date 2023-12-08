import os
import io
import uuid
import qrcode
import base64
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    url = req.params.get('url')
    if not url:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            url = req_body.get('url')

    if url:
        # Create a QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')

        # Upload the QR code to Azure Blob Storage
        connection_string = os.environ['StorageConnection']
        container_name = os.environ.get('BLOB_CONTAINER_NAME', 'qr-codes')
        blob_name = str(url) + '.png'

        blob_client = BlobServiceClient.from_connection_string(conn_str=connection_string,container_name=container_name)
        blob_client.upload_blob(img_byte_arr)

        # Return the QR code image and URL
        return func.HttpResponse(
            f"QR code generated and saved to Azure Blob Storage!\nBlob URL: {blob_client.url}\n",
            headers={"Content-Type": "text/plain"},
        )

    else:
        return func.HttpResponse(
            "Please pass a url on the query string or in the request body",
            status_code=400
        )
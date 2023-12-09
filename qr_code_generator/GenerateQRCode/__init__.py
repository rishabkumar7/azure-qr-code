import os
import qrcode
import io
import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    url = req.params.get('url')
    if not url:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            url = req_body.get('url')

    if url:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Convert the image to a byte array
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        img_byte_arr = byte_arr.getvalue()

        # Get Azure Blob Storage details
        connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.environ.get('BLOB_CONTAINER_NAME', 'qr-codes')
        blob_name = str(url) + '.png'

        # Create a blob client using the local file name as the name for the blob
        blob_client = BlobServiceClient.from_connection_string(connection_string).get_blob_client(container_name, blob_name)

        # Upload the created file
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
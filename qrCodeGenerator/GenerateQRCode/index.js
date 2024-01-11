const QRCode = require('qrcode');
const { BlobServiceClient } = require('@azure/storage-blob');
const connectionString = process.env.STORAGE_CONNECTION_STRING;

module.exports = async function (context, req) {
    context.log('Generating QR code');

    const url = (req.query.url || (req.body && req.body.url));
    if (!url) {
        context.res = {
            status: 400,
            body: "Please pass a url on the query string or in the request body"
        };
        return;
    }

    try {
        // Generate QR Code
        const qrCodeData = await QRCode.toDataURL(url);

        // Upload to Azure Blob Storage
        const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);
        const containerName = 'qr-codes';
        const containerClient = blobServiceClient.getContainerClient(containerName);
        await containerClient.createIfNotExists({ access: 'blob' });

        // Using regex to remove 'https://' from the URL
        const modifiedUrl = url.replace(/^https?:\/\//, '');
        const blobName = modifiedUrl + '.png';
        const blockBlobClient = containerClient.getBlockBlobClient(blobName);

        const matches = qrCodeData.match(/^data:([A-Za-z-+\/]+);base64,(.+)$/);
        const buffer = Buffer.from(matches[2], 'base64');

        await blockBlobClient.upload(buffer, buffer.length);

        context.res = {
            status: 200,
            body: { qr_code_url: blockBlobClient.url },
            headers: {
                'Content-Type': 'application/json'
            }
        };
    } catch (error) {
        context.res = {
            status: 500,
            body: `Error: ${error.message}`
        };
    }
};

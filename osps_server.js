const express = require('express');
const bodyParser = require('body-parser');
const syslog = require('syslog-client');
const axios = require('axios');
const AWS = require('aws-sdk');
const { BlobServiceClient } = require('@azure/storage-blob');
const { Storage } = require('@google-cloud/storage');
const splunkLogger = require('splunk-logging').Logger;
const fs = require('fs');
const path = require('path');

// Load configuration from JSON file
let config = require('./config.json');

// Initialize AWS SDK for S3
const s3 = new AWS.S3();

// Initialize Azure Blob Service
const blobServiceClient = BlobServiceClient.fromConnectionString(config.azureConnectionString);
const containerClient = blobServiceClient.getContainerClient(config.azureContainerName);

// Initialize Google Cloud Storage
const storage = new Storage();
const gcsBucket = storage.bucket(config.gcsBucketName);

// Initialize Splunk HEC
const splunk = new splunkLogger({
  token: config.splunkToken,
  url: config.splunkUrl
});

// Express App Setup
const app = express();
const port = 3000;

app.use(bodyParser.json());

// Web interface route to serve the configuration file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Route to get current configuration
app.get('/config', (req, res) => {
  res.json(config);
});

// Route to update configuration
app.post('/config', (req, res) => {
  config = req.body;
  fs.writeFileSync('config.json', JSON.stringify(config, null, 2));
  res.send('Configuration updated');
});

// Function to route logs to S3
async function routeToS3(log) {
  const params = {
    Bucket: config.s3BucketName,
    Key: `${Date.now()}.log`,
    Body: JSON.stringify(log)
  };
  await s3.upload(params).promise();
}

// Function to route logs to Azure Blob
async function routeToAzure(log) {
  const blockBlobClient = containerClient.getBlockBlobClient(`${Date.now()}.log`);
  await blockBlobClient.upload(JSON.stringify(log), Buffer.byteLength(JSON.stringify(log)));
}

// Function to route logs to GCS
async function routeToGCS(log) {
  const file = gcsBucket.file(`${Date.now()}.log`);
  await file.save(JSON.stringify(log));
}

// Function to route logs to Splunk HEC
async function routeToSplunk(log) {
  const payload = {
    event: log,
    sourcetype: 'json',
    index: 'main'
  };
  splunk.send(payload, (error, response) => {
    if (error) {
      console.error('Error sending to Splunk:', error);
    } else {
      console.log('Log sent to Splunk:', response);
    }
  });
}

// Function to route logs to filesystem
function routeToFileSystem(log) {
  const logFilePath = path.join(__dirname, 'logs', `${Date.now()}.log`);
  fs.writeFileSync(logFilePath, JSON.stringify(log));
}

// Function to process incoming logs
async function processLog(log) {
  if (config.routes.s3) await routeToS3(log);
  if (config.routes.azure) await routeToAzure(log);
  if (config.routes.gcs) await routeToGCS(log);
  if (config.routes.splunk) await routeToSplunk(log);
  if (config.routes.filesystem) routeToFileSystem(log);
}

// TCP Route (Raw Data)
const tcpPort = 5000;
const net = require('net');
const tcpServer = net.createServer((socket) => {
  socket.on('data', (data) => {
    const log = { message: data.toString(), source: 'TCP' };
    processLog(log);
  });
});

tcpServer.listen(tcpPort, () => {
  console.log(`TCP server listening on port ${tcpPort}`);
});

// Syslog Route
const syslogPort = 514;
const syslogServer = syslog.createClient('localhost', syslogPort);
syslogServer.on('message', (message) => {
  const log = { message, source: 'Syslog' };
  processLog(log);
});

syslogServer.listen();

// API Collector Route
app.post('/api/logs', (req, res) => {
  const log = req.body;
  log.source = 'API';
  processLog(log);
  res.send('Log received and processed');
});

// Start the Express Server
app.listen(port, () => {
  console.log(`Log router running on http://localhost:${port}`);
});


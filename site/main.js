const brokerUrl = 'wss://broker.hivemq.com:8884/mqtt';
const topic = 'myhome/esp32s3/led';

const client = mqtt.connect(brokerUrl);

function sendMQTT(command) {
    client.publish(topic, command);
    console.log('Sent command: ' + command);
}
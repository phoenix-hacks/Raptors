import requests
import json
import time

with open('/home/mayankch283/carboncare-logistics-agent/server/synthetic_data_1.json', 'r') as f:
    data = json.load(f)

# Train the model
response = requests.post('http://localhost:5000/api/v1/sustainability/train', json={
    'historical_data': data['data']['shipments'],
    'historical_scores': data['data']['sustainability_scores']
})

time.sleep(5)

#analyze single shipment
# shipment_to_analyze = data['data']['shipments'][0]
# complete_shipment = {
#     'shipment_id': shipment_to_analyze.get('shipment_id', 'SAMPLE_ID'),
#     'origin': shipment_to_analyze.get('origin', 'Sample Origin'),
#     'destination': shipment_to_analyze.get('destination', 'Sample Destination'),
#     'transport_mode': shipment_to_analyze.get('transport_mode', 'truck'),
#     'packages': shipment_to_analyze.get('packages', [{'weight': 10, 'dimensions': '10x10x10'}])
# }

# Analyze single shipment
# response2 = requests.post('http://localhost:5000/api/v1/sustainability/analyze', json=complete_shipment)

# Prepare the payload for batch analysis
batch_payload = {
    'data': {
        'shipments': data['data']['shipments']
    }
}

# Send a POST request to the batch-analyze endpoint
response = requests.post('http://localhost:5000/api/v1/sustainability/batch-analyze', json=batch_payload)

# Print the response
print("Status Code:", response.status_code)
print("Response JSON:")
print(json.dumps(response.json(), indent=1))
        
import requests

url = 'http://localhost:5000/insert-event'  # Adjust the URL if necessary
data = {
    'date': '2024-03-05',
    'description': 'Study for exam'
}

response = requests.post(url, json=data)
print(response.text)

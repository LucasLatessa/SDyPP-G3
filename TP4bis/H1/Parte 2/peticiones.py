import requests
from concurrent.futures import ThreadPoolExecutor

def send_request(url):
    files = {
        'imagen': open('/C:/Users/Leone/Downloads/Vane+David_ 001.jpg', 'rb'),
    }
    data = {
        'particion-x': '10',
        'particion-y': '10'
    }
    response = requests.post(url, files=files, data=data)
    print(response.text)

if __name__ == "__main__":
    url = 'http://127.0.0.1:5000/sobel'
    num_requests = 10
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        executor.map(send_request, [url]*num_requests)

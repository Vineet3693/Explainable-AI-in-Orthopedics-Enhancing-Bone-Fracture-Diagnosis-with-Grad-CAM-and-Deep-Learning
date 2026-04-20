import requests
import json

API_URL = "http://localhost:8001"
TEST_IMG = "D:\\Coding Workspace\\fracture detection ai\\data\\raw\\FracAtlas\\images\\Fractured\\IMG0000019.jpg"

def main():
    print("--- 1. Health Check ---")
    res = requests.get(f"{API_URL}/health")
    print(json.dumps(res.json(), indent=2))

    print("\n--- 2. Get Models ---")
    res = requests.get(f"{API_URL}/api/v1/models")
    print(json.dumps(res.json(), indent=2))

    print("\n--- 3. Predict (Ensemble) ---")
    with open(TEST_IMG, "rb") as buf:
        res = requests.post(f"{API_URL}/api/v1/predict", files={"file": ("IMG0000019.jpg", buf, "image/jpeg")}, params={"model_name": "ensemble"})
        print(json.dumps(res.json(), indent=2))
        
    print("\n--- 4. Predict (VGG16) ---")
    with open(TEST_IMG, "rb") as buf:
        res = requests.post(f"{API_URL}/api/v1/predict", files={"file": ("IMG0000019.jpg", buf, "image/jpeg")}, params={"model_name": "VGG16"})
        print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    main()

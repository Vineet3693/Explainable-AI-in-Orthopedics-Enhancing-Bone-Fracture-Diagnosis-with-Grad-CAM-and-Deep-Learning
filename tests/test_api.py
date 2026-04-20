from fastapi.testclient import TestClient
from deployment.api.ensemble_api import app
from PIL import Image
import pytest

client = TestClient(app)


def test_get_models_endpoint():
    """Models endpoint should return JSON with model list or appropriate error."""
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert 'models' in data
    # best_model is optional but when present should be one of the names
    if 'best_model' in data and data['models']:
        names = [m['name'] for m in data['models']]
        assert data['best_model'] in names


def test_predict_without_file():
    """POST /predict without a file should error with validation"""
    response = client.post("/predict")
    assert response.status_code in (400, 422)


def test_predict_invalid_model_param(tmp_path):
    """Providing a nonexistent model name should return 400"""
    img_path = tmp_path / "x.jpg"
    Image.new('RGB', (224,224)).save(img_path)
    with open(img_path, 'rb') as f:
        response = client.post("/predict?model=nonexistent", files={"file": f})
    assert response.status_code == 400
    assert "not available" in response.text

# note: we don't run a full prediction since it requires trained weights
# but the invalid-model check above exercises the new query param handling.


def test_simple_app_models_endpoint():
    """Verify that the legacy app also exposes /api/v1/models"""
    from app import app as simple_app
    client2 = TestClient(simple_app)
    resp = client2.get("/api/v1/models")
    assert resp.status_code == 200
    data = resp.json()
    assert 'models' in data
    # if ensemble is running inside simple app, best_model may be present
    if 'best_model' in data and data['models']:
        assert data['best_model'] in [m['name'] for m in data['models']]

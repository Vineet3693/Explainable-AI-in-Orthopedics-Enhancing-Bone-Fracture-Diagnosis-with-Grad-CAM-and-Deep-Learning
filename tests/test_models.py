"""
Test suite for models
"""

import pytest
import numpy as np
from src.models.base_model import BaseModel
from src.models.resnet50_model import ResNet50Model
from src.models.vgg16_model import VGG16Model
from src.models.efficientnet_model import EfficientNetModel
from src.models.model_factory import ModelFactory


class TestResNet50Model:
    """Test ResNet50Model class"""
    
    def test_model_creation(self):
        """Test model creation"""
        model = ResNet50Model(
            input_shape=(224, 224, 3),
            num_classes=1,
            freeze_base=True
        )
        
        model.build_model()
        
        assert model.model is not None
        assert model.model.name == 'ResNet50_Fracture'
    
    def test_model_compilation(self):
        """Test model compilation"""
        model = ResNet50Model()
        model.build_model()
        model.compile_model()
        
        assert model.model.optimizer is not None
    
    def test_model_prediction(self):
        """Test model prediction"""
        model = ResNet50Model()
        model.build_model()
        
        # Create dummy input
        dummy_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
        
        # Predict
        output = model.model.predict(dummy_input, verbose=0)
        
        assert output.shape == (1, 1)


class TestVGG16Model:
    """Test VGG16Model class"""
    
    def test_model_creation(self):
        """Test VGG16 model creation"""
        model = VGG16Model()
        model.build_model()
        
        assert model.model is not None
        assert model.model.name == 'VGG16_Fracture'


class TestEfficientNetModel:
    """Test EfficientNetModel class"""
    
    def test_model_creation(self):
        """Test EfficientNet model creation"""
        model = EfficientNetModel(variant='B0')
        model.build_model()
        
        assert model.model is not None
        assert 'EfficientNet' in model.model.name


class TestModelFactory:
    """Test ModelFactory class"""
    
    def test_create_resnet50(self):
        """Test creating ResNet50 via factory"""
        model = ModelFactory.create_model('resnet50')
        
        assert isinstance(model, ResNet50Model)
    
    def test_create_vgg16(self):
        """Test creating VGG16 via factory"""
        model = ModelFactory.create_model('vgg16')
        
        assert isinstance(model, VGG16Model)
    
    def test_create_efficientnet(self):
        """Test creating EfficientNet via factory"""
        model = ModelFactory.create_model('efficientnet_b0')
        
        assert isinstance(model, EfficientNetModel)
    
    def test_list_models(self):
        """Test listing available models"""
        models = ModelFactory.list_models()
        
        assert 'resnet50' in models
        assert 'vgg16' in models
        assert 'efficientnet_b0' in models


def test_fracture_ensemble_individual_and_summary(tmp_path):
    """Verify that FractureEnsemble can produce predictions for a given model and summarize"""
    from src.ensemble.ensemble_predictor import FractureEnsemble
    import tensorflow as tf
    from PIL import Image

    # Build a minimal dummy model for testing
    dummy = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(224,224,3)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    dummy.compile(optimizer='adam', loss='binary_crossentropy')

    # instantiate ensemble without invoking __init__
    ens = FractureEnsemble.__new__(FractureEnsemble)
    ens.models_dir = ''
    ens.models = {'dummy': dummy}
    ens.model_weights = {'dummy': 1.0}
    ens.model_info = {'dummy': {'accuracy': 0.5, 'auc':0.5, 'recall':0.5}}

    # create a fake image file
    img_path = tmp_path / "test.jpg"
    Image.new('RGB', (224,224)).save(img_path)

    # test individual prediction
    result = ens.predict_individual(str(img_path), 'dummy')
    assert result['model'] == 'dummy'
    assert 'confidence' in result
    assert result['prediction'] in ['Fractured', 'Non-Fractured']

    # test summary returns the dummy entry
    summary = ens.get_model_summary()
    assert summary['total_models'] == 1
    assert summary['models'][0]['name'] == 'dummy'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

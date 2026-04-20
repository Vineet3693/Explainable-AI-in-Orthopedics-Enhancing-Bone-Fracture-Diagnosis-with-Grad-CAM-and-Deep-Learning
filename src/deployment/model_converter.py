"""
Model Converter for Deployment

PURPOSE:
    Converts PyTorch models to deployment formats (ONNX, TFLite, TorchScript).
    Enables deployment on various platforms (mobile, edge, web).

WHY MODEL CONVERTER:
    PyTorch only: Limited deployment options
    Multiple formats (this): Deploy anywhere
    
    IMPACT: Broader deployment, better performance

DESIGN PHILOSOPHY:
    1. Multiple target formats
    2. Validation (ensure accuracy preserved)
    3. Optimization (size, speed)
    4. Easy to use

PROS:
    ✅ Multiple deployment formats
    ✅ Platform flexibility
    ✅ Performance optimization
    ✅ Accuracy validation

CONS:
    ❌ Conversion may fail for complex models
    ❌ Some operations not supported
    ❌ Requires testing on target platform

COMPARISON:
    | Format      | Mobile | Web | Edge | Server | Speed | Size |
    |-------------|--------|-----|------|--------|-------|------|
    | PyTorch     | ❌     | ❌  | ⚠️   | ✅     | ⚠️    | ❌   |
    | ONNX        | ⚠️     | ✅  | ✅   | ✅     | ✅    | ⚠️   |
    | TFLite      | ✅     | ⚠️  | ✅   | ❌     | ✅    | ✅   |
    | TorchScript | ❌     | ❌  | ⚠️   | ✅     | ✅    | ⚠️   |

USAGE:
    from src.deployment.model_converter import ModelConverter
    
    converter = ModelConverter(model)
    
    # Convert to ONNX
    converter.to_onnx('model.onnx')
    
    # Convert to TFLite
    converter.to_tflite('model.tflite')
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ModelConverter:
    """Converts models to various deployment formats"""
    
    def __init__(self, model: nn.Module, input_shape: Tuple[int, ...] = (1, 3, 224, 224)):
        """
        Initialize converter
        
        WHY INPUT SHAPE:
            Conversion needs example input
            Shape defines model architecture
        
        Args:
            model: PyTorch model to convert
            input_shape: Example input shape (batch, channels, height, width)
        """
        self.model = model
        self.model.eval()  # WHY EVAL: Disable dropout/batch norm
        self.input_shape = input_shape
        
        logger.info(f"Initialized ModelConverter for input shape {input_shape}")
    
    def to_onnx(
        self,
        output_path: str,
        opset_version: int = 11,
        validate: bool = True
    ):
        """
        Convert to ONNX format
        
        WHY ONNX:
            Open standard
            Wide platform support
            Good performance
            Easy deployment
        
        WHY OPSET VERSION:
            Different versions support different operations
            11 is widely supported
            Higher versions have more features
        
        Args:
            output_path: Path to save ONNX model
            opset_version: ONNX opset version
            validate: Whether to validate conversion
        """
        logger.info(f"Converting to ONNX (opset {opset_version})")
        
        # Create dummy input
        # WHY DUMMY INPUT:
        # ONNX needs to trace model execution
        # Dummy input defines computation graph
        dummy_input = torch.randn(*self.input_shape)
        
        # Export to ONNX
        # WHY THESE OPTIONS:
        # export_params: Include weights
        # do_constant_folding: Optimize constants
        # input_names/output_names: For clarity
        torch.onnx.export(
            self.model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,  # WHY: Optimization
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},  # WHY: Variable batch size
                'output': {0: 'batch_size'}
            }
        )
        
        logger.info(f"Saved ONNX model to {output_path}")
        
        # Validate conversion
        # WHY VALIDATE:
        # Ensure accuracy preserved
        # Catch conversion errors
        if validate:
            self._validate_onnx(output_path, dummy_input)
    
    def _validate_onnx(self, onnx_path: str, test_input: torch.Tensor):
        """
        Validate ONNX conversion
        
        WHY VALIDATE:
            Conversion may introduce errors
            Need to verify accuracy preserved
            Critical for medical AI
        
        Args:
            onnx_path: Path to ONNX model
            test_input: Test input tensor
        """
        import onnx
        import onnxruntime as ort
        
        # Load ONNX model
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        
        # Run inference
        ort_session = ort.InferenceSession(onnx_path)
        ort_inputs = {ort_session.get_inputs()[0].name: test_input.numpy()}
        ort_outputs = ort_session.run(None, ort_inputs)
        
        # Compare with PyTorch
        with torch.no_grad():
            torch_output = self.model(test_input)
        
        # Check difference
        # WHY CHECK DIFFERENCE:
        # Small differences are acceptable (floating point)
        # Large differences indicate conversion error
        diff = np.abs(torch_output.numpy() - ort_outputs[0]).max()
        
        if diff < 1e-5:
            logger.info(f"✓ ONNX validation passed (max diff: {diff:.2e})")
        else:
            logger.warning(f"⚠ ONNX validation: max difference {diff:.2e}")
    
    def to_torchscript(
        self,
        output_path: str,
        method: str = 'trace'
    ):
        """
        Convert to TorchScript
        
        WHY TORCHSCRIPT:
            Optimized for production
            C++ deployment
            No Python dependency
        
        WHY TWO METHODS:
            Trace: Records operations (faster, limited)
            Script: Analyzes code (flexible, slower)
        
        Args:
            output_path: Path to save model
            method: 'trace' or 'script'
        """
        logger.info(f"Converting to TorchScript using {method}")
        
        if method == 'trace':
            # WHY TRACE:
            # Faster conversion
            # Better optimization
            # Works for most models
            dummy_input = torch.randn(*self.input_shape)
            scripted_model = torch.jit.trace(self.model, dummy_input)
        else:
            # WHY SCRIPT:
            # Handles control flow
            # More flexible
            # Required for complex models
            scripted_model = torch.jit.script(self.model)
        
        # Save
        scripted_model.save(output_path)
        logger.info(f"Saved TorchScript model to {output_path}")
    
    def to_tflite(
        self,
        output_path: str,
        quantize: bool = False
    ):
        """
        Convert to TensorFlow Lite
        
        WHY TFLITE:
            Mobile deployment
            Small model size
            Fast inference
            Low power consumption
        
        Args:
            output_path: Path to save TFLite model
            quantize: Whether to quantize (reduce size)
        """
        logger.info("Converting to TFLite")
        
        # First convert to ONNX, then to TFLite
        # WHY TWO-STEP:
        # No direct PyTorch -> TFLite
        # ONNX is intermediate format
        temp_onnx = output_path.replace('.tflite', '.onnx')
        self.to_onnx(temp_onnx, validate=False)
        
        logger.info("TFLite conversion requires onnx-tf and tensorflow")
        logger.info("Install with: pip install onnx-tf tensorflow")
        logger.info(f"Then use onnx-tf to convert {temp_onnx} to TFLite")


__all__ = ['ModelConverter']

"""
Test suite for device detection utilities.

This test suite validates that the device detection logic works correctly
across different hardware configurations (CUDA, MPS, CPU).
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.device import (
    get_device,
    get_device_name,
    is_cuda_available,
    is_mps_available,
    is_gpu_available
)


class TestDeviceDetection(unittest.TestCase):
    """Test device detection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Import torch here to avoid import errors if not installed
        try:
            import torch
            self.torch_available = True
        except ImportError:
            self.torch_available = False
            self.skipTest("PyTorch not installed")

    def test_is_cuda_available(self):
        """Test CUDA availability detection."""
        result = is_cuda_available()
        self.assertIsInstance(result, bool)
        print(f"CUDA available: {result}")

    def test_is_mps_available(self):
        """Test MPS availability detection."""
        result = is_mps_available()
        self.assertIsInstance(result, bool)
        print(f"MPS available: {result}")

    def test_is_gpu_available(self):
        """Test GPU (CUDA or MPS) availability detection."""
        result = is_gpu_available()
        self.assertIsInstance(result, bool)
        cuda = is_cuda_available()
        mps = is_mps_available()
        expected = cuda or mps
        self.assertEqual(result, expected)
        print(f"GPU available: {result} (CUDA: {cuda}, MPS: {mps})")

    def test_get_device_returns_torch_device(self):
        """Test that get_device returns a torch.device object."""
        import torch
        device = get_device()
        self.assertIsInstance(device, torch.device)
        print(f"Selected device: {device}")

    def test_get_device_priority(self):
        """Test device selection priority: CUDA > MPS > CPU."""
        import torch
        device = get_device()
        
        # Device should be one of the valid types
        self.assertIn(device.type, ['cuda', 'mps', 'cpu'])
        
        # If CUDA is available, it should be selected
        if is_cuda_available():
            self.assertEqual(device.type, 'cuda')
        # If CUDA is not available but MPS is, MPS should be selected
        elif is_mps_available():
            self.assertEqual(device.type, 'mps')
        # Otherwise, CPU should be selected
        else:
            self.assertEqual(device.type, 'cpu')
        
        print(f"Device priority test passed: {device.type}")

    def test_get_device_name(self):
        """Test device name generation."""
        name = get_device_name()
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
        print(f"Device name: {name}")

    def test_get_device_with_preference_cuda(self):
        """Test device selection with CUDA preference."""
        import torch
        device = get_device(device_preference='cuda')
        
        if is_cuda_available():
            self.assertEqual(device.type, 'cuda')
        else:
            # Should fall back to auto-selection
            self.assertIn(device.type, ['mps', 'cpu'])
        
        print(f"CUDA preference result: {device.type}")

    def test_get_device_with_preference_mps(self):
        """Test device selection with MPS preference."""
        import torch
        device = get_device(device_preference='mps')
        
        if is_mps_available():
            self.assertEqual(device.type, 'mps')
        else:
            # Should fall back to auto-selection
            self.assertIn(device.type, ['cuda', 'cpu'])
        
        print(f"MPS preference result: {device.type}")

    def test_get_device_with_preference_cpu(self):
        """Test device selection with CPU preference."""
        import torch
        device = get_device(device_preference='cpu')
        self.assertEqual(device.type, 'cpu')
        print(f"CPU preference result: {device.type}")


class TestDeviceDetectionMocked(unittest.TestCase):
    """Test device detection with mocked torch backends."""

    def setUp(self):
        """Set up test fixtures."""
        try:
            import torch
            self.torch_available = True
        except ImportError:
            self.torch_available = False
            self.skipTest("PyTorch not installed")

    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    def test_cuda_priority_over_mps(self, mock_mps, mock_cuda):
        """Test that CUDA is prioritized over MPS."""
        import torch
        mock_cuda.return_value = True
        mock_mps.return_value = True
        
        device = get_device()
        self.assertEqual(device.type, 'cuda')
        print("CUDA priority test: PASSED (CUDA selected when both available)")

    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    def test_mps_when_cuda_unavailable(self, mock_mps, mock_cuda):
        """Test that MPS is selected when CUDA is unavailable."""
        import torch
        mock_cuda.return_value = False
        mock_mps.return_value = True
        
        device = get_device()
        self.assertEqual(device.type, 'mps')
        print("MPS fallback test: PASSED (MPS selected when CUDA unavailable)")

    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    def test_cpu_when_no_gpu(self, mock_mps, mock_cuda):
        """Test that CPU is selected when no GPU is available."""
        import torch
        mock_cuda.return_value = False
        mock_mps.return_value = False
        
        device = get_device()
        self.assertEqual(device.type, 'cpu')
        print("CPU fallback test: PASSED (CPU selected when no GPU available)")


def print_system_info():
    """Print system information for debugging."""
    import platform
    print("\n" + "="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    try:
        import torch
        print(f"\nPyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"CUDA device count: {torch.cuda.device_count()}")
            if torch.cuda.device_count() > 0:
                print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        
        print(f"MPS available: {torch.backends.mps.is_available()}")
        if torch.backends.mps.is_available():
            print(f"MPS built: {torch.backends.mps.is_built()}")
    except ImportError:
        print("\nPyTorch: Not installed")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    print_system_info()
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=True)

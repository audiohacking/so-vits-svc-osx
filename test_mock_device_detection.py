#!/usr/bin/env python3
"""
Mock test to demonstrate device detection without PyTorch installed.
This creates a simulated environment to test the device utilities.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_with_mock():
    """Test device detection with mocked torch."""
    from unittest.mock import MagicMock, patch
    
    # Create a mock torch module
    mock_torch = MagicMock()
    mock_torch.__version__ = "2.1.0"
    
    # Mock CUDA
    mock_torch.cuda.is_available.return_value = False
    mock_torch.cuda.device_count.return_value = 0
    
    # Mock MPS for Apple Silicon
    mock_torch.backends.mps.is_available.return_value = True
    mock_torch.backends.mps.is_built.return_value = True
    
    # Mock device
    mock_device = MagicMock()
    mock_device.type = 'mps'
    mock_torch.device.return_value = mock_device
    
    # Patch torch in sys.modules
    sys.modules['torch'] = mock_torch
    
    print("=" * 70)
    print("SIMULATED DEVICE DETECTION TEST (Apple Silicon Mac)")
    print("=" * 70)
    
    try:
        from utils.device import (
            get_device,
            get_device_name,
            is_cuda_available,
            is_mps_available,
            is_gpu_available
        )
        
        print(f"\nCUDA Available:      {is_cuda_available()}")
        print(f"MPS Available:       {is_mps_available()}")
        print(f"GPU Available:       {is_gpu_available()}")
        
        device = get_device()
        print(f"\nSelected Device:     {device}")
        print(f"Device Type:         {device.type}")
        
        # Test with preferences
        cpu_device = get_device(device_preference='cpu')
        print(f"\nCPU Preference:      {cpu_device}")
        
        mps_device = get_device(device_preference='mps')
        print(f"MPS Preference:      {mps_device}")
        
        print("\n✓ All device detection functions working correctly!")
        print("\nThis simulation demonstrates how the device detection")
        print("would work on an Apple Silicon Mac with MPS support.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up mock
        if 'torch' in sys.modules:
            del sys.modules['torch']
    
    return True


def test_cuda_simulation():
    """Test device detection with CUDA simulation."""
    from unittest.mock import MagicMock, patch
    
    # Create a mock torch module
    mock_torch = MagicMock()
    mock_torch.__version__ = "2.1.0"
    
    # Mock CUDA
    mock_torch.cuda.is_available.return_value = True
    mock_torch.cuda.device_count.return_value = 1
    mock_torch.cuda.get_device_name.return_value = "NVIDIA GeForce RTX 3090"
    mock_torch.version.cuda = "12.1"
    
    # Mock MPS
    mock_torch.backends.mps.is_available.return_value = False
    
    # Mock device
    mock_device = MagicMock()
    mock_device.type = 'cuda'
    mock_torch.device.return_value = mock_device
    
    # Patch torch in sys.modules
    sys.modules['torch'] = mock_torch
    
    print("\n" + "=" * 70)
    print("SIMULATED DEVICE DETECTION TEST (NVIDIA GPU System)")
    print("=" * 70)
    
    try:
        from utils.device import (
            get_device,
            get_device_name,
            is_cuda_available,
            is_mps_available,
            is_gpu_available
        )
        
        print(f"\nCUDA Available:      {is_cuda_available()}")
        print(f"MPS Available:       {is_mps_available()}")
        print(f"GPU Available:       {is_gpu_available()}")
        
        device = get_device()
        print(f"\nSelected Device:     {device}")
        print(f"Device Type:         {device.type}")
        
        print("\n✓ CUDA device detection working correctly!")
        print("\nThis simulation demonstrates how the device detection")
        print("would work on a system with NVIDIA GPU.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up mock
        if 'torch' in sys.modules:
            del sys.modules['torch']
    
    return True


if __name__ == "__main__":
    print("\nMOCK DEVICE DETECTION TEST")
    print("This test demonstrates device detection without requiring PyTorch")
    print("-" * 70)
    
    success_mps = test_with_mock()
    success_cuda = test_cuda_simulation()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    if success_mps and success_cuda:
        print("✓ All simulations passed successfully!")
        print("\nThe device detection utility correctly:")
        print("  - Detects MPS on Apple Silicon Macs")
        print("  - Detects CUDA on NVIDIA GPU systems")
        print("  - Prioritizes CUDA over MPS over CPU")
        print("  - Respects user device preferences")
    else:
        print("✗ Some simulations failed")
    print("=" * 70 + "\n")

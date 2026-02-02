#!/usr/bin/env python3
"""
Device Detection Verification Script

This script verifies that the device detection is working correctly
and displays information about the detected hardware.

Usage:
    python verify_device.py
"""

import sys
import os
import platform

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_section(title):
    """Print a section header."""
    print(f"\n{title}")
    print("-"*70)


def get_system_info():
    """Gather system information."""
    print_header("SYSTEM INFORMATION")
    
    print(f"Platform:        {platform.platform()}")
    print(f"System:          {platform.system()}")
    print(f"Release:         {platform.release()}")
    print(f"Machine:         {platform.machine()}")
    print(f"Processor:       {platform.processor()}")
    print(f"Python Version:  {platform.python_version()}")
    
    # Check for macOS specific information
    if platform.system() == "Darwin":
        try:
            import subprocess
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"CPU Brand:       {result.stdout.strip()}")
            
            # Check for Apple Silicon
            result = subprocess.run(['sysctl', '-n', 'hw.optional.arm64'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip() == '1':
                print(f"Apple Silicon:   Yes (M-series chip)")
            else:
                print(f"Apple Silicon:   No (Intel chip)")
        except Exception as e:
            print(f"Could not detect macOS details: {e}")


def check_pytorch():
    """Check PyTorch installation and device support."""
    print_header("PYTORCH CONFIGURATION")
    
    try:
        import torch
        print(f"PyTorch Version:     {torch.__version__}")
        print(f"PyTorch Path:        {torch.__file__}")
        
        print_section("Device Availability")
        
        # Check CUDA
        cuda_available = torch.cuda.is_available()
        print(f"CUDA Available:      {cuda_available}")
        if cuda_available:
            print(f"  - CUDA Version:    {torch.version.cuda}")
            print(f"  - Device Count:    {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  - Device {i}:        {torch.cuda.get_device_name(i)}")
        
        # Check MPS
        mps_available = torch.backends.mps.is_available()
        print(f"MPS Available:       {mps_available}")
        if mps_available:
            print(f"  - MPS Built:       {torch.backends.mps.is_built()}")
        
        return True
        
    except ImportError:
        print("PyTorch is NOT installed!")
        print("\nTo install PyTorch, visit: https://pytorch.org/get-started/locally/")
        print("\nFor Apple Silicon Macs, use:")
        print("  pip3 install torch torchvision torchaudio")
        return False


def check_device_utils():
    """Check the custom device utilities."""
    print_header("DEVICE DETECTION UTILITIES")
    
    try:
        from utils.device import (
            get_device, 
            get_device_name,
            is_cuda_available,
            is_mps_available,
            is_gpu_available
        )
        
        print(f"CUDA Available:      {is_cuda_available()}")
        print(f"MPS Available:       {is_mps_available()}")
        print(f"GPU Available:       {is_gpu_available()}")
        
        print_section("Selected Device")
        device = get_device()
        device_name = get_device_name(device)
        
        print(f"Selected Device:     {device}")
        print(f"Device Type:         {device.type}")
        print(f"Device Name:         {device_name}")
        
        # Test device preferences
        print_section("Device Preference Tests")
        
        cpu_device = get_device(device_preference='cpu')
        print(f"CPU Preference:      {cpu_device} ({cpu_device.type})")
        
        if is_cuda_available():
            cuda_device = get_device(device_preference='cuda')
            print(f"CUDA Preference:     {cuda_device} ({cuda_device.type})")
        
        if is_mps_available():
            mps_device = get_device(device_preference='mps')
            print(f"MPS Preference:      {mps_device} ({mps_device.type})")
        
        return True
        
    except ImportError as e:
        print(f"Error importing device utilities: {e}")
        print("\nMake sure you're running this script from the project root directory.")
        return False


def test_simple_tensor_operation():
    """Test a simple tensor operation on the detected device."""
    print_header("DEVICE FUNCTIONALITY TEST")
    
    try:
        import torch
        from utils.device import get_device, get_device_name
        
        device = get_device()
        print(f"Testing tensor operations on: {get_device_name(device)}")
        
        # Create a simple tensor and move it to the device
        print("\nCreating test tensor...")
        tensor = torch.randn(3, 3)
        print(f"CPU Tensor:\n{tensor}")
        
        print(f"\nMoving tensor to {device}...")
        tensor_device = tensor.to(device)
        print(f"Device Tensor location: {tensor_device.device}")
        
        print("\nPerforming matrix multiplication...")
        result = torch.mm(tensor_device, tensor_device)
        print(f"Result shape: {result.shape}")
        print(f"Result device: {result.device}")
        
        print("\n✓ Tensor operations successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during tensor operations: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print_header("SO-VITS-SVC DEVICE DETECTION VERIFICATION")
    print("This script verifies that device detection is working correctly.")
    
    # Get system information
    get_system_info()
    
    # Check PyTorch
    pytorch_ok = check_pytorch()
    
    if pytorch_ok:
        # Check device utilities
        utils_ok = check_device_utils()
        
        if utils_ok:
            # Test tensor operations
            test_simple_tensor_operation()
    
    # Final summary
    print_header("VERIFICATION SUMMARY")
    
    if pytorch_ok:
        from utils.device import is_cuda_available, is_mps_available, get_device_name
        
        if is_cuda_available():
            print("✓ CUDA GPU acceleration is available and working")
        elif is_mps_available():
            print("✓ Apple Silicon (MPS) GPU acceleration is available and working")
        else:
            print("⚠ No GPU acceleration available - will use CPU")
            print("  This is normal if you don't have a CUDA GPU or Apple Silicon Mac")
        
        device_name = get_device_name()
        print(f"\nYour system will use: {device_name}")
    else:
        print("✗ PyTorch is not installed - please install it to continue")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()

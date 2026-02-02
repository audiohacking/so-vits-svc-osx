"""
Device selection utility for supporting CUDA, MPS, and CPU devices.
"""
import torch


def get_device(device_preference=None):
    """
    Get the best available device based on preference and availability.
    
    Args:
        device_preference: Optional string specifying device preference ('cuda', 'mps', 'cpu').
                          If None, automatically selects the best available device.
    
    Returns:
        torch.device: The selected device.
    """
    if device_preference is not None:
        if device_preference == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")
        elif device_preference == "mps" and torch.backends.mps.is_available():
            return torch.device("mps")
        elif device_preference == "cpu":
            return torch.device("cpu")
        else:
            print(f"Warning: Requested device '{device_preference}' is not available. Falling back to auto-selection.")
    
    # Auto-select best available device
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def get_device_name(device=None):
    """
    Get a human-readable name for the device.
    
    Args:
        device: torch.device or None. If None, gets the default device.
    
    Returns:
        str: Name of the device.
    """
    if device is None:
        device = get_device()
    
    if device.type == "cuda":
        return f"CUDA ({torch.cuda.get_device_name(device)})"
    elif device.type == "mps":
        return "MPS (Apple Silicon)"
    else:
        return "CPU"


def is_cuda_available():
    """Check if CUDA is available."""
    return torch.cuda.is_available()


def is_mps_available():
    """Check if MPS is available."""
    return torch.backends.mps.is_available()


def is_gpu_available():
    """Check if any GPU (CUDA or MPS) is available."""
    return torch.cuda.is_available() or torch.backends.mps.is_available()

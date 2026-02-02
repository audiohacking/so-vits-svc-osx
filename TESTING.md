# Testing and Verification Guide

This document provides comprehensive information about testing device detection and MPS support in so-vits-svc.

## Quick Start

### 1. Verify Your Device

Run the device verification script to check what hardware acceleration is available:

```bash
python verify_device.py
```

**Expected Output on Apple Silicon Mac:**
```
======================================================================
  SO-VITS-SVC DEVICE DETECTION VERIFICATION
======================================================================

======================================================================
  SYSTEM INFORMATION
======================================================================
Platform:        macOS-14.0-arm64
Machine:         arm64
Apple Silicon:   Yes (M-series chip)
Python Version:  3.11.x

======================================================================
  PYTORCH CONFIGURATION
======================================================================
PyTorch Version:     2.1.0+
MPS Available:       True
  - MPS Built:       True

======================================================================
  DEVICE DETECTION UTILITIES
======================================================================
CUDA Available:      False
MPS Available:       True
GPU Available:       True

Selected Device:     mps
Device Type:         mps
Device Name:         MPS (Apple Silicon)

======================================================================
  DEVICE FUNCTIONALITY TEST
======================================================================
Testing tensor operations on: MPS (Apple Silicon)
✓ Tensor operations successful!

======================================================================
  VERIFICATION SUMMARY
======================================================================
✓ Apple Silicon (MPS) GPU acceleration is available and working

Your system will use: MPS (Apple Silicon)
```

### 2. Run Tests

Run the comprehensive test suite:

```bash
# With PyTorch installed
python tests/test_device_detection.py

# Without PyTorch (mock test)
python test_mock_device_detection.py
```

## Test Coverage

### Device Detection Tests (`tests/test_device_detection.py`)

Tests the following functionality:

#### Basic Detection
- ✅ `test_is_cuda_available()` - Verifies CUDA detection works
- ✅ `test_is_mps_available()` - Verifies MPS detection works
- ✅ `test_is_gpu_available()` - Verifies GPU detection (CUDA or MPS)

#### Device Selection
- ✅ `test_get_device_returns_torch_device()` - Returns proper torch.device object
- ✅ `test_get_device_priority()` - Validates priority: CUDA > MPS > CPU
- ✅ `test_get_device_name()` - Returns human-readable device name

#### Device Preferences
- ✅ `test_get_device_with_preference_cuda()` - Respects CUDA preference
- ✅ `test_get_device_with_preference_mps()` - Respects MPS preference
- ✅ `test_get_device_with_preference_cpu()` - Respects CPU preference

#### Mock Tests (Simulated Environments)
- ✅ `test_cuda_priority_over_mps()` - CUDA selected when both available
- ✅ `test_mps_when_cuda_unavailable()` - MPS selected when CUDA unavailable
- ✅ `test_cpu_when_no_gpu()` - CPU selected when no GPU available

## Continuous Integration

Tests automatically run on GitHub Actions for multiple platforms:

### Test Matrix

| Platform | Hardware | PyTorch | Status |
|----------|----------|---------|--------|
| macOS-14 | Apple Silicon (M1) | Full | ✅ Tests MPS support |
| Ubuntu | CPU | CPU-only | ✅ Tests CPU fallback |
| Ubuntu | N/A | Mock (no PyTorch) | ✅ Tests logic |

### Running CI Tests Locally

You can simulate CI tests locally:

```bash
# Simulate macOS test
python3 verify_device.py

# Simulate Linux CPU test
CUDA_VISIBLE_DEVICES="" python3 verify_device.py

# Simulate mock test
python3 test_mock_device_detection.py
```

## Platform-Specific Testing

### Testing on Apple Silicon (M1/M2/M3)

1. **Verify macOS version** (requires 12.3+):
   ```bash
   sw_vers
   ```

2. **Verify PyTorch MPS support**:
   ```bash
   python3 -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
   ```

3. **Run full verification**:
   ```bash
   python3 verify_device.py
   ```

4. **Test inference** (if models are available):
   ```bash
   python svc_inference.py --config configs/base.yaml --model ./vits_pretrain/sovits5.0.pretrain.pth --spk ./configs/singers/singer0001.npy --wave test.wav
   ```
   You should see: `Using device: MPS (Apple Silicon)`

### Testing on NVIDIA GPU Systems

1. **Verify CUDA**:
   ```bash
   python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
   ```

2. **Run verification**:
   ```bash
   python3 verify_device.py
   ```
   You should see: `Using device: CUDA (NVIDIA ...)`

### Testing on CPU-Only Systems

1. **Run verification**:
   ```bash
   python3 verify_device.py
   ```
   You should see: `Using device: CPU`

## Troubleshooting Test Issues

### PyTorch Not Installed

**Symptom**: 
```
PyTorch is NOT installed!
```

**Solution**:
```bash
# For Apple Silicon
pip3 install torch torchvision torchaudio

# For CUDA (Linux/Windows)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CPU only
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### MPS Not Detected on Mac

**Symptom**:
```
MPS Available:       False
```

**Possible Causes**:
1. macOS version < 12.3
2. PyTorch version < 1.12
3. Intel Mac (not Apple Silicon)

**Solution**:
1. Check macOS version: `sw_vers`
2. Update PyTorch: `pip3 install --upgrade torch`
3. Verify chip: `sysctl -n machdep.cpu.brand_string`

### Tests Fail with Import Error

**Symptom**:
```
ModuleNotFoundError: No module named 'utils.device'
```

**Solution**:
Run tests from the project root directory:
```bash
cd /path/to/so-vits-svc-5.8
python tests/test_device_detection.py
```

## Performance Benchmarking

To benchmark device performance:

```python
import torch
import time
from utils.device import get_device

device = get_device()
print(f"Testing on: {device}")

# Create large tensor
size = 1000
a = torch.randn(size, size).to(device)
b = torch.randn(size, size).to(device)

# Warm up
for _ in range(10):
    c = torch.mm(a, b)

# Benchmark
start = time.time()
for _ in range(100):
    c = torch.mm(a, b)
end = time.time()

print(f"Time: {(end - start):.4f}s for 100 iterations")
print(f"Average: {(end - start) / 100 * 1000:.2f}ms per iteration")
```

**Expected Performance**:
- **MPS (M1)**: ~5-10ms per iteration
- **CUDA (RTX 3090)**: ~2-5ms per iteration
- **CPU (Intel i9)**: ~50-100ms per iteration

## Test Results Archive

Test results are automatically collected in CI runs. To view:

1. Go to GitHub Actions tab
2. Select "Test Device Detection" workflow
3. View logs for each platform

## Contributing Tests

When adding new device-related features:

1. Add tests to `tests/test_device_detection.py`
2. Update mock test in `test_mock_device_detection.py`
3. Update this documentation
4. Ensure CI passes on all platforms

## Related Documentation

- [README.md](README.md) - Main project documentation
- [README_ZH.md](README_ZH.md) - Chinese documentation
- [tests/README.md](tests/README.md) - Test suite documentation
- [utils/device.py](utils/device.py) - Device detection implementation

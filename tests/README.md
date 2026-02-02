# Device Detection Tests

This directory contains tests for verifying that device detection (CUDA, MPS, CPU) works correctly across different hardware configurations.

## Running Tests

### With PyTorch Installed

If you have PyTorch installed, you can run the full test suite:

```bash
# Run with unittest
python tests/test_device_detection.py

# Run with pytest (if installed)
pytest tests/test_device_detection.py -v
```

### Without PyTorch

If PyTorch is not installed, you can still verify the device detection logic works using the mock test:

```bash
python test_mock_device_detection.py
```

This will simulate device detection for:
- Apple Silicon Macs (MPS)
- NVIDIA GPU systems (CUDA)
- CPU-only systems

## Test Coverage

The test suite covers:

1. **Basic Device Detection**
   - CUDA availability detection
   - MPS availability detection
   - GPU (CUDA or MPS) availability detection
   - Device priority (CUDA > MPS > CPU)

2. **Device Selection**
   - Automatic device selection
   - Device preference handling
   - Fallback behavior

3. **Mock Tests**
   - Simulated CUDA environments
   - Simulated MPS environments
   - Simulated CPU-only environments

## Continuous Integration

The tests are automatically run on GitHub Actions for:
- macOS with Apple Silicon (M1/M2/M3)
- Linux with CPU
- Mock tests without PyTorch

See `.github/workflows/test-device-detection.yml` for CI configuration.

## Test Output Examples

### On Apple Silicon Mac:
```
Selected Device:     mps
Device Type:         mps
Device Name:         MPS (Apple Silicon)
✓ Apple Silicon (MPS) GPU acceleration is available and working
```

### On NVIDIA GPU System:
```
Selected Device:     cuda:0
Device Type:         cuda
Device Name:         CUDA (NVIDIA GeForce RTX 3090)
✓ CUDA GPU acceleration is available and working
```

### On CPU-only System:
```
Selected Device:     cpu
Device Type:         cpu
Device Name:         CPU
⚠ No GPU acceleration available - will use CPU
```

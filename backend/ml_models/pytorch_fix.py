"""
PyTorch 2.6 compatibility fix for ultralytics
"""
import torch
from typing import Optional

_ORIGINAL_TORCH_LOAD: Optional[callable] = None


def apply_pytorch_fix():
    """Apply compatibility fixes for PyTorch 2.6"""
    global _ORIGINAL_TORCH_LOAD

    try:
        # Import ultralytics classes dynamically - only import what exists
        from ultralytics.nn.tasks import DetectionModel
        from ultralytics.nn.modules.block import C2f, Bottleneck, SPPF, DWConv
        from ultralytics.nn.modules.conv import Conv
        from ultralytics.nn.modules.head import Detect
        from ultralytics.nn.modules.transformer import TransformerEncoderLayer
        from torch.nn.modules.container import Sequential

        # Add safe globals for ultralytics classes
        safe_classes = [
            DetectionModel,
            C2f,
            Bottleneck,
            SPPF,
            Conv,
            Detect,
            DWConv,
            TransformerEncoderLayer,
            Sequential,
        ]

        torch.serialization.add_safe_globals(safe_classes)
        print("  ✓ Added ultralytics classes to safe globals")

    except ImportError as e:
        print(f"  ⚠ Could not import ultralytics classes: {e}")
    except Exception as e:
        print(f"  ⚠ Failed to add safe globals: {e}")

    # Always add string-based safe globals as fallback
    try:
        torch.serialization.add_safe_globals([
            'ultralytics.nn.tasks.DetectionModel',
            'ultralytics.nn.modules.block.C2f',
            'ultralytics.nn.modules.block.Bottleneck',
            'ultralytics.nn.modules.block.SPPF',
            'ultralytics.nn.modules.conv.Conv',
            'ultralytics.nn.modules.head.Detect',
            'ultralytics.nn.modules.block.DWConv',
            'ultralytics.nn.modules.transformer.TransformerEncoderLayer',
            'torch.nn.modules.container.Sequential',
        ])
    except Exception:
        pass

    # Patch torch.load once to force weights_only=False by default
    if _ORIGINAL_TORCH_LOAD is None:
        _ORIGINAL_TORCH_LOAD = torch.load

        def patched_torch_load(*args, **kwargs):
            kwargs.setdefault("weights_only", False)
            return _ORIGINAL_TORCH_LOAD(*args, **kwargs)

        torch.load = patched_torch_load
        print("  ✓ Patched torch.load to allow trusted checkpoints")


def safe_load_context():
    """Context manager for safe loading of ultralytics models"""
    return torch.serialization.safe_globals([
        'ultralytics.nn.tasks.DetectionModel',
        'ultralytics.nn.modules.block.C2f',
        'ultralytics.nn.modules.block.Bottleneck',
        'ultralytics.nn.modules.block.SPPF',
        'ultralytics.nn.modules.conv.Conv',
        'ultralytics.nn.modules.head.Detect',
        'ultralytics.nn.modules.block.DWConv',
        'ultralytics.nn.modules.transformer.TransformerEncoderLayer',
        'torch.nn.modules.container.Sequential',
    ])


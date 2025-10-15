"""
PyTorch 2.6 compatibility fix for ultralytics
"""
import torch

def apply_pytorch_fix():
    """Apply compatibility fixes for PyTorch 2.6"""
    # Add safe globals for ultralytics classes
    safe_globals = [
        'ultralytics.nn.tasks.DetectionModel',
        'ultralytics.nn.modules.block.C2f',
        'ultralytics.nn.modules.block.Bottleneck', 
        'ultralytics.nn.modules.block.SPPF',
        'ultralytics.nn.modules.conv.Conv',
        'ultralytics.nn.modules.head.Detect',
        'ultralytics.nn.modules.block.DWConv',
        'ultralytics.nn.modules.transformer.TransformerEncoderLayer',
        'ultralytics.nn.modules.transformer.TransformerDecoderLayer'
    ]
    
    for global_name in safe_globals:
        try:
            torch.serialization.add_safe_globals([global_name])
        except:
            pass  # Ignore if already added


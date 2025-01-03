import os
import torch
from torch import autocast, nn
from typing import Union, Tuple, List
from torch import distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from typing import Tuple, Union, List


from dynamic_network_architectures.architectures.unet import ResidualEncoderUNet, PlainConvUNet
from nnunetv2.training.nnUNetTrainer.variants.network_architecture.NexToU import NexToU
from dynamic_network_architectures.building_blocks.helper import convert_dim_to_conv_op, get_matching_batchnorm
from dynamic_network_architectures.initialization.weight_init import init_last_bn_before_add_to_0, InitWeights_He
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from nnunetv2.utilities.plans_handling.plans_handler import ConfigurationManager, PlansManager
from nnunetv2.utilities.get_network_from_plans import get_network_from_plans
from nnunetv2.utilities.label_handling.label_handling import convert_labelmap_to_one_hot, determine_num_input_channels

class nnUNetTrainer_NexToU(nnUNetTrainer):
    def build_network_architecture(self, architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        dim = len(self.configuration_manager.conv_kernel_sizes[0])
        conv_op = convert_dim_to_conv_op(dim)

        label_manager = self.plans_manager.get_label_manager(self.dataset_json)

        segmentation_network_class_name = 'NexToU' #configuration_manager.UNet_class_name
        mapping = {
            'PlainConvUNet': PlainConvUNet,
            'ResidualEncoderUNet': ResidualEncoderUNet,
            'NexToU': NexToU
        }
        kwargs = {
            'PlainConvUNet': {
                'conv_bias': True,
                'norm_op': get_matching_batchnorm(conv_op),
                'norm_op_kwargs': {'eps': 1e-5, 'affine': True},
                'dropout_op': None, 'dropout_op_kwargs': None,
                'nonlin': nn.LeakyReLU, 'nonlin_kwargs': {'inplace': True},
            },
            'ResidualEncoderUNet': {
                'conv_bias': True,
                'norm_op': get_matching_batchnorm(conv_op),
                'norm_op_kwargs': {'eps': 1e-5, 'affine': True},
                'dropout_op': None, 'dropout_op_kwargs': None,
                'nonlin': nn.LeakyReLU, 'nonlin_kwargs': {'inplace': True},
            },
            'NexToU': {
                'conv_bias': True,
                'norm_op': get_matching_batchnorm(conv_op),
                'norm_op_kwargs': {'eps': 1e-5, 'affine': True},
                'dropout_op': None, 'dropout_op_kwargs': None,
                'nonlin': nn.LeakyReLU, 'nonlin_kwargs': {'inplace': True},
            }
        }
        assert segmentation_network_class_name in mapping.keys(), 'The network architecture specified by the plans file ' \
                                                                  'is non-standard (maybe your own?). Yo\'ll have to dive ' \
                                                                  'into either this ' \
                                                                  'function (get_network_from_plans) or ' \
                                                                  'the init of your nnUNetModule to accomodate that.'
        network_class = mapping[segmentation_network_class_name]

        conv_or_blocks_per_stage = {
            # encoder is stored as "n_blocks_per_stage" in the JSON
            'n_blocks_per_stage': self.configuration_manager.n_blocks_per_stage,
            # decoder is stored as "n_blocks_per_stage_decoder" in the JSON
            'n_blocks_per_stage_decoder': self.configuration_manager.n_conv_per_stage_decoder
        }

        # network class name!!
        model = network_class(
            input_channels=num_input_channels,
            patch_size=self.configuration_manager.patch_size,
            n_stages=self.configuration_manager.n_stages,
            features_per_stage=[min(self.configuration_manager.UNet_base_num_features * 2 ** i,
                                    self.configuration_manager.unet_max_num_features) for i in range(self.configuration_manager.n_stages)],
            conv_op=conv_op,
            kernel_sizes=self.configuration_manager.conv_kernel_sizes,
            strides=self.configuration_manager.pool_op_kernel_sizes,
            num_classes=label_manager.num_segmentation_heads,
            deep_supervision=enable_deep_supervision,
            **conv_or_blocks_per_stage,
            **kwargs[segmentation_network_class_name]
        )
        model.apply(InitWeights_He(1e-2))
        if network_class == ResidualEncoderUNet:
            model.apply(init_last_bn_before_add_to_0)
        return model

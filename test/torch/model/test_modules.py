# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import pytest
import torch

from gluonts.torch.model.deepar import DeepARModel
from gluonts.torch.model.mqf2 import MQF2MultiHorizonModel
from gluonts.torch.model.simple_feedforward import SimpleFeedForwardModel


def construct_batch(module, batch_size=1):
    return tuple(
        [
            torch.zeros(shape, dtype=module.input_types()[name])
            for (name, shape) in module.input_shapes(
                batch_size=batch_size
            ).items()
        ]
    )


def assert_shapes_and_dtypes(tensors, shapes, dtypes):
    if isinstance(tensors, torch.Tensor):
        assert tensors.shape == shapes
        assert tensors.dtype == dtypes
    else:
        for tensor, shape, dtype in zip(tensors, shapes, dtypes):
            assert_shapes_and_dtypes(tensor, shape, dtype)


@pytest.mark.parametrize(
    "module, batch_size, expected_shapes, expected_dtypes",
    [
        (
            DeepARModel(
                freq="1H",
                context_length=24,
                prediction_length=12,
                num_feat_dynamic_real=1,
                num_feat_static_real=1,
                num_feat_static_cat=1,
                cardinality=[1],
            ),
            4,
            (4, 100, 12),
            torch.float,
        ),
        (
            MQF2MultiHorizonModel(
                freq="1H",
                context_length=24,
                prediction_length=12,
                num_feat_dynamic_real=1,
                num_feat_static_real=1,
                num_feat_static_cat=1,
                cardinality=[1],
            ),
            4,
            (4, 100, 12),
            torch.float,
        ),
        (
            SimpleFeedForwardModel(
                context_length=24,
                prediction_length=12,
            ),
            4,
            [[(4, 12), (4, 12), (4, 12)], (4, 1), (4, 1)],
            [
                [torch.float, torch.float, torch.float],
                torch.float,
                torch.float,
            ],
        ),
    ],
)
def test_module_smoke(module, batch_size, expected_shapes, expected_dtypes):
    batch = construct_batch(module, batch_size=batch_size)
    outputs = module(*batch)
    assert_shapes_and_dtypes(outputs, expected_shapes, expected_dtypes)

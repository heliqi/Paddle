#   Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import unittest

import numpy as np

sys.path.append("..")
from op_test_xpu import XPUOpTest
from xpu.get_test_cover_info import (
    XPUOpTestWrapper,
    create_test_class,
    get_xpu_op_support_types,
)

import paddle

paddle.enable_static()


def numpy_topk(x, k=1, axis=-1, largest=True):
    if axis < 0:
        axis = len(x.shape) + axis
    if largest:
        indices = np.argsort(-x, axis=axis)
    else:
        indices = np.argsort(x, axis=axis)
    if largest:
        value = -np.sort(-x, axis=axis)
    else:
        value = np.sort(x, axis=axis)
    indices = indices.take(indices=range(0, k), axis=axis)
    value = value.take(indices=range(0, k), axis=axis)
    return value, indices


class XPUTestTopKV2Op(XPUOpTestWrapper):
    def __init__(self):
        self.op_name = 'top_k_v2'
        self.use_dynamic_create_class = False

    class TestTopkOp(XPUOpTest):
        def init_args(self):
            self.k = 3
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 20).astype(self.dtype)

        def setUp(self):
            self.op_type = "top_k_v2"
            self.init_args()
            self.dtype = self.in_type
            self.inputs = {'X': self.input_data}
            self.attrs = {
                'k': self.k,
                'axis': self.axis,
                'largest': self.largest,
            }
            output, indices = numpy_topk(
                self.input_data, axis=self.axis, k=self.k, largest=self.largest
            )
            self.outputs = {'Out': output, 'Indices': indices}

        def test_check_output(self):
            if paddle.is_compiled_with_xpu():
                place = paddle.XPUPlace(0)
                self.check_output_with_place(place)

        def test_check_grad(self):
            if paddle.is_compiled_with_xpu():
                place = paddle.XPUPlace(0)
                self.check_grad(set(['X']), 'Out')

    class TestTopkOp1(TestTopkOp):
        def init_args(self):
            self.k = 3
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(100, 155).astype(self.dtype)

    class TestTopkOp2(TestTopkOp):
        def init_args(self):
            self.k = 3
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)

    class TestTopkOp3(TestTopkOp):
        def init_args(self):
            self.k = 5
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)

    class TestTopkOp4(TestTopkOp):
        def init_args(self):
            self.k = 1
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)

    class TestTopkOp5(TestTopkOp):
        def init_args(self):
            self.k = 3
            self.axis = 2
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)

    class TestTopkOp6(TestTopkOp):
        def init_args(self):
            self.k = 5
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(8, 32, 64).astype(self.dtype)

    class TestTopkOp7(TestTopkOp):
        def init_args(self):
            self.k = 10
            self.axis = 2
            self.largest = True
            self.input_data = np.random.rand(8, 5, 10, 16).astype(self.dtype)

    class TestTopkOp8(TestTopkOp):
        def init_args(self):
            self.k = 1
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(8, 32, 64).astype(self.dtype)

    class TestTopkOp9(TestTopkOp):
        def init_args(self):
            self.k = 3
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)

    class TestTopkOp10(TestTopkOp):
        def init_args(self):
            self.k = 3
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)

    class TestTopkOp11(TestTopkOp):
        def init_args(self):
            self.k = 5
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)

    class TestTopkOp12(TestTopkOp):
        def init_args(self):
            self.k = 1
            self.axis = 1
            self.largest = True
            self.input_data = np.random.rand(10, 10, 5).astype(self.dtype)


support_types = get_xpu_op_support_types('top_k_v2')
for stype in support_types:
    create_test_class(globals(), XPUTestTopKV2Op, stype)

if __name__ == "__main__":
    unittest.main()

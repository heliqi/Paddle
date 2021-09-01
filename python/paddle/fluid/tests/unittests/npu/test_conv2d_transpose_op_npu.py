#   Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
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
from __future__ import print_function

import unittest
import numpy as np
import sys
sys.path.append("..")
import paddle
import paddle.nn as nn
import paddle.fluid.core as core
import paddle.fluid as fluid
from op_test import OpTest, skip_check_grad_ci

from test_conv2d_transpose_op import conv2dtranspose_forward_naive

paddle.enable_static()


@skip_check_grad_ci(
    reason='''Inference only, it doesn't need to call check_grad.''')
class TestConv2DTransposeOp(OpTest):
    def set_npu(self):
        self.__class__.use_npu = True
        self.place = paddle.NPUPlace(0)

    def init_dtype(self):
        self.dtype = np.float16

    def init_data_format(self):
        self.data_format = "NCHW"

    def setUp(self):
        self.init_op_type()
        self.init_dtype()
        self.set_npu()
        self.init_data_format()
        self.output_padding = []
        self.pad = [0, 0]
        self.padding_algorithm = "EXPLICIT"
        self.init_test_case()
        self.output_size = None

        input_ = np.random.random(self.input_size).astype(self.dtype)
        filter_ = np.random.random(self.filter_size).astype(self.dtype)

        self.inputs = {'Input': input_, 'Filter': filter_}
        self.attrs = {
            'strides': self.stride,
            'paddings': self.pad,
            'padding_algorithm': self.padding_algorithm,
            'groups': self.groups,
            'dilations': self.dilations,
            'use_cudnn': False,
            'is_test': False,
            'use_mkldnn': False,
            'data_format': self.data_format
        }
        if self.output_size is not None:
            self.attrs['output_size'] = self.output_size

        if len(self.output_padding) > 0:
            self.attrs['output_padding'] = self.output_padding

        output = conv2dtranspose_forward_naive(input_, filter_,
                                               self.attrs).astype(self.dtype)

        self.outputs = {'Output': output}

    def test_check_output(self):
        self.check_output_with_place(self.place, atol=1e-2)

    def init_test_case(self):
        self.pad = [0, 0]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]

    def init_op_type(self):
        self.op_type = "conv2d_transpose"


class TestWithSymmetricPad_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithSymmetricPad(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]


class TestWithAsymmetricPad_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 0, 1, 2]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithAsymmetricPad(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 0, 1, 2]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]


class TestWithSAMEPad_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.stride = [2, 1]
        self.dilations = [1, 2]
        self.groups = 1
        self.input_size = [2, 3, 6, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 4, 3]
        self.padding_algorithm = 'SAME'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithSAMEPad(TestConv2DTransposeOp):
    def init_test_case(self):
        self.stride = [2, 1]
        self.dilations = [1, 2]
        self.groups = 1
        self.input_size = [2, 3, 6, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 4, 3]
        self.padding_algorithm = 'SAME'


class TestWithVALIDPad_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]
        self.padding_algorithm = 'VALID'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithVALIDPad(TestConv2DTransposeOp):
    def init_test_case(self):
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]
        self.padding_algorithm = 'VALID'


class TestWithGroups_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 2
        self.input_size = [2, 4, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 3, 3, 3]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithGroups(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 2
        self.input_size = [2, 4, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 3, 3, 3]


class TestWithStride_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [2, 2]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithStride(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [2, 2]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]


class TestWithDilation_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.groups = 1
        self.dilations = [2, 2]
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithDilation(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.groups = 1
        self.dilations = [2, 2]
        self.input_size = [2, 3, 5, 5]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 3, 3]


class TestWithEvenUpsample_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_size = [14, 14]
        self.input_size = [2, 3, 7, 7]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 5, 5]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithEvenUpsample(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_size = [14, 14]
        self.input_size = [2, 3, 7, 7]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 5, 5]


class TestWithEvenUpsampleOutputPadding_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_padding = [1, 1]
        self.input_size = [2, 3, 7, 7]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 5, 5]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithEvenUpsampleOutputPadding(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_padding = [1, 1]
        self.input_size = [2, 3, 7, 7]  # NCHW
        f_c = self.input_size[1]
        self.filter_size = [f_c, 6, 5, 5]


class Test_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [0, 0]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class Test_NHWC(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [0, 0]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'


class TestWithSymmetricPad_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithSymmetricPad_NHWC(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'


class TestWithAsymmetricPad_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 0, 1, 2]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithAsymmetricPad_NHWC(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 0, 1, 2]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'


class TestWithGroups_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 2
        self.input_size = [2, 5, 5, 4]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 3, 3, 3]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithGroups_NHWC(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.dilations = [1, 1]
        self.groups = 2
        self.input_size = [2, 5, 5, 4]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 3, 3, 3]
        self.data_format = 'NHWC'


class TestWithStride_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [2, 2]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NCHW
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithStride_NHWC(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [2, 2]
        self.dilations = [1, 1]
        self.groups = 1
        self.input_size = [2, 5, 5, 3]  # NCHW
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'


class TestWithDilation_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.groups = 1
        self.dilations = [2, 2]
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithDilation_NHWC(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [1, 1]
        self.stride = [1, 1]
        self.groups = 1
        self.dilations = [2, 2]
        self.input_size = [2, 5, 5, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 3, 3]
        self.data_format = 'NHWC'


class TestWithEvenUpsample_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_size = [14, 14]
        self.input_size = [2, 7, 7, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 5, 5]

    def init_dtype(self):
        self.dtype = np.float32


class TestWithEvenUpsample_NHWC_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_size = [14, 14]
        self.input_size = [2, 7, 7, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 5, 5]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithEvenUpsample_NHWC(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_size = [14, 14]
        self.input_size = [2, 7, 7, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 5, 5]
        self.data_format = 'NHWC'


class TestWithEvenUpsample_NHWC_output_padding_FP32(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_padding = [1, 1]
        self.input_size = [2, 7, 7, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 5, 5]
        self.data_format = 'NHWC'

    def init_dtype(self):
        self.dtype = np.float32


class TestWithEvenUpsample_NHWC_output_padding(TestConv2DTransposeOp):
    def init_test_case(self):
        self.pad = [2, 2]
        self.stride = [2, 2]
        self.groups = 1
        self.dilations = [1, 1]
        self.output_padding = [1, 1]
        self.input_size = [2, 7, 7, 3]  # NHWC
        f_c = self.input_size[-1]
        self.filter_size = [f_c, 6, 5, 5]
        self.data_format = 'NHWC'


class TestConv2DTransposeAPI(unittest.TestCase):
    def test_case1(self):
        data1 = fluid.layers.data(
            name='data1', shape=[3, 5, 5], dtype='float32')
        data2 = fluid.layers.data(
            name='data2', shape=[5, 5, 3], dtype='float32')
        out1 = fluid.layers.conv2d_transpose(
            input=data1,
            groups=1,
            num_filters=6,
            filter_size=3,
            data_format='NCHW')
        out2 = fluid.layers.conv2d_transpose(
            input=data2,
            groups=1,
            num_filters=6,
            filter_size=3,
            data_format='NHWC')
        out3 = fluid.layers.conv2d_transpose(
            input=data1,
            groups=1,
            num_filters=6,
            filter_size=3,
            padding=[[0, 0], [1, 1], [1, 1], [0, 0]],
            data_format='NHWC')
        out4 = fluid.layers.conv2d_transpose(
            input=data1,
            groups=3,
            num_filters=6,
            filter_size=3,
            padding=[[0, 0], [0, 0], [2, 1], [0, 0]],
            data_format='NCHW')
        out5 = fluid.layers.conv2d_transpose(
            input=data2,
            groups=1,
            num_filters=6,
            filter_size=3,
            padding='SAME',
            data_format='NCHW')
        out6 = fluid.layers.conv2d_transpose(
            input=data1,
            groups=1,
            num_filters=6,
            filter_size=3,
            padding='VALID',
            data_format='NHWC')
        out7 = fluid.layers.conv2d_transpose(
            input=data1,
            groups=1,
            num_filters=6,
            output_size=[7, 7],
            padding=[0, 0],
            data_format='NHWC')

        data1_np = np.random.random((2, 3, 5, 5)).astype("float32")
        data2_np = np.random.random((2, 5, 5, 3)).astype("float32")

        place = core.NPUPlace(0)
        exe = fluid.Executor(place)
        exe.run(fluid.default_startup_program())
        results = exe.run(
            fluid.default_main_program(),
            feed={"data1": data1_np,
                  "data2": data2_np},
            fetch_list=[out1, out2, out3, out4, out5, out6, out7],
            return_numpy=True)
        self.assertIsNotNone(results[0])
        self.assertIsNotNone(results[1])
        self.assertIsNotNone(results[2])
        self.assertIsNotNone(results[3])
        self.assertIsNotNone(results[4])
        self.assertIsNotNone(results[5])
        self.assertIsNotNone(results[6])


class TestConv2DTransposeOpException(unittest.TestCase):
    def test_exception(self):
        data = fluid.layers.data(name='data', shape=[3, 5, 5], dtype="float32")

        def attr_data_format():
            out = fluid.layers.conv2d_transpose(
                input=data,
                groups=1,
                num_filters=6,
                filter_size=3,
                data_format="NCDHW")

        self.assertRaises(ValueError, attr_data_format)

        def attr_padding_str():
            out = fluid.layers.conv2d_transpose(
                input=data,
                groups=1,
                num_filters=6,
                filter_size=3,
                padding='Vald')

        self.assertRaises(ValueError, attr_padding_str)

        def attr_padding_list():
            out = fluid.layers.conv2d_transpose(
                input=data,
                groups=1,
                num_filters=6,
                filter_size=3,
                padding=[[1, 1], [1, 1], [0, 0], [0, 0]])

        self.assertRaises(ValueError, attr_padding_list)

        def attr_padding_with_data_format():
            out = fluid.layers.conv2d_transpose(
                input=data,
                groups=1,
                num_filters=6,
                filter_size=3,
                padding=[[1, 1], [0, 0], [0, 0], [1, 1]],
                data_format='NHWC')

        self.assertRaises(ValueError, attr_padding_with_data_format)

        error_input = fluid.layers.data(
            name='error_data', shape=[1], dtype="float32")

        def error_input_size():
            out = fluid.layers.conv2d_transpose(
                input=error_input, groups=1, num_filters=6, filter_size=3)

        self.assertRaises(ValueError, error_input_size)

        def error_groups():
            out = fluid.layers.conv2d_transpose(
                input=data,
                groups=0,
                num_filters=6,
                filter_size=3,
                data_format='NHWC')

        self.assertRaises(ValueError, error_groups)


class TestConv2DTransposeRepr(unittest.TestCase):
    def test_case(self):
        paddle.disable_static()
        x_var = paddle.uniform((2, 4, 8, 8), dtype='float32', min=-1., max=1.)
        conv = nn.Conv2DTranspose(4, 6, (3, 3), output_padding=1, stride=2)
        print(conv)
        y_var = conv(x_var)
        y_np = y_var.numpy()
        self.assertIsNotNone(y_np)
        paddle.enable_static()


if __name__ == '__main__':
    unittest.main()

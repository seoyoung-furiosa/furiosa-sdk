"""Model and its methods to access model metadata"""
from abc import ABC, abstractmethod
from ctypes import c_void_p
from typing import List

from ._api import LIBNUX, convert_to_cchar_array
from .tensor import TensorDesc, TensorArray
from ._util import list_to_dict


class Model(ABC):
    """NPU model binary compiled by Renegade compiler"""

    @abstractmethod
    def _get_model_ref(self) -> c_void_p:
        """
        Returns a raw model pointer

        :return: a raw pointer of a Model
        """

    @property
    def input_num(self) -> int:
        """Number of input tensors of Model"""
        return LIBNUX.nux_input_num(self._get_model_ref())

    @property
    def output_num(self) -> int:
        """Number of output tensors of Model"""
        return LIBNUX.nux_output_num(self._get_model_ref())

    def _input(self, idx) -> TensorDesc:
        return TensorDesc(LIBNUX.nux_input_desc(self._get_model_ref(), idx))

    def input(self, idx) -> TensorDesc:
        """Return tensor description of i-th input tensor of Model"""
        if idx < 0 or self.input_num <= idx:
            raise IndexError('list index out of input tensors')

        return self._input(idx)

    def inputs(self) -> [TensorDesc]:
        """Tensor descriptions of all input tensors of Model"""
        return [self._input(idx) for idx in range(self.input_num)]

    def _output(self, idx) -> TensorDesc:
        return TensorDesc(LIBNUX.nux_output_desc(self._get_model_ref(), idx))

    def output(self, idx) -> TensorDesc:
        """Returns tensor description of i-th output tensor of Model"""
        if idx < 0 or self.output_num <= idx:
            raise IndexError('list index out of output tensors')

        return self._output(idx)

    def outputs(self) -> [TensorDesc]:
        """Tensor descriptions of all output tensors of Model"""
        return [self._output(idx) for idx in range(self.output_num)]

    def allocate_tensors(self, names: List[str]) -> TensorArray:
        """Creates an array of tensors corresponding to tensor names with allocated buffers"""
        ptrs = convert_to_cchar_array(names)
        return TensorArray(LIBNUX.nux_tensor_array_allocate_by_names(self._get_model_ref(), ptrs, len(names)),
                           self.inputs(), allocated=True)

    def create_tensors(self, names: List[str]) -> TensorArray:
        """Creates an array of tensors corresponding to tensor names without allocated buffers"""
        ptrs = convert_to_cchar_array(names)
        return TensorArray(LIBNUX.nux_tensor_array_create_by_names(self._get_model_ref(), ptrs, len(names)),
                           self.inputs(), allocated=True)

    def allocate_inputs(self) -> TensorArray:
        """Creates an array of input tensors with allocated buffers"""
        return TensorArray(LIBNUX.nux_tensor_array_allocate_inputs(self._get_model_ref()),
                           self.inputs(), allocated=True)

    def create_inputs(self) -> TensorArray:
        """Creates an array of input tensors without allocated buffers"""
        return TensorArray(LIBNUX.nux_tensor_array_create_inputs(self._get_model_ref()),
                           self.inputs(), allocated=True)

    def allocate_outputs(self) -> TensorArray:
        """Creates an array of output tensors with allocated buffers"""
        return TensorArray(LIBNUX.nux_tensor_array_allocate_outputs(self._get_model_ref()),
                           self.outputs(), allocated=True)

    def create_outputs(self) -> TensorArray:
        """Creates an array of output tensors without allocated buffers"""
        return TensorArray(LIBNUX.nux_tensor_array_create_outputs(self._get_model_ref()),
                           self.outputs(), allocated=True)

    def summary(self) -> str:
        """Returns the summary of this model"""
        return "Inputs:\n{}\nOutputs:\n{}".format(
            list_to_dict(self.inputs()).__repr__(), list_to_dict(self.outputs()).__repr__())

    def print_summary(self):
        """Prints the summary of this model"""
        print(self.summary())
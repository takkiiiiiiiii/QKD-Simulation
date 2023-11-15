from abc import ABCMeta, abstractmethod
from contextlib import contextmanager


class Qubit(metaclass=ABCMeta):
    def __init__(self, state: bool, basis: bool, bit: bool):
        self.state = state
        self.basis = basis
        self.bit = bit
        

    @abstractmethod
    def h(self): pass

    @abstractmethod
    def x(self): pass

    @abstractmethod
    def measure(self) -> bool : pass

    @abstractmethod
    def reset(self): pass

    def to_bytes(self) -> bytes:
        return bytes(f'{self.state:01b}')
    
class QuantumDevice(metaclass=ABCMeta):
    @abstractmethod # Any implementation of a quantum device must implement this method, allowing users to obtain qubits.
    def allocate_qubit(self) -> Qubit:
        pass

    @abstractmethod # When users are done with a qubit, imple- mentations of deallocate_qubit will allow users to return the qubit to the device.
    def deallocate_qubit(self, qubit: Qubit):
        pass

    @contextmanager # We can provide a Python context manager to make it easy to allocate and deallocate qubits safely.
    def using_qubit(self):
        qubit = self.allocate_qubit()
        try:
            yield qubit
        finally:
            qubit.reset()
            self.deallocate_qubit(qubit)
from abc import ABC, abstractmethod
import torch
import numpy as np
import jax.numpy as jnp


class BaseTransform(ABC):
    @abstractmethod
    def transform(self, x):
        pass

    @abstractmethod
    def inverse_transform(self, x):
        pass


class LogTransform(BaseTransform):
    def transform(self, x):
        if type(x) == torch.Tensor:
            return torch.log10(x)
        elif type(x) == np.ndarray:
            return np.log10(x)

    def inverse_transform(self, x):
        return 10**x


class ArcsinhTransform(BaseTransform):
    def transform(self, x):
        if type(x) == torch.Tensor:
            return torch.asinh(x)
        elif type(x) == np.ndarray:
            return np.arcsinh(x)
        else:
            return jnp.arcsinh(x)

    def inverse_transform(self, x):
        if type(x) == torch.Tensor:
            return torch.sinh(x)
        elif type(x) == np.ndarray:
            return np.sinh(x)
        else:
            return jnp.sinh(x)

class WeiLiuOutputTransForm(BaseTransform):
    """Class to reconcile output the Minkowski functionals model
    trained with Wei Liu's scripts with those from the ACM repository.
    """
    def transform(self, x):
        return x

    def inverse_transform(self, x):
        data = np.load('/pscratch/sd/e/epaillas/emc/v1.1/abacus/training_sets/cosmo+hod/raw/minkowski_dummy.npy', allow_pickle=True).item()
        return x * data['train_y_std'] + data['train_y_mean']

class WeiLiuInputTransform(BaseTransform):
    """Class to reconcile input of the Minkowski functionals model
    trained with Wei Liu's scripts with those from the ACM repository.
    """
    def transform(self, x):
        data = np.load('/pscratch/sd/e/epaillas/emc/v1.1/abacus/training_sets/cosmo+hod/raw/minkowski_dummy.npy', allow_pickle=True).item()
        return ((x - data['train_x_mean']) / data['train_x_std']).to(torch.float32)

    def inverse_transform(self, x):
        return x
        
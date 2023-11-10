import tensorflow as tf
from gpflow import likelihoods
from check_shapes import inherit_check_shapes
from gpflow.base import TensorType
from tensorflow_probability import distributions as tfd


class ExpGaussian(likelihoods.ScalarLikelihood):
  def Y_given_F(self, F: TensorType) -> tfd.Normal:
    mu = tf.math.exp(F)
    sigma = tf.math.sqrt(4 * mu)
    return tfd.Normal(mu, sigma)

  @inherit_check_shapes
  def _scalar_log_prob(
      self, X: TensorType, F: TensorType, Y: TensorType
  ) -> tf.Tensor:
    return self.Y_given_F(F).log_prob(Y)

  @inherit_check_shapes
  def _conditional_mean(self, X: TensorType, F: TensorType) -> tf.Tensor:
    return self.Y_given_F(F).mean()

  @inherit_check_shapes
  def _conditional_variance(self, X: TensorType, F: TensorType) -> tf.Tensor:
    return self.Y_given_F(F).variance()

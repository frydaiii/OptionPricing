import tensorflow as tf
import gpflow

def run_adam(model, iterations, train_iter):
    """
    :param model: GPflow model
    :param iterations: number of iterations
    :param train_iter: number of train iterations
    """
    # Create an Adam Optimizer action
    logf = []
    training_loss = model.training_loss_closure(train_iter, compile=True)
    optimizer = tf.optimizers.Adam()

    @tf.function
    def optimization_step():
        optimizer.minimize(training_loss, model.trainable_variables)

    for step in range(iterations):
        optimization_step()
        if step % 1000 == 0:
            elbo = -training_loss().numpy()
            print(step, elbo)
            logf.append(elbo)
    return logf

def run_natgrad(model, iterations, train_iter):
    """
    :param model: GPflow model
    :param iterations: number of iterations
    :param train_iter: number of train iterations
    """
    # Create an Natural Gradient Decent Optimizer action
    logf = []
    training_loss = model.training_loss_closure(train_iter, compile=True)
    optimizer = gpflow.optimizers.NaturalGradient(gamma=0.1)

    @tf.function
    def optimization_step():
        optimizer.minimize(training_loss, [(model.q_mu, model.q_sqrt)])

    for step in range(iterations):
        optimization_step()
        if step % 1000 == 0:
            elbo = -training_loss().numpy()
            print(step, elbo)
            logf.append(elbo)
    return logf
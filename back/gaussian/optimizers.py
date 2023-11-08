import tensorflow as tf
import gpflow
from back.cache import pricing

async def run_adam(client_key, model, iterations, train_iter):
    """
    :param model: GPflow model
    :param iterations: number of iterations
    :param train_iter: number of train iterations
    """
    # Create an Adam Optimizer action
    price = await pricing.get(client_key)
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
            # print(step, elbo)
            price["gp_status"] = "Adam training {step}/{total} with ELBO {elbo}".format(step=step, total=iterations, elbo=elbo)
            await pricing.set(client_key, price)
            logf.append(elbo)
    return logf

async def run_natgrad(client_key, model, iterations, train_iter):
    """
    :param model: GPflow model
    :param iterations: number of iterations
    :param train_iter: number of train iterations
    """
    # Create an Natural Gradient Decent Optimizer action
    price = await pricing.get(client_key)
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
            # print(step, elbo)
            price["gp_status"] = "NatGrad training {step}/{total} with ELBO {elbo}".format(step=step, total=iterations, elbo=elbo)
            await pricing.set(client_key, price)
            logf.append(elbo)
    return logf
import numpy as np
import tensorflow as tf
from tensorflow.python.framework import ops

from tf_models.rbm_models import dbn
from utils import datasets

# #################### #
#   Flags definition   #
# #################### #
flags = tf.app.flags
FLAGS = flags.FLAGS

# Global configuration
flags.DEFINE_string('dataset', 'mnist', 'Which dataset to use. ["mnist", "cifar10"]')
flags.DEFINE_string('cifar_dir', '', 'Path to the cifar 10 dataset directory.')
flags.DEFINE_string('model_name', 'srbm', 'Name of the model.')
flags.DEFINE_boolean('do_pretrain', True, 'Whether or not pretrain the network.')

# Supervised fine tuning parameters
flags.DEFINE_integer('verbose', 0, 'Level of verbosity. 0 - silent, 1 - print accuracy.')
flags.DEFINE_string('main_dir', 'dbn/', 'Directory to store data relative to the algorithm.')
# RBMs layers specific parameters
flags.DEFINE_string('rbm_names', 'rbm', 'Name for the rbm stored_models.')
flags.DEFINE_string('layers', '256,', 'Comma-separated values for the layers in the sdae.')
flags.DEFINE_boolean('gauss_visible', False, 'Whether to use Gaussian units for the visible layer.')
flags.DEFINE_float('stddev', 0.1, 'Standard deviation for Gaussian visible units.')
flags.DEFINE_string('rbm_learning_rate', '0.01,', 'Initial learning rate.')
flags.DEFINE_string('rbm_num_epochs', '10,', 'Number of epochs.')
flags.DEFINE_string('rbm_batch_size', '10,', 'Size of each mini-batch.')
flags.DEFINE_string('rbm_gibbs_k', '1,', 'Gibbs sampling steps.')

flags.DEFINE_float('learning_rate', 0.01, 'Learning rate.')
flags.DEFINE_float('momentum', 0.7, 'Momentum parameter.')
flags.DEFINE_integer('num_epochs', 10, 'Number of epochs.')
flags.DEFINE_integer('batch_size', 10, 'Size of each mini-batch.')
flags.DEFINE_string('opt', 'gradient_descent', 'Which optimizer to use.')
flags.DEFINE_string('loss_func', 'mean_squared', 'Loss function.')
flags.DEFINE_float('dropout', 1, 'Dropout parameter.')

# Conversion of Autoencoder layers parameters from string to their specific type
rbm_names = [_ for _ in FLAGS.rbm_names.split(',') if _]
layers = [int(_) for _ in FLAGS.layers.split(',') if _]
rbm_learning_rate = [float(_) for _ in FLAGS.rbm_learning_rate.split(',') if _]
rbm_num_epochs = [int(_) for _ in FLAGS.rbm_num_epochs.split(',') if _]
rbm_batch_size = [int(_) for _ in FLAGS.rbm_batch_size.split(',') if _]
rbm_gibbs_k = [float(_) for _ in FLAGS.rbm_gibbs_k.split(',') if _]

# Parameters normalization: if a parameter is not specified, it must be made of the same length of the others
dae_params = {'layers': layers,  'learning_rate': rbm_learning_rate, 'num_epochs': rbm_num_epochs,
              'batch_size': rbm_batch_size, 'gibbs_k': rbm_gibbs_k, 'rbm_names': rbm_names}

for p in dae_params:
    if len(dae_params[p]) != len(layers):
        # The current parameter is not specified by the user, should default it for all the layers
        dae_params[p] = [dae_params[p][0] for _ in layers]

# Parameters validation
assert FLAGS.dataset in ['mnist', 'cifar10']
assert len(layers) > 0

if __name__ == '__main__':

    if FLAGS.dataset == 'mnist':

        # ################# #
        #   MNIST Dataset   #
        # ################# #

        trX, trY, vlX, vlY, teX, teY = datasets.load_mnist_dataset(mode='supervised')

    elif FLAGS.dataset == 'cifar10':

        # ################### #
        #   Cifar10 Dataset   #
        # ################### #

        trX, trY, teX, teY = datasets.load_cifar10_dataset(FLAGS.cifar_dir, mode='supervised')
        vlX = teX[:5000]  # Validation set is the first half of the test set
        vlY = teY[:5000]

    else:  # cannot be reached, just for completeness
        trX, trY, vlX, vlY, teX, teY = None, None, None, None, None, None

    # Create the object
    srbm = dbn.DBN(
        model_name=FLAGS.model_name, rbm_names=dae_params['rbm_names'], do_pretrain=FLAGS.do_pretrain,
        layers=dae_params['layers'], dataset=FLAGS.dataset, main_dir=FLAGS.main_dir,
        rbm_learning_rate=dae_params['learning_rate'], rbm_gibbs_k=dae_params['gibbs_k'],
        verbose=FLAGS.verbose, rbm_num_epochs=dae_params['num_epochs'], momentum=FLAGS.momentum,
        rbm_batch_size=dae_params['batch_size'], learning_rate=FLAGS.learning_rate, num_epochs=FLAGS.num_epochs,
        batch_size=FLAGS.batch_size, opt=FLAGS.opt, loss_func=FLAGS.loss_func, dropout=FLAGS.dropout,
        gauss_visible=FLAGS.gauss_visible, stddev=FLAGS.stddev)

    # Fit the model (unsupervised pretraining)
    srbm.pretrain(trX, vlX)

    ops.reset_default_graph()

    # finetuning
    print('Start deep belief net finetuning...')
    srbm.finetune(trX, trY, vlX, vlY)

    params = srbm.get_model_parameters()

    np.savez('data/dbn/{}_W_params'.format(FLAGS.model_name), params['W'])
    np.savez('data/dbn/{}_bh_params'.format(FLAGS.model_name), params['bh'])
    np.savez('data/dbn/{}_bv_params'.format(FLAGS.model_name), params['bv'])

    # Test the model
    print('Test set accuracy: {}'.format(srbm.predict(teX, teY)))

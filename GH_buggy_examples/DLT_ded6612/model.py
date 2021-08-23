import tensorflow as tf
import config
import os


class Model(object):

    """ Class representing an abstract Model.
    """

    def __init__(self, model_name, main_dir):

        """
        :param model_name: name of the model, used as filename. string, default 'dae'
        :param main_dir: main directory to put the stored_models, data and summary directories
        """

        self.model_name = model_name
        self.main_dir = main_dir
        self.models_dir, self.data_dir, self.tf_summary_dir = self._create_data_directories()
        self.model_path = self.models_dir + self.model_name

        self.train_step = None
        self.cost = None

        # tensorflow objects
        self.tf_session = None
        self.tf_saver = None
        self.tf_merged_summaries = None
        self.tf_summary_writer = None

    def _create_data_directories(self):

        """ Create the three directories for storing respectively the stored_models,
        the data generated by training and the TensorFlow's summaries.
        :return: tuple of strings(models_dir, data_dir, summary_dir)
        """

        models_dir = os.path.join(config.models_dir, self.main_dir)
        data_dir = os.path.join(config.data_dir, self.main_dir)
        summary_dir = os.path.join(config.summary_dir, self.main_dir)

        for d in [models_dir, data_dir, summary_dir]:
            if not os.path.isdir(d):
                os.mkdir(d)

        return models_dir, data_dir, summary_dir

    def _initialize_tf_utilities_and_ops(self, restore_previous_model):

        """ Initialize TensorFlow operations: summaries, init operations, saver, summary_writer.
        Restore a previously trained model if the flag restore_previous_model is true.
        :param restore_previous_model:
                    if true, a previous trained model
                    with the same name of this model is restored from disk to continue training.
        """

        self.tf_merged_summaries = tf.merge_all_summaries()
        init_op = tf.initialize_all_variables()
        self.tf_saver = tf.train.Saver()

        self.tf_session.run(init_op)

        if restore_previous_model:
            self.tf_saver.restore(self.tf_session, self.model_path)

        self.tf_summary_writer = tf.train.SummaryWriter(self.tf_summary_dir, self.tf_session.graph)

    def _initialize_training_parameters(self, loss_func, learning_rate, num_epochs, batch_size,
                                        dataset, opt, momentum=None, l2reg=None):

        """ Initialize training parameters common to all models.
        :param loss_func: Loss function. ['mean_squared', 'cross_entropy']
        :param learning_rate: Initial learning rate
        :param num_epochs: Number of epochs
        :param batch_size: Size of each mini-batch
        :param dataset: Which dataset to use. ['mnist', 'cifar10', 'custom'].
        :param opt: Which tensorflow optimizer to use. ['gradient_descent', 'momentum', 'ada_grad']
        :param momentum: Momentum parameter
        :param l2reg: regularization parameter
        :return: self
        """

        self.loss_func = loss_func
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.dataset = dataset
        self.opt = opt
        self.momentum = momentum
        self.l2reg = l2reg

    def _create_cost_function_node(self, loss_func, model_output, ref_input, regterm=None):

        """ Create the cost function node.
        :param loss_func: cost function. ['cross_entropy', 'mean_squared']
        :param model_output: model output node
        :param ref_input: reference input placeholder node
        :param regterm: regularization term
        :return: self
        """

        with tf.name_scope("cost"):
            if loss_func == 'cross_entropy':
                cost = - tf.reduce_mean(ref_input * tf.log(tf.clip_by_value(model_output, 1e-10, float('inf'))) +
                                        (1 - ref_input) * tf.log(tf.clip_by_value(1 - model_output, 1e-10, float('inf'))))
                _ = tf.summary.scalar("cross_entropy", cost)
                self.cost = cost + regterm if regterm is not None else cost

            elif loss_func == 'mean_squared':
                cost = tf.sqrt(tf.reduce_mean(tf.square(ref_input - model_output)))
                _ = tf.summary.scalar("mean_squared", cost)
                self.cost = cost + regterm if regterm is not None else cost

            else:
                self.cost = None

    def _create_train_step_node(self, opt, learning_rate, momentum=None):

        """ Create the training step node of the network.
        :param opt: tensorflow optimizer
        :param learning_rate: learning rate parameter
        :param momentum: momentum parameter (used only for momentum optimizer)
        :return: self
        """

        with tf.name_scope("train"):
            if opt == 'gradient_descent':
                self.train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(self.cost)

            elif opt == 'ada_grad':
                self.train_step = tf.train.AdagradOptimizer(learning_rate).minimize(self.cost)

            elif opt == 'momentum':
                self.train_step = tf.train.MomentumOptimizer(learning_rate, momentum).minimize(self.cost)

            elif opt == 'adam':
                self.train_step = tf.train.AdamOptimizer(learning_rate).minimize(self.cost)

            else:
                self.train_step = None

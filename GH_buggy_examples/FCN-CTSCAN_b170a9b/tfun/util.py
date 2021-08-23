import numpy as np
import tensorflow as tf
import tfun.global_config as global_cfg

def create_one_hot(target_vector, num_class, dtype=np.float32):
    """create_one_hot
    Generate one-hot 4D tensor from a target vector of length N (num sample)
    The one-hot tensor will have the shape of (N x 1 x 1 x num_class)

    :param target_vector: Index vector, values are ranged from 0 to num_class-1

    :param num_class: number of classes/labels
    :return: target vector as a 4D tensor
    """
    one_hot = np.eye(num_class+1, num_class, dtype=dtype)
    one_hot = one_hot[target_vector]
    result = np.reshape(one_hot, (target_vector.shape[0], 1, 1, num_class))
    
    return result

def create_var(name, shape=None, initializer=None, trainable=True):
    """create_var
    Create a tensor variable
    If GPU should be used, specify it with global_cfg.device = '/gpu:0'
    :param name: name of the variable
    :param shape: the shape of the variable, tuple or list of int
    :param initializer: an tf initializer instance or a numpy array
    :param trainable: specify if the var should be trained in the main loop
    """ 
    with tf.device(global_cfg.device):
        dtype = global_cfg.dtype
        
        var = tf.get_variable(name, shape, initializer=initializer, dtype=dtype, trainable=trainable)
        return var

def create_conv_layer(x, kernel_shape, use_bias, stride=[1,1,1,1], padding='SAME', activation=None, wkey='weight', initializer=tf.contrib.layers.xavier_initializer(), name=None):
    """create_conv_layer
    Create a 2D convlutional with optinal bias and activation function
    :param x: input, 4D tensor of shape [batch_size, h, w, in_dim]
    :param kernel_shape: shape of the conv2d kernel, [h, w, in_dim, out_dim]
    :param use_bias: boolean, specify if bias should be used here
    :param stride: stride of the convolution operator
    :param padding: 'SAME' or 'VALID'
    :param activation: activation function, can be None. If an activation functin is passed, it should only take on argument
    :param wkey: name of the kernel variable. Since, the loss.l2_loss is computed based on the name of the variable, you can use this to include the variable in l2_loss or not
    :param initializer: tensorflow intializer
    :param name: name of the operator
    """

    kernel = create_var(wkey, shape=kernel_shape, initializer=initializer)
    conv_result = tf.nn.conv2d(x, kernel, stride, padding=padding)
    if (use_bias):
        bias_shape = [1,1,1,kernel_shape[3]]
        bias = create_var('bias', shape=bias_shape, initializer=tf.constant_initializer(np.zeros(bias_shape)))
        conv_result = conv_result + bias
    if (activation != None):
        conv_result = activation(conv_result, name='relu')
    
    return conv_result

def create_linear_layer(x, w_shape, use_bias, activation=None, wkey='weight', initializer=tf.contrib.layers.xavier_initializer(), name=None):
    """create_linear_layer
    Create a linear layer with optional bias and activation function
    :param x: input, a tensor with num dim >= 2
    :param w_shape: shape of the weight, [in_dim, out_dim]
    :param use_bias: boolean, specify if bias should be used here
    :param activation: activation function, can be None. If an activation functin is passed, it should only take on argument
    :param wkey: name of the kernel variable. Since, the loss.l2_loss is computed based on the name of the variable, you can use this to include the variable in l2_loss or not
    :param initializer: tensorflow intializer
    :param name: name of the operator
    """
    # Preprocess x so that we could perform 2D matrix multiplication
    x_shape = tf.shape(x)
    x_reshape = tf.reshape(x, [x_shape[0], -1], name='reshape')
    
    bias_shape = (w_shape[1], )
    w = create_var('weight', shape=w_shape, initializer=initializer)
    b = create_var('bias', shape=bias_shape, initializer=tf.constant_initializer(np.zeros(bias_shape)))
    x = tf.nn.bias_add(tf.matmul(x_reshape, w), b, name=name)
    if (activation != None):
        x = activation(x, name='relu')
    return x

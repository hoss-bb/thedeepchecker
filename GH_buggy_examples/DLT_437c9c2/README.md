# Deep Learning algorithms with TensorFlow

This repository is a collection of various Deep Learning algorithms implemented using the
[TensorFlow](http://www.tensorflow.org) library.

### Requirements:

* tensorflow >= 0.6

Available models:

* Restricted Boltzmann Machine
* Deep Belief Network
* Deep Autoencoder
* Denoising Autoencoder
* Stacked Denoising Autoencoder

The `command_line` package has a run script for each algorithm, where the parameters can be specified.
Example Usage:

    python command_line/run_rbm.py --verbose 1 --num_hidden 250 --num_epochs 10 --batch_size 128 --model_name rbm --learning_rate 0.0001

If no dataset is specified, the MNIST dataset will be used.

Configuration:

* config.py: Configuration file, used to set the path to the data directories:
  * models_dir: directory where trained model are saved/restored
  * data_dir: directory to store data generated by the model (for example generated images)
  * summary_dir: directory to store TensorFlow logs and events (this data can be visualized using TensorBoard)
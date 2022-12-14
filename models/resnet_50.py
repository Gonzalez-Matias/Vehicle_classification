from utils.data_aug import create_data_aug_layer
from keras import layers
from tensorflow import float32
from tensorflow.keras.applications import resnet50
from keras import Model
from tensorflow.keras import regularizers
from keras.models import load_model


def create_model(
    weights: str = "imagenet",
    input_shape: tuple = (224, 224, 3),
    dropout_rate: float = 0.0,
    data_aug_layer: dict = None,
    classes: int = None,
    train_all: bool = False,
    l2_: float = 0.0,
    l1_: float = 0.0,
):
    """
    Creates and loads the Resnet50 model we will use for our experiments.
    Depending on the `weights` parameter, this function will return one of
    two possible keras models:
        1. weights='imagenet': Returns a model ready for performing finetuning
                               on your custom dataset using imagenet weights
                               as starting point.
        2. weights!='imagenet': Then `weights` must be a valid path to a
                                pre-trained model on our custom dataset.
                                This function will return a model that can
                                be used to get predictions on our custom task.

    See an extensive tutorial about finetuning with Keras here:
    https://www.tensorflow.org/tutorials/images/transfer_learning.

    Parameters
    ----------
    weights : str
        One of None (random initialization),
        'imagenet' (pre-training on ImageNet), or the path to the
        weights file to be loaded.

    input_shape	: tuple
        Model input image shape as (height, width, channels).
        Only needed when weights='imagenet'. Otherwise, the trained model
        already has the input shape defined and we shouldn't change it.
        Input image size cannot be no smaller than 32. E.g. (224, 224, 3)
        would be one valid value.

    dropout_rate : float
        Value used for Dropout layer to randomly set input units
        to 0 with a frequency of `dropout_rate` at each step during training
        time, which helps prevent overfitting.
        Only needed when weights='imagenet'.

    data_aug_layer : dict
        Configuration from experiment YAML file used to setup the data
        augmentation process during finetuning.
        Only needed when weights='imagenet'.

    classes : int
        Model output classes.
        Only needed when weights='imagenet'. Otherwise, the trained model
        already has the output classes number defined and we shouldn't change
        it.

    Returns
    -------
    model : keras.Model
        Loaded model either ready for performing finetuning or to start doing
        predictions.
    """


    if weights == "imagenet":
        
        input_layer = layers.Input(dtype=float32, shape=input_shape)

        if data_aug_layer:
            data_aug = create_data_aug_layer(data_aug_layer)

        prepreprocessing_layer = resnet50.preprocess_input

        base_model = resnet50.ResNet50(include_top=False, pooling="avg", weights=weights)
        base_model.trainable = train_all

        drop_out_layer = layers.Dropout(dropout_rate)

        output_layer = layers.Dense(units=classes, activation="softmax", kernel_regularizer= regularizers.L1L2(l1=l1_, l2=l2_))

        inputs = input_layer
        if data_aug_layer:
            x = data_aug(inputs)
            x = prepreprocessing_layer(x)
        else:
            x = prepreprocessing_layer(inputs)
        x = base_model(x)
        x = drop_out_layer(x)
        outputs = output_layer(x)
        model = Model(inputs, outputs)
    else:

        model = load_model(weights)

    return model

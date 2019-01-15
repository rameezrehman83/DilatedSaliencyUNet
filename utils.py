import keras
from keras.layers import Layer
import tensorflow as tf

class Padding(Layer):
    '''
       Keras padding layer including symmetric, zero, reflect modes. 
       The mode value is same as tf.pad mode. 
       ("CONSTANT", "REFLECT", "SYMMETRIC") 
    '''
    def __init__(self, kernel_size, dilation, mode, **kwargs):
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.mode = mode
        super(Padding, self).__init__(**kwargs)

    def build(self, input_shape):
        
        super(Padding, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x):
        pad = [int(((self.kernel_size[0]-1)*self.dilation)/2),int(((self.kernel_size[1]-1)*self.dilation)/2)] 
        paddings = tf.constant([[0,0],[pad[0], pad[0]], [pad[1], pad[1]],[0,0]])
        return tf.pad(x, paddings, self.mode)

    def compute_output_shape(self, input_shape):
        #input_shape[1] = input_shape[1]+self.kernel_size[0]
        #input_shape[2] = input_shape[2]+self.kernel_size[1]
        return input_shape


class TestCallback(keras.callbacks.Callback):
    
    def __init__(self, test_data, test_label, save_dir, epoch=1):
        self.test_data = test_data
        self.test_label = test_label
        self.save_dir = save_dir
        self.ep = epoch
    
    def on_train_begin(self, logs={}):
        self.test_loss = []
        self.test_accuracy = []
        self.test_dicecoef = []

    def on_epoch_end(self, epoch, logs={}):
        if (epoch%self.ep)==0:
            metrics= self.model.evaluate(self.test_data, self.test_label, batch_size=16, verbose=0)
            self.test_loss.append(metrics[0])
            self.test_accuracy.append(metrics[1])
            self.test_dicecoef.append(metrics[2])
            print('Testing loss: {}, categorical-acc: {}, dice-coef: {}\n'.format(metrics[0], metrics[1], metrics[2]))
            
            if len(self.test_dicecoef) == 1 or (self.test_dicecoef[-2] < self.test_dicecoef[-1]):
                self.model.save_weights(self.save_dir+'best_train_models.h5')
                
    
    def on_train_end(self, logs={}):
        with open(self.save_dir+'test_loss.txt',"w") as n:
            for val in self.test_loss: n.write(str(val)+'\n')
         
        with open(self.save_dir+'test_categorical_accuracy.txt',"w") as n:
            for val in self.test_accuracy: n.write(str(val)+'\n')
                
        with open(self.save_dir+'test_dice_coef.txt',"w") as n:
            for val in self.test_dicecoef: n.write(str(val)+'\n')

class TrainConfig(object):
    
    def __init__(self, args):
        self.lr = args.lr
        self.num_epochs = args.num_epochs
        self.fold = args.fold
        self.batch_size = args.batch_size
        self.VISUALISATION = args.visualisation
        self.Patch = args.Patch
        self.hist_freq = 10 if self.VISUALISATION else 0
        self.loss = args.loss
        self.fold = args.fold
        self.n_class = 3
        self.reduce_lr_factor = args.reduce_lr_factor
        self.reduce_lr_patience = args.reduce_lr_patience
        self.dir_name = args.dir_name
        self.interim_vis = args.interim_vis

def set_parser(parser):
    # Arguments for training
    parser.add_argument('--shuffle_epoch', type=bool,default=True)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--num_epochs', type=int, default=80)
    parser.add_argument('--bn_momentum', type=float, default=0.99)
    parser.add_argument('--TRSH', type=float, default=0.0)
    parser.add_argument('--data_chn_num', type=int, default=3)
    parser.add_argument('--fold', type=int, default=2)
    parser.add_argument('--random_num', type=int, default=500)
    parser.add_argument('--img_size', type=int, default=64)
    parser.add_argument('--batch_norm', dest='batch_norm', action='store_true', default=True)
    parser.add_argument('--no_batch_norm', dest='batch_norm',action='store_false')
    parser.add_argument('--dir_name', type=str, default='')
    parser.add_argument('--gpu_device', type=str, required=True,
                        help='Available GPU number')
    parser.add_argument('--depth', type=int, default=4)
    parser.add_argument('--reduce_lr_factor', type=float, default=0.2)
    parser.add_argument('--reduce_lr_patience', type=int, default=4)
    parser.add_argument('--loss', type=str, default='crossentropy')
    
    parser.add_argument('--test', dest='test', action='store_true', default=False)
    parser.add_argument('--restore', dest='restore', action='store_true', default=False)
    parser.add_argument('--Patch', dest='Patch', action='store_true', default=True)
    parser.add_argument('--Slice',dest='Patch', action='store_false')
    parser.add_argument('--visualisation', dest='visualisation', action='store_true', default=False)
    parser.add_argument('--interim_vis', dest='interim_vis', action='store_true', default=False)
    
    return parser
    
    

import numpy as np
import tensorflow as tf


class nn:
    __batch_size=None
    __datatype=tf.float32
    __epochs=10
    __hidden_layers=None
    __activation_choice=None
    __learning_rate = 0.1
    __dropout_rate=.8
    __n_classes=None
    __feature_size=None
    __working_dir='./'
    __model_saving=False
    __model_restore=False
    __shape=None
    train_result=None
    test_result = None
    training_test_prediction=None
    training_test_accuracy=None
    def __init__(self):
        return
    def set_batch_size(self,value):
        self.__batch_size=value
    def set_datatype(self,value):
        self.__datatype=value
    def set_epochs(self,value):
        self.__epochs=value
    def set_hidden_layers(self,list,activation_choice_list):
        self.__hidden_layers=list
        self.__activation_choice=activation_choice_list
    def set_learningrate(self,value):
        self.__learning_rate=value
    def set_dropout(self,value):
        self.__dropout_rate=value
    def set_n_classes(self,classes):
        self.__n_classes=classes
    def set_feature_size(self,value):
        self.__feature_size=value
    def set_save_summary_path(self,path):
        self.__working_dir=path
        print 'run this command on terminal'
        print 'tensorboard --logdir='+path
        self.__model_saving = True
    def set_model_restore_state(self,state):
        self.__model_restore=state
    def set_train_shape(self,shape):
        self.__shape=shape
    def __choose_activation_function(self,node, choice):
        if choice == 0:
            return node
        if choice == 1:
            return tf.nn.relu(node)
        if choice == 2:
            return tf.nn.sigmoid(node)
        if choice == 3:
            return tf.nn.tanh(node)
        if choice == 4:
            return tf.nn.dropout(node,self.__dropout_rate)
        if choice == 5:
            return tf.nn.crelu(node)
        if choice == 6:
            return tf.nn.relu6(node)
        if choice == 7:
            return tf.nn.elu(node)
        if choice == 8:
            return tf.nn.softplus(node)
        if choice == 9:
            return tf.nn.softsign(node)
    def get_activation_function_name(self,choice):
        if choice == 0:
            return 'None'
        if choice == 1:
            return 'Relu'
        if choice == 2:
            return 'Sigmoid'
        if choice == 3:
            return 'Tanh'
        if choice == 4:
            return 'Softsign'
        if choice == 5:
            return 'Softplus'
        if choice == 6:
            return 'Relu6'
        if choice == 7:
            return 'Elu'
        if choice == 8:
            return 'Crelu'
        if choice == 9:
            return 'Dropout'
    def __look_for_last_checkpoint(self,mode_dir):
        try:
            fr=open(mode_dir+'checkpoint',"r")
        except:
            return None
        f_line=fr.readline()
        start=f_line.find('"')
        end=f_line.rfind('"')
        return f_line[start+1:end]


    def __variable_summaries(self,var,name):
        with tf.name_scope(name):
            mean = tf.reduce_mean(var)
            tf.summary.scalar('mean', mean)
            with tf.name_scope('stddev'):
              stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
            tf.summary.scalar('stddev', stddev)
            tf.summary.scalar('max', tf.reduce_max(var))
            tf.summary.scalar('min', tf.reduce_min(var))
            tf.summary.histogram('histogram', var)
    def __model_defination(self,x):
        hidden_layer_weights_biases = {}
        layer_output = {}
        for i in range(len(self.__hidden_layers)):
            with tf.name_scope('Hidden_Layer_'+str(i+1)):
                if i == 0:
                    hidden_layer_weights_biases.update(
                        {'weights' + str(i): tf.Variable(tf.truncated_normal([self.__feature_size, self.__hidden_layers[i]]),name='weight'),
                         'biases' + str(i): tf.Variable(tf.truncated_normal([1, self.__hidden_layers[i]]),name='biases')})
                    self.__variable_summaries(hidden_layer_weights_biases['weights' + str(i)],"weights")
                    self.__variable_summaries(hidden_layer_weights_biases['biases' + str(i)],"biases")
                    mul=tf.matmul(x, hidden_layer_weights_biases['weights' + str(i)])
                    add=tf.add(mul,hidden_layer_weights_biases['biases' + str(i)])
                    act=self.__choose_activation_function(add,self.__activation_choice[i])
                    layer_output.update({str(i):act})
                    self.__variable_summaries(mul,"Multiply")
                    self.__variable_summaries( add,"Add")
                    self.__variable_summaries(act,self.get_activation_function_name(self.__activation_choice[i]))

                else:
                    hidden_layer_weights_biases.update(
                        {'weights' + str(i): tf.Variable(tf.truncated_normal([self.__hidden_layers[i - 1], self.__hidden_layers[i]]),name='weight'),
                         'biases' + str(i): tf.Variable(tf.truncated_normal([1, self.__hidden_layers[i]]),name='biases')})
                    self.__variable_summaries(hidden_layer_weights_biases['weights' + str(i)],"weights")
                    self.__variable_summaries(hidden_layer_weights_biases['biases' + str(i)],"biases")
                    mul=tf.matmul(layer_output[str(i - 1)], hidden_layer_weights_biases['weights' + str(i)])
                    add=tf.add(mul,hidden_layer_weights_biases['biases' + str(i)])
                    act=self.__choose_activation_function(add, self.__activation_choice[i])
                    layer_output.update({str(i):act})
                    self.__variable_summaries(mul,"Multiply")
                    self.__variable_summaries( add,"Add")
                    self.__variable_summaries(act, self.get_activation_function_name(self.__activation_choice[i]))

        with tf.name_scope('Output_Layer'):
            output_layer = {'weights': tf.Variable(tf.random_normal([self.__hidden_layers[len(self.__hidden_layers) - 1], self.__n_classes]),name='weight'),
                        'biases': tf.Variable(tf.random_normal([1, self.__n_classes]),name='biases') }
            self.__variable_summaries( output_layer['weights'],"weights")
            self.__variable_summaries(output_layer['biases'],"biases" )
            mul=tf.matmul(layer_output[str(len(self.__hidden_layers) - 1)], output_layer['weights'])
            logits= tf.add(mul,output_layer['biases'],name="logits")
            self.__variable_summaries(mul, "Multiply")
            self.__variable_summaries(logits, "logits")
        return logits
    def pretrained_test(self,data):
        tf.reset_default_graph()
        x = tf.placeholder(dtype=self.__datatype, shape=[None, self.__feature_size],name="input")
        y = tf.placeholder(dtype=self.__datatype, shape=[None, self.__n_classes],name="labels")
        logits = self.__model_defination(x)

        with tf.name_scope('Accuracy'):
            #cross_entropy = tf.reduce_mean(tf.square(tf.subtract(hypothesis,y)),name='Cross_entropy')
            cross_entropy=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits,labels=y,name='Cross_entropy'))
            hypothesis = tf.nn.softmax(logits, name="softmax")
            prediction=tf.argmax(hypothesis, 1,name='Prediction')
            correct_prediction = tf.equal(prediction, tf.argmax(y, 1),name='Correct_prediction')
            accuracy=tf.reduce_mean(tf.cast(correct_prediction, tf.float32),name='Accuracy')
            tf.summary.scalar("Cross_Entropy", cross_entropy)
            tf.summary.scalar("Accuracy", accuracy)

        with tf.name_scope('Optimizer'):
            learningRate = tf.train.exponential_decay(learning_rate=self.__learning_rate,global_step=1,
                                                  decay_steps=self.__shape[0],decay_rate=0.97,staircase=True,name='Learning_Rate')
            #optimizer = tf.train.GradientDescentOptimizer(self.__learning_rate).minimize(cross_entropy)
            optimizer = tf.train.AdamOptimizer(self.__learning_rate).minimize(cross_entropy)

        session = tf.InteractiveSession()
        saver = tf.train.Saver()
        saver.restore(session, tf.train.latest_checkpoint(self.__working_dir+'/model/'))
        merged = tf.summary.merge_all()
        if data.has_key('test_x') and data['test_x'].shape[0] > 0:
            i = 0
            iteration = 0
            accu = 0
            test_prediction=[]
            while i < len(data['test_x']):
                start = i
                end = i + self.__batch_size
                if (end > len(data['test_x'])): end = len(data['test_x'])
                batch_x = data['test_x'][start:end]
                if data.has_key('test_y') and data['test_y'].shape[0] > 0:
                    batch_y = data['test_y'][start:end]
                    pred,acc = session.run([prediction,accuracy], feed_dict={x: batch_x, y: batch_y})
                    accu += acc
                else:
                    pred= session.run([prediction], feed_dict={x: batch_x})
                iteration += 1
                i += self.__batch_size
                test_prediction+=list(pred)
        return np.reshape(np.array(test_prediction),[-1]), accu/iteration
    def train(self,data):
        if self.__batch_size == None: self.__batch_size = data['train_x'].shape[0]
        tf.reset_default_graph()

        x = tf.placeholder(dtype=self.__datatype, shape=[None, self.__feature_size],name="input")
        y = tf.placeholder(dtype=self.__datatype, shape=[None, self.__n_classes],name="labels")
        logits = self.__model_defination(x)

        with tf.name_scope('Accuracy'):
            #cross_entropy = tf.reduce_mean(tf.square(tf.subtract(hypothesis,y)),name='Cross_entropy')
            cross_entropy=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits,labels=y,name='Cross_entropy'))
            hypothesis = tf.nn.softmax(logits, name="softmax")
            prediction=tf.argmax(hypothesis, 1,name='Prediction')
            correct_prediction = tf.equal(prediction, tf.argmax(y, 1),name='Correct_prediction')
            accuracy=tf.reduce_mean(tf.cast(correct_prediction, tf.float32),name='Accuracy')
            tf.summary.scalar("Cross_Entropy", cross_entropy)
            tf.summary.scalar("Accuracy", accuracy)

        with tf.name_scope('Optimizer'):
            learningRate = tf.train.exponential_decay(learning_rate=self.__learning_rate,global_step=1,
                                                  decay_steps=self.__shape[0],decay_rate=0.97,staircase=True,name='Learning_Rate')
            #optimizer = tf.train.GradientDescentOptimizer(self.__learning_rate).minimize(cross_entropy)
            optimizer = tf.train.AdamOptimizer(self.__learning_rate).minimize(cross_entropy)

        init = tf.global_variables_initializer()
        session = tf.InteractiveSession()
        session.run(init)
        saver = tf.train.Saver()
        if self.__model_restore == True:
            name=self.__look_for_last_checkpoint(self.__working_dir+"/model/")
            if name is not None:
                saver.restore(session,self.__working_dir+"/model/"+name)
        merged = tf.summary.merge_all()
        train_writer = tf.summary.FileWriter(self.__working_dir + '/train',session.graph)
        test_writer = tf.summary.FileWriter(self.__working_dir + '/test')
        test_result =[]
        train_result =[]
        for epoch in range(self.__epochs):
            epoch_loss = 0
            accu=0
            i = 0
            iteration=0
            while i < len(data['train_x']):
                start = i
                end = i + self.__batch_size
                if (end > len(data['train_x'])): end = len(data['train_x'])
                batch_x = data['train_x'][start:end]
                batch_y = data['train_y'][start:end]
                summary ,_,loss , acc= session.run([merged,optimizer, cross_entropy,accuracy], feed_dict={x: batch_x, y: batch_y})
                epoch_loss += loss
                accu+=acc
                iteration+=1
                i += self.__batch_size
            train_writer.add_summary(summary, epoch)
            train_result.append([epoch,epoch_loss,accu/iteration])
            if data.has_key('test_x') and data['test_x'].shape[0]>0:
                epoch_loss = 0
                accu = 0
                i = 0
                iteration = 0
                while i < len(data['test_x']):
                    start = i
                    end = i + self.__batch_size
                    if (end > len(data['test_x'])): end = len(data['test_x'])
                    batch_x = data['test_x'][start:end]
                    batch_y = data['test_y'][start:end]
                    summary,loss,acc = session.run([merged,cross_entropy,accuracy],feed_dict={x: batch_x, y: batch_y})
                    epoch_loss += loss
                    accu += acc
                    iteration += 1
                    i += self.__batch_size
                test_writer.add_summary(summary, epoch)
                test_result.append([epoch, epoch_loss, accu/iteration])
                print "Training:",train_result[len(train_result)-1],"Test:",test_result[len(test_result)-1]
            else:
                print "Training :", train_result[len(train_result) - 1]

            if self.__model_saving == True:
                save_path = saver.save(session, self.__working_dir + "/model/" + 'nn_model%d.ckpt' % epoch)
                #print("Model saved in file: %s" % save_path)
        print 'Training Succesfully Complete'
        if data.has_key('test_x') and data['test_x'].shape[0] > 0:
            i = 0
            iteration = 0
            accu = 0
            test_prediction=[]
            while i < len(data['test_x']):
                start = i
                end = i + self.__batch_size
                if (end > len(data['test_x'])): end = len(data['test_x'])
                batch_x = data['test_x'][start:end]
                batch_y = data['test_y'][start:end]
                pred,acc = session.run([prediction,accuracy], feed_dict={x: batch_x, y: batch_y})
                accu += acc
                iteration += 1
                i += self.__batch_size
                test_prediction+=list(pred)
            self.training_test_prediction =np.reshape(np.array(test_prediction),[-1])
            self.training_test_accuracy=accu/iteration
        self.train_result=train_result
        self.test_result=test_result
def get_model():
    return nn()
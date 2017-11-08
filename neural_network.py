import tensorflow as tf
import numpy as np


def get_data():
    import pandas as pd
    from sklearn.model_selection import train_test_split

    X_ = pd.read_csv('X.csv').values
    Y_ = pd.read_csv('Y.csv').values

    X_train, X_test, y_train, y_test = train_test_split(X_, Y_, test_size=0.2, random_state=42)

    print('Images Read')

    return X_train, X_test, y_train, y_test


def build_graph(epochs=10, learning_rate=0.01, num_nodes_hl1=500, num_nodes_hl2=500, num_nodes_hl3=500):
    tf.reset_default_graph()

    num_nodes_hl1 = num_nodes_hl1
    num_nodes_hl2 = num_nodes_hl2
    num_nodes_hl3 = num_nodes_hl3

    training_epochs = epochs

    n_classes = 2
    learning_rate = learning_rate
    # The size of our imput data is 784
    input_dim = 784

    # None -> batch size can be any size, 784 -> flattened mnist image
    x = tf.placeholder('float', shape=[None, input_dim], name='x_placeholder')
    # target 10 output classes
    y = tf.placeholder('float', shape=[None, n_classes], name='y_placeholder')

    W1 = tf.Variable(tf.random_normal([input_dim, num_nodes_hl1], name='hidden_layer_1'))
    W2 = tf.Variable(tf.random_normal([num_nodes_hl1, num_nodes_hl2], name='hidden_layer_2'))
    W3 = tf.Variable(tf.random_normal([num_nodes_hl2, num_nodes_hl3], name='hidden_layer_3'))
    out_w = tf.Variable(tf.random_normal([num_nodes_hl3, n_classes], name='hidden_layer_1'))

    # bias

    b1 = tf.Variable(tf.random_normal([num_nodes_hl1]))
    b2 = tf.Variable(tf.random_normal([num_nodes_hl2]))
    b3 = tf.Variable(tf.random_normal([num_nodes_hl3]))
    out_b = tf.Variable(tf.random_normal([n_classes]))

    # y is our prediction
    l1 = tf.add(tf.matmul(x, W1), b1)

    # Add activation function to run this data
    l1 = tf.nn.relu(l1, name='relu_l1')

    l2 = tf.add(tf.matmul(l1, W2), b2)
    l2 = tf.nn.relu(l2, name='relu_l2')

    l3 = tf.add(tf.matmul(l2, W3), b3)
    l3 = tf.nn.relu(l3, name='relu_l3')

    output = tf.add(tf.matmul(l3, out_w), out_b, name='output')

    # specify cost function

    # this is our cost
    cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=output, name='loss'))
    tf.summary.scalar("cost", cost)

    # specify optimizer


    # optimizer is an "operation" which we can execute in a session
    # Our stochastic gradient descent function to determine what our function should do next to decrease cost
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost, name='optimizer')

    # Accuracy
    correct_prediction = tf.equal(tf.argmax(output, 1), tf.argmax(y, 1), name='correct_prediction')
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name='accuracy')
    tf.summary.scalar("accuracy", accuracy)

    # create a summary for our cost and accuracy



    # merge all summaries into a single "operation" which we can execute in a session
    summary_op = tf.summary.merge_all()

    saver = tf.train.Saver(max_to_keep=1)

    init = tf.global_variables_initializer()

    print('Graph Built')

    return x, y, cost, accuracy, optimizer, summary_op, saver, init, training_epochs


def execute_nn(X_train, X_test, y_train, y_test, x, y, cost, accuracy, optimizer, summary_op, saver, init,
               training_epochs):

    # Need to create the "save_model" directory first
    model_path = "saved_model/model.ckpt"
    # These are the number of nodes we want to have in each layer,
    # we can set these values to whatever we want.

    # config
    batch_size = 100
    training_epochs = training_epochs
    logs_path = "logs"

    with tf.Session() as sess:
        # variables need to be initialized before we can use them

        sess.run(init)

        # create log writer object
        writer = tf.summary.FileWriter(logs_path, graph=tf.get_default_graph(), max_queue=2)

        # perform training cycles
        for epoch in range(training_epochs):

            batch_count = int(len(X_train) / batch_size)
            total_loss = 0
            for i in range(int(len(X_train) / batch_size)):
                randidx = np.random.randint(len(X_train), size=batch_size)

                batch_x = np.array(X_train)[randidx]
                batch_y = np.array(y_train)[randidx]

                # perform the operations we defined earlier on batch
                _, summary, c = sess.run([optimizer, summary_op, cost], feed_dict={x: batch_x, y: batch_y})

                total_loss += c
                # write log
                writer.add_summary(summary, epoch * batch_count + i)



            print("Testing Accuracy:", sess.run(accuracy, feed_dict={x: X_test, y: y_test}))




            print('Epoch ', epoch, ' completed out of ', training_epochs, ', loss: ', total_loss)

        # Save model weights to disk

        save_path = saver.save(sess, model_path)

        print("Model saved in file: %s" % save_path)

        return total_loss, accuracy


def main():
    X_train, X_test, y_train, y_test = get_data()
    x, y, cost, accuracy, optimizer, summary_op, saver, init, training_epochs = build_graph(epochs=20, learning_rate=.000001)
    execute_nn(X_train, X_test, y_train, y_test, x, y, cost, accuracy, optimizer, summary_op, saver, init,
               training_epochs)


if __name__ == "__main__":
    main()
import pickle
from keras.preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer
from keras.models import Sequential, Model
from keras.layers import Dense, Embedding, Activation, merge, Input, Lambda, Reshape, LSTM, RNN, CuDNNLSTM, \
    SimpleRNNCell, SpatialDropout1D, Add, Maximum
from keras.layers import Conv1D, Flatten, Dropout, MaxPool1D, GlobalAveragePooling1D, concatenate, AveragePooling1D
from keras import optimizers
from keras import regularizers
from keras.layers import BatchNormalization
from keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint
from keras.utils import to_categorical
import time
import numpy as np
from keras import backend as K
from sklearn.model_selection import StratifiedKFold
from keras.models import load_model

config = K.tf.ConfigProto()
config.gpu_options.allow_growth = True
session = K.tf.Session(config=config)

Fname = 'malware_cnn_and_lstm_'
Time = Fname + str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
tensorboard = TensorBoard(log_dir='./Logs/' + Time, histogram_freq=0, write_graph=False, write_images=False,
                          embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)

# with open("security_test.csv.pkl", "rb") as f:
#     file_names = pickle.load(f)
#     outfiles = pickle.load(f)
with open("dynamic_feature_train.csv.pkl", "rb") as f:
    labels_d = pickle.load(f)
with open("dynamic_feature_train.csv.pkl", "rb") as f:
    labels = pickle.load(f)
    files = pickle.load(f)
maxlen = 2000


labels = np.asarray(labels)
labels = to_categorical(labels, num_classes=2)
tokenizer = pickle.load(open('tokenizer.pkl', 'rb'))
x_train_word_ids = tokenizer.texts_to_sequences(files)#用于向量化文本,将文本转换为序列
x_train_padded_seqs = pad_sequences(x_train_word_ids, maxlen=maxlen)#将序列填充到maxlen长度
vocab = tokenizer.word_index
MAX_NB_WORDS = 20000
def text_cnn_lstm():
    main_input = Input(shape=(maxlen,), dtype='float64')
    embedder = Embedding(min(MAX_NB_WORDS, len(vocab))+1, 128, input_length=maxlen)
    embed = embedder(main_input)
    # cnn1模块，kernel_size = 3
    conv1_1 = Conv1D(16, 3, padding='same')(embed)
    bn1_1 = BatchNormalization()(conv1_1)
    relu1_1 = Activation('relu')(bn1_1)
    conv1_2 = Conv1D(32, 3, padding='same')(relu1_1)
    bn1_2 = BatchNormalization()(conv1_2)
    relu1_2 = Activation('relu')(bn1_2)
    cnn1 = MaxPool1D(pool_size=4)(relu1_2)
    # cnn2模块，kernel_size = 4
    conv2_1 = Conv1D(16, 4, padding='same')(embed)
    bn2_1 = BatchNormalization()(conv2_1)
    relu2_1 = Activation('relu')(bn2_1)
    conv2_2 = Conv1D(32, 4, padding='same')(relu2_1)
    bn2_2 = BatchNormalization()(conv2_2)
    relu2_2 = Activation('relu')(bn2_2)
    cnn2 = MaxPool1D(pool_size=4)(relu2_2)
    # cnn3模块，kernel_size = 5
    conv3_1 = Conv1D(16, 5, padding='same')(embed)
    bn3_1 = BatchNormalization()(conv3_1)
    relu3_1 = Activation('relu')(bn3_1)
    conv3_2 = Conv1D(32, 5, padding='same')(relu3_1)
    bn3_2 = BatchNormalization()(conv3_2)
    relu3_2 = Activation('relu')(bn3_2)
    cnn3 = MaxPool1D(pool_size=4)(relu3_2)
    # 拼接三个模块
    cnn = concatenate([cnn1, cnn2, cnn3], axis=-1)
    # cnn = concatenate([cnn1, cnn2], axis=-1)
    lstm = CuDNNLSTM(128)(cnn)
    # f = Flatten()(cnn1)
    # fc = Dense(256, activation='relu')(f)
    # D = Dropout(0.5)(fc)
    main_output = Dense(2, activation='softmax')(lstm)
    model = Model(inputs=main_input, outputs=main_output)
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


# meta_train = np.zeros(shape=(len(x_train_padded_seqs), 7))
skf = StratifiedKFold(n_splits=10, random_state=4, shuffle=True)
for i, (tr_ind, te_ind) in enumerate(skf.split(x_train_padded_seqs, labels_d)):
    print('FOLD: {}'.format(str(i)))
    print(len(te_ind), len(tr_ind))
    X_train, X_train_label = x_train_padded_seqs[tr_ind], labels[tr_ind]
    X_val, X_val_label = x_train_padded_seqs[te_ind], labels[te_ind]

    model = text_cnn_lstm()
    print(model.summary())


    model_save_path = './model/model_weight_text_cnn_and_lstm_{}.h5'.format(str(i+2))
    print(model_save_path)
    if i in [-1]:
        model=load_model(model_save_path)
        print(model.evaluate(X_val, X_val_label))
    else:
        checkpoint = model_checkpoint = ModelCheckpoint(model_save_path, save_best_only=True, save_weights_only=False)
        ear = EarlyStopping(monitor='val_loss', min_delta=0, patience=5, verbose=0, mode='min', baseline=None,
                            restore_best_weights=False)
        history = model.fit(X_train, X_train_label,
                            batch_size=32,
                            epochs=200,
                            validation_data=(X_val, X_val_label), callbacks=[ear,checkpoint])

        # model.save('./model/model_weight_cnn_lstm_{}.h5'.format(str(i)))
        # model.load_weights(model_save_path)
    # model = load_model(model_save_path)
    # pred_val = model.predict(X_val)
    # meta_train[te_ind] = pred_val
    K.clear_session()

#
# with open("text_cnn_and_lstm_result.pkl", 'wb') as f:
#     pickle.dump(meta_train, f)



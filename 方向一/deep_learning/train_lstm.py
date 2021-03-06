import pickle
from keras.preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer
from keras.models import Model
from keras.models import Sequential
from keras.layers import Dense, Embedding, Input, CuDNNLSTM
from keras.layers import Conv1D, MaxPool1D
from keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint
from keras.utils import to_categorical
import time
import numpy as np
from keras import backend as K
from sklearn.model_selection import StratifiedKFold
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM, GRU
from keras.models import load_model

config = K.tf.ConfigProto()
config.gpu_options.allow_growth = True
session = K.tf.Session(config=config)

Fname = 'malware_LSTM_'
Time = Fname + str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
tensorboard = TensorBoard(log_dir='./Logs/' + Time, histogram_freq=0, write_graph=False, write_images=False,
                          embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)#tensorboard日志

with open("dynamic_feature_train.csv.pkl", "rb") as f:
    labels_d = pickle.load(f)
with open("dynamic_feature_train.csv.pkl", "rb") as f:
    labels = pickle.load(f)
    files = pickle.load(f)
MAX_NB_WORDS = 20000
maxlen = 2000
labels = np.asarray(labels)
labels = to_categorical(labels, num_classes=7)

tokenizer = pickle.load(open('tokenizer.pkl', 'rb'))
x_train_word_ids = tokenizer.texts_to_sequences(files)#用于向量化文本,将文本转换为序列
x_train_padded_seqs = pad_sequences(x_train_word_ids, maxlen=maxlen)#将序列填充到maxlen长度
vocab = tokenizer.word_index

def lstm_model():
    main_input = Input(shape=(maxlen,), dtype='float64')
    embedder = Embedding(min(len(vocab),MAX_NB_WORDS) + 1, 256, input_length=maxlen)
    embed = embedder(main_input)
    # avg = GlobalAveragePooling1D()(embed)
    # cnn1模块，kernel_size = 3
    # conv1_1 = Conv1D(64, 3, padding='same', activation='relu')(embed)
    # conv1_2 = Conv1D(64, 3, padding='same', activation='relu')(conv1_1)
    # cnn1 = MaxPool1D(pool_size=2)(conv1_2)
    # conv1_1 = Conv1D(64, 3, padding='same', activation='relu')(cnn1)
    # conv1_2 = Conv1D(64, 3, padding='same', activation='relu')(conv1_1)
    # cnn1 = MaxPool1D(pool_size=2)(conv1_2)
    # conv1_1 = Conv1D(64, 3, padding='same', activation='relu')(cnn1)
    # conv1_2 = Conv1D(64, 3, padding='same', activation='relu')(conv1_1)
    # cnn1 = MaxPool1D(pool_size=2)(conv1_2)
    rl = CuDNNLSTM(256)(embed)
    # flat = Flatten()(cnn3)
    # drop = Dropout(0.5)(flat)
    fc = Dense(256)(rl)
    drop = Dropout(0.5)(fc)
    main_output = Dense(7, activation='softmax')(drop)
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
    X_train, X_train_label = x_train_padded_seqs[tr_ind], np.array(labels[tr_ind])
    X_val, X_val_label = x_train_padded_seqs[te_ind], np.array(labels[te_ind])

    model = lstm_model()
    # model = load_model('model_weight.h5')
    # print(model.summary())
    # exit()

    model_save_path = './model/model_weight_lstm_{}.h5'.format(str(i))
    print(model_save_path)
    if i in [-1]:
        model=load_model(model_save_path)
        print(model.evaluate(X_val, X_val_label))
    else:
        model_checkpoint = ModelCheckpoint(model_save_path, save_best_only=True, save_weights_only=False)
        ear = EarlyStopping(monitor='val_loss', min_delta=0, patience=5, verbose=0, mode='min', baseline=None,
                            restore_best_weights=False)
        history = model.fit(X_train, X_train_label,
                            batch_size=32,
                            epochs=200,
                            validation_data=(X_val, X_val_label), callbacks=[tensorboard, ear,model_checkpoint])


    model = load_model(model_save_path)
    pred_val = model.predict(X_val)
    K.clear_session()

# with open("lstm_result.pkl", 'wb') as f:
#     pickle.dump(meta_train, f)
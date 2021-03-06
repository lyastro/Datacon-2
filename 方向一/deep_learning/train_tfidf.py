import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
import numpy  as np
from sklearn.metrics import accuracy_score

with open("dynamic_feature_train.csv.pkl", "rb") as f:
    labels = pickle.load(f)#train 类别
    files = pickle.load(f)#files 文件api

print("start tfidf...")
vectorizer = pickle.load(open('tfidf_transformer.pkl', 'rb'))
train_features = vectorizer.transform(files)
# vectorizer = TfidfVectorizer(ngram_range=(1, 5), min_df=3, max_df=0.9, )  # tf-idf特征抽取ngram_range=(1,5)，如果词的df超过某一阈值则被词表过滤
# train_features = vectorizer.fit_transform(files) #将文本中的词语转换为词频矩阵 ,先拟合数据再标准化
#
#
# tfidftransformer_path = 'tfidf_transformer.pkl'
# with open(tfidftransformer_path, 'wb') as fw:
#     pickle.dump(vectorizer, fw)

# meta_train = np.zeros(shape=(len(files), 7))

#StratifiedKFold 分层采样交叉切分，确保训练集，测试集中各类别样本的比例与原始数据集中相同
skf = StratifiedKFold(n_splits=10, random_state=4, shuffle=True)#5折
for i,(tr_ind, te_ind) in enumerate(skf.split(train_features, labels)):#5
    X_train, y_train = train_features[tr_ind], np.array(labels)[tr_ind]
    X_test, y_test = train_features[te_ind], np.array(labels)[te_ind]
    print('FOLD: {}'.format(str(i)))
    dtrain = xgb.DMatrix(X_train, y_train)
    dtest = xgb.DMatrix(X_test, y_test)

    print(np.shape(X_train))
    print(np.shape(X_test))
    param = {'max_depth': 6,# # 构建树的深度，越大越容易过拟合
             'eta': 0.1, #如同学习率
             'eval_metric': 'mlogloss',
             'silent': 1,##设置成1则没有运行信息输出，最好是设置为0.
             'objective': 'multi:softprob',
             'num_class': 2,#多分类类别数
             'subsample': 0.8,# 随机采样训练样本
             'colsample_bytree': 0.85}  # 生成树时进行的列采样

    # evallist = [(dtrain, 'train'), (dtest, 'eval')]  # 测试 , (dtrain, 'train')
    evallist = [(dtrain, 'train'), (dtest, 'val')]
    num_round = 300  # 循环次数
    bst = xgb.train(param, dtrain, num_round, evallist, early_stopping_rounds=100)#训练

    pred_val = bst.predict(dtest)
    # meta_train[te_ind] = pred_val
    predict_type_list=[]
    for l in pred_val:
        l_tmp=l.tolist()
        predict_type=l_tmp.index(max(l_tmp))
        predict_type_list.append(predict_type)

    # y_test=list(y_test)
    #
    # cnt1=0
    # cnt2=0
    # for t in range(0,len(predict_type_list)):
    #     if predict_type_list[t]==y_test[t]:
    #         cnt1+=1
    #     else:
    #         cnt2+=1
    #
    # print("Train Accuary: %.2f%%" % (100.0 * cnt1/(cnt1+cnt2) ))

    #保存模型
    bst.save_model('tfidf_'+str(i)+'.model')

#
# with open("tfidf_result.pkl", 'wb') as f:
#     pickle.dump(meta_train, f)


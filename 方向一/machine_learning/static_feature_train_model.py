# -*- coding: UTF-8 -*-

from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
from sklearn import metrics
import matplotlib.pyplot as plt
import numpy as np

def train_model_RF(X_train,y_train):
    srf = RF(n_estimators=500,oob_score = True, n_jobs=-1,random_state =42,bootstrap=True)
    #训练模型
    srf.fit(X_train,y_train)
    return srf


# def train_model_KNN(X_train, y_train):
#     knn = KNeighborsClassifier(n_neighbors=4)
#     # 定义一个knn分类器对象
#     knn.fit(X_train, y_train)
#     return knn

def train_model_DecisionTree(X_train, y_train):
    '''
    决策树分类器
    :param X_train:
    :param y_train:
    :return:
    '''
    dt = DecisionTreeClassifier(presort=True)
    dt.fit(X_train, y_train)
    return dt
#
def train_model_SVM(X_train, y_train):# clf = svm.SVC(C=0.8, kernel='rbf', gamma=20, decision_function_shape='ovr')
    sv = svm.SVC(C=0.8, kernel='rbf', gamma=20, decision_function_shape='ovr')
    sv.fit(X_train, y_train)
    return sv
#
#
def train_model_LR(X_train, y_train):
    lr = LogisticRegression()
    lr.fit(X_train, y_train)
    return lr


#ok
# # GBDT(Gradient Boosting Decision Tree) Classifier
def train_model_gradient_boosting_classifier(X_train, y_train):
    gbdt = GradientBoostingClassifier()
    gbdt.fit(X_train, y_train)
    return gbdt


def plot_confusion_matrix(cm, title='Confusion Matrix'):
    labels = [1,2,3,4,5,6,7]
    plt.imshow(cm, interpolation='nearest')
    plt.title(title)
    plt.colorbar()
    xlocations = np.array(range(len(labels)))
    plt.xticks(xlocations, labels, rotation=90)
    plt.yticks(xlocations, labels)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

def plot_matrix(name,y_test,y_pred):

    tick_marks = np.array(range(7)) + 0.5
    cm = confusion_matrix(y_test, y_pred)
    np.set_printoptions(precision=2)
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.figure(figsize=(12, 8), dpi=120)
    ind_array = np.arange(7)
    x, y = np.meshgrid(ind_array, ind_array)

    for x_val, y_val in zip(x.flatten(), y.flatten()):
        c = cm_normalized[y_val][x_val]
        if c > 0.01:
            plt.text(x_val, y_val, "%0.2f" % (c,), color='white', fontsize=7, va='center', ha='center')
    # offset the tick
    plt.gca().set_xticks(tick_marks, minor=True)
    plt.gca().set_yticks(tick_marks, minor=True)
    plt.gca().xaxis.set_ticks_position('none')
    plt.gca().yaxis.set_ticks_position('none')
    plt.grid(True, which='minor', linestyle='-')
    plt.gcf().subplots_adjust(bottom=0.15)

    plot_confusion_matrix(cm_normalized, title='Normalized confusion matrix')
    # show confusion matrix
    plt.savefig('./result/' + name +'_confusion_matrix.png', format='jpeg')
    plt.show()




if __name__ == "__main__":

        '''
        opcode_train
        '''
        # subtrainLabel = pd.read_csv('static_trainLabels.csv')
        # subtrainfeature = pd.read_csv("4gramfeature.csv")
        # subtrain = pd.merge(subtrainLabel, subtrainfeature, on='Id')
        # labels = subtrain.Class
        # subtrain.drop(["Class", "Id"], axis=1, inplace=True)  # 不管空值与否删除Class、Id列，直接在内存中生效
        # subtrain = subtrain.as_matrix()  # 将表格转换为矩阵


        '''
        PE_header_train
        '''
        # subtrain = pd.read_csv('PE_header_feature.csv')
        # labels = subtrain.Class
        # subtrain.drop(["Class", "Id"], axis=1, inplace=True)  # 不管空值与否删除Class、Id列，直接在内存中生效
        # subtrain = subtrain.as_matrix()  # 将表格转换为矩阵

        '''
        two_feature_ensemble
        '''

        subtrainLabel = pd.read_csv('static_trainLabels.csv')
        subtrain_opcode_feature = pd.read_csv("4gramfeature.csv")
        subtrain_tmp = pd.merge(subtrainLabel, subtrain_opcode_feature, on='Id')
        subtrain_header_feature = pd.read_csv("PE_header_feature_for_mix.csv")
        subtrain = pd.merge(subtrain_tmp, subtrain_header_feature, on='Id')
        subtrain.to_csv("static_feature_for_mix.csv", index=False, sep=',')

        labels = subtrain.Class
        subtrain.drop(["Class", "Id"], axis=1, inplace=True)  # 不管空值与否删除Class、Id列，直接在内存中生效
        subtrain = subtrain.as_matrix()  # 将表格转换为矩阵

        X_train, X_test, y_train, y_test = train_test_split(subtrain, labels, test_size=0.2)


        #1、逻辑回归
        print('LogisticRegression: \r')
        lr_model=train_model_LR(X_train, y_train)
        joblib.dump(lr_model, 'mix_lr_model.pkl')
        # score = lr_model.score(X_test, y_test, sample_weight=None)
        # print(score)
        y_pred=lr_model.predict(X_test)

        # #准确率
        # accuracy=metrics.accuracy_score(y_test, y_pred)
        # print("准确率： "+ str(accuracy))
        # #精确率
        # precision=metrics.precision_score(y_test, y_pred, average='macro')
        # print("精确率： "+ str(precision))
        # #召回率
        # recall=metrics.recall_score(y_test, y_pred, average='macro')
        # print("召回率： "+ str(recall))
        # #F1-score
        # f1=metrics.f1_score(y_test, y_pred, average='weighted')
        # print("F1-score： " + str(f1))
        #混淆矩阵
        plot_matrix("mix_lr_model", y_test, y_pred)
        # lr_model = joblib.load('lr_model.pkl')
        # score = lr_model.score(X_test, y_test)
        # print(score)



        #2、梯度提升树
        print('GBDT: \r')
        gbc_model=train_model_gradient_boosting_classifier(X_train, y_train)
        joblib.dump(gbc_model, 'mix_gbc_model.pkl')
        # score = gbc_model.score(X_test, y_test)
        # print(score)
        # gbc_model = joblib.load('gbc_model.pkl')
        # score = gbc_model.score(X_test, y_test)
        # print(score)
        y_pred = gbc_model.predict(X_test)

        # # 准确率
        # accuracy = metrics.accuracy_score(y_test, y_pred)
        # print("准确率： " + str(accuracy))
        # # 精确率
        # precision = metrics.precision_score(y_test, y_pred, average='macro')
        # print("精确率： " + str(precision))
        # # 召回率
        # recall = metrics.recall_score(y_test, y_pred, average='macro')
        # print("召回率： " + str(recall))
        # # F1-score
        # f1 = metrics.f1_score(y_test, y_pred, average='weighted')
        # print("F1-score： " + str(f1))
        #混淆矩阵
        plot_matrix("mix_gbc_model", y_test, y_pred)

        #3、支持向量机
        print('SVM: \r')
        svm_model=train_model_SVM(X_train, y_train)
        joblib.dump(svm_model, 'mix_svm_model.pkl')
        # score = svm_model.score(X_test, y_test)
        # print(score)
        # svm_model = joblib.load('svm_model.pkl')
        # score = svm_model.score(X_test, y_test)
        # print(score)
        y_pred = svm_model.predict(X_test)

        # # 准确率
        # accuracy = metrics.accuracy_score(y_test, y_pred)
        # print("准确率： " + str(accuracy))
        # # 精确率
        # precision = metrics.precision_score(y_test, y_pred, average='macro')
        # print("精确率： " + str(precision))
        # # 召回率
        # recall = metrics.recall_score(y_test, y_pred, average='macro')
        # print("召回率： " + str(recall))
        # # F1-score
        # f1 = metrics.f1_score(y_test, y_pred, average='weighted')
        # print("F1-score： " + str(f1))
        # 混淆矩阵
        plot_matrix("mix_svm_model", y_test, y_pred)

        #4、决策树
        print('Decision Tree: \r')
        dt_model=train_model_DecisionTree(X_train, y_train)
        joblib.dump(dt_model, 'mix_dt_model.pkl')
        # score = dt_model.score(X_test, y_test)
        # print(score)
        # dt_model = joblib.load('dt_model.pkl')
        # score = dt_model.score(X_test, y_test)
        # print(score)
        y_pred = dt_model.predict(X_test)

        # # 准确率
        # accuracy = metrics.accuracy_score(y_test, y_pred)
        # print("准确率： " + str(accuracy))
        # # 精确率
        # precision = metrics.precision_score(y_test, y_pred, average='macro')
        # print("精确率： " + str(precision))
        # # 召回率
        # recall = metrics.recall_score(y_test, y_pred, average='macro')
        # print("召回率： " + str(recall))
        # # F1-score
        # f1 = metrics.f1_score(y_test, y_pred, average='weighted')
        # print("F1-score： " + str(f1))
        # 混淆矩阵
        plot_matrix("mix_dt_model", y_test, y_pred)

        #5、随机森林
        print('Random Forest: \r')
        rf_model=train_model_RF(X_train, y_train)
        joblib.dump(rf_model, 'mix_rf_model.pkl')
        # score=rf_model.score(X_test, y_test)
        # print(score)
        # rf_model = joblib.load('rf_model.pkl')
        # score = rf_model.score(X_test, y_test)
        # print(score)
        y_pred = rf_model.predict(X_test)

        # # 准确率
        # accuracy = metrics.accuracy_score(y_test, y_pred)
        # print("准确率： " + str(accuracy))
        # # 精确率
        # precision = metrics.precision_score(y_test, y_pred, average='macro')
        # print("精确率： " + str(precision))
        # # 召回率
        # recall = metrics.recall_score(y_test, y_pred, average='macro')
        # print("召回率： " + str(recall))
        # # F1-score
        # f1 = metrics.f1_score(y_test, y_pred, average='weighted')
        # print("F1-score： " + str(f1))
        # 混淆矩阵
        plot_matrix("mix_rf_model", y_test, y_pred)



#评估模型准确率
# print(srf.score(X_test,y_test))

# y_pred = srf.predict(X_test)

# print confusion_matrix(y_test, y_pred)

#测试
import numpy as np
import random
from sklearn.svm import SVC
from sklearn.grid_search import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import KFold
from sklearn.externals import joblib
import matplotlib.pyplot as plt

scaler = StandardScaler() 

def gen_classifier(X, y):
    #scaler.fit_transform(X)
    clf = KNeighborsClassifier(n_neighbors=1, weights='distance')
    clf.fit(X, y)
    #joblib.dump(clf, filename)
    return clf

def main(datas, labels):
    global scaler
    # datas, labels = loadFile('data/data3.txt')
    
    scaler.fit_transform(datas)

    for i in range(len(datas)):
        #datas[i] = datas[i][1000:-300]
        for j in range(1050, 1700, 50):
            datas.append(np.absolute(np.fft.fft(datas[i][j:j+50])))
            labels.append(labels[i])
        datas[i] = np.absolute(np.fft.fft(datas[i][1000:1050]))

        #datas[i] = np.absolute(np.fft.fft( datas[i] ))
    datas = np.array(datas)
    labels = np.array(labels)

    kf = KFold(len(labels), n_folds=5)
    for train, test in kf:
        neigh = KNeighborsClassifier(n_neighbors=1, weights='distance')
        neigh.fit(datas[train], labels[train])
        #print neigh.predict(datas[test])
        #print labels[test]
        print neigh.score(datas[test], labels[test])


if __name__ == '__main__':
    main()

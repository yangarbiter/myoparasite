import numpy as np
from itertools import combinations
from sklearn.preprocessing import MinMaxScaler
from sklearn.grid_search import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
import sklearn.svm.libsvm
from sklearn.svm import SVC

import random
import threading

NUM_OF_LABELS = 4
WINDOW_SIZE = 500
WINDOW_SHIFT_TRAIN = 50
WINDOW_SHIFT_TEST = 50

def data_of_two_labels(data, ans, y1, y2):
    tmp = []
    tmpa = []
    for i in range(len(data)):
        if ans[i] != y1 and ans[i] != y2:
            continue
        tmp.append(data[i])
        tmpa.append(ans[i])
    return tmp, tmpa

class SVM_train_thread(threading.Thread):
    def __init__(self, data, ans, clf, labels):
        super(SVM_train_thread, self).__init__()
        self.data = data
        self.ans = ans
        self.clf = clf
        self.label = labels
    def run(self):
        self.clf.fit( self.data, self.ans )

def gen_model(train_data, train_ans, verbose=True):
    scalers = []
    classifiers = []
    scores = []
    threads = []
    tuned_parameters = [
            {'kernel': ['rbf'], 'gamma': [], 'C': []},
        ]
    now = 1.0
    while now > 0.001:
        tuned_parameters[0]['gamma'].append(now)
        if now >= 1:
            tuned_parameters[0]['C'].append(now) 
        now /= 2;

    for i in combinations(range(NUM_OF_LABELS), 2):
        data, ans = data_of_two_labels(train_data, train_ans, i[0], i[1])
        data = np.array(data)

        tmp = zip(data, ans)
        random.shuffle(tmp)
        data, ans = zip(*tmp)
        
        scalers.append( MinMaxScaler(feature_range=(-1,1)) )
        #scalers.append( StandardScaler() )
        data = scalers[-1].fit_transform( data )
        clf = GridSearchCV( SVC(), tuned_parameters, cv=5, refit=True )
        threads.append( SVM_train_thread(data, ans, clf, i) )
        threads[-1].start()

    for t in threads:
        t.join()
        classifiers.append( t.clf.best_estimator_ )
        scores.append(t.clf.best_score_)
        if verbose:
            print(t.label, t.clf.best_params_, t.clf.best_score_)

    scores = [1] * NUM_OF_LABELS
    return scalers, classifiers, scores


def multi_classification(datas, scalers, clfs, scores):
    predictions = []
    ret = []
    j = 0
    for i in combinations(range(NUM_OF_LABELS), 2):
        predictions.append(clfs[j].predict(scalers[j].transform(np.array(datas))))
        j += 1
    predictions = np.array(predictions).T
    #print predictions
    for i in predictions:
        label_score = [0.0] * NUM_OF_LABELS
        for j in i:
            label_score[j] += scores[j]
        #print label_score
        ret.append(label_score.index(max(label_score)))
    return ret

def main():
    import json
    with open("data/rawdata_0_2_4_serial", "r") as f:
        y, X1, X2 = zip(*json.loads(f.readline()))

    testX1 = np.array(X1[-3 * NUM_OF_LABELS:]).reshape(1, -1)[0]
    testX2 = np.array(X2[-3 * NUM_OF_LABELS:]).reshape(1, -1)[0]
    testy = y[-3 * NUM_OF_LABELS:]
    X1 = X1[:-3 * NUM_OF_LABELS]
    X2 = X2[:-3 * NUM_OF_LABELS]
    y = y[:-3 * NUM_OF_LABELS]
    X = []
    y_2 = []

    print len(testX1)
    for yi, x1, x2 in zip(y, X1, X2):
        for i in range(700, 1300, WINDOW_SHIFT_TRAIN):
            X.append( np.concatenate(( 
                    np.absolute(np.fft.fft(x1[i: i+WINDOW_SIZE])) , 
                    np.absolute(np.fft.fft(x2[i: i+WINDOW_SIZE])) ) ).tolist())
            y_2.append( yi )

    y = y_2
    scalers, classifiers, scores = gen_model(X, y)

    print testy
    ans = []
    for i in range(0, len(testX1)-WINDOW_SIZE, WINDOW_SHIFT_TEST):
        x = np.concatenate(( 
                np.absolute(np.fft.fft(testX1[i: i+WINDOW_SIZE])) , 
                np.absolute(np.fft.fft(testX2[i: i+WINDOW_SIZE])) ) ).tolist()
        ans.append( multi_classification(x, scalers, classifiers, scores)[0] )

    ans += [0] * (WINDOW_SIZE / WINDOW_SHIFT_TEST)
    for i in np.array(ans).reshape(-1,40).tolist():
        print i

if __name__ == '__main__':
    main()

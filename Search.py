import porter
# import this to calculate log
import math
# import this to remove punctuations
import string
# import this to get the address of the program
import os
# import this to get what users' entered and exit the system
import sys

# get the current address of the program
path = os.path.abspath(os.path.dirname(__file__))

# set the value of k and b
K = 1
B = 0.75

stemming = porter.PorterStemmer()


# The method to remove punctuations
def removePunctuation(text):
    result = ''.join(pun for pun in text if pun not in string.punctuation)
    return result


# get the location of the documents
doc_path = path + '\\documents'
docs = os.listdir(doc_path)

# create dictionaries
# dict for frequency
f_dict = {}
#dict for n
n_dict = {}
# dict for length
len_dict = {}
# record doc id
docid_list = []

# calculate total length to get avg_len
total_len = 0
num = 0

index_path = path + '\\index_dict.txt'

# Load stopwords
stopwords = set()
with open(path + '\\files\stopwords.txt', 'r') as f:
    for line in f:
        stopwords.add(line.rstrip())

if not os.path.exists(index_path):
    for doc in docs:
        with open(doc_path + '\\' + doc, 'r', encoding='utf-8') as f:
            # docid_list.append(str(doc))
            doc_len = 0
            doc_dict = {}
            for line in f:
                line = removePunctuation(line)
                words = line.split()
                for word in words:
                    if word not in stopwords:
                        doc_len += 1
                        total_len += 1
                        term = stemming.stem(word)
                        if term not in doc_dict:
                            doc_dict[term] = 1
                            if term not in n_dict:
                                n_dict[term] = 1
                            else:
                                n_dict[term] += 1
                        else:
                            doc_dict[term] += 1
        f_dict[doc] = doc_dict
        len_dict[doc] = doc_len
        num += 1

    # write the indexes into a text file
    with open(index_path, 'w+', encoding = 'utf-8') as f:
        avg_len = int(total_len / num)
        for doc in f_dict:
            f.write(doc + ' ')
            length = len_dict[doc]
            for k, v in f_dict[doc].items():
                bm25 = 0
                n = n_dict[k]
                bm25 = (int(v) * (1 + int(K)) / (
                                int(v) + int(K) * ((1 - float(B)) + float(B) * int(length) / int(avg_len)))) * math.log2((int(num) - int(n) + 0.5) / (int(n) + 0.5))
                f.write(k + ': ' + str(bm25) + ' ')
            f.write('\n')

def getResult(q_dict):
    with open(index_path, 'r', encoding='utf-8') as f:
        bm25 = {}
        for line in f:
            items = line.split()
            fid = items[0]
            result = 0
            for k, v in q_dict.items():
                index = 1
                while index < len(items):
                    if items[index] == ( k + ':' ):
                        result += v * float(items[index + 1])
                        index += 2
                        break
                    else:
                        index += 2
            bm25[fid] = result
    return bm25



# manual mode
if sys.argv[2] == "manual":
    while True:
        Query = input("Please enter a query. Or enter 'QUIT' to exit the system. \n")
        q_dict = {}
        bm25_dict = {}

        if Query == "QUIT":
            sys.exit(0)

        else:
            print("Loading...")
            Query = removePunctuation(Query)
            words = Query.split()
            for word in words:
                if word not in stopwords:
                    term = stemming.stem(word)
                    if term not in q_dict:
                        q_dict[term] = 1
                    else:
                        q_dict[term] += 1


            bm25_dict = getResult(q_dict)

            print("No\t Docid\t Score\t")

            i = 1
            # for docid in BM25:
            sorted_keys = sorted(bm25_dict.items(), key=lambda x: x[1], reverse=True)
            for k, v in sorted_keys:
                if i < 16:
                    print(i, ' \t', k, ' \t', v, ' \t')
                    i += 1
                else:
                    break

# evaluation mode
elif sys.argv[2] == "evaluation":
    print("Loading...")
    start = 1
    bm25 = {}
    if not os.path.exists(path + '\\output.txt'):
        with open(path+'\\files\queries.txt', 'r',  encoding='utf-8') as f:
            for line in f:
                line = removePunctuation(line)
                items = line.split()
                qid = items[0]
                q_dict = {}
                for item in items[1:]:
                    if item not in stopwords:
                        term = stemming.stem(item)
                        if term not in q_dict:
                            q_dict[term] = 1
                        else:
                            q_dict[term] += 1

                bm25[qid] = getResult(q_dict)
                print(qid)

        with open(path + '\\output.txt', 'w+', encoding='utf-8') as f:
            for qid in bm25:
                sortedkeys = sorted(bm25[qid].items(), key=lambda x: x[1], reverse=True)
                i = 1
                for k, v in sortedkeys:
                    if not v == 0:
                        f.write(
                            str(qid) + '\t' + 'Q0' + '\t' + str(k) + '\t' + str(i) + '\t' + str(v) + '\t' + '18206369' + '\n')
                        i += 1


    print("Please see the result in the output.txt.")

with open(path + '\\files\qrels.txt', 'r', encoding='utf-8') as f:
    rel = {}
    set = []
    is_first = 1
    for line in f:
        items = line.split()
        qid = items[0]
        rele = items[2]
        if is_first == 1:
            former_qid = qid
            is_first = 0
        if former_qid == qid:
            set.append(rele)
        else:
            rel[former_qid] = set
            set = []
            set.append(rele)
            former_qid = qid

with open(path + '\\output.txt', 'r', encoding='utf-8') as f:
    ret = {}
    set = []
    is_first = 1
    for line in f:
        items = line.split()
        qid = items[0]
        rele = items[2]
        if is_first == 1:
            former_qid = qid
            is_first = 0
        if former_qid == qid:
            set.append(rele)
        else:
            ret[former_qid] = set
            set = []
            set.append(rele)
            former_qid = qid


# Precision
# Recall
# P@10
# R-precision
# MAP
# bpref
qnum = 0
pat10 = 0
rpre = 0
bpre = 0
precision = 0
recall = 0
ap = 0

for qid in ret:
    ret_num = len(ret[qid])
    rel_num = len(rel[qid])
    relret_num = 0
    index = 0
    bprefer = 0
    while index < len(ret[qid]):
        if ret[qid][index] in rel[qid]:
            relret_num += 1
            ap += relret_num / (index + 1)
            if (index + 1 - relret_num < rel_num):
                bprefer += 1 - (index + 1 - relret_num) / rel_num
        # p @ 10
        if index == 9:
            pat10 += (relret_num / 10)

        # R - precision
        if index == (rel_num - 1):
            rpre += (relret_num / rel_num)

        index += 1

    qnum += 1

    precision += relret_num / ret_num
    recall += relret_num / rel_num
    ap = ap / rel_num
    bpre += bprefer / rel_num

print("Precision: \t" + str(precision / qnum))
print("Recall: \t" + str(recall / qnum))
print("P @ 10: \t" + str(pat10 / qnum))
print("R-precision: \t" + str(rpre / qnum))
print("MAP: \t" + str(ap / qnum))
print("bpref: \t" + str(bpre / qnum))

sys.exit(0)
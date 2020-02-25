import nltk
from nltk.corpus import gutenberg
from nltk.corpus import brown
from nltk.corpus import stopwords

# from nltk.tokenize import word_tokenize

nltk.download('brown')
nltk.download('gutenberg')


class Preprocess:
    stemmer = nltk.PorterStemmer()
    stop_words = set(stopwords.words('english'))

    def remove_stopwords(self, list):
        return [word for word in list if word not in self.stop_words]

    def clean(self, string):
        string = string.replace(".", "")
        string = string.replace("\s+", " ")
        string = string.lower()
        return string

    def tokenise(self, string):
        string = self.clean(string)
        words = string.split(" ")
        return [self.stemmer.stem(word) for word in words]

    def prep(self, document):
        clean_text = self.clean(document['text'])
        all_terms = self.tokenise(clean_text)
        return self.remove_stopwords(all_terms)


class Appearance:

    def __init__(self, docId, frequency):
        self.docId = docId
        self.frequency = frequency

    def __repr__(self):
        return str(self.__dict__)


class Database:

    def __init__(self):
        self.db = dict()

    def __repr__(self):
        return str(self.__dict__)

    def get(self, id):
        return self.db.get(id, None)

    def add(self, document):
        return self.db.update({document['id']: document})

    def remove(self, document):
        return self.db.pop(document['id'], None)


class InvertedIndex:
    """
    Inverted Index class.
    """

    def __init__(self, db):
        self.index = dict()
        self.db = db

    def __repr__(self):
        return str(self.index)

    def index_document(self, document):
        preproc = Preprocess()

        # clean_text = main.clean(document['text'])
        # all_terms = main.tokenise(clean_text)
        # terms = main.remove_stopwords(all_terms)

        terms = preproc.prep(document)
        appearances_dict = dict()

        for term in terms:
            term_frequency = appearances_dict[term].frequency if term in appearances_dict else 0
            appearances_dict[term] = Appearance(document['id'], term_frequency + 1)

        update_dict = {key: [appearance]
        if key not in self.index
        else self.index[key] + [appearance]
                       for (key, appearance) in appearances_dict.items()}
        self.index.update(update_dict)

        self.db.add(document)
        return document

    def lookup_query(self, query):
        """
        Returns the dictionary of terms with their correspondent Appearances.
        This is a very naive search since it will just split the terms and show
        the documents where they appear.
        """
        return {term: self.index[term] for term in query.split(' ') if term in self.index}

    def lookup_vect(self,query):
        list= {term: self.index[term] for term in query.split(' ') if term in self.index}



class Vectorize:
    def getVectorKeywordIndex(self, wordList):
        vectorIndex = {}
        offset = 0
        # Associate a position with the keywords which maps to the dimension on the vector used to represent this word
        for word in wordList:
            vectorIndex[word] = offset
            offset += 1
        return vectorIndex

    def makeVector(self, vectorIndex, document):
        """ @pre: unique(vectorIndex) """
        # Initialise vector with 0's
        vector = [0] * len(vectorIndex)
        preproc = Preprocess()
        wordList = preproc.prep(document)
        for word in wordList:
            vector[word] += 1;  # Use simple Term Count Model
        return vector


def highlight_term(id, term, text):
    replaced_text = text.replace(term, "\033[1;32;40m {term} \033[0;0m".format(term=term))
    return "--- document {id}: {replaced}".format(id=id, replaced=replaced_text)


def Main():
    db = Database()
    index = InvertedIndex(db)
    brown_list = brown.fileids()
    gutenberg_list = gutenberg.fileids()
    # document1 = {
    #     'id': '1',
    #     'text': 'The big sharks of Belgium drink beer.'
    # }
    # document2 = {
    #     'id': '2',
    #     'text': 'Belgium has great beer. They drink beer all the time.'
    # }
    i = 0;
    for item in brown_list:
        documentTemp = {
            'id': str(i),
            'text': brown.raw(item)
        }
        index.index_document(documentTemp)

    for item in gutenberg_list:
        documentTemp = {
            'id': str(i),
            'text': gutenberg.raw(item)
        }
        index.index_document(documentTemp)

    while True:
        search_term = input("Enter term(s) to search: ")
        result = index.lookup_query(search_term.lower())
        for term in result.keys():
            for appearance in result[term]:
                # Belgium: { docId: 1, frequency: 1}
                document = db.get(appearance.docId)
                print(highlight_term(appearance.docId, term, document['text']))
            print("-----------------------------")


Main()

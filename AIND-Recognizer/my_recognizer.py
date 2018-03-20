import warnings
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    
        
       
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    for word_id in range(len(test_set.wordlist)):
        wordProbabilities = {}
        testX , testLength = test_set.get_item_Xlengths(word_id)
        for key in models.keys():
            logL = None
            try:
                if models[key] == None:
                    logL = float("-inf")
                else:
                    logL = models[key].score(testX, testLength)
            except ValueError as e:
                logL = float("-inf")
                
            wordProbabilities[key] = logL
        probabilities.append(wordProbabilities)
        
    guesses = [max(i, key= i.get ) for i in probabilities]
    # TODO implement the recognizer
    return probabilities, guesses


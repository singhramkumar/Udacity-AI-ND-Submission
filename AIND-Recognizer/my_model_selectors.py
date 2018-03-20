import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Baysian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components
        
        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        bestBic = float("inf")
        bestModel = None
        for numStates in range(self.min_n_components , self.max_n_components + 1):
            try:
                model = GaussianHMM(n_components=numStates, covariance_type="diag", n_iter=1000,
                                        random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
                
                #try:
                logL = model.score(self.X, self.lengths)
                #except ValueError as e:
                    #print("error occured : " + str(e))
                
                InitialStateOccupationProbabilities = numStates
                TransitionProbabilities = numStates*(numStates - 1)
                EmissionProbabilities = numStates*len(self.X[0])*2
                Parameters = InitialStateOccupationProbabilities + TransitionProbabilities + EmissionProbabilities
                
                bic = (-2) * logL + Parameters * math.log(len(self.X))
                
                if bic < bestBic:
                    bestBic = bic
                    bestModel = model
            except ValueError as e:
                #print("Error Occured :" + str(e))
                continue
        return bestModel
        
       

        # TODO implement model selection based on BIC scores
       


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        
        # TODO implement model selection based on DIC scores
        allWords =  self.words.keys()
                
        bestDic = float("-inf")
        bestModel = None
        calculatedProbability = {}
        
        for numStates in range(self.min_n_components , self.max_n_components + 1):
            try:
            
                allNonLikeliyhoodProb = []
                
                model = GaussianHMM(n_components=numStates, covariance_type="diag", n_iter=1000,
                                        random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
                try:
                    
                    logL = model.score(self.X, self.lengths)
                    calculatedProbability[self.this_word +  str(numStates)] = logL
                    
                except ValueError as e:
                    #print("An error occured :" + str(e))
                    continue
                
                for word in allWords:
                    try:
                        if word != self.this_word:
                            key = word + str(numStates)
                            if key in calculatedProbability.keys():
                                allNonLikeliyhoodProb.append(calculatedProbability[key])
                            else:
                                otherX, otherLengths = self.hwords[word]
                                otherModel = GaussianHMM(n_components=numStates, covariance_type="diag", n_iter=1000,
                                                random_state=self.random_state, verbose=False).fit(otherX, otherLengths)
                                otherLogL = otherModel.score(self.X, self.lengths)
                                calculatedProbability[key] = otherLogL
                                allNonLikeliyhoodProb.append(otherLogL)   
                    except ValueError as e:
                        #print("Error occured for other word")
                        continue
                
                dic =  logL - np.mean(allNonLikeliyhoodProb)
                
                if dic > bestDic:
                    bestDic = dic
                    bestModel = model
            except ValueError as e:
                #print("Error Occured :" + str(e))
                continue
                
        return bestModel      
        


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        
        if len(self.lengths) <=1:
            return None
        
        split_method = KFold(n_splits=min(3,len(self.lengths)))
        bestAvgLogL = float("-inf")
        bestNumState = None
        for numStates in range(self.min_n_components , self.max_n_components + 1):
            try:
                logLScore = []
                for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                    train_sequence_X, train_sequence_lengths = combine_sequences(cv_train_idx, self.sequences)
                    test_sequence_X, test_sequence_lengths = combine_sequences(cv_test_idx,self.sequences)
                    
                    model = GaussianHMM(n_components=numStates, covariance_type="diag", n_iter=1000,
                                        random_state=self.random_state, verbose=False).fit(train_sequence_X, train_sequence_lengths)
                    
                    #try:
                    logL = model.score(test_sequence_X, test_sequence_lengths)
                    logLScore.append(logL)
                    #except ValueError as e:
                        #print("An error occured :" + str(e))
                
                if np.mean(logLScore) > bestAvgLogL:
                    bestAvgLogL = np.mean(logLScore)
                    bestNumState = numStates
                    
            except ValueError as e:
                #print("Error Occured :" + str(e))
                continue
        
        return self.base_model(bestNumState)


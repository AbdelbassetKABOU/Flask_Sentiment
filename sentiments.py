
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random

def get_score_v1(sentence):
    number = random.uniform(-1, 1)
    print("random = {}".format(random))
    return number



def get_score_v2(sentence):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(sentence)
    return vs

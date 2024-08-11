from boto3.dynamodb.conditions import Key
from flask import Flask, render_template, request
import boto3
import re
import string 

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('tfidf')

stopwords_set = set(["a", "as", "able", "about", "above", "according", "accordingly",
       "across", "actually", "after", "afterwards", "again", "against", "aint", "all", "allow",
       "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among",
       "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway",
       "anyways", "anywhere", "apart", "appear","appreciate", "appropriate", "are", "arent", "around",
       "as", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "be", "became",
       "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below",
       "beside", "besides", "best", "better", "between", "beyond", "both", "brief", "but", "by", "cmon",
       "cs", "came", "can", "cant", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes",
       "clearly", "co", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing",
       "contains", "corresponding", "could", "couldnt", "course", "currently", "definitely", "described", "despite", "did", "didnt",
       "different", "do", "does", "doesnt", "doing", "dont", "done", "down", "downwards", "during", "each",
       "edu", "eg", "eight", "either", "else", "elsewhere", "enough", "entirely", "especially", "et", "etc",
       "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except",
       "far", "few", "ff", "fifth", "first", "five", "followed", "following", "follows", "for", "former",
       "formerly", "forth", "four", "from", "further", "furthermore", "get", "gets", "getting", "given", "gives",
       "go", "goes", "going", "gone", "got", "gotten", "greetings", "had", "hadnt", "happens", "hardly",
       "has", "hasnt", "have", "havent", "having", "he", "hes", "hello", "help", "hence", "her",
       "here", "heres", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him", "himself",
       "his", "hither", "hopefully", "how", "howbeit", "however", "i", "id", "ill", "im", "ive",
       "ie", "if", "ignored", "immediate", "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates",
       "inner", "insofar", "instead", "into", "inward", "is", "isnt", "it", "itd", "itll", "its",
       "its", "itself", "just", "keep", "keeps", "kept", "know", "knows", "known", "last", "lately",
       "later", "latter", "latterly", "least", "less", "lest", "let", "lets", "like", "liked", "likely",
       "little", "look", "looking", "looks", "ltd", "mainly", "many", "may", "maybe", "me", "mean",
       "meanwhile", "merely", "might", "more", "moreover", "most", "mostly", "much", "must", "my", "myself",
       "name", "namely", "nd", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless",
       "new", "next", "nine", "no", "nobody", "non", "none", "noone", "nor", "normally", "not",
       "nothing", "novel", "now", "nowhere", "obviously", "of", "off", "often", "oh", "ok", "okay",
       "old", "on", "once", "one", "ones", "only", "onto", "or", "other", "others", "otherwise",
       "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", "particular", "particularly",
       "per", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provides", "que", "quite",
       "qv", "rather", "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively",
       "right", "said", "same", "saw", "say", "saying", "says", "second", "secondly", "see", "seeing",
       "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously",
       "seven", "several", "shall", "she", "should", "shouldnt", "since", "six", "so", "some", "somebody",
       "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify",
       "specifying", "still", "sub", "such", "sup", "sure", "ts", "take", "taken", "tell", "tends",
       "th", "than", "thank", "thanks", "thanx", "that", "thats", "thats", "the", "their", "theirs",
       "them", "themselves", "then", "thence", "there", "theres", "thereafter", "thereby", "therefore", "therein", "theres",
       "thereupon", "these", "they", "theyd", "theyll", "theyre", "theyve", "think", "third", "this", "thorough",
       "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too",
       "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "twice", "two", "un",
       "under", "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", "used",
       "useful", "uses", "using", "usually", "value", "various", "very", "via", "viz", "vs", "want",
       "wants", "was", "wasnt", "way", "we", "wed", "well", "were", "weve", "welcome", "well",
       "went", "were", "werent", "what", "whats", "whatever", "when", "whence", "whenever", "where", "wheres",
       "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who",
       "whos", "whoever", "whole", "whom", "whose", "why", "will", "willing", "wish", "with", "within",
       "without", "wont", "wonder", "would", "would", "wouldnt", "yes", "yet", "you", "youd", "youll",
       "youre", "youve", "your", "yours", "yourself", "yourselves", "zero"])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    # Get input from the user
    user_input = request.form['user_input'].strip()
    # Remove punctuations from the text
    user_input = user_input.translate(str.maketrans('', '', string.punctuation))
    # Remove whitespaces and stopwords from the text
    terms = [term.lower() for term in re.findall('\w+', user_input) if term.lower() not in stopwords_set]

    # Calculate relevance score for each document
    docs = {}
    for term in terms:
        response = table.query(
            KeyConditionExpression=Key('term').eq(term)
        )
        for item in response['Items']:
            doc_id = item['doc_id']
            tfidf_value = item['tfidf_value']
            if doc_id not in docs:
                docs[doc_id] = 0
            docs[doc_id] += float(tfidf_value) / len(terms)

    # Sort documents by relevance score and return the top 5
    relevant_scores = []
    for doc_id, score in docs.items():
        relevance = score
        if relevance > 0:
            relevant_scores.append((doc_id, relevance))
    relevant_scores.sort(key=lambda x: x[1], reverse=True)
    most_relevant = relevant_scores[:5]

    if len(most_relevant) == 0:
        return render_template('index.html', error_message="No relevant documents found")
    else:
        columns = ["doc_id", "relevance score"]
        return render_template('index.html', columns=columns, relevant_docs=most_relevant)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5330, debug=True)
    
    #http://44.212.10.28:5330

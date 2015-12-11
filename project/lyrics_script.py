from project.store import *
from project.lyrics import *

# Read in data from known
adict = fread("known_data.pkl")

# Read in database
words, output = gen_database("mxm_dataset_train.txt")
output.update(gen_database("mxm_dataset_test.txt")[1])

# Figure out which songs have lyrics, and read them in
lyrics_songs = []
for a_name,artist in adict.iteritems():
	for s_name,song in artist.songs.iteritems():
		if song.from_database(output):
			lyrics_songs.append(song)

# We no longer need the database
del output

# Get the response variable and the list of IDs
full_response = np.array(fread('full_response.pkl'))
song_ids_list = fread('song_ids_list.pkl')

# Turn this into a dict for indexing
song_ids_dict = {song_ids_list[i]:i for i in xrange(len(song_ids_list))}

# Turn the lyrics into vector format (flatten out the song layer)
lyrics = []
for l in lyrics_songs:
	for i in l.id:
		if i in song_ids_dict:
			lyrics.append([i, full_response[song_ids_dict[i]], l.lyrics])

# Zip into IDs, Y, and X variables
ids, resp, lyrs_raw = zip(*lyrics)

# Flatten this array
lyrs = []
for l in lyrs_raw:
	if l.__class__ == list:
		lyrs.append(l[0])
	else:
		lyrs.append(l)

# Vectorize into a matrix
from sklearn.feature_extraction import DictVectorizer
v = DictVectorizer()
v_lyrics = v.fit_transform(lyrs)

# Make sure that we have a training and testing set
from sklearn.cross_validation import train_test_split
Xtrain, Xtest, ytrain, ytest = train_test_split(v_lyrics, resp, test_size=0.33)

# Train + Test on classifier
from sklearn.linear_model import Lasso
clf = Lasso(alpha=0.004)
clf.fit(Xtrain, ytrain)
y_resp = clf.predict(Xtest)

# Turn into vocab so we know the words
vocab = v.vocabulary_
to_word = {}
for i,w in enumerate(words):
	if i in vocab:
		to_word[vocab[i]] = w

# Use the classifier weights
weights = clf.coef_
word_weight = []
for i,w in enumerate(weights):
	word_weight.append((to_word[i], w))

word_weight = sorted(word_weight, key=lambda x: x[1])

# Get back into score form by ID
scores = {}
for i in xrange(len(ids)):
	ly = lyrs[i]
	score = 0
	for k,v in ly.iteritems():
		score += float(v)*weights[vocab[k]]
	scores[ids[i]] = score

# Sanity check to make sure that we have the correct numbers
in_100 = 0
not_in_100 = 0
for i in xrange(len(resp)):
	if resp[i]:
		in_100 += scores[ids[i]]
	else:
		not_in_100 += scores[ids[i]]

print in_100/np.sum(resp)
print not_in_100/(len(resp)-np.sum(resp))

# Output scores
fwrite(scores, "lyric_scores.pkl")
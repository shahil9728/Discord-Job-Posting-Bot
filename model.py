import spacy
from spacy.training import Example
import random
import pandas as pd
from sklearn.model_selection import train_test_split,GridSearchCV
# from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score,classification_report

file_path = './dataset.csv'  # Replace with the actual path to your dataset
df = pd.read_csv(file_path)

df = df.dropna()

X = df['Content']
Y = df['Status']

X_train, X_test, y_train, y_test = train_test_split(X,Y, test_size=0.3, random_state=45)

vectorizer = TfidfVectorizer(ngram_range=(2, 5))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)


lr = LogisticRegression(C=1,class_weight='balanced')
lr.fit(X_train_tfidf,y_train)

y_train_pred = lr.predict(X_train_tfidf)
y_test_pred = lr.predict(X_test_tfidf)

# pipeline = Pipeline([
#     ('tfidf', TfidfVectorizer()),
#     ('clf', LogisticRegression(class_weight='balanced'))
# ])

# param_grid = {
#     'tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)],
#     'clf__C': [0.1, 1, 10, 100]
# }

# grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, scoring='accuracy')
# grid_search.fit(X_train, y_train)

# print("Best Parameters:", grid_search.best_params_)
# print("Best Score:", grid_search.best_score_)
# grid_search.fit(X_train_tfidf, y_train)

# # Best parameters and score
# print("Best Parameters:", grid_search.best_params_)
# print("Best Score:", grid_search.best_score_)

# # Evaluate on test data
# best_model = grid_search.best_estimator_
# y_test_pred = best_model.predict(X_test_tfidf)
# print("Test Accuracy:", accuracy_score(y_test, y_test_pred))
# print("Classification Report:\n", classification_report(y_test, y_test_pred))


# print(X_train,X_test,y_train,y_test)

# Train the model
# Linear Regression model can only be used for number prediction not for the text based dataset.
# lr = LinearRegression()
# lr.fit(X_train, y_train)

# # Applying the model to make prediction 
# y_lr_train_pred = lr.predict(X_train)
# y_lr_test_pred = lr.predict(X_test)

# print(y_lr_train_pred, y_lr_test_pred)

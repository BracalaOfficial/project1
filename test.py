import requests

# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "qZBpbR5niKZ3OvjzdlHGQA", "isbns": "9781632168146"})
res = requests.get("https://www.goodreads.com/book/review_counts.json/api/080213825X")
# print(res.json()['books'][0]['ratings_count'])

print(res)

# if "":
#     print("True")

# else:
#     print("False")

# from flask import flash

# flash("Tvoju ribu sta resim")

# # print(get_flashed_messages(with_categories=True))
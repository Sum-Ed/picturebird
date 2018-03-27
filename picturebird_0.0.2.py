# -*- coding:utf-8 -*-

import sys
import time
import json
import requests
import requests_oauthlib

keys = {
	"ConsumerKey"		:"",
	"ConsumerSecret"	:""
	}

tokens = {
	"AccessTokenKey"	:"",
	"AccessTokenSecret"	:""
	}

# 除外ID
exclude_id = [
	""
	]

# 短縮URL展開関数
#def expandurl(shorturl):
#	return requests.get(shorturl).url

if __name__ == "__main__":
	print("picturebird ver.0.0.2")

	# Twitter API OAuth認証
	twapi = requests_oauthlib.OAuth1Session(
		keys["ConsumerKey"],
		keys["ConsumerSecret"],
		tokens["AccessTokenKey"],
		tokens["AccessTokenSecret"]
		)

	# Twitter APIパラメータ
	apiparams = {"count":"10"}
	since_id = 0

	while True:
		# タイムライン取得API
		resp = twapi.get("https://api.twitter.com/1.1/statuses/home_timeline.json", params=apiparams)

		# 200のみ処理
		if resp.status_code == 200:
			# JSONデータを読み込む
			tweets = json.loads(resp.text)

			# 古いツイートから処理
			for tweet in reversed(tweets):
				# 取得済みツイートを再取得しない
				if tweet["id"] > since_id:
					since_id = tweet["id"]
					apiparams = {"count":"200", "since_id":since_id}

				# 画像のURL
				media_urls = []

				# 画像が複数ある場合
				if "extended_entities" in tweet.keys():
					for media in tweet["extended_entities"]["media"]:
						media_urls.append(media["media_url_https"])

				# 画像が１枚の場合
				elif "media" in tweet["entities"].keys():
					media_urls.append(tweet["entities"]["media"][0]["media_url_https"])

				# 画像が無い場合
				else:
					continue

				# 除外ID以外のツイートのみ処理
				if tweet["user"]["screen_name"] not in exclude_id:
					# ふぁぼ数
					favorites = 0

					# RTツイートのふぁぼ数
					if "retweeted_status" in tweet.keys():
						favorites = tweet["retweeted_status"]["favorite_count"]

					# 本人ツイートのふぁぼ数
					else:
						favorites = tweet["favorite_count"]

					# 閾値以上でふぁぼ処理
					if favorites >= 5:
						# ふぁぼAPI
						resp = twapi.post("https://api.twitter.com/1.1/favorites/create.json?id=" + str(tweet["id"]))

						# 表示
						print("------------------------------- favorite REST API response status code :", resp.status_code)
						print("ID   >>", tweet["id"])
						print("Date >>", tweet["created_at"])
						print(tweet["user"]["name"], "@", tweet["user"]["screen_name"], "-", favorites, "favorites")
						print(tweet["text"])
						for media_url in media_urls:
							print("Media", media_url)

						# API制限回避
						time.sleep(20.0)

		# API制限制限回避
		print("> wait...")
		time.sleep(60.0)

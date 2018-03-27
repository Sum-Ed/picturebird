# -*- coding:utf-8 -*-

import sys
import time
import json
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

if __name__ == "__main__":
	print("picturebird ver.0.0.3")

	# Twitter API OAuth認証
	twapi = requests_oauthlib.OAuth1Session(
		keys["ConsumerKey"],
		keys["ConsumerSecret"],
		tokens["AccessTokenKey"],
		tokens["AccessTokenSecret"]
		)

	while True:
		# タイムライン取得API
		resp = twapi.get("https://api.twitter.com/1.1/statuses/home_timeline.json", params={"count":"200"})

		# 200のみ処理
		if resp.status_code == 200:
			# JSONデータを読み込む
			tweets = json.loads(resp.text)

			# 古いツイートから処理
			for tweet in reversed(tweets):
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

					# 未ふぁぼ＆閾値以上でふぁぼ処理
					if tweet["favorited"] is False and favorites >= 50:
						# API制限回避&人気評価待機
						time.sleep(20.0)

						# ふぁぼAPI
						resp = twapi.post("https://api.twitter.com/1.1/favorites/create.json?id=" + str(tweet["id"]))

						# 表示
						print("------------------------------- favorite REST API response status code :", resp.status_code)
						print(tweet["user"]["name"], "@", tweet["user"]["screen_name"])
						print(tweet["text"])

		# API制限回避
		print("> wait...")
		time.sleep(60.0)

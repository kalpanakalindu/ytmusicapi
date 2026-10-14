"""Vortify backend: a small read-only API on top of ytmusicapi (no login needed).

Deploy on Vercel as a Python serverless function (see README.md).
"""
import os
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from ytmusicapi import YTMusic

app = Flask(__name__)
yt = YTMusic(location=os.environ.get("YTM_LOCATION") or None)  # e.g. LK, US, GB


@app.after_request
def add_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = os.environ.get("ALLOW_ORIGIN", "*")
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    # let Vercel's CDN cache responses for 5 minutes, serve stale while refreshing
    resp.headers.setdefault("Cache-Control", "public, s-maxage=300, stale-while-revalidate=600")
    return resp


def need(name):
    v = request.args.get(name, "").strip()
    if not v:
        raise ValueError(f"missing query parameter: {name}")
    return v


@app.errorhandler(ValueError)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(HTTPException)  # keep real status codes (404 stays 404)
def http_error(e):
    return jsonify(error=e.description), e.code


@app.errorhandler(Exception)
def server_error(e):
    return jsonify(error=f"{type(e).__name__}: {e}"), 502


@app.get("/")
@app.get("/health")
def health():
    return jsonify(ok=True, endpoints=[
        "/search?q=&filter=songs|videos|albums|artists|playlists",
        "/suggest?q=", "/watch?videoId=", "/lyrics?videoId=", "/song?videoId=",
        "/artist?channelId=", "/album?browseId=", "/playlist?playlistId=",
        "/charts?country=LK", "/moods", "/mood?params=", "/home"])


@app.get("/search")
def search():
    flt = request.args.get("filter") or None
    return jsonify(yt.search(need("q"), filter=flt, limit=int(request.args.get("limit", 20))))


@app.get("/suggest")
def suggest():
    return jsonify(yt.get_search_suggestions(need("q")))


@app.get("/watch")  # "up next" / radio for a song
def watch():
    return jsonify(yt.get_watch_playlist(videoId=need("videoId"), limit=int(request.args.get("limit", 25))))


@app.get("/lyrics")
def lyrics():
    wp = yt.get_watch_playlist(videoId=need("videoId"))
    bid = wp.get("lyrics")
    if not bid:
        return jsonify(error="no lyrics for this track"), 404
    return jsonify(yt.get_lyrics(bid))


@app.get("/song")
def song():
    return jsonify(yt.get_song(need("videoId")))


@app.get("/artist")
def artist():
    return jsonify(yt.get_artist(need("channelId")))


@app.get("/album")
def album():
    return jsonify(yt.get_album(need("browseId")))


@app.get("/playlist")
def playlist():
    return jsonify(yt.get_playlist(need("playlistId"), limit=int(request.args.get("limit", 50))))


@app.get("/charts")
def charts():
    return jsonify(yt.get_charts(country=request.args.get("country", "ZZ")))


@app.get("/moods")
def moods():
    return jsonify(yt.get_mood_categories())


@app.get("/mood")
def mood():
    return jsonify(yt.get_mood_playlists(need("params")))


@app.get("/home")
def home():
    return jsonify(yt.get_home(limit=int(request.args.get("limit", 6))))


if __name__ == "__main__":  # local run: python api/index.py
    app.run(port=5000, debug=True)

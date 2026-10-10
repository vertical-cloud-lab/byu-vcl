import json, sys
sys.path.insert(0, "/home/runner/work/byu-vcl/byu-vcl")
from youtube.yt_service import get_youtube_service
yt = get_youtube_service("upload")
ch = yt.channels().list(part="snippet,contentDetails", mine=True).execute()["items"][0]
print("channel:", ch["snippet"]["title"], ch["id"])
uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
items, token = [], None
while True:
    r = yt.playlistItems().list(part="snippet,status", playlistId=uploads, maxResults=50, pageToken=token).execute()
    items += r["items"]
    token = r.get("nextPageToken")
    if not token: break
ids = [i["snippet"]["resourceId"]["videoId"] for i in items]
vids = []
for k in range(0, len(ids), 50):
    r = yt.videos().list(part="snippet,contentDetails,status", id=",".join(ids[k:k+50])).execute()
    vids += r["items"]
out = []
for v in vids:
    out.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                "duration": v["contentDetails"]["duration"], "privacy": v["status"]["privacyStatus"],
                "description": v["snippet"].get("description","")[:300]})
json.dump(out, open("/tmp/work/channel_videos.json","w"), indent=1)
for o in sorted(out, key=lambda x: x["published"]):
    print(o["published"][:16], o["privacy"][:3], o["duration"].ljust(10), o["id"], o["title"][:90])
print("total", len(out))

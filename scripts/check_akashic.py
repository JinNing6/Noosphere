import urllib.request
import json
try:
    resp = urllib.request.urlopen("https://pypi.org/pypi/akashic/json")
    data = json.loads(resp.read())
    info = data.get("info", {})
    print("Name:", info.get("name"))
    print("Version:", info.get("version"))
    print("Author:", info.get("author"))
    print("Summary:", info.get("summary"))
    print("Home Page:", info.get("home_page"))
    print("Project URLs:", info.get("project_urls"))
except Exception as e:
    print("Error:", e)

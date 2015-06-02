
import os
os.system("python stats.py > stats.html")
html = open("stats.html", "r").read()
html = html.replace("\n", "<br/>\n").replace(" ", "&nbsp;").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
html = "<html><head><title>stats</title><script>setTimeout(\"document.location = document.location;\", 70000);</script></head><body>"+html+"</body></html>"
if "Darwin" in os.popen("uname").read():
	open("stats.html", "w").write(html)
else:
	open("/home/rabshakeh/www/www_newsrivr_com/templates/stats.html", "w").write(html)
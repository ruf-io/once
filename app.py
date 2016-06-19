""" View Once -
		Description: POST <100kb of data, it gets saved in an encrypted file,
					 you get a URL that contains the file id and an encryption
					 key, requesting the url decrypts and deletes the file, returns
					 what you originally posted.
		Author: @andyhattemer
		License: MIT
"""
#!/usr/bin/env python
# -*- coding:utf-8 -*-

import web, json, yaml, os, random, base64, shortuuid
from Crypto.Cipher import AES

web.config.debug = False
app = web.application(('/(.{16}~.{16})?', 'App'), globals())

class App:
	def GET(self, content_key_secret_key):
		if content_key_secret_key:
			[content_key, secret_key] = content_key_secret_key.split('~')
			if os.path.isfile('/home/once/app/files/' + content_key):
				cipher = AES.new(secret_key, AES.MODE_ECB)
				f = open('/home/once/app/files/' + content_key)
				output = cipher.decrypt(base64.b64decode(f.read()))
				f.close()
				os.remove('/home/once/app/files/' + content_key)
				accept_header = web.ctx.env.get('HTTP_ACCEPT')
				if accept_header == None or accept_header.find('xhtml') == -1:
					web.header('Content-Type', 'text/plain')
					return output.lstrip()
				return '<html><body>' + output.lstrip() + '<br><br><form action="/" method="POST"><input type="hidden" name="content" value="' + output.lstrip() + '"><input type="submit" value="Re-Save with a new URL"></form></body></html>'
			else:
				raise web.seeother('/')
		return """<html><body><form action="/" method="POST">
			<fieldset style="float:left;">
				<textarea name="content0" rows="5" cols="80"></textarea><br><br>
				<textarea name="content1" rows="5" cols="80"></textarea><br><br>
				<textarea name="content2" rows="5" cols="80"></textarea><br><br>
				<textarea name="content3" rows="5" cols="80"></textarea><br><br>
				<textarea name="content4" rows="5" cols="80"></textarea>
			</fieldset>
			<input type="submit" style="float:left; font-size:4em;">
			</form></body></html>"""

	def POST(self, ignored):
		v = web.input()
		if 'content0' in v:
			output = "<html><body>REMEMBER THESE CAN ONLY BE LOADED ONCE!<br><table><tr><td>Content</td><td>URL</td></tr>"
			content = v['content0']
			ct = 0
			while len(content) > 0:
				try:
					content = json.dumps(json.loads(content))
				except:
					try:
						content = json.dumps(yaml.load(content))
						if content.find('"') == 0:
							content = content[1:-1]
					except:
						pass
				secret_key = shortuuid.ShortUUID().random(length=16)
				cipher = AES.new(secret_key, AES.MODE_ECB)
				content_key = shortuuid.ShortUUID().random(length=16)
				f = open('/home/once/app/files/' + content_key, 'w')
				content += ' ' * (16 - (len(content) % 16))
				f.write(base64.b64encode(cipher.encrypt(content)))
				f.close()
				output += "<tr><td>" + content[0:16] + "</td><td>https://once.ruf.io/" + content_key + "~" + secret_key + "</td></tr>"
				content = ''
				ct += 1
				if 'content'+str(ct) in v:
					content = v['content'+str(ct)]
			return output
		else:
			raise web.seeother('/')

if __name__ == "__main__":
	app.run()

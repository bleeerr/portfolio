from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import json
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parent.parent
from threading import Thread
from playwright.sync_api import sync_playwright
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(ROOT/'dist'),**kw)
 def do_GET(self):
  if self.path.split('?')[0] in ['/portfolio','/portfolio/']:
   self.path='/index.html'
  elif self.path.startswith('/portfolio/'):
   self.path=self.path[len('/portfolio'):]
  else:
   self.send_error(404);return
  super().do_GET()
 def copyfile(self,source,outputfile):
  try:super().copyfile(source,outputfile)
  except (BrokenPipeError,ConnectionResetError):pass
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',8765),Handler);Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page()
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 for address in ['/portfolio/','/portfolio']:
  page.goto('http://127.0.0.1:8765'+address,wait_until='networkidle')
  assert page.locator('.project-carousel').count()==13
  for card in page.locator('.project-carousel').all():
   card.scroll_into_view_if_needed()
   page.wait_for_function("()=>[...document.querySelectorAll('.inline-image')].filter(i=>i.getBoundingClientRect().top<innerHeight && i.getBoundingClientRect().bottom>0).every(i=>i.complete&&i.naturalWidth>0)")
   card.locator('.stage-arrow.next').click()
   card.locator('.inline-image').evaluate('(i)=>i.decode()')
   assert '/portfolio/media/' in card.locator('.inline-image').get_attribute('src')
  assert page.locator('.hero-actions a[download]').get_attribute('href')=='/portfolio/resume.pdf'
  print('PASS: all 13 carousel images and navigation at '+address)
 for project in json.loads((ROOT/'src/projects.json').read_text()):
  for image in project['images']:
   with urlopen('http://127.0.0.1:8765/portfolio/'+image) as response:
    assert response.status==200 and response.headers.get_content_type()=='image/webp'
 with urlopen('http://127.0.0.1:8765/portfolio/resume.pdf') as response:
  assert response.status==200 and response.read(4)==b'%PDF'
 assert not errors,errors
 print('PASS: all 66 media URLs and PDF under /portfolio/; no JavaScript errors')
 browser.close()
server.shutdown()

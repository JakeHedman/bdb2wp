#coding: utf-8
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media
from wordpress_xmlrpc.methods.posts import NewPost
import datetime
import re
import requests

wp_url = raw_input("Wordpress URL: ")
wp_user = raw_input("Wordpress username: ")
wp_pass = raw_input("Wordpress password: ")
wp = Client('http://' + wp_url + '/xmlrpc.php', wp_user, wp_pass)

next_url = raw_input("URL of first image: ")
next_match = True
i = 0
while next_match != None:
    res = requests.get(next_url)
    
    # Get date
    pattern = r'setSelectedDay\((\d+?),(\d+?),(\d+?)\)'
    match = re.search(pattern, res.text)
    date = datetime.datetime(year=int(match.group(1)),
                             month=int(match.group(2)), day=int(match.group(3)))
    
    # Get image file url
    pattern = r'src="(.*?)" id="picture"'
    img_url = re.search(pattern, res.text).group(1)
    
    # Get description
    pattern = r'<div id="showContentText">(.*?)</div>.*?<div id="showContentImageInfo"'
    body = re.search(pattern, res.text, re.MULTILINE | re.DOTALL).group(1)
    
    # Upload image
    data = {
        'name': img_url.split("/")[-1], 
        'type': 'image/jpg',
    }
    data['bits'] = xmlrpc_client.Binary(requests.get(img_url).content)
    file_res = wp.call(media.UploadFile(data))
    
    # Wordpress post
    post = WordPressPost()
    post.title = "dayviews {d}/{m}-{y}".format(d=date.day, m=date.month,
                                               y=date.year)
    post.content = u'<img src="{url}"><br>{body}'.format(url=file_res['url'],
                                                         body=body)
    post.date = date
    post.tags = ['dayviews']
    post.post_status = 'publish'
    wp.call(NewPost(post))
    
    # Get url of next image
    pattern = r'href="(.*?)" title="Next'
    next_match = re.search(pattern, res.text)
    if next_match:
        next_url = next_match.group(1)
    i += 1
    print i

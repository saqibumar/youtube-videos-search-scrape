import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
#from scraper.items import ScraperItem
import re
from scrapy import Request
from youtubeScraper.items import ScraperItem
from PIL import Image
import base64
import os
import json
import uuid
import io

import requests 
from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import urlparse
from urllib.request import urlopen
from io import BytesIO
# import m3u8
# from selenium import webdriver
# import pafy
# import youtube_dl
from pytube import YouTube
import json
# import ffmpy
from .extract import json_extract
import shutil
import time
# scrapy crawl youtube -a city="mexico-city" -a country="mexico" -a countryCode="MX" -a lang="es" -a skeyword="cdmx"
class YoutubeSpider(scrapy.Spider):
    name = "youtube"
    rule = (Rule(LinkExtractor(canonicalize=True, unique=True), callback="parse", follow=True))
    #allowed_domains = ["google.com"]
    allowed_domains = ["*"]
    start_urls = []
    keyword = ""
    country = ""
    CountryCode = ""
    rotate_user_agent = True
    content_title = ""

    def __init__(self, city=None, country=None, countryCode=None, lang=None, skeyword=None, *args, **kwargs):
        super(YoutubeSpider, self).__init__(*args, **kwargs)
        country = country.replace(" ", "%20")
        skeyword = skeyword.replace(" ", "%20")
        self.start_urls = ['https://www.youtube.com/results?search_query={}'.format(skeyword)]
        # self.start_urls = ['file:///Users/saqib/Documents/Git/noozter-scrapy/yt2.html']
        print("Parsing -> %s" % self.start_urls)
        self.city = city
        self.country = country
        self.count = 0
        self.CountryCode = countryCode
        self.content_title = 'No title'
        self.headers = {
            'authority': 'www.google.com',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en,en-US;q=0.9,es;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        }
        # SAQIB: below write content to file
        self.path_to_html = 'ytX2.html'
        self.html_file = open(self.path_to_html, 'w')

    def parse_coords2(self, response):
        item = response.meta['item']
        print("++++++++++++COORDS2++++++++++++++")
        latlon = response.xpath('//*/p[@class="font-bold text-blue-500 mt-3 lg:text-lg"]/text()').extract()
        yield {"latlon": latlon}
        #latlon = response.xpath('//div[@role="heading"]/div').getall()
        print('>>>>')
        print(latlon)
        print('<<<<<')
        #33.7130° N, 73.1615° E
        #if len(latlon)>=1:
        split_coords = str(latlon).split(", ")
        item["lat"] = split_coords[0].split('°')[0].replace("'", "").replace("[", "").replace("]", "")
        item["lon"] = split_coords[1].split('°')[0].replace("'", "").replace("[", "").replace("]", "")
        yield {'lat':item["lat"]}
        yield {'lon':item["lon"]}
        if len(item["links"])>0:
            for link in item["links"]:
                print(link)
                yield {'links': link}
                self.get_youtube(item, link)

            # self.get_youtube(item, item["links"][0])
                # yield Request(link, callback=self.get_youtube, dont_filter=True, meta={'item':item})
        #return item

    def youtube_Search_v2(self, query, html):
        ''' local_url = 'yt2.html'
        page = open(local_url)
        soup = BeautifulSoup(page.read()) '''
        url = query
        g_clean = []
        try:            
            html1 = requests.get(url, headers=self.headers)
            print('???????? url = '+url)
            #SAQIB: below write content to file
            self.html_file.write(html.text)
            self.html_file.close()
            #print(html)
            # if True:
            if html1.status_code==200:
                soup = BeautifulSoup(html.text, 'lxml')
                pattern = re.compile(r'ytInitialData\s*=\s*(\{.*?\})\s*;\s*')
                # pattern = re.compile(r'ytInitialData\s*=\s*(\{.*?\})\s*;\s*\n')
                # pattern = re.compile(r'window\["ytInitialData"\]\s*=\s*(\{.*?\})\s*;\s*\n')
                script = soup.find_all("script", string=pattern)
                print('ytInitialData Pattern found -> ' + str(len(script)))
                data = pattern.search(script[0].string).group(1)
                data = json.loads(data)
                contents = data['contents']
                # print(contents)
                
                data2 = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
                arr_content2 = data2[0]
                all_media_renderer = arr_content2['itemSectionRenderer']['contents']
                print('all_media_renderer = '+str(len(all_media_renderer)))
                # 
                # arr_content3 = arr_content2['itemSectionRenderer']['contents'][0]
                # videoRenderer = arr_content3['videoRenderer']
                # print(len(arr_content2['itemSectionRenderer']['contents']))
                # print(videoRenderer.items())
                
                for i in range(len(all_media_renderer)):
                    dict_content = arr_content2['itemSectionRenderer']['contents'][i]
                    for key, value in dict_content.items():
                        if "videoRenderer" in key:
                            # print(key + " = ")
                            # print('--------------')
                            # print(value)
                            videoRenderer = dict_content['videoRenderer']
                            for key1, value1 in videoRenderer.items():
                                # print(key1 + " = ")
                                # if "title" in key1:
                                #     nooz_title = json_extract(value1, 'text')[0]
                                    # print(nooz_title)
                                    # self.content_title = nooz_title
                                    # item = ScraperItem()
                                    # item['content'] = nooz_title
                                if "publishedTimeText" in key1:
                                    # print('@@@@@@@@@@@@@@@@@@')
                                    # print(value1)
                                    time_ago = json_extract(value1, 'simpleText')[0]
                                    # print(time_ago)
                                    # print('@@@@@@@@@@@@@@@@@@')
                                if "navigationEndpoint" in key1:
                                    # print('@@@@@@@@@@@@@@@@@@')
                                    # print(value1)
                                    watch_url = json_extract(value1, 'url')[0]
                                    m1 = re.compile(r'^(\d+ min(.*?|\s) ago)|(\d+ hour ago)|(\d+ hours ago)|(hace \d+ hora)|(hace \d+ horas)|(hace \d+ min)')
                                    n1 = m1.search(time_ago)
                                    # print(n1)
                                    if watch_url and n1 is not None:
                                        ''' print('###############')
                                        print('Found video')
                                        print(watch_url)
                                        print(time_ago) 
                                        print('###############') '''
                                        g_clean.append('https://youtube.com'+watch_url)
                                        # g_clean.append(watch_url)
                                    # print('@@@@@@@@@@@@@@@@@@')
                        # print('======================')

        except Exception as ex:
            print(str(ex))
            return str(ex)
        finally:
            print(g_clean)
            return g_clean

    def parse(self, response):
        ''' # ANALYZE THESE LINKS
        # 1- https://youtube.com/watch?v=DKyTPOXNLN4
        # 2- https://youtube.com/watch?v=lyjIpWHMo9w
        item = ScraperItem()
        self.get_youtube_Test(item, 'https://youtube.com/watch?v=DKyTPOXNLN4')
        return '''
        print('User-Agent : %s' % response.request.headers['User-Agent'])
        links_2 = self.youtube_Search_v2(self.start_urls[0], response)
        print('Number of links to parse = ' + str(len(links_2)))
        if len(links_2)>0:
            yield {'links-1': links_2}
            item = ScraperItem()
            item["links"] = links_2
            item["lat"] = 1
            item["lon"] = 1
            coordinates_search_str = 'https://www.geodatos.net/en/coordinates/{}/{}'.format(self.country , self.city)
            print(coordinates_search_str)
            yield Request(coordinates_search_str, callback=self.parse_coords2, dont_filter=True, meta={'item':item})
        else:
            print("NO LINKS FOUND :/")

    def add_nooz(self, item):
        print("add nooz text API HERE....")
        meta = item['content']
        links = item['links']
        url = 'https://api.programmingalternatives.com/api/v1/nooz'
        item['REQ_ID'] = str(uuid.uuid4())
        my_data = {
        "Latitude": item["lat"],
        "Longitude": item["lon"],
        "User":
        {
            "UserId": 3
        },
        "Country": self.country.title(), #"Pakistan",
        "City": self.city.replace('-', ' ').title(),
        "Blurb": meta,
        "Story": meta,
        "CountryCode": self.CountryCode,
        "ShareLocation": 1,
        "IsPublished": 1,
        "REQ_ID": item['REQ_ID'], #str(uuid.uuid4()) #"2E11CA3D-7FE8-43DC-A159-B99DDB95856B"
        "DeviceInfo": "Scrapy"
        }
        headers={'Content-Type':'application/json', 'Authorization':'Basic YOUR_AUTH_STRING'}
        #print(my_data)
        try:
            response = requests.post(url, headers=headers, data=json.dumps(my_data))
            response = json.loads(response.text)
            item['NoozId'] = response["NoozId"]
            # self.add_noozMedia(item)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(response)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            return item['NoozId']
        except Exception as ex:
            print(str(ex))

    def add_noozMedia(self, item, isImage=True):
        api_url = "https://api.programmingalternatives.com/api/v1/Documents/{}/noozMediasHost".format(item['NoozId'])
        #api_url = "https://api.programmingalternatives.com/api/v1/Documents/{}/noozMedias".format(item['NoozId'])
        print(api_url)
        uuid_append = str(uuid.uuid4())
        boundary = "-------------------------{}".format(uuid_append)
        #print(boundary)
        contentType = "multipart/form-data; boundary=%s" % boundary
        #print(contentType)

        request_headers = {
            'Authorization': 'Basic YOUR_AUTH_STRING',
            'Content-Type': contentType
        }
        #print(' ==========HEADER========== ')
        #print(request_headers)
        body1 = "\r\n--%s\r\n" % boundary
        body2 = "Content-Disposition: form-data; name=model\r\n"
        body3 = "Content-Type: text/plain; charset=UTF-8\r\n\r\n"
        my_data = {
            "Title": "",
            "DisplayPosition": item['DisplayPosition'], 
            "REQ_ID": item['REQ_ID']
        }
        body4 = json.dumps(my_data)
        body5 = "\r\n--%s\r\n" % boundary
        if isImage==True:
            print('IMAGE PROCESSING')
            body6 = "Content-Disposition: form-data; model=\"test123\"; filename=\"123.jpg\"\r\n"
            body7 = "Content-Type: image/jpeg\r\n\r\n"
            img64 = base64.decodebytes(item["base64images"])

        if isImage==False:
            print('VIDEO PROCESSING')
            body6 = "Content-Disposition: form-data; model=\"test123\"; filename=\"123.mp4\"\r\n"
            body7 = "Content-Type: video/mp4\r\n\r\n"
            img64 = item["video"]

        #body8 = img64
        body9 = "\r\n"
        body10 = "--%s--\r\n" % boundary

        #body_data = body1 + body2 + body3 + body4 + body5 + body6 + body7 + body8 + body9 + body10
        #request_body = body_data.encode('UTF-8')
        request_body = body1.encode('UTF-8') + body2.encode('UTF-8') + body3.encode('UTF-8') + body4.encode('UTF-8') + body5.encode('UTF-8') + body6.encode('UTF-8') + body7.encode('UTF-8') + img64 + body9.encode('UTF-8') + body10.encode('UTF-8')
        # print(' ==========BODY========== ')
        # print(body6.encode('UTF-8'))
        response = requests.post(api_url, headers=request_headers, data=request_body)
        print(response.reason)
        print(response.status_code)
        response = json.loads(response.text)
        print(response)

    def get_youtube(self, item, yt_link):
        # item = response.meta['item']
        # prohibited_words = []
        prohibited_words = ['asesin', 'balazos', 'balacer', 'asalta', ' matar', 'murder', 'muere', 
                'partido', 'crime', 'arrest', 'protest', 'homicid', 'crimi',
                'assault', 'arrest', 'dead', 'mensaje de los ángeles', 'death', 'died']
        print("!!!!!!!!!!GETTING.............." + yt_link)
        try:            
            if not os.path.exists('videos'):
                os.makedirs('videos')
            try:
                yt = YouTube(yt_link)
            except Exception as ex:
                print("YouTube failed")
                print(str(ex))
                return

            print(yt.title.upper())
            if any(word.upper() in yt.title.upper() for word in prohibited_words):
                print('---------------------------------------->>>>>>> Encountered PROHIBITED WORD')
                return

            len_to_crop = 40
            if yt.length<40:
                len_to_crop = yt.length
            print('Video length = ' + str(yt.length))
            if yt.length>=1 and yt.length<=1200:
                item["content"] = '* VIDEO: ' + yt.title + '\n' + yt_link
                try:
                    # dest = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download('videos')
                    dest = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')[-1].download('videos')
                    new_name = 'videos/{}_original.mp4'.format(yt.title.split(' ')[0].replace("'", "").replace("!", "").replace("(", "").replace(")", ""))
                    os.rename(dest, new_name)
                    print("2- " + new_name)
                    print('FFMPEG RUN...')
                    cmd = 'ffmpeg -nostdin -loglevel panic -y -ss 0 -i {} -t {} -y -c:v copy -c:a copy -movflags +faststart videos/clipped.mp4'.format(new_name, str(len_to_crop))
                    os.system(cmd)
                    # print("SLEEP FOR 10")
                    # time.sleep(10)
                    print(yt.title+" - has been downloaded !!!")
                except Exception as ex:
                    print("Download video failed")
                    print(str(ex))
                finally:
                    noozid = self.add_nooz(item)
                    print('Returned noozid = '+ str(noozid))  
                    if not noozid:
                        print('Failed on inserting nooz add_nooz')
                        return;                  
                    # item['NoozId'] = 7031
                    print("SLEEP FOR 2")
                    time.sleep(2)
                    # old command fails -> ffmpeg_cmd_extract_img = 'ffmpeg -loglevel panic -i videos/clipped.mp4 -vf "select=\'eq(t,12)\'" -frames:v 1 videos/frame_12_sec.png'
                    # without scaling the image = ffmpeg_cmd_extract_img = 'ffmpeg -nostdin -loglevel panic -ss 00:00:05 -i {} -vframes 1 -q:v 2 videos/frame_12_sec.png'.format(new_name)
                    ffmpeg_cmd_extract_img = 'ffmpeg -nostdin -loglevel panic -ss 00:00:05 -i {} -vframes 1 -q:v 2 -vf "scale=-1:300" videos/frame_12_sec.png'.format(new_name)
                    os.system(ffmpeg_cmd_extract_img)

                    with open("videos/frame_12_sec.png", "rb") as videoImageFile:
                        foo = Image.open("videos/frame_12_sec.png")
                        width, height = foo.size
                        print("IMAGE W = {}, H = {}". format(width, height))
                        print('@@@@@@@@@----GETTING IMAGE FROM VIDEO----@@@@@@@@@@@@@')
                        size_in_bytes = os.stat('videos/frame_12_sec.png').st_size
                        print("size in bytes")
                        print(size_in_bytes)
                        if size_in_bytes > 300000:
                        # if height > 300:
                            print("Reduce further using ffmpeg resolution")
                            ffmpeg_cmd_extract_img_further = 'ffmpeg -nostdin -loglevel panic -i videos/frame_12_sec.png -vf "scale=-1:250" videos/frame_12_sec_2.png'
                            os.system(ffmpeg_cmd_extract_img_further)
                            with open("videos/frame_12_sec_2.png", "rb") as videoImageFile2:
                                enc_videoImageFile = base64.b64encode(videoImageFile2.read())
                        else:
                            enc_videoImageFile = base64.b64encode(videoImageFile.read())

                        item['VideoImageFile'] = enc_videoImageFile
                        item["base64images"] = enc_videoImageFile
                        item['DisplayPosition'] = -4
                        item['REQ_ID'] = str(uuid.uuid4())
                        self.add_noozMedia(item, True)

                    with open("videos/clipped.mp4", "rb") as videoFile:
                        print('@@@@@@@@@----GETTING VIDEO----@@@@@@@@@@@@@')
                        msg = videoFile.read()
                        item["video"] = msg
                        # print(msg)
                        item['REQ_ID'] = str(uuid.uuid4())
                        item['DisplayPosition'] = 4
                        self.add_noozMedia(item, False)
                    print('@@@@@@@@@@----END OF GETTING VIDEO----@@@@@@@@@@@@')
            else:
                raise Exception("Video too big for processing...")
        except Exception as ex:
            print("ERRRRRRRRR 1=> " + str(ex))
        finally:
            if os.path.exists('videos'):
                # os.remove(new_name)
                shutil.rmtree('videos')
                print("REMOVED THE DIRECTORY")
            else:
                print('directory does not exist')
    
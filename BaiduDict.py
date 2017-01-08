def lookup(string):
    class HtmlFilter:
        def __init__(self):
            self.contents = "";
            self.result = {}

        def fillBuffer(self, buf):
            self.contents += buf;

        def filter(self):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.contents, "lxml");
            [s.extract() for s in soup('script')]
            data_name = soup.body["data-name"];
            pronounce = soup.find(id="pinyin");
            phonetic = None;
            if (pronounce):
                pronounce = pronounce.find("span");
                if (pronounce):
                    phonetic = pronounce.get_text().strip();
                    if (phonetic[0] != "["):
                        phonetic = "[%(pinyin)s]" % {"pinyin": phonetic};
            soup = soup.find("div", id="basicmean-wrapper");
            if (soup):
                soup = soup.find("div", "tab-content");
            else:
                self.contents = "";
                return;
            if (soup):
                [s.extract() for s in soup.find_all('span')];
                senses = soup.get_text().strip();
                self.contents = senses;
                sense = [];
                for xx in senses.split("\n"):
                    import re;
                    xx = re.sub(r"^[0-9]\.", "", xx);
                    sense.append(xx);
                self.result = {data_name: {"phonetic": phonetic, "sense": sense}};
                
    if isinstance(string, unicode):
        string = string.encode("utf-8");
    url = "http://hanyu.baidu.com/s?wd=%(word)s&ptype=zici" % {"word": string};
    import pycurl;
    curl = pycurl.Curl();
    curl.setopt(curl.URL, url);
    htmlFilter = HtmlFilter();
    curl.setopt(curl.WRITEFUNCTION, htmlFilter.fillBuffer);
    curl.setopt(curl.FOLLOWLOCATION, 1);
    curl.perform();
    htmlFilter.filter();
    return htmlFilter.result;

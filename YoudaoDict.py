def lookup(string):
    class HtmlFilter:
        def __init__(self):
            self.contents = "";
            self.result = {}

        def fillBuffer(self, buf):
            self.contents += buf;

        def filter(self):
            from bs4 import BeautifulSoup;
            soup = BeautifulSoup(self.contents, "lxml");
            [s.extract() for s in soup('script')];
            soup = soup.find("div", id="hhDictTrans");
            if (soup):
                [s.extract() for s in soup.find_all("div", "via ar")];
                [s.extract() for s in soup.find_all("ul", "sense-ex")];
                items = {};
                key = None;
                phonetic = None;
                for s in soup.children:
                    if (s.name):
                        if (s.name == "h4"):
                            phonetic_obj = s.find("span", "phonetic");
                            if (phonetic_obj):
                                phonetic = phonetic_obj.get_text();
                                phonetic_obj.extract();
                            key = s.get_text().strip();
                        else:
                            sense = [];
                            for x in s.find_all(class_="sense-title"):
                                sense_i = x.get_text().strip();
                                sense.append(sense_i);
                            items[key] = {"phonetic": phonetic, "sense": sense};
                self.contents = soup.get_text();
                self.result = items;
            else:
                self.contents = "";

    if isinstance(string, unicode):
        string = string.encode("utf-8");
    url = "http://dict.youdao.com/w/%(word)s/#keyfrom=dict2.top" % {"word": string };
    #print url;
    import pycurl;
    curl = pycurl.Curl();
    curl.setopt(curl.URL, url);
    htmlFilter = HtmlFilter();
    curl.setopt(curl.WRITEFUNCTION, htmlFilter.fillBuffer);
    curl.setopt(curl.FOLLOWLOCATION, 1);
    curl.perform();
    htmlFilter.filter();
    return htmlFilter.result;

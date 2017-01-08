def lookup(string):
    class Table:
        def __init__(self):
            self.header = None;
            self.values = [];

        def setHeader(self, header):
            self.header = header;

        def addValues(self, values):
            if self.header:
                self.values.append(values);
            else:
                self.values.extend(values);

        def p(self, level = 0):
            if self.header:
                print "    " * level,
                for x in self.header:
                    print x + "\t\t",
                print;
                for g in self.values:
                    print "    " * level,
                    for x in g:
                        print x + "\t\t",
                    print;
            else:
                print "    " * level,
                for x in self.values:
                    print x + " ",
                print;

    class Doc:
        def __init__(self):
            self.paragraphs = [];
            self.subs = {};
            self.tables = [];

        def p(self, level = 0):
            for p in self.paragraphs:
                print "    " * level,
                print p;
            for x in self.subs:
                print "    " * level,
                print x;
                self.subs[x].p(level + 1);
            for x in self.tables:
                x.p(level + 1);

    class HtmlFilter:
        def __init__(self):
            self.contents = "";
            self.summary = "";
            self.tag = "";
            self.attrs = {};
            self.details = None;
            self.result = {};

        def fillBuffer(self, buf):
            self.contents += buf;

        def filter(self):
            from bs4 import BeautifulSoup;
            soup = BeautifulSoup(self.contents, "lxml");

            def reparagraph(string):
                import re;
                s = re.sub(r"\n+","\n", string);
                return s.strip();
            def reparagraphmore(string):
                import re;
                reparagraph(string);
                return re.sub(r'\n|&nbsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020', '', string);

            [s.extract() for s in soup.findAll("script")];
            soup = soup.find("div", class_="main-content");
            [s.extract() for s in soup.findAll(class_=[
                "lemmaWgt-lemmaCatalog","lemmaWgt-declaration","lemma-reference",
                "edit-lemma","lock-lemma","top-tool","anchor-list","album-list",
                "rs-container-foot","edit-icon","j-edit-link","lemma-picture","text-pic"
            ])];
            if soup:
                self.contents = reparagraph(soup.get_text());
                opentag = soup.find(id="open-tag");
                if opentag:
                    tags = opentag.find(class_="taglist");
                    if tags:
                        self.tag = reparagraph(tags.get_text());
                        self.result["tag"] = self.tag;
                    [s.extract() for s in soup.findAll(id="open-tag")];
                summary = soup.find(class_="lemma-summary");
                if summary:
                    self.summary = reparagraph(summary.get_text());
                    self.result["summary"] = self.summary;
                    [s.extract() for s in soup.findAll(class_="lemma-summary")];
                table = soup.find(class_="basic-info");
                if table:
                    for block in table.findAll(class_="basicInfo-block"):
                        name = "";
                        for item in block.findAll(class_="basicInfo-item"):
                            if "name" in item.attrs["class"]:
                                name = reparagraphmore(item.get_text());
                            if "value" in item.attrs["class"]:
                                value = reparagraph(item.get_text());
                                self.attrs[name] = value;
                    self.result["basicInfo"] = self.attrs;
                    [s.extract() for s in soup.findAll(class_="basic-info")];

                self.details = Doc();
                titleStack = {1:self.details};
                curLevel = 1;
                def getLevel(p):
                    import re;
                    for x in p.attrs["class"]:
                        r = re.match(r'^level-(\d+)', x);
                        if r:
                            return r.group(1);
                    return -1;
                for p in soup.findAll(["table", "div"]):
                    if p.name == "table":
                        table = Table();
                        for tr in p.findAll("tr"):
                            headers = [];
                            for th in tr.findAll("th"):
                                headers.append(reparagraphmore(th.get_text()));
                            if len(headers) != 0:
                                table.setHeader(headers);

                            values = [];
                            for td in tr.findAll("td"):
                                values.append(reparagraphmore(td.get_text()));
                            if len(values):
                                table.addValues(values);
                        titleStack[curLevel].tables.append(table);
                    if p.has_attr("class"):
                        def parentIsTable(p):
                            while p.parent:
                                if p.parent.name == "table":
                                    return True;
                                p = p.parent;
                            return False;
                        if parentIsTable(p):
                            continue;
                        if "para-title" in p.attrs["class"]:
                            curLevel = int(getLevel(p));
                            title = reparagraphmore(p.get_text());
                            doc = Doc();
                            titleStack[curLevel - 1].subs[title] = doc;
                            titleStack[curLevel] = doc;
                        if "para" in p.attrs["class"]:
                            titleStack[curLevel].paragraphs.append(reparagraph(p.get_text()));
                self.result["details"] = self.details;
            else:
                self.contents = "";
                return;

    if isinstance(string, unicode):
        string = string.encode("utf-8");
    url = "http://baike.baidu.com/item/%(word)s" % {"word": string};
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

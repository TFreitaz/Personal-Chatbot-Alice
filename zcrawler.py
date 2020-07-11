from robobrowser import RoboBrowser
import os


class ZCrawler:
    def ituv_info_covid(self, folder="Ituverava", path=None):
        if folder not in os.listdir(path):
            os.mkdir(folder)
        browser = RoboBrowser(parser="html.parser")
        url = "http://www.ituverava.sp.gov.br/"
        browser.open(url)
        banner = browser.find_all(class_="slidehomecropimg1 wp-post-image")[0]
        img = browser.session.get(banner["src"])
        filepath = f"{folder}/ituv_info_covid.png"
        if path:
            if path[-1] == "/":
                path = path[:-1]
            filepath = f"{path}/{filepath}"
        with open(filepath, "wb") as f:
            f.write(img.content)

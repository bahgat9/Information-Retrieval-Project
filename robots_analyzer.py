
from urllib.robotparser import RobotFileParser
import requests


class RobotsAnalyzer:
    def __init__(self, domain="https://www.booking.com"):
        self.domain = domain
        self.rp = RobotFileParser()

    def analyze(self):
        self.rp.set_url(f"{self.domain}/robots.txt")
        try:
            self.rp.read()
            return {
                "crawl_delay": self.rp.crawl_delay("*"),
                "sitemaps": self.rp.site_maps(),
                "can_fetch_home": self.rp.can_fetch("*", "/"),
                "can_fetch_search": self.rp.can_fetch("*", "/searchresults.en-us.html")
            }
        except Exception as e:
            return {"error": str(e)}

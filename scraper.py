import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from simhash import Simhash

visited_url = []
visited_links = set()
unique_urls = 0

def scraper(url, resp):
    global unique_urls
    links = extract_next_links(url, resp)
    need_to_visit = []
    for link in links:
        if is_valid(link) and hash(link) not in visited_links and not garbage_page(link):
            need_to_visit.append(link)
            visited_links.add(hash(link))
            unique_urls += 1
    return need_to_visit

def garbage_page(url):
    if not url.startswith("http://archive.ics.uci.edu") and not url.startswith("https://archive.ics.uci.edu"):
        return False
    
    if url.endswith("view=table") or url.endswith("view=list"):
        return True
    
    return False

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if resp.status != 200:
        if resp.status in [301, 302]:
            redirect_url = resp.header['Location']
            redirect_url = urljoin(url, redirect_url)
            return [redirect_url]
        return []

    """
    page_simhash = Simhash(resp.raw_response.content.decode())
    for x in visited_url:
        if x.distance(page_simhash) < 4:
            return []
    
    visited_url.append(page_simhash)
    """

    if len(resp.raw_response.content) > 1 * 1024 * 1024:
        return []

    parsed = BeautifulSoup(resp.raw_response.content, 'html.parser')

    if high_textual_info(parsed) == False:
        return []
    
    urls = []
    for i in parsed.find_all('a', href = True):
        new_url = i["href"]
        new_url = urljoin(url, new_url) # in case it is a relative url
        new_url = urldefrag(new_url)[0]
        urls.append(new_url)
    return urls


def high_textual_info(parsed):
    min_words = 200
    text = parsed.find('body')
    if text is None:
        return False
    text = text.get_text()

    if len(text.split()) >= min_words:
        page_simhash = Simhash(text)
        for x in visited_url:
            if x.distance(page_simhash) < 3:
                return False
        visited_url.append(page_simhash)
        return True
    return False



def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|ppsx"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        
        requirement_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu", "www.ics.uci.edu",
                                "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu"]
        if parsed.netloc in requirement_domains:
            return True
            """
        for domains in requirement_domains:
            if parsed.netloc.endswith(domains):
                return True
            """
        return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise

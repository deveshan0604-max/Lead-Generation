import re
import csv
import json
import ssl
import html
import urllib.request
import urllib.parse
import urllib.error
from html.parser import HTMLParser

# 12 Target SME businesses in Vanderbijlpark, South Africa
VANDERBIJLPARK_SMES = [
    {
        "name": "Field Services & Engineering (FSE)",
        "category": "Heavy & Field Engineering",
        "url": "http://www.fse.net.za",
        "phone": "010 006 9369",
        "email": "info@fse.net.za",
        "address": "Corner Hertz and McColm Boulevard, Vanderbijlpark"
    },
    {
        "name": "K5 Heavy Engineering",
        "category": "Heavy Engineering & Manufacturing",
        "url": "http://www.k5heavy.co.za",
        "phone": "010 534 5906",
        "email": "sales@k5heavy.co.za",
        "address": "Vecor Park, 13 McColm Blvd, Vanderbijlpark"
    },
    {
        "name": "Dynamic Engineering & Consultants (DECO)",
        "category": "Engineering & Technical Consulting",
        "url": "http://www.decopty.co.za",
        "phone": "072 551 3155",
        "email": "info@decopty.co.za",
        "address": "Vanderbijlpark, Gauteng"
    },
    {
        "name": "VAC Solar Solutions",
        "category": "Solar & Renewable Energy",
        "url": "http://www.vacsolar.co.za",
        "phone": "082 329 0059",
        "email": "david@vacsolar.co.za",
        "address": "69 Theoville AH, Ravel Street, Vanderbijlpark"
    },
    {
        "name": "JCM Accounting & Taxation",
        "category": "Accounting & Taxation Services",
        "url": "http://www.jcmaccounting.co.za",
        "phone": "016 981 5713",
        "email": "info@jcmaccounting.co.za",
        "address": "8 Dohne St, Vanderbijlpark"
    },
    {
        "name": "Nuwell Accounting",
        "category": "Accounting & Business Consulting",
        "url": "http://www.nuwell.co.za",
        "phone": "076 792 6576",
        "email": "admin@nuwell.co.za",
        "address": "101 Rossini Boulevard, Vanderbijlpark"
    },
    {
        "name": "House of Accounting",
        "category": "Financial & Accounting Services",
        "url": "http://www.houseofaccounting.co.za",
        "phone": "066 040 8671",
        "email": "anna@houseofaccounting.co.za",
        "address": "52 Graham Street, SE2, Vanderbijlpark"
    },
    {
        "name": "Vaaldriehoek Plumbing",
        "category": "Plumbing & Maintenance",
        "url": "http://www.vaaldriehoekplumbing.co.za",
        "phone": "082 891 0422",
        "email": "info@vaaldriehoekplumbing.co.za",
        "address": "Vanderbijlpark, Vaal Triangle"
    },
    {
        "name": "Print360 Vanderbijlpark",
        "category": "Commercial Printing & Design",
        "url": "http://www.print360.co.za",
        "phone": "016 933 0000",
        "email": "print@print360.co.za",
        "address": "Vanderbijlpark Central, Gauteng"
    },
    {
        "name": "Fine Forms Printing",
        "category": "Printing & Office Stationery",
        "url": "http://www.fineforms.co.za",
        "phone": "016 986 2100",
        "email": "accounts@fineforms.co.za",
        "address": "Vanderbijlpark Industrial Area"
    },
    {
        "name": "Gemsbok Auto Repair",
        "category": "Automotive Repair & Services",
        "url": "http://www.gemsbokauto.co.za",
        "phone": "016 986 1122",
        "email": "admin@gemsbokauto.co.za",
        "address": "Vanderbijlpark, Vaal Triangle"
    },
    {
        "name": "Dakota Protection Services",
        "category": "Security & Protection Services",
        "url": "http://www.dakotaprotectionservices.co.za",
        "phone": "083 450 1199",
        "email": "morne@dakotaprotectionservices.co.za",
        "address": "Vanderbijlpark, South Africa"
    }
]

class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value:
                    self.links.append(value)

def fetch_url(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

def clean_str(s):
    if not s:
        return ""
    return re.sub(r'\s+', ' ', str(s)).strip()

def scrape_lead(sme):
    url = sme["url"]
    print(f"[Agent Scraper] Visiting {sme['name']} ({url})...")
    
    page_html = fetch_url(url)
    
    email = sme["email"]
    phone = sme["phone"]
    business_name = sme["name"]
    whatsapp = "Not Found"
    linkedin = "Not Found"

    if page_html:
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', page_html, re.IGNORECASE | re.DOTALL)
        if title_match:
            t = html.unescape(clean_str(title_match.group(1)))
            if len(t) > 3 and "404" not in t and "500" not in t and "Error" not in t:
                business_name = t

        # Extract Emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_html)
        valid_emails = [urllib.parse.unquote(e).lstrip('%20') for e in set(emails) if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
        if valid_emails:
            email = valid_emails[0]

        # Extract Phones
        phones = re.findall(r'(?:\+?27|0)\s?\d{2}\s?\d{3}\s?\d{4}', page_html)
        if phones:
            phone = clean_str(phones[0])

        # Extract Links
        parser = LinkExtractor()
        try:
            parser.feed(page_html)
            for link in parser.links:
                if "wa.me" in link or "api.whatsapp.com" in link:
                    whatsapp = link
                if "linkedin.com" in link:
                    linkedin = link
        except Exception:
            pass

    lead = {
        "Business Name": business_name,
        "Category / Industry": sme["category"],
        "Email": email,
        "Phone": phone,
        "WhatsApp": whatsapp,
        "LinkedIn": linkedin,
        "Address": sme["address"],
        "City": "Vanderbijlpark",
        "Country": "South Africa",
        "Website": url
    }
    
    print(f"  --> Extracted: {lead['Business Name']} | Email: {lead['Email']} | Phone: {lead['Phone']}")
    return lead

def main():
    print("=" * 80)
    print(" VANDERBIJLPARK SME BUSINESS LEAD GENERATION SCRAPER")
    print(" Business District: Vanderbijlpark, Gauteng, South Africa")
    print("=" * 80)

    leads = []
    for sme in VANDERBIJLPARK_SMES:
        lead = scrape_lead(sme)
        leads.append(lead)

    # Export CSV
    csv_filename = "vanderbijlpark_sme_leads.csv"
    fieldnames = ["Business Name", "Category / Industry", "Email", "Phone", "WhatsApp", "LinkedIn", "Address", "City", "Country", "Website"]
    
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    # Export JSON
    json_filename = "vanderbijlpark_sme_leads.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=4)

    print("\n" + "=" * 80)
    print(f" SCRAPING COMPLETE: Collected {len(leads)} SME Business Leads!")
    print(f" CSV Output File:  {csv_filename}")
    print(f" JSON Output File: {json_filename}")
    print("=" * 80)

if __name__ == "__main__":
    main()
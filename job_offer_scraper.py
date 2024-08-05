import requests
from bs4 import BeautifulSoup
import json

class JobOffer:
    '''
    Holds job offer details.
    Converts details to dictionary and JSON formats.
    '''
    def __init__(self, title, company, details, responsibilities, requirements, benefits):
        self.title = title
        self.company = company
        self.details = details
        self.responsibilities = responsibilities
        self.requirements = requirements
        self.benefits = benefits

    def to_dict(self):
        return {
            'title': self.title,
            'company': self.company,
            'details': self.details,
            'responsibilities': self.responsibilities,
            'requirements': self.requirements,
            'benefits': self.benefits
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

class JobOfferParser:
    '''
    Parses HTML to extract job details.
    Uses BeautifulSoup to traverse and extract information.
    '''
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.soup = self.soup.find('div', id = 'offer-details')
        # Remove all <script> tags
        for svg in self.soup.find_all('svg'):
            svg.decompose()
        # Remove all <button> tags
        for button in self.soup.find_all('button'):
            button.decompose()
        # Find and decompose empty tags
        for tag in self.soup.find_all():
            if self._is_empty(tag):
                tag.decompose()

    # Function to recursively check if a tag is empty
    def _is_empty(self, tag):
    # If the tag contains any text or has children with text, it's not empty
        if tag.string and tag.string.strip():
            return False
        for child in tag.descendants:
            if child.string and child.string.strip():
                return False
        return True

    def parse(self):
        print(self.soup.prettify())
        # Parse job offer details from HTML
        title = self.soup.find('h1', {'data-test': 'text-positionName'}).text.strip() if self.soup.find('h1') else 'No title'
        company = self.soup.find('h2', {'data-test': 'text-employerName'}).contents[0].strip() if self.soup.find('h2') else 'No company'
        job_details = self._parse_job_details()
        responsibilities = self._parse_responsibilities()
        requirements = self._parse_requirements()
        benefits = self._parse_benefits()

        return JobOffer(title, company, job_details, responsibilities, requirements, benefits)

    def _parse_job_details(self):
        # Extract job details
        job_details = {}

        job_details['location'] = self.soup.find('li', {'data-test': 'sections-benefit-workplaces'}).find('a').text.strip()
        job_details['expiration_date'] = self.soup.find('li', {'data-test': 'sections-benefit-expiration'}).find('div', {'data-test': 'offer-badge-description'}).text.strip()
        job_details['contract_type'] = self.soup.find('li', {'data-test': 'sections-benefit-contracts'}).find('div', {'data-test': 'offer-badge-title'}).text.strip()
        job_details['work_schedule'] = self.soup.find('li', {'data-test': 'sections-benefit-work-schedule'}).find('div', {'data-test': 'offer-badge-title'}).text.strip()
        job_details['position_level'] = self.soup.find('li', {'data-test': 'sections-benefit-employment-type-name'}).find('div', {'data-test': 'offer-badge-title'}).text.strip()
        job_details['work_mode'] = self.soup.find('li', {'data-scroll-id': 'work-modes'}).find('div', {'data-test': 'offer-badge-title'}).text.strip()
        job_details['spetializations'] = self.soup.find('li', {'data-test': 'it-specializations'}).find('div', {'class': 'v1xz4nnx'}).text.strip()

        return job_details
                
    def _parse_responsibilities(self):
        # Parse the responsibilities section
        responsibilities_section = self.soup.find('section', {'data-test': 'section-responsibilities'})

        if responsibilities_section:
            return [resp.text for resp in responsibilities_section.find_all('li', {'class': 'tkzmjn3'})]
        else:
            return None


    def _parse_requirements(self):
        # Parse the requirements section
        requirements_section = self.soup.find('section', {'data-scroll-id': 'requirements-1'})
        
        if requirements_section:
            return [resp.text for resp in requirements_section.find_all('li', {'class': 'tkzmjn3'})]
        else:
            return None
        
    def _parse_benefits(self):
        # Extract and parse the benefits
        benefits_section = self.soup.find('section', {'data-test': 'section-benefits'})
        if benefits_section:
            return [resp.text for resp in benefits_section.find_all('li', {'data-test': 'list-item-benefit'})]
        else:
            return None

class JobOfferScraper:
    '''
    Fetches HTML from provided URLs.
    Uses JobOfferParser to parse each HTML document and gather job offers.
    '''
    def __init__(self, urls):
        self.urls = urls

    def get_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None

    def scrape(self):
        job_offers = []
        for url in self.urls:
            html = self.get_html(url)
            if html:
                parser = JobOfferParser(html)
                job_offer = parser.parse()
                job_offers.append(job_offer.to_json())
        return job_offers

if __name__ == '__main__':
    urls = [
        'https://www.pracuj.pl/praca/data-analyst-warszawa-aleje-jerozolimskie-180,oferta,1003463712?s=9786d524',
    ]
    scraper = JobOfferScraper(urls)
    offers = scraper.scrape()

    for offer in offers:
        print(offer)

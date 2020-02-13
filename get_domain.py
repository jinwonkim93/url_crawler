from tld import get_tld

def get_domain_name(url):
    domain = get_tld(url, as_object=True)
    domain_name = domain.parsed_url.scheme + "://" + domain.fld
    return domain_name

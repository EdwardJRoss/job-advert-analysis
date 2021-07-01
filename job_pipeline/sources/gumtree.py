from job_pipeline.lib.extractlib import parse_js_obj
from job_pipeline.lib.normalise import (
    WOF_AUS,
    WOF_NZ,
    Geocoder,
    datetime_from_iso_utc,
    html2plain,
)
from job_pipeline.lib.salary import get_salary_data
from job_pipeline.sources.abstract_datasource import module_name
from job_pipeline.sources.commoncrawl_datasource import CommonCrawlDatasource

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))

JS_STR_APP = "window.APP_DATA ="


class Datasource(CommonCrawlDatasource):
    name = module_name(__name__)
    query = "gumtree.com.au/s-ad/*"
    query_filters = [
        "~url:.*/(account-manager|account-relationship-management|accounting|accounts-officer-clerk|accounts-payable|accounts-receivable-credit-control|admin|administration-office-support|administrative-assistant|advertising-arts-media|aged-disability-support|agronomy-farm-services|air-conditioning-refrigeration|analysis-reporting|architecture|art-director|assembly-process-work|automotive-engineering|automotive-trades|bakers-pastry-chefs|banking-financial-services|banking-retail-branch|bar-beverage-staff|bookkeeping-small-practice-accounting|building-services-engineering|building-trades|business-services-corporate-advisory|butcher|call-centre-customer-service|carpentry-cabinet-making|chef-cook|child-welfare-youth-family-services|childcare-after-school-care|civil-structural-engineering|cleaner-housekeeper|coaching-instruction|commercial-sales-leasing-property-mgmt|community-services-development|construction|consulting-generalist-hr|contract-management|corporate-commercial-law|courier-driver-postal-service|customer-service-call-centre|customer-service-customer-facing|defence|dental-dentist|design-architecture|developer-programmer|digital-search-marketing|education-teaching|electrician|employment-services|engineering|event-management|facilities-management-body-corporate|farm-management|farming-veterinary|financial-accounting-reporting|financial-manager-controller|financial-planning|fitter-turner-machinist|florist|foreman-supervisor|freight-cargo-forwarding|front-office-guest-services|funds-management|gardening-landscaping|general-practitioner-gp-|generalist|government-defence|government|graphic-design|hair-beauty-services|healthcare-administration|healthcare-nursing|horticulture|hospitality-tourism|information-communication-technology|interaction-web-design|interior-design|it-support-help-desk|kitchen-sandwich-hand|labourer|legal-secretary|legal|locksmith|machine-operators|machine-plant-operator|maintenance-handyman|maintenance|management|manufacturing-transport-logistics|marketing-assistants|marketing-communications|marketing-communications|marketing-manager|mechanical-engineering|media-planning-strategy-buying|merchandiser|mining-engineering-maintenance|mining-operations|mining-resources-energy|mortgage-broker|nanny-babysitter|new-business-development|nursing|oil-gas-engineering-maintenance|oil-gas-operations|other-jobs|other|pa-ea-secretary|painter-sign-writer|paralegal-law-clerk|payroll-accounting|performing-arts|personal-trainer|pharmacy|physiotherapy-ot-rehabilitation|plumber|police-corrections-officer|printing-publishing-services|production-planning-scheduling|project-management|property-law|public-relations-corporate-affairs|purchasing-procurement-inventory|real-estate-property|receptionist|recruitment-agency|recruitment-hr|recruitment-internal|relationship-account-management|removalist|residential-leasing-property-management|residential-sales|retail-assistant|retail-management|retail|road-transport|sales-call-centre|sales-coordinator|sales-customer-facing|sales-management|sales-representative-consultant|sales|security-services|sports-management|sports-recreation|systems-business-analyst|tailor-dressmaker|taxation|teaching|technician|tour-guide|trade-marketing|trades-services|training-development|travel-agent-consultant|tutoring|vet-animal-welfare|waiting-staff|warehousing-storage-distribution|web-development-production|workplace-training-assessment|writing-journalist|welder-boilermaker)/"
    ]

    def extract(self, html: bytes, uri, view_date):
        text = html.decode("utf-8")
        obj = parse_js_obj(text, JS_STR_APP)
        if obj is None:
            return []
        else:
            data = obj["vip"]["item"]
            # adType: OFFER is job ad, WANTED is ask for work
            if data["isJobsCategory"] and data["adType"] == "OFFER":
                return [{"data": data, "uri": uri, "view_date": view_date}]
            else:
                return []

    def normalise(self, data, uri, view_date):
        metadata = {row["value"]: row["name"] for row in data["mainAttributes"]}
        salary_raw = metadata.get("Salary Detail")
        salary_data = get_salary_data(salary_raw)
        return {
            "title": data["title"],
            "description": html2plain(data["description"]),
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": None,
            **salary_data,
            "location_raw": data["mapAddress"],
            **AU_GEOCODER.geocode(data["mapAddress"]),
        }

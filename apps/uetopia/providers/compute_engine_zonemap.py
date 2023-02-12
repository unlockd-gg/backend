import logging

## other files that need to be updated:
## static/app/partials/user.detail.html
## static/app/partials/games/Tournament/create.html
## static/app/partials/developer/server/detail.html

## https://cloud.google.com/compute/docs/regions-zones/

region_list_ce_readable = ["northamerica-northeast1",
                            "us-central1",
                            "us-west1",
                            "us-west2",
                            "us-west3",
                            "us-west4",
                            "us-east4",
                            "us-east1",
                            "southamerica-east1",
                            "europe-north1",
                            "europe-west1",
                            "europe-west2",
                            "europe-west3",
                            "europe-west4",
                            "europe-west6",
                            "asia-south1",
                            "asia-southeast1",
                            "asia-east1",
                            "asia-east2",
                            "asia-northeast1",
                            "asia-northeast2",
                            "asia-northeast3",
                            "australia-southeast1"]

def region_zone_mapper(region_name):
    """ convert a region to zone """
    if region_name == "northamerica-northeast1":
        return "northamerica-northeast1-a"
    elif region_name == "us-central1":
        return "us-central1-b"
    elif region_name == "us-west1":
        return "us-west1-a"
    elif region_name == "us-west2":
        return "us-west2-a"
    elif region_name == "us-west3":
        return "us-west3-a"
    elif region_name == "us-west4":
        return "us-west4-a"


    elif region_name == "us-east4":
        return "us-east4-a"
    elif region_name == "us-east1":
        return "us-east1-b"
    elif region_name == "southamerica-east1":
        return "southamerica-east1-a"

    elif region_name == "europe-north1":
        return "europe-north1-a"

    elif region_name == "europe-west1":
        return "europe-west1-b"
    elif region_name == "europe-west2":
        return "europe-west2-a"

    elif region_name == "europe-west3":
        return "europe-west3-a"
    elif region_name == "europe-west4":
        return "europe-west4-b"
    elif region_name == "europe-west6":
        return "europe-west6-b"

    elif region_name == "asia-south1":
        return "asia-south1-a"

    elif region_name == "asia-southeast1":
        return "asia-southeast1-a"
    elif region_name == "asia-east1":
        return "asia-east1-a"
    elif region_name == "asia-east2":
        return "asia-east2-a"

    elif region_name == "asia-northeast1":
        return "asia-northeast1-a"
    elif region_name == "asia-northeast2":
        return "asia-northeast2-a"
    elif region_name == "asia-northeast3":
        return "asia-northeast3-a"
    elif region_name == "australia-southeast1":
        return "australia-southeast1-a"
    else:
        logging.error('Region zone mapper got an unknown region')
        return "us-central1-b"

def region_human_to_ce_readable(region_name):
    """ convert a human readable region to CE readable region """
    if region_name == "Montreal, Canada":
        return "northamerica-northeast1"
    elif region_name == "Western US: Oregon":
        return "us-west1"
    elif region_name == "Western US: Los Angeles":
        return "us-west2"

    elif region_name == "Western US: Salt Lake City":
        return "us-west3"
    elif region_name == "Western US: Las Vegas":
        return "us-west4"

    elif region_name == "Central US: Iowa":
        return "us-central1"
    elif region_name == "Eastern US: South Carolina":
        return "us-east1"
    elif region_name == "Eastern US: Northern Virginia":
        return "us-east4"
    elif region_name == "Sao Paulo, Brazil":
        return "southamerica-east1"

    elif region_name == "North Europe: Hamina, Finland":
        return "europe-north1"

    elif region_name == "Western Europe: Belgium":
        return "europe-west1"
    elif region_name == "Western Europe: London U.K.":
        return "europe-west2"

    elif region_name == "Western Europe: Frankfurt, Germany":
        return "europe-west3"
    elif region_name == "Western Europe: Eemshaven, Netherlands":
        return "europe-west4"

    elif region_name == "Western Europe: Zurich":
        return "europe-west6"

    elif region_name == "South Asia: Mumbai, India":
        return "asia-south1"

    elif region_name == "Southeast Asia: Singapore":
        return "asia-southeast1"
    elif region_name == "East Asia: Taiwan":
        return "asia-east1"
    elif region_name == "East Asia: Hong Kong":
        return "asia-east2"

    elif region_name == "Northeast Asia: Tokyo":
        return "asia-northeast1"

    elif region_name == "Northeast Asia: Osaka":
        return "asia-northeast2"
    elif region_name == "Northeast Asia: Seoul":
        return "asia-northeast3"

    elif region_name == "Southeast Australia: Sydney":
        return "australia-southeast1"
    elif region_name == "Central US: Iowa":
        return "us-central1"
    else:
        logging.error('region_human_to_ce_readable got an unknown region')
        return "us-central1"

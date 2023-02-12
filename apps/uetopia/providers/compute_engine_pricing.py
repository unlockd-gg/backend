## Compute engine HOURLY prices
# from: https://cloud.google.com/compute/pricing
compute_engine_pricing_dict = {
    'northamerica-northeast1': { #Montreal
        'n1-standard-1' : 0.0523,
        'n1-standard-2' : 0.1046,
        'n1-standard-4' : 0.2092,
        'n1-standard-8' : 0.4184,
        'n1-standard-16' : 0.8368,
        'n1-standard-32' : 1.6736,
        'n1-standard-64' : 3.3472
    },
    'us-central1': { #Iowa
        'n1-standard-1' : 0.0475,
        'n1-standard-2' : 0.0950,
        'n1-standard-4' : 0.19,
        'n1-standard-8' : 0.38,
        'n1-standard-16' : 0.76,
        'n1-standard-32' : 1.52,
        'n1-standard-64' : 3.04
    },
    'us-west1': { #Oregon
        'n1-standard-1' : 0.0475,
        'n1-standard-2' : 0.0950,
        'n1-standard-4' : 0.19,
        'n1-standard-8' : 0.38,
        'n1-standard-16' : 0.76,
        'n1-standard-32' : 1.52,
        'n1-standard-64' : 3.04
    },

    'us-west2': { #Los Angeles
        'n1-standard-1' : 0.0571,
        'n1-standard-2' : 0.1142,
        'n1-standard-4' : 0.2284,
        'n1-standard-8' : 0.4568,
        'n1-standard-16' : 0.9136,
        'n1-standard-32' : 1.8272,
        'n1-standard-64' : 3.6544
    },
    'us-west3': { #Salt Lake City
        'n1-standard-1' : 0.0571,
        'n1-standard-2' : 0.1142,
        'n1-standard-4' : 0.2284,
        'n1-standard-8' : 0.4568,
        'n1-standard-16' : 0.9136,
        'n1-standard-32' : 1.8272,
        'n1-standard-64' : 3.6544
    },
    'us-west4': { #Las Vegas
        'n1-standard-1' : 0.0535,
        'n1-standard-2' : 0.1070,
        'n1-standard-4' : 0.2140,
        'n1-standard-8' : 0.4280,
        'n1-standard-16' : 0.8560,
        'n1-standard-32' : 1.7120,
        'n1-standard-64' : 3.4240
    },

    'us-east4': { #Nothern Verginia
        'n1-standard-1' : 0.0535,
        'n1-standard-2' : 0.107,
        'n1-standard-4' : 0.214,
        'n1-standard-8' : 0.428,
        'n1-standard-16' : 0.856,
        'n1-standard-32' : 1.712,
        'n1-standard-64' : 3.424
    },
    'us-east1': { #South Carolina
        'n1-standard-1' : 0.0475,
        'n1-standard-2' : 0.0950,
        'n1-standard-4' : 0.19,
        'n1-standard-8' : 0.38,
        'n1-standard-16' : 0.76,
        'n1-standard-32' : 1.52,
        'n1-standard-64' : 3.04
    },
    'southamerica-east1': { # Sao Paulo, Brazil
        'n1-standard-1' : 0.0754,
        'n1-standard-2' : 0.1508,
        'n1-standard-4' : 0.3017,
        'n1-standard-8' : 0.6034,
        'n1-standard-16' : 1.2068,
        'n1-standard-32' : 2.4136,
        'n1-standard-64' : 4.8271
    },

    'europe-north1': { #Finland
        'n1-standard-1' : 0.0523,
        'n1-standard-2' : 0.1046,
        'n1-standard-4' : 0.2092,
        'n1-standard-8' : 0.4184,
        'n1-standard-16' : 0.8368,
        'n1-standard-32' : 1.6736,
        'n1-standard-64' : 3.3472
    },

    'europe-west1': { #Belgium
        'n1-standard-1' : 0.0523,
        'n1-standard-2' : 0.1046,
        'n1-standard-4' : 0.2092,
        'n1-standard-8' : 0.4184,
        'n1-standard-16' : 0.8368,
        'n1-standard-32' : 1.6736,
        'n1-standard-64' : 3.3472
    },
    'europe-west2': { # London
        'n1-standard-1' : 0.0612,
        'n1-standard-2' : 0.1224,
        'n1-standard-4' : 0.2448,
        'n1-standard-8' : 0.4896,
        'n1-standard-16' : 0.9792,
        'n1-standard-32' : 1.9584,
        'n1-standard-64' : 3.9168
    },
    'europe-west3': { # Frankfurt
        'n1-standard-1' : 0.0612,
        'n1-standard-2' : 0.1224,
        'n1-standard-4' : 0.2448,
        'n1-standard-8' : 0.4896,
        'n1-standard-16' : 0.9792,
        'n1-standard-32' : 1.9584,
        'n1-standard-64' : 3.9168
    },
    'europe-west4': { # Eemshaven, Netherlands
        'n1-standard-1' : 0.0523,
        'n1-standard-2' : 0.1046,
        'n1-standard-4' : 0.2092,
        'n1-standard-8' : 0.4184,
        'n1-standard-16' : 0.8368,
        'n1-standard-32' : 1.6736,
        'n1-standard-64' : 3.3472
    },
    'europe-west6': { # Zurich
        'n1-standard-1' : 0.0665,
        'n1-standard-2' : 0.1329,
        'n1-standard-4' : 0.2658,
        'n1-standard-8' : 0.5317,
        'n1-standard-16' : 1.0634,
        'n1-standard-32' : 2.1268,
        'n1-standard-64' : 4.2535
    },
    'asia-south1': { # Mumbai, India
        'n1-standard-1' : 0.0570,
        'n1-standard-2' : 0.1141,
        'n1-standard-4' : 0.2282,
        'n1-standard-8' : 0.4564,
        'n1-standard-16' : 0.9127,
        'n1-standard-32' : 1.8255,
        'n1-standard-64' : 3.6510
    },
    'asia-southeast1': { #Singapore
        'n1-standard-1' : 0.0586,
        'n1-standard-2' : 0.1172,
        'n1-standard-4' : 0.2344,
        'n1-standard-8' : 0.4688,
        'n1-standard-16' : 0.9376,
        'n1-standard-32' : 1.8752,
        'n1-standard-64' : 3.7504
    },
    'asia-east1': { # Taiwan
        'n1-standard-1' : 0.055,
        'n1-standard-2' : 0.11,
        'n1-standard-4' : 0.22,
        'n1-standard-8' : 0.44,
        'n1-standard-16' : 0.88,
        'n1-standard-32' : 1.76,
        'n1-standard-64' : 3.52
    },
    'asia-east2': { # Hong Kong
        'n1-standard-1' : 0.0665,
        'n1-standard-2' : 0.1329,
        'n1-standard-4' : 0.2658,
        'n1-standard-8' : 0.5317,
        'n1-standard-16' : 1.0634,
        'n1-standard-32' : 2.1268,
        'n1-standard-64' : 4.2535
    },
    'asia-northeast1': { #Tokyo
        'n1-standard-1' : 0.061,
        'n1-standard-2' : 0.122,
        'n1-standard-4' : 0.244,
        'n1-standard-8' : 0.488,
        'n1-standard-16' : 0.976,
        'n1-standard-32' : 1.952,
        'n1-standard-64' : 3.904
    },
    'asia-northeast2': { # Osaka
        'n1-standard-1' : 0.061,
        'n1-standard-2' : 0.122,
        'n1-standard-4' : 0.244,
        'n1-standard-8' : 0.488,
        'n1-standard-16' : 0.976,
        'n1-standard-32' : 1.952,
        'n1-standard-64' : 3.904
    },
    'asia-northeast3': { # Seoul
        'n1-standard-1' : 0.061,
        'n1-standard-2' : 0.122,
        'n1-standard-4' : 0.244,
        'n1-standard-8' : 0.488,
        'n1-standard-16' : 0.976,
        'n1-standard-32' : 1.952,
        'n1-standard-64' : 3.904
    },
    'australia-southeast1': { # Sydney
        'n1-standard-1' : 0.0674,
        'n1-standard-2' : 0.1348,
        'n1-standard-4' : 0.2697,
        'n1-standard-8' : 0.5393,
        'n1-standard-16' : 1.0787,
        'n1-standard-32' : 2.1574,
        'n1-standard-64' : 4.3147
    },
}

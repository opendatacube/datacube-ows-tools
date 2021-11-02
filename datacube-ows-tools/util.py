from owslib.wms import WebMapService

def enclosed_bbox(bbox):
    lon_min, lat_min, lon_max, lat_max = bbox
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min

    return (
        lon_min + 0.8 * lon_range,
        lat_min + 0.8 * lat_range,
        lon_max - 0.8 * lon_range,
        lat_max - 0.8 * lat_range,
    )


def fixed_bbox(bbox):
    return (
        15028131.257091936,
        -2504688.542848654,
        15654303.392804097,
        -1878516.4071364924,
    )


def disjoint_bbox(bbox):
    lon_min, lat_min, lon_max, lat_max = bbox
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min

    return (
        lon_min - 0.4 * lon_range,
        lat_min - 0.4 * lat_range,
        lon_min - 0.2 * lon_range,
        lat_min - 0.2 * lat_range,
    )

def v7_catalog_list(catalog_data, catalog_name):
    catalog_list = []
    for catalog in catalog_data["catalog"]:
        if catalog["name"] == catalog_name:
            for group in catalog["items"]:
                for item in group["items"]:
                    if "layers" in item:
                        catalog_list.append(item["layers"])
                    else:
                        for i in item["items"]:
                            if "layers" in i:
                                catalog_list.append(i["layers"])

    return catalog_list

def wms_endpoint_layers_list(wms_endpoint_url):
    prod_wms = WebMapService(url=wms_endpoint_url + "/wms", version="1.3.0", timeout=120)
    return list(prod_wms.contents)


def v8_catalog_list(catalog_data, wms_endpoint):
    catalog_list = []
    for catalog in catalog_data["catalog"]:
        if catalog["members"]:
            for item in catalog["members"]:
                if "url" in item:
                     if item["url"] == wms_endpoint +'/':
                        catalog_list.append(item["layers"])
                else:
                    for subitem in item["members"]:
                        if "url" in subitem:
                            if subitem["url"] == wms_endpoint + '/':
                                catalog_list.append(subitem["layers"])
                        else:
                            for subsubitem in subitem["members"]:
                                if "url" in subsubitem:
                                    if subsubitem["url"] == wms_endpoint + '/':
                                        catalog_list.append(subsubitem["layers"])
                                else:
                                    for subsubsubitem in subsubitem["members"]:
                                        if "url" in subsubsubitem:
                                            if subsubsubitem["url"] == wms_endpoint + '/':
                                                catalog_list.append(subsubsubitem["layers"])

    print(catalog_data)

    return catalog_list
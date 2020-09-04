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

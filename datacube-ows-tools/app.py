import os
import sys
import uuid
import json
import urllib
from flask import Flask, request, send_file, Response, send_from_directory
from flask import render_template, jsonify, json as flask_json
from flask_s3 import FlaskS3
from owslib.wms import WebMapService
from .util import disjoint_bbox, enclosed_bbox, fixed_bbox, v7_catalog_list, wms_endpoint_layers_list, v8_catalog_list

app = Flask(__name__, static_url_path=os.getenv("STATIC_PATH", None))
app.config["FLASKS3_BUCKET_NAME"] = "dea-web-webtools-static"
s3 = FlaskS3(app)

# for terria catalog generator
@app.route("/")
def terria_au():
    return render_template("terria-au.html")


@app.route("/terria-africa")
def terria_afr():
    return render_template("terria-afr.html")


# for terria WPS catalog generator
@app.route("/wps")
def terria_wps():
    return render_template("wps.html")


# for Testing
@app.route("/legend_comp")
def comp_legend():
    return render_template("legend-comparison.html")

@app.route("/getmap_comp")
def comp_getmap():

    return render_template("getmap-comparison.html")


@app.route("/getfeatureinfo_comp")
def comp_getfeatureinfo():
    return render_template("legend-comparison.html")


# Utility functions
@app.route("/getmap-url-generator", methods=["POST"])
def getmap_url_generator():
    getmap_urls = []
    paramsJson = request.get_json()
    stable_url = paramsJson['stable_url']
    bbox = paramsJson['bbox']
    crs = paramsJson['crs']

    # print(f"request.get_json(): {request.get_json()}")

    wms = WebMapService(url=stable_url + "/wms", version="1.3.0", timeout=120)
    contents = list(wms.contents)
    for layer_name in contents:
        layer = wms.contents[layer_name]

        # Layer bbox and crs info. Not really useful to us.
        # print(f"INFO: layer.boundingBox: {layer.boundingBox}")
        # bbox_raw = layer.boundingBox # Array of 4 coordinates, plus a format specification such as EPSG:3857
        # bbox_coordinates_url_encoded = '%2C'.join(map(str,bbox_raw[:4])) # First 4 elements -> str > separated with url encoding of comma.
        # crs_url_encoded = "EPSG%3A" + bbox_raw[4].split(':')[1] # Note format is always 'EPSG:n' where n is the format

        # print(f"INFO: Formatted: {bbox_coordinates_url_encoded, crs_url_encoded}")

        # fixed_espg = "EPSG%3A3857"
        # fixed_bbox = "15028131.257091936%2C-2504688.542848654%2C15654303.392804097%2C-1878516.4071364924"

        # bbox=bbox_coordinates_url_encoded
        # crs=crs_url_encoded

        # print(f"INFO: Using bbox: {bbox} CRS: {crs}")

        time = ""
        if layer.timepositions:
            time = layer.timepositions[len(layer.timepositions) // 2].strip()

        layers_url_list = []
        for style in layer.styles:
            # print(time, file=sys.stdout)
            
            url = f"{stable_url}wms?service=WMS&version=1.3.0&request=GetMap&layers={layer_name}&styles={style}&width=250&height=250&crs={crs}&bbox={bbox}&format=image%2Fpng&transparent=TRUE&bgcolor=0xFFFFFF&exceptions=XML&time={time}"
            layers_url_list.append({"style": style, "url": url})
        getmap_urls.append({"name": layer_name, "layersList": layers_url_list})

    return json.dumps(getmap_urls)

# Utility functions
@app.route("/catalog-match")
def catalog_match_checker():

    prod_wms_url = "https://ows.dea.ga.gov.au"
    prod_wms_layers = wms_endpoint_layers_list(prod_wms_url)
    dev_wms_url = "https://ows.dev.dea.ga.gov.au"
    dev_wms_layers = wms_endpoint_layers_list(dev_wms_url)

    terria_url = "https://raw.githubusercontent.com/GeoscienceAustralia/dea-config/master/dev/terria/terria-cube-v8.json"
    terria_catalog_json = urllib.request.urlopen(terria_url)
    # TODO: optimise this
    # this is to by pass JSONDecodeError: Invalid \escape: line 626 column 79 (char 68035)
    a = terria_catalog_json.read().decode(terria_catalog_json.headers.get_content_charset())
    b = a.replace("\\n", "iampin").replace("\\\n", "iamnotpin")
    terria_data = json.loads(b)


    dea_map_url = "https://raw.githubusercontent.com/GeoscienceAustralia/dea-config/master/dev/terria/dea-maps-v8.json"
    dea_catalog_json = urllib.request.urlopen(dea_map_url)
    dea_map_data = json.loads(dea_catalog_json.read())

    terria_prod_catalog_list = v8_catalog_list(terria_data, prod_wms_url)
    terria_prod_non_released = list(set(prod_wms_layers)-set(terria_prod_catalog_list))

    terria_dev_catalog_list = v8_catalog_list(terria_data, dev_wms_url)
    terria_dev_non_released = list(set(dev_wms_layers)-set(terria_dev_catalog_list))


    dea_map_catalog_list = v8_catalog_list(dea_map_data, prod_wms_url)
    dea_map_non_released = list(set(prod_wms_layers)-set(dea_map_catalog_list))

    return render_template("catalog-comparison.html", data={
        "dev_non_released": terria_dev_non_released,
        "dev_wms_layers": dev_wms_layers,
        "dev_catalog_list": terria_dev_catalog_list,
        "prod_non_released": terria_prod_non_released,
        "prod_wms_layers": prod_wms_layers,
        "prod_catalog_list": terria_prod_catalog_list,
        "dea_map_non_released": dea_map_non_released,
        "dea_map_catalog_list": dea_map_catalog_list,
    })


@app.route("/jsongenerator", methods=["POST"])
def json_generator():
    data = request.get_json()
    filename = str(uuid.uuid4())
    with open("/tmp/" + filename, "w", encoding="utf8") as f:
        json.dump(data, f)
    return {"filename": filename}


@app.route("/download_catalog", methods=["GET", "POST"])
def download_catalog():
    fname = request.form["filename"]
    cname = request.form["catalogname"]
    return send_from_directory(
        "/tmp",
        fname,
        as_attachment=True,
        mimetype="application/json",
        attachment_filename=cname,
    )


if __name__ == "__main__":
    app.run()

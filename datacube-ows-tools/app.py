import os
import sys
import uuid
import json
import urllib
from flask import Flask, request, send_file, Response, send_from_directory
from flask import render_template, jsonify, json as flask_json
from flask_s3 import FlaskS3
from owslib.wms import WebMapService
from .util import disjoint_bbox, enclosed_bbox, fixed_bbox

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
    stable_url = request.get_json()

    wms = WebMapService(url=stable_url + "/wms", version="1.3.0", timeout=120)
    contents = list(wms.contents)
    for layer in contents:
        test_layer_name = layer
        test_layer = wms.contents[test_layer_name]
        time = ""
        bbox = test_layer.boundingBoxWGS84
        layers_url_list = []
        fixed_espg = "EPSG%3A3857"
        fixed_bbox = "15028131.257091936%2C-2504688.542848654%2C15654303.392804097%2C-1878516.4071364924"
        if test_layer.timepositions:
            time = test_layer.timepositions[len(test_layer.timepositions) // 2].strip()
        for style in test_layer.styles:
            print(time, file=sys.stdout)

            url = f"{stable_url}wms?service=WMS&version=1.3.0&request=GetMap&layers={test_layer_name}&styles={style}&width=250&height=250&crs={fixed_espg}&bbox={fixed_bbox}&format=image%2Fpng&transparent=TRUE&bgcolor=0xFFFFFF&exceptions=XML&time={time}"
            layers_url_list.append({"style": style, "url": url})
        getmap_urls.append({"name": test_layer_name, "layersList": layers_url_list})

    # return jsonify(getmap_urls)
    return json.dumps(getmap_urls)

# Utility functions
@app.route("/catalog-match")
def catalog_match_checker():
    url = "https://raw.githubusercontent.com/GeoscienceAustralia/dea-config/master/dev/terria/dea.json"
    catalog_json = urllib.request.urlopen(url)
    data = json.loads(catalog_json.read())

    prod_catalog_list = []
    for catalog in data["catalog"]:
        if catalog["name"] == "DEA Production":
            for group in catalog["items"]:
                for item in group["items"]:
                    if "layers" in item:
                        prod_catalog_list.append(item["layers"])
                    else:
                        for i in item["items"]:
                            if "layers" in i:
                                prod_catalog_list.append(i["layers"])


    prod_wms_url = "https://ows.dea.ga.gov.au"
    prod_wms = WebMapService(url=prod_wms_url + "/wms", version="1.3.0", timeout=120)
    prod_wms_layers = list(prod_wms.contents)
    prod_non_released = list(set(prod_wms_layers)-set(prod_catalog_list))


    dev_catalog_list = []
    for catalog in data["catalog"]:
        if catalog["name"] == "DEA Development":
            for group in catalog["items"]:
                for item in group["items"]:
                    if "layers" in item:
                        dev_catalog_list.append(item["layers"])
                    else:
                        for i in item["items"]:
                            if "layers" in i:
                                dev_catalog_list.append(i["layers"])
    dev_wms_url = "https://ows.dev.dea.ga.gov.au"
    dev_wms = WebMapService(url=dev_wms_url + "/wms", version="1.3.0", timeout=120)
    dev_wms_layers = list(dev_wms.contents)
    dev_non_released = list(set(dev_wms_layers)-set(dev_catalog_list))
    return render_template("catalog-comparison.html", data={
        "dev_non_released": dev_non_released,
        "prod_non_released": prod_non_released,
        "prod_wms_layers": prod_wms_layers,
        "dev_wms_layers": dev_wms_layers,
        "dev_catalog_list": dev_catalog_list,
        "prod_catalog_list": prod_catalog_list,
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

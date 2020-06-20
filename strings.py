import requests
from table_num_mapper import mapper
import io
import zipfile

PATCH_URL = "http://patch.florensia-online.eu/LIVE/Patch/Update"


def get_strings():
    table_to_item_data = {}

    for key, mapper_value in mapper.items():
        key: str
        mapper_value: dict

        if mapper_value is None:
            continue

        table_to_item_data[key] = {}

        fname: str = mapper_value["file"]
        url = f"{PATCH_URL}/Data/DataTable/StringTable/{fname}.zip"

        resp = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zipf:
            data = zipf.read(fname).decode("utf-16")

            lines = data.splitlines()
            lines = lines[1:len(lines)-1]  # strips header and END__

            for index, line in enumerate(lines):
                code, _, _, english, *_, = line.split("\t")
                table_to_item_data[key][str(index)] = {
                    "code": code,
                    "name": english,
                    "type": mapper_value["name"],
                }

    return table_to_item_data

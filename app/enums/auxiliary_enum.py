EXPORTITEMS = [
    {"key": "translation", "label": "配置翻译"},
    {"key": "comparison", "label": "配置对比"},
    {"key": "traffic", "label": "打流表"}
]


def getExportItems(items=None):
    if not items:
        return EXPORTITEMS

    result = []
    for export_item in EXPORTITEMS:
        if export_item.get("key") in items:
            result.append(export_item)

    return result

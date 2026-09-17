def normalize_severity(value: str | None) -> str:
    mapping = {"critical":"Critical","high":"High","medium":"Medium","moderate":"Medium","low":"Low","info":"Informational","informational":"Informational"}
    return mapping.get(str(value or "informational").lower(), "Informational")

def cvss_for_severity(severity: str) -> float:
    return {"Critical":9.8,"High":8.1,"Medium":5.3,"Low":3.1,"Informational":0.0}.get(severity, 0.0)

"""Localized labels for API paths not known at integration build time.

Static entities use Home Assistant translation keys. Dynamic API fields use
a translated name template and these language-aware path labels.
"""
from __future__ import annotations

import re

CS = {
    "licenseplate": "registrační značka", "registrationplate": "registrační značka",
    "operations": "operace", "operation": "operace",
    "car": "vozidlo", "captured": "pořízení údajů",
    "render": "vizualizace vozidla", "renderurl": "obrázek vozidla",
    "vehiclerenderurl": "obrázek vozidla",
    "vehicle": "vozidlo", "vehicles": "vozidla", "status": "stav",
    "state": "stav", "charging": "nabíjení", "charge": "nabití",
    "battery": "baterie", "batterylevel": "úroveň baterie",
    "stateofcharge": "stav nabití", "stateofchargeinpercent": "stav nabití (%)",
    "targetstateofchargeinpercent": "cílové nabití (%)",
    "soc": "stav nabití", "range": "dojezd", "electricrange": "elektrický dojezd",
    "remainingrange": "zbývající dojezd", "odometer": "stav tachometru",
    "mileage": "nájezd", "tripmeter": "denní počítadlo",
    "distance": "vzdálenost", "distancecovered": "ujetá vzdálenost",
    "consumption": "spotřeba", "averageconsumption": "průměrná spotřeba",
    "totaldistance": "celková vzdálenost", "power": "výkon",
    "voltage": "napětí", "current": "proud", "temperature": "teplota",
    "outside": "venkovní", "inside": "vnitřní", "interior": "interiér",
    "exterior": "exteriér", "ambient": "okolní", "target": "cílová",
    "targettemperature": "cílová teplota", "airconditioning": "klimatizace",
    "auxiliaryheating": "nezávislé topení", "activeventilation": "aktivní větrání",
    "heating": "topení", "ventilation": "větrání", "climate": "klima",
    "doors": "dveře", "door": "dveře", "windows": "okna", "window": "okno",
    "front": "přední", "rear": "zadní", "left": "levé", "right": "pravé",
    "frontleft": "přední levé", "frontright": "přední pravé",
    "rearleft": "zadní levé", "rearright": "zadní pravé",
    "trunk": "kufr", "bonnet": "kapota", "hood": "kapota",
    "tailgate": "víko kufru", "lock": "zámek", "locked": "zamčeno",
    "unlocked": "odemčeno", "open": "otevřeno", "closed": "zavřeno",
    "lights": "světla", "light": "světlo", "lowbeam": "potkávací světla",
    "highbeam": "dálková světla", "parkinglights": "obrysová světla",
    "position": "poloha", "parking": "parkování", "latitude": "zeměpisná šířka",
    "longitude": "zeměpisná délka", "coordinates": "souřadnice",
    "address": "adresa", "location": "poloha", "fuel": "palivo",
    "fuellevel": "hladina paliva", "engine": "motor", "oil": "olej",
    "settings": "nastavení", "configuration": "konfigurace",
    "enabled": "povoleno", "active": "aktivní", "available": "dostupné",
    "connected": "připojeno", "plug": "konektor", "plugged": "zapojeno",
    "connector": "konektor", "cable": "kabel", "remaining": "zbývající",
    "time": "čas", "duration": "doba trvání", "start": "začátek",
    "end": "konec", "departure": "odjezd", "arrival": "příjezd",
    "estimated": "odhadovaný", "last": "poslední", "updated": "aktualizováno",
    "update": "aktualizace", "timestamp": "časové razítko",
    "name": "název", "model": "model", "vin": "VIN",
    "production": "výroba", "year": "rok", "registration": "registrace",
    "color": "barva", "colour": "barva", "image": "obrázek",
    "picture": "obrázek", "photo": "fotografie", "thumbnail": "náhled",
    "url": "URL", "uri": "URI", "icon": "ikona",
    "profile": "profil", "profiles": "profily", "chargingprofiles": "nabíjecí profily",
    "mode": "režim", "type": "typ", "value": "hodnota", "unit": "jednotka",
    "percent": "procenta", "inpercent": "(%)", "inkm": "(km)",
    "inmeters": "(m)", "inkwh": "(kWh)", "inkw": "(kW)",
    "inminutes": "(min)", "inseconds": "(s)", "incelsius": "(°C)",
    "inliters": "(l)", "speed": "rychlost", "pressure": "tlak",
    "health": "stav zdraví", "capacity": "kapacita", "maximum": "maximum",
    "minimum": "minimum", "max": "maximum", "min": "minimum",
    "total": "celkem", "average": "průměr", "is": "je", "has": "má",
    "in": "v", "of": "", "the": "", "data": "data", "error": "chyba",
    "errors": "chyby", "request": "požadavek", "requests": "požadavky",
}


def localized_path(path: str, language: str) -> str:
    """Readable path label; Czech for cs locales, English otherwise."""
    if not language.lower().startswith("cs"):
        return humanize_path(path)
    parts = []
    for segment in path.split("."):
        if segment.isdigit():
            parts.append(str(int(segment) + 1))
            continue
        words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", segment).replace("_", " ").split()
        key = segment.replace("_", "").lower()
        if key in CS:
            parts.append(CS[key])
        else:
            parts.extend(CS.get(word.lower(), word.lower()) for word in words)
    result = " ".join(part for part in parts if part).strip()
    if result.lower().startswith("operace ") and result.lower().endswith(" název"):
        result = result[:-6] + " – název"
    if path.lower() == "status.carcaptured.timestamp":
        return "Čas pořízení údajů o vozidle"
    return result[:1].upper() + result[1:] if result else path


def humanize_path(path: str) -> str:
    parts = []
    for segment in path.split("."):
        if segment.isdigit():
            parts.append(str(int(segment) + 1))
        else:
            parts.append(re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", segment).replace("_", " ").lower())
    text = " ".join(parts)
    return text[:1].upper() + text[1:]

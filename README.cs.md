<p align="center">
  <img src="https://raw.githubusercontent.com/JS-CODE-LAB/api4-czech-cars/main/custom_components/skoda_public/brand/logo%402x.png" alt="API 4 Czech Cars" width="320">
</p>

# API 4 Czech Cars (public API) pro Home Assistant

Integrace Home Assistantu pro připojená vozidla ŠKODA postavená na oficiálním
[MyŠkoda Public API](https://public.api.connect.skoda-auto.cz/docs). English: [README.md](README.md).

> **Neoficiální komunitní projekt.** Nemá žádné spojení se společností ŠKODA AUTO a.s., koncernem Volkswagen,
> Home Assistantem ani HACS. Příkazy ovládají skutečné vozidlo – před použitím si přečti
> [UPOZORNĚNÍ](DISCLAIMER.md) (včetně bezpečnostních pokynů).

## Funkce
Z každé hodnoty, kterou API vrátí, vznikne entita (nová pole se doplní sama):

| Platforma | Co dostaneš |
|---|---|
| `sensor` | Stav baterie, **dojezd (km)**, tachometr, palivo, stav a nastavení nabíjení, nabíjecí profily, klimatizace, stav dveří/oken/světel … (jednotky a třídy zařízení se odvozují z názvů polí) |
| `binary_sensor` | Všechna pole ano/ne (např. zamčené dveře), **nabíjení baterie** |
| `device_tracker` | Poloha parkování |
| `switch` | Start/stop nabíjení, přídavné topení, aktivní větrání |
| `number` | Limit nabití (50–100 %, krok 10) |
| `climate` | Zapnutí/vypnutí klimatizace a cílová teplota |
| diagnostika | Zbývající požadavky API, platnost API klíče, vynechané části dat |

Ovládací entity se zobrazí jen tehdy, když vozidlo příslušnou funkci hlásí. Stav baterie a ikona nabíjení jsou
nahoře na stránce zařízení.

Služba `skoda_public.request` pošle libovolný požadavek na `/api/v1/vehicles/{vin}{path}` (např. pro funkce bez
vlastní entity).

## Požadavky
- Home Assistant **2026.3.0** nebo novější (obrázky značky jsou součástí integrace).
- Vozidlo ŠKODA s aktivní službou MyŠkoda a **API klíč MyŠkoda** pro toto vozidlo
  (vytvoříš ho v aplikaci MyŠkoda: <https://go.skoda.eu/api-keys>).

## Instalace

### HACS (vlastní repozitář)
1. HACS → ⋮ → **Vlastní repozitáře**.
2. Repozitář: `https://github.com/JS-CODE-LAB/api4-czech-cars`, typ **Integrace** → Přidat.
3. V HACS najdi **API 4 Czech Cars (public API)** → **Stáhnout**.
4. Restartuj Home Assistant.

### Ručně
Zkopíruj `custom_components/skoda_public` do `<config>/custom_components/` a restartuj.

## Nastavení
Nastavení → Zařízení a služby → **Přidat integraci** → *API 4 Czech Cars (public API)*, zadej API klíč a VIN.
Každé vozidlo se přidává zvlášť.

### Možnosti
| Možnost | Význam |
|---|---|
| Interval aktualizace | Sekundy mezi dotazy (výchozí 600, minimum 300). |
| Klimatizace bez externího napájení | Povolí start klimatizace, i když auto není zapojené. |
| Délka přídavného topení | Doba běhu topení v sekundách (výchozí 600). |
| S-PIN | API ho vyžaduje pro přídavné topení. Home Assistant ho ukládá nešifrovaně. |

## Dobré vědět
- **Limit:** API povoluje zhruba 20 požadavků za hodinu na vozidlo. Každý příkaz navíc vyvolá jedno obnovení
  stavu asi za 30 s.
- **Teplota klimatizace:** API neumí nastavit jen teplotu. Při vypnuté klimatizaci se změna cíle jen uloží v HA
  a použije se při dalším zapnutí. Při běžící klimatizaci se odešle nový start.
- **Vozidlo může příkaz odmítnout** (nepodporuje, je offline, nízká baterie …); důvod se zobrazí v HA.
- Jako entity chybí změna režimu nabíjení a úprava nabíjecích profilů (použij službu).
- Rozsah dat závisí na vozidle; nepodporované části API vynechá.

## Řešení potíží
- *Chyba ověření / opětovné ověření:* API klíč vypršel nebo nepatří k VINu – vytvoř nový a zadej ho, až se HA zeptá.
  Diagnostický senzor *API key expires at* pomůže klíč obnovit včas.
- *Příliš mnoho požadavků (429):* zvyš interval aktualizace.
- Chyby nahlašuj v [Issues](../../issues) a předtím **odstraň VIN, API klíč, S-PIN a GPS polohu**.

## Soukromí
Data putují jen mezi tvým Home Assistantem a API společnosti ŠKODA. Žádná telemetrie. Přihlašovací údaje a S-PIN
jsou v konfiguraci Home Assistantu (nešifrovaně, součástí záloh). Poloha vozidla se ukládá do historie HA, pokud ji
nevyřadíš.

## Poděkování
Podrobnosti o endpointech jsem ověřoval podle open-source knihovny
[skoda-public-api](https://github.com/mobility-lab-vsb/skoda-public-api) a oficiální dokumentace API.
Žádný její kód není součástí integrace.

## Licence
[MIT](LICENSE) – viz také [UPOZORNĚNÍ](DISCLAIMER.md). Ochranné známky patří jejich vlastníkům.


## Novinky ve verzi 0.3.0

Dynamicky objevené senzory a binární senzory mají atribut `functional_group` pro přehledné rozdělení do oblastí baterie, nabíjení, stav vozidla, klimatizace, motor, poloha, informace o vozidle a diagnostika. Home Assistant nepodporuje vlastní oddíly uvnitř jednoho zařízení, proto zůstává jedno zařízení na vozidlo a členění lze využít na dashboardu. Přibylo diagnostické tlačítko pro ruční aktualizaci (spotřebuje API požadavek) a čas poslední úspěšné aktualizace. Dosavadní identifikátory entit zůstávají zachovány.

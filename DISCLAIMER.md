# Disclaimer / Upozornění

## English

**Unofficial project.** "API 4 Czech Cars (public API)" is an independent, community-made
integration. It is **not** affiliated with, authorised, sponsored or endorsed by ŠKODA AUTO a.s.,
the Volkswagen Group, Home Assistant, Nabu Casa or HACS. ŠKODA and related names and logos are
trademarks of their respective owners and are used here only to describe compatibility. The logo
shipped in this repository is the project's own and contains no ŠKODA trademarks.

**Use of the API.** The integration talks to the MyŠkoda Public API
(https://public.api.connect.skoda-auto.cz/docs). That API is provided by ŠKODA AUTO under its own terms,
which can change at any time; its documentation describes it as intended for personal use. You are
solely responsible for complying with the current terms, including rate limits. Do not use this
integration to build commercial services. The API or your vehicle can stop working with it at any time.

**Remote commands act on a real vehicle.** The generic `skoda_public.request` action can issue remote commands from automations without additional confirmation; restrict access to Home Assistant and review automations before enabling them.

**Remote commands act on a real vehicle.** Charging, air conditioning, auxiliary heating and
ventilation commands are sent to your car. Make sure it is safe to run them.
**Never run a fuel-fired auxiliary heater or leave an engine running in a closed or poorly
ventilated space (e.g. a closed garage): exhaust gases can cause serious injury or death.**
Commands can drain the 12 V battery, interfere with scheduled charging, or be refused or executed
with delay by the vehicle. Do not rely on this integration for safety-critical purposes.

**Privacy and security.**
- Your API key, VIN and (optionally) S-PIN are stored by Home Assistant in its configuration
  storage, which is not encrypted and is included in backups. Protect your instance and backups.
- Vehicle data (including the parking position) is sent only between your Home Assistant and
  ŠKODA's API. The integration has no telemetry and sends nothing to the author.
- Position and other vehicle data become part of your Home Assistant history. Exclude entities from the
  recorder if you do not want this, and remove personal data (VIN, API key, location) from logs and
  bug reports before sharing them.

**No warranty.** The software is provided "as is" under the MIT License, without warranty of any
kind. To the maximum extent permitted by law the author is not liable for any damage, data loss,
vehicle malfunction, battery discharge, charging costs, account restrictions or other consequences
of using it.

## Česky

**Neoficiální projekt.** „API 4 Czech Cars (public API)“ je nezávislá komunitní integrace. **Nemá**
žádné spojení se společností ŠKODA AUTO a.s., koncernem Volkswagen, Home Assistantem, Nabu Casa ani
HACS a tyto subjekty ji neschvalují ani nepodporují. ŠKODA a související názvy a loga jsou ochranné
známky příslušných vlastníků a zde se používají jen k popisu kompatibility. Logo v tomto repozitáři je
vlastní logo projektu a neobsahuje ochranné známky ŠKODA.

**Používání API.** Integrace komunikuje s MyŠkoda Public API
(https://public.api.connect.skoda-auto.cz/docs). API poskytuje ŠKODA AUTO podle vlastních podmínek,
které se mohou kdykoli změnit; dokumentace ho popisuje jako určené pro osobní použití. Za dodržování
aktuálních podmínek včetně limitů požadavků odpovídáš sám. Integraci nepoužívej pro komerční služby.
API nebo vozidlo mohou s integrací kdykoli přestat fungovat.

**Obecná akce `skoda_public.request` může spouštět příkazy vozidla z automatizací bez dalšího potvrzení.** Omezte přístup k Home Assistantu a před zapnutím automatizace zkontrolujte.

**Příkazy ovládají skutečné vozidlo.** Příkazy pro nabíjení, klimatizaci, přídavné topení a větrání se
odesílají do tvého auta. Přesvědč se, že je jejich spuštění bezpečné.
**Nikdy nespouštěj palivové přídavné topení ani nenech běžet motor v uzavřeném či špatně větraném
prostoru (např. v zavřené garáži): výfukové plyny mohou způsobit vážné zranění nebo smrt.**
Příkazy mohou vybít 12V baterii, zasáhnout do plánovaného nabíjení nebo je vozidlo odmítne či provede
se zpožděním. Na integraci nespoléhej v bezpečnostně kritických situacích.

**Soukromí a bezpečnost.**
- API klíč, VIN a (volitelně) S-PIN ukládá Home Assistant do své konfigurace, která není šifrovaná
  a je součástí záloh. Chraň svou instalaci i zálohy.
- Data vozidla (včetně polohy parkování) se přenášejí jen mezi tvým Home Assistantem a API společnosti
  ŠKODA. Integrace neobsahuje telemetrii a autorovi nic neposílá.
- Poloha a další data se ukládají do historie Home Assistantu. Pokud to nechceš, vyřaď entity z recorderu
  a před sdílením logů a hlášení chyb z nich odstraň osobní údaje (VIN, API klíč, polohu).

**Bez záruky.** Software je poskytován „tak, jak je“, podle licence MIT, bez jakékoli záruky. V maximální
míře povolené zákonem autor neodpovídá za žádné škody, ztrátu dat, poruchu vozidla, vybití baterie, náklady
na nabíjení, omezení účtu ani jiné následky jeho používání.

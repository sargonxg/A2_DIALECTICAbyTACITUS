"""
Seed DIALECTICA Neo4j with massively expanded conflict data.
3 cases × Full Tier 3 (all 15 node types, all 20 edge types).
"""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone

from neo4j import AsyncGraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://f53b9bee.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "05NMpTmlUQ8FYGRk2aq5uZ6LihYpm7GH5Q4w2YIjeyM")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def uid() -> str:
    return str(uuid.uuid4())[:12]


async def run_query(session, query: str, params: dict | None = None):
    result = await session.run(query, params or {})
    return await result.consume()


async def create_node(session, ws: str, tenant: str, label: str, props: dict):
    nid = props.get("id", uid())
    props["id"] = nid
    props["workspace_id"] = ws
    props["tenant_id"] = tenant
    props["created_at"] = datetime.now(timezone.utc).isoformat()
    props["category"] = "MOCK_DIALECTICA"
    prop_str = ", ".join(f"n.{k} = ${k}" for k in props)
    q = f"MERGE (n:{label} {{id: $id}}) SET {prop_str} SET n:MOCK_DIALECTICA RETURN n.id"
    await run_query(session, q, props)
    return nid


async def create_edge(session, ws: str, tenant: str, edge_type: str, src: str, tgt: str, src_label: str, tgt_label: str, props: dict | None = None):
    eid = uid()
    p = props or {}
    p["id"] = eid
    p["workspace_id"] = ws
    p["tenant_id"] = tenant
    p["type"] = edge_type
    p["source_id"] = src
    p["target_id"] = tgt
    p["source_label"] = src_label
    p["target_label"] = tgt_label
    p["category"] = "MOCK_DIALECTICA"
    prop_str = ", ".join(f"r.{k} = ${k}" for k in p)
    q = f"""
    MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
    MERGE (a)-[r:{edge_type} {{id: $id}}]->(b)
    SET {prop_str}
    """
    await run_query(session, q, p)
    return eid


# ═══════════════════════════════════════════════════════════════════
# CASE 1: JCPOA — Full Geopolitical Complexity
# ═══════════════════════════════════════════════════════════════════

async def seed_jcpoa(session):
    ws = "jcpoa-full"
    t = "tacitus"
    print("  Seeding JCPOA (macro geopolitical)...")

    # ── LOCATIONS ──
    loc_vienna = await create_node(session, ws, t, "Location", {"id": "loc-vienna", "name": "Vienna", "location_type": "city", "country_code": "AUT", "latitude": 48.2082, "longitude": 16.3738})
    loc_geneva = await create_node(session, ws, t, "Location", {"id": "loc-geneva", "name": "Geneva", "location_type": "city", "country_code": "CHE", "latitude": 46.2044, "longitude": 6.1432})
    loc_tehran = await create_node(session, ws, t, "Location", {"id": "loc-tehran", "name": "Tehran", "location_type": "city", "country_code": "IRN", "latitude": 35.6892, "longitude": 51.389})
    loc_washington = await create_node(session, ws, t, "Location", {"id": "loc-washington", "name": "Washington D.C.", "location_type": "city", "country_code": "USA", "latitude": 38.9072, "longitude": -77.0369})
    loc_new_york = await create_node(session, ws, t, "Location", {"id": "loc-newyork", "name": "New York (UN HQ)", "location_type": "city", "country_code": "USA", "latitude": 40.749, "longitude": -73.968})
    loc_baghdad = await create_node(session, ws, t, "Location", {"id": "loc-baghdad", "name": "Baghdad", "location_type": "city", "country_code": "IRQ", "latitude": 33.3152, "longitude": 44.3661})
    loc_natanz = await create_node(session, ws, t, "Location", {"id": "loc-natanz", "name": "Natanz Nuclear Facility", "location_type": "building", "country_code": "IRN", "latitude": 33.7214, "longitude": 51.7275})
    loc_fordow = await create_node(session, ws, t, "Location", {"id": "loc-fordow", "name": "Fordow Enrichment Plant", "location_type": "building", "country_code": "IRN", "latitude": 34.883, "longitude": 51.2})
    loc_iran = await create_node(session, ws, t, "Location", {"id": "loc-iran", "name": "Iran", "location_type": "country", "country_code": "IRN"})
    loc_usa = await create_node(session, ws, t, "Location", {"id": "loc-usa", "name": "United States", "location_type": "country", "country_code": "USA"})

    # Location hierarchy
    await create_edge(session, ws, t, "WITHIN", "loc-tehran", "loc-iran", "Location", "Location")
    await create_edge(session, ws, t, "WITHIN", "loc-natanz", "loc-iran", "Location", "Location")
    await create_edge(session, ws, t, "WITHIN", "loc-fordow", "loc-iran", "Location", "Location")
    await create_edge(session, ws, t, "WITHIN", "loc-washington", "loc-usa", "Location", "Location")

    # ── ACTORS (15 — full geopolitical web) ──
    iran = await create_node(session, ws, t, "Actor", {"id": "iran", "name": "Islamic Republic of Iran", "actor_type": "state", "description": "Theocratic republic, NPT signatory, pursuing nuclear program since 1950s. Supreme Leader holds final authority on nuclear policy.", "influence_score": 0.75, "regime_type": "theocratic republic", "iso_code": "IRN", "sovereignty": "full"})
    usa = await create_node(session, ws, t, "Actor", {"id": "usa", "name": "United States of America", "actor_type": "state", "description": "Global hegemon, primary sanctions architect, nuclear weapons state. Policy oscillates between engagement (Obama) and maximum pressure (Trump).", "influence_score": 0.95, "regime_type": "federal republic", "iso_code": "USA", "sovereignty": "full"})
    russia = await create_node(session, ws, t, "Actor", {"id": "russia", "name": "Russian Federation", "actor_type": "state", "description": "P5+1 member, built Bushehr reactor, strategic interest in Iran as counterbalance to US. Arms supplier and diplomatic shield.", "influence_score": 0.82, "regime_type": "federal republic", "iso_code": "RUS", "sovereignty": "full"})
    china = await create_node(session, ws, t, "Actor", {"id": "china", "name": "People's Republic of China", "actor_type": "state", "description": "P5+1 member, major Iranian oil buyer, opposes unilateral sanctions. Belt and Road interests in Iran.", "influence_score": 0.88, "regime_type": "one-party state", "iso_code": "CHN", "sovereignty": "full"})
    uk = await create_node(session, ws, t, "Actor", {"id": "uk", "name": "United Kingdom", "actor_type": "state", "description": "E3 member, close US ally but maintained JCPOA commitment post-withdrawal. INSTEX co-founder.", "influence_score": 0.7, "iso_code": "GBR"})
    france = await create_node(session, ws, t, "Actor", {"id": "france", "name": "French Republic", "actor_type": "state", "description": "E3 member, proposed supplemental deal on ballistic missiles. Macron attempted US-Iran bridge diplomacy.", "influence_score": 0.68, "iso_code": "FRA"})
    germany = await create_node(session, ws, t, "Actor", {"id": "germany", "name": "Federal Republic of Germany", "actor_type": "state", "description": "E3 member, Iran's largest European trade partner pre-sanctions. INSTEX co-founder.", "influence_score": 0.65, "iso_code": "DEU"})
    eu = await create_node(session, ws, t, "Actor", {"id": "eu", "name": "European Union", "actor_type": "organization", "description": "JCPOA coordinator (HR/VP Mogherini/Borrell), created INSTEX trade mechanism to bypass US sanctions.", "influence_score": 0.72, "org_type": "supranational", "sector": "government"})
    iaea = await create_node(session, ws, t, "Actor", {"id": "iaea", "name": "International Atomic Energy Agency", "actor_type": "organization", "description": "UN watchdog, verifies Iran nuclear commitments. Access to declared sites; disputes over undeclared sites.", "influence_score": 0.65, "org_type": "international", "sector": "security"})
    israel = await create_node(session, ws, t, "Actor", {"id": "israel", "name": "State of Israel", "actor_type": "state", "description": "Undeclared nuclear power, considers Iranian nuclear capability existential threat. Conducted sabotage operations (Stuxnet, assassinations).", "influence_score": 0.72, "iso_code": "ISR"})
    saudi = await create_node(session, ws, t, "Actor", {"id": "saudi", "name": "Kingdom of Saudi Arabia", "actor_type": "state", "description": "Iran's primary regional rival (Sunni vs Shia axis). Announced reciprocal enrichment policy. Supported maximum pressure.", "influence_score": 0.68, "iso_code": "SAU"})
    irgc = await create_node(session, ws, t, "Actor", {"id": "irgc", "name": "Islamic Revolutionary Guard Corps", "actor_type": "organization", "description": "Iran's elite military force, controls ballistic missile program and proxy network. Designated as FTO by US in 2019.", "influence_score": 0.6, "org_type": "military"})
    khamenei = await create_node(session, ws, t, "Actor", {"id": "khamenei", "name": "Ayatollah Ali Khamenei", "actor_type": "person", "description": "Supreme Leader of Iran since 1989. Final authority on nuclear policy. Issued fatwa against nuclear weapons but maintains ambiguity.", "influence_score": 0.85, "role_title": "Supreme Leader"})
    rouhani = await create_node(session, ws, t, "Actor", {"id": "rouhani", "name": "Hassan Rouhani", "actor_type": "person", "description": "President of Iran 2013-2021. Moderate reformist who championed JCPOA negotiations. Former nuclear negotiator.", "influence_score": 0.55, "role_title": "President of Iran"})
    zarif = await create_node(session, ws, t, "Actor", {"id": "zarif", "name": "Mohammad Javad Zarif", "actor_type": "person", "description": "Foreign Minister 2013-2021. Lead Iranian JCPOA negotiator. Columbia-educated diplomat. Sanctioned by US in 2019.", "influence_score": 0.5, "role_title": "Foreign Minister"})
    trump = await create_node(session, ws, t, "Actor", {"id": "trump", "name": "Donald Trump", "actor_type": "person", "description": "US President 2017-2021. Withdrew from JCPOA May 2018. Imposed maximum pressure sanctions campaign.", "influence_score": 0.9, "role_title": "President of the US"})
    obama = await create_node(session, ws, t, "Actor", {"id": "obama", "name": "Barack Obama", "actor_type": "person", "description": "US President 2009-2017. Architect of P5+1 engagement strategy. Signed JCPOA in 2015.", "influence_score": 0.85, "role_title": "President of the US"})
    hezbollah = await create_node(session, ws, t, "Actor", {"id": "hezbollah", "name": "Hezbollah", "actor_type": "organization", "description": "Lebanese Shia militant group, primary Iranian proxy. Receives estimated $700M annually from Iran. IRGC-trained.", "influence_score": 0.45, "org_type": "paramilitary"})
    unsc = await create_node(session, ws, t, "Actor", {"id": "unsc", "name": "UN Security Council", "actor_type": "organization", "description": "Passed 6 rounds of sanctions on Iran (2006-2010). Resolution 2231 endorsed JCPOA. Snapback mechanism.", "influence_score": 0.8, "org_type": "international"})

    # ── CONFLICT ──
    conflict = await create_node(session, ws, t, "Conflict", {"id": "jcpoa-conflict", "name": "Iran Nuclear Program Dispute", "scale": "macro", "domain": "political", "status": "active", "incompatibility": "government", "glasl_stage": 6, "glasl_level": "win_lose", "kriesberg_phase": "stalemate", "violence_type": "structural", "intensity": "high", "summary": "Decades-long dispute over Iran's nuclear program. Core tension: Iran claims right to peaceful nuclear energy under NPT; Western powers suspect weapons program. JCPOA (2015) temporarily resolved enrichment levels but collapsed after US withdrawal (2018). By 2024, Iran enriching to 60-84% with breakout time under 2 weeks.", "started_at": "2002-08-14"})

    # Party_to edges with sides
    for actor_id, side, role in [
        ("iran", "side_a", "primary disputant"), ("usa", "side_b", "primary disputant"),
        ("russia", "third_party", "P5+1 negotiator"), ("china", "third_party", "P5+1 negotiator"),
        ("uk", "side_b", "E3 member"), ("france", "side_b", "E3 member"),
        ("germany", "side_b", "E3 member"), ("eu", "third_party", "coordinator"),
        ("iaea", "third_party", "verification body"), ("israel", "observer", "external pressure"),
        ("saudi", "observer", "regional rival"), ("unsc", "third_party", "enforcement body"),
    ]:
        await create_edge(session, ws, t, "PARTY_TO", actor_id, "jcpoa-conflict", "Actor", "Conflict", {"role": role, "side": side})

    # ── MEMBERSHIP / HIERARCHY ──
    await create_edge(session, ws, t, "MEMBER_OF", "irgc", "iran", "Actor", "Actor", {"role": "elite military branch", "since": "1979-05-05"})
    await create_edge(session, ws, t, "MEMBER_OF", "uk", "eu", "Actor", "Actor", {"role": "member state", "until": "2020-01-31"})
    await create_edge(session, ws, t, "MEMBER_OF", "france", "eu", "Actor", "Actor", {"role": "founding member"})
    await create_edge(session, ws, t, "MEMBER_OF", "germany", "eu", "Actor", "Actor", {"role": "founding member"})
    await create_edge(session, ws, t, "MEMBER_OF", "hezbollah", "iran", "Actor", "Actor", {"role": "proxy force"})

    # ── ALLIANCES & OPPOSITIONS ──
    await create_edge(session, ws, t, "ALLIED_WITH", "usa", "israel", "Actor", "Actor", {"strength": 0.95, "formality": "formal", "since": "1948-05-14"})
    await create_edge(session, ws, t, "ALLIED_WITH", "usa", "saudi", "Actor", "Actor", {"strength": 0.8, "formality": "formal"})
    await create_edge(session, ws, t, "ALLIED_WITH", "iran", "russia", "Actor", "Actor", {"strength": 0.65, "formality": "tacit"})
    await create_edge(session, ws, t, "ALLIED_WITH", "iran", "china", "Actor", "Actor", {"strength": 0.6, "formality": "tacit"})
    await create_edge(session, ws, t, "ALLIED_WITH", "iran", "hezbollah", "Actor", "Actor", {"strength": 0.9, "formality": "formal"})
    await create_edge(session, ws, t, "ALLIED_WITH", "uk", "france", "Actor", "Actor", {"strength": 0.85, "formality": "formal"})
    await create_edge(session, ws, t, "OPPOSED_TO", "iran", "usa", "Actor", "Actor", {"intensity": 0.85, "since": "1979-11-04"})
    await create_edge(session, ws, t, "OPPOSED_TO", "iran", "israel", "Actor", "Actor", {"intensity": 0.95, "since": "1979-02-11"})
    await create_edge(session, ws, t, "OPPOSED_TO", "iran", "saudi", "Actor", "Actor", {"intensity": 0.75})
    await create_edge(session, ws, t, "OPPOSED_TO", "israel", "hezbollah", "Actor", "Actor", {"intensity": 0.95})

    # ── EVENTS (20 key moments) ──
    events = [
        ("ev-natanz-reveal", "Natanz facility revealed by MEK dissidents", "investigate", "2002-08-14", 0.85, "political", "verbal", "Intelligence revealing secret enrichment at Natanz and heavy water at Arak. Triggered IAEA inspections."),
        ("ev-iaea-referral", "IAEA refers Iran to UN Security Council", "demand", "2006-02-04", 0.7, "political", "diplomatic", "Board of Governors votes 27-3-5 to report Iran to UNSC after safeguards failures."),
        ("ev-unsc-sanctions-1", "UNSC Resolution 1737 — first sanctions", "coerce", "2006-12-23", 0.75, "economic", "diplomatic", "Bans nuclear tech transfers, freezes assets of entities linked to nuclear program."),
        ("ev-stuxnet", "Stuxnet cyberattack on Natanz centrifuges", "assault", "2010-06-01", 0.9, "political", "cyber", "US-Israeli cyber weapon destroyed ~1000 IR-1 centrifuges. Set program back 1-2 years. First known cyber weapon targeting physical infrastructure."),
        ("ev-scientist-assassinations", "Assassination of Iranian nuclear scientists", "assault", "2010-11-29", 0.85, "political", "unconventional", "Series of assassinations: Majid Shahriari killed, Fereydoon Abbasi wounded. 5 scientists killed 2010-2012, attributed to Israel's Mossad."),
        ("ev-rouhani-elected", "Rouhani elected President on engagement platform", "cooperate", "2013-06-14", 0.5, "political", "verbal", "Moderate cleric wins presidency promising to resolve nuclear issue and lift sanctions. Khamenei gives cautious blessing."),
        ("ev-geneva-interim", "Geneva Interim Agreement (JPOA) signed", "agree", "2013-11-24", 0.6, "political", "diplomatic", "Iran freezes 20% enrichment, neutralizes UF6 stockpile. Gets $7B sanctions relief. 6-month confidence-building measure."),
        ("ev-lausanne-framework", "Lausanne Framework Agreement", "agree", "2015-04-02", 0.55, "political", "diplomatic", "Key parameters: 300kg LEU cap, 5060 centrifuges, 15-year sunset, Arak redesign, IAEA access protocol."),
        ("ev-jcpoa-signed", "JCPOA signed in Vienna", "agree", "2015-07-14", 0.3, "political", "diplomatic", "Comprehensive deal: Iran limits enrichment to 3.67%, reduces centrifuges to 5060 IR-1, redesigns Arak, grants IAEA enhanced access. Sanctions lifted."),
        ("ev-implementation-day", "JCPOA Implementation Day — sanctions lifted", "yield", "2016-01-16", 0.25, "economic", "diplomatic", "IAEA verifies Iran compliance. EU/US/UN nuclear-related sanctions lifted. Iran accesses $100B+ frozen assets."),
        ("ev-trump-withdrawal", "US withdraws from JCPOA", "reject", "2018-05-08", 0.9, "political", "diplomatic", "Trump signs NSPM-11, reimposing all US sanctions. Calls JCPOA 'worst deal ever.' E3/EU condemn but cannot prevent."),
        ("ev-max-pressure", "Maximum pressure sanctions imposed", "coerce", "2018-11-05", 0.85, "economic", "economic", "Full reimposition: oil exports drop from 2.5M to <500K bpd. SWIFT access cut. Secondary sanctions threaten allied companies."),
        ("ev-irgc-designation", "IRGC designated as Foreign Terrorist Organization", "coerce", "2019-04-08", 0.8, "political", "diplomatic", "First time US designates foreign government military as FTO. Iran retaliates by designating CENTCOM as terrorist."),
        ("ev-iran-enrichment-breach", "Iran begins exceeding JCPOA enrichment limits", "reject", "2019-07-01", 0.75, "political", "diplomatic", "Graduated response: surpasses 300kg LEU cap, enriches to 4.5%, installs advanced centrifuges. Each step reversible."),
        ("ev-soleimani", "US kills Qasem Soleimani in Baghdad drone strike", "assault", "2020-01-03", 0.95, "political", "conventional_military", "IRGC Quds Force commander killed at Baghdad airport. Iran retaliates with ballistic missiles on Al-Asad airbase (no US casualties). Near-war crisis."),
        ("ev-iran-retaliation", "Iran ballistic missile strike on Al-Asad airbase", "assault", "2020-01-08", 0.8, "political", "conventional_military", "22 ballistic missiles hit Al-Asad. Iran signals via Iraq to allow evacuation. Deliberate de-escalation after face-saving strike."),
        ("ev-vienna-talks-2021", "Vienna indirect negotiations resume", "consult", "2021-04-06", 0.5, "political", "diplomatic", "EU-mediated proximity talks (US and Iran in separate hotels). Progress stalls on sequencing and verification."),
        ("ev-raisi-elected", "Raisi elected President — hardliner shift", "reject", "2021-06-18", 0.65, "political", "verbal", "Ultra-conservative judiciary chief wins with 48.8% on low turnout. Signals tougher stance but Khamenei still controls nuclear file."),
        ("ev-iran-60pct", "Iran enriches uranium to 60% purity", "reject", "2021-04-13", 0.85, "political", "diplomatic", "Response to Natanz sabotage. 60% is 90% of the way to weapons-grade by SWU. Breakout time shrinks to weeks."),
        ("ev-snapback-2024", "Snapback mechanism triggered — all UN sanctions restored", "coerce", "2024-10-01", 0.8, "political", "diplomatic", "E3 triggers Resolution 2231 snapback before Oct 18 expiry. All pre-JCPOA UN sanctions reimposed. Iran announces no further JCPOA compliance."),
    ]
    event_ids = []
    for eid, name, etype, date, sev, ctx, mode, desc in events:
        nid = await create_node(session, ws, t, "Event", {"id": eid, "name": name, "event_type": etype, "occurred_at": date, "severity": sev, "context": ctx, "mode": mode, "description": desc})
        event_ids.append(nid)
        await create_edge(session, ws, t, "PART_OF", nid, "jcpoa-conflict", "Event", "Conflict")

    # Event locations
    event_locations = {
        "ev-natanz-reveal": "loc-natanz", "ev-iaea-referral": "loc-vienna", "ev-stuxnet": "loc-natanz",
        "ev-geneva-interim": "loc-geneva", "ev-lausanne-framework": "loc-geneva", "ev-jcpoa-signed": "loc-vienna",
        "ev-trump-withdrawal": "loc-washington", "ev-soleimani": "loc-baghdad", "ev-iran-retaliation": "loc-baghdad",
        "ev-vienna-talks-2021": "loc-vienna", "ev-iran-60pct": "loc-natanz", "ev-snapback-2024": "loc-newyork",
        "ev-fordow": "loc-fordow",
    }
    for ev, loc in event_locations.items():
        await create_edge(session, ws, t, "AT_LOCATION", ev, loc, "Event", "Location")

    # Causal chains
    causal = [
        ("ev-natanz-reveal", "ev-iaea-referral", "precedent", 0.9),
        ("ev-iaea-referral", "ev-unsc-sanctions-1", "escalation", 0.85),
        ("ev-unsc-sanctions-1", "ev-stuxnet", "escalation", 0.6),
        ("ev-stuxnet", "ev-scientist-assassinations", "escalation", 0.5),
        ("ev-rouhani-elected", "ev-geneva-interim", "precedent", 0.8),
        ("ev-geneva-interim", "ev-lausanne-framework", "precedent", 0.9),
        ("ev-lausanne-framework", "ev-jcpoa-signed", "precedent", 0.95),
        ("ev-jcpoa-signed", "ev-implementation-day", "precedent", 0.95),
        ("ev-trump-withdrawal", "ev-max-pressure", "escalation", 0.95),
        ("ev-max-pressure", "ev-iran-enrichment-breach", "retaliation", 0.9),
        ("ev-irgc-designation", "ev-iran-enrichment-breach", "retaliation", 0.7),
        ("ev-iran-enrichment-breach", "ev-soleimani", "escalation", 0.5),
        ("ev-soleimani", "ev-iran-retaliation", "retaliation", 0.99),
        ("ev-iran-retaliation", "ev-vienna-talks-2021", "precedent", 0.4),
        ("ev-raisi-elected", "ev-iran-60pct", "escalation", 0.6),
        ("ev-iran-60pct", "ev-snapback-2024", "escalation", 0.8),
    ]
    for src, tgt, mech, strength in causal:
        await create_edge(session, ws, t, "CAUSED", src, tgt, "Event", "Event", {"mechanism": mech, "strength": strength})

    # Actor participation in events
    participations = [
        ("iran", "ev-jcpoa-signed", "signatory"), ("usa", "ev-jcpoa-signed", "signatory"),
        ("russia", "ev-jcpoa-signed", "signatory"), ("china", "ev-jcpoa-signed", "signatory"),
        ("zarif", "ev-jcpoa-signed", "lead negotiator"), ("obama", "ev-jcpoa-signed", "authorizer"),
        ("trump", "ev-trump-withdrawal", "decision maker"), ("usa", "ev-stuxnet", "perpetrator"),
        ("israel", "ev-stuxnet", "perpetrator"), ("israel", "ev-scientist-assassinations", "perpetrator"),
        ("usa", "ev-soleimani", "perpetrator"), ("iran", "ev-iran-retaliation", "perpetrator"),
        ("iaea", "ev-iaea-referral", "reporter"), ("iaea", "ev-implementation-day", "verifier"),
        ("iran", "ev-iran-60pct", "perpetrator"), ("rouhani", "ev-geneva-interim", "lead negotiator"),
        ("eu", "ev-vienna-talks-2021", "mediator"), ("unsc", "ev-snapback-2024", "enforcer"),
    ]
    for actor, event, role in participations:
        await create_edge(session, ws, t, "PARTICIPATES_IN", actor, event, "Actor", "Event", {"role_type": role})

    # ── ISSUES (8) ──
    issues = [
        ("iss-enrichment", "Right to uranium enrichment", "substantive", 0.95, 0.3, "Iran claims NPT Article IV right; West disputes scope."),
        ("iss-sanctions", "Sanctions relief and economic recovery", "substantive", 0.9, 0.5, "Iran demands full, verifiable, irreversible lifting. US demands front-loaded compliance."),
        ("iss-irgc-fto", "IRGC terrorist designation removal", "procedural", 0.85, 0.1, "Iran demands FTO delisting as precondition. US sees it as separate from nuclear file."),
        ("iss-regional", "Iran's regional proxy activities", "substantive", 0.7, 0.2, "US/Israel/Saudi demand addressing ballistic missiles and proxies. Iran calls it sovereign right."),
        ("iss-verification", "IAEA inspection access and verification", "procedural", 0.8, 0.6, "Dispute over access to undeclared sites, real-time monitoring cameras."),
        ("iss-sunset", "Sunset clause timelines", "procedural", 0.75, 0.4, "JCPOA restrictions expire 2025-2031. Critics say this legitimizes program post-sunset."),
        ("iss-breakout", "Nuclear breakout time", "substantive", 0.98, 0.1, "Time to produce enough fissile material for one weapon. Was 12+ months under JCPOA, now <2 weeks."),
        ("iss-compensation", "Compensation for sanctions damages", "substantive", 0.6, 0.3, "Iran demands reparations for economic damage from maximum pressure. Estimated $1T+ in losses."),
    ]
    for iid, name, itype, sal, div, desc in issues:
        nid = await create_node(session, ws, t, "Issue", {"id": iid, "name": name, "issue_type": itype, "salience": sal, "divisibility": div, "description": desc})
        await create_edge(session, ws, t, "PART_OF", nid, "jcpoa-conflict", "Issue", "Conflict")

    # ── INTERESTS (12 — with BATNA) ──
    interests = [
        ("int-iran-security", "iran", "Regime survival and security from external attack", "substantive", 5, True, "Self-defense capability, deterrence", 0.2, "strong", 0.8),
        ("int-iran-sovereignty", "iran", "Sovereign right to nuclear technology under NPT", "procedural", 5, True, "Full fuel-cycle capability", 0.15, "moderate", 0.5),
        ("int-iran-economy", "iran", "Economic recovery and sanctions relief", "substantive", 4, True, "Full access to global financial system", 0.35, "weak", 0.3),
        ("int-iran-regional", "iran", "Regional influence through proxy network", "substantive", 4, False, "Axis of resistance as strategic depth", 0.6, "strong", 0.7),
        ("int-usa-nonprolif", "usa", "Preventing nuclear weapons proliferation", "substantive", 5, True, "No Iranian nuclear weapon", 0.15, "strong", 0.85),
        ("int-usa-regional", "usa", "Regional stability and ally security", "substantive", 4, True, "Israel and Gulf state security", 0.45, "strong", 0.7),
        ("int-usa-credibility", "usa", "Credibility of US commitments and alliances", "psychological", 3, False, "Global deterrence posture", 0.5, "moderate", 0.6),
        ("int-israel-existential", "israel", "Preventing existential nuclear threat from Iran", "substantive", 5, True, "Iran cannot achieve breakout capability", 0.05, "strong", 0.9),
        ("int-saudi-parity", "saudi", "Nuclear parity — if Iran enriches, Saudi will too", "substantive", 4, True, "Matching nuclear capability", 0.3, "moderate", 0.5),
        ("int-russia-influence", "russia", "Maintaining influence in Middle East", "substantive", 3, False, "Arms sales, Bushehr contracts, strategic partner", 0.5, "moderate", 0.6),
        ("int-china-energy", "china", "Securing Iranian oil and gas supply", "substantive", 4, False, "Energy security for Belt and Road", 0.55, "strong", 0.65),
        ("int-eu-stability", "eu", "European security and nuclear nonproliferation", "substantive", 4, True, "No nuclear-armed Iran within missile range", 0.3, "weak", 0.4),
    ]
    for iid, actor, desc, itype, prio, stated, pos, sat, batna, rv in interests:
        nid = await create_node(session, ws, t, "Interest", {"id": iid, "description": desc, "interest_type": itype, "priority": prio, "stated": stated, "stated_position": pos, "satisfaction": sat, "batna_strength": batna, "reservation_value": rv})
        await create_edge(session, ws, t, "HAS_INTEREST", actor, nid, "Actor", "Interest", {"priority": prio, "in_conflict": "jcpoa-conflict"})

    # ── NORMS (6 — treaties, resolutions, designations) ──
    norms = [
        ("norm-npt", "Treaty on the Non-Proliferation of Nuclear Weapons (NPT)", "treaty", "binding", "international", "Art. IV: inalienable right to peaceful nuclear energy. Art. II: non-nuclear states shall not acquire weapons.", "1970-03-05"),
        ("norm-res2231", "UN Security Council Resolution 2231", "treaty", "binding", "international", "Endorses JCPOA, establishes snapback mechanism, arms embargo, ballistic missile restrictions.", "2015-07-20"),
        ("norm-res1737", "UN Security Council Resolution 1737", "treaty", "binding", "international", "First UNSC sanctions on Iran: bans nuclear tech transfers, freezes assets.", "2006-12-23"),
        ("norm-additional-protocol", "IAEA Additional Protocol", "treaty", "binding", "international", "Grants IAEA expanded access for inspections of undeclared activities. Iran suspended in 2006, briefly reinstated under JCPOA.", "1997-05-15"),
        ("norm-irgc-fto", "IRGC Foreign Terrorist Organization Designation", "regulation", "binding", "USA", "US designates IRGC as FTO under Section 219 of INA. Criminalizes material support.", "2019-04-15"),
        ("norm-jcpoa-text", "JCPOA Full Text (159 pages + 5 annexes)", "treaty", "binding", "international", "Enrichment cap 3.67%, 5060 IR-1 centrifuges, 300kg LEU stockpile, Arak redesigned, procurement channel.", "2015-07-14"),
    ]
    for nid, name, ntype, enf, juris, text, eff in norms:
        nid_created = await create_node(session, ws, t, "Norm", {"id": nid, "name": name, "norm_type": ntype, "enforceability": enf, "jurisdiction": juris, "text": text, "effective_from": eff})
        await create_edge(session, ws, t, "GOVERNED_BY", "jcpoa-conflict", nid_created, "Conflict", "Norm")

    # Violations
    await create_edge(session, ws, t, "VIOLATES", "ev-iran-enrichment-breach", "norm-jcpoa-text", "Event", "Norm", {"severity": 0.8, "intentional": True})
    await create_edge(session, ws, t, "VIOLATES", "ev-trump-withdrawal", "norm-res2231", "Event", "Norm", {"severity": 0.9, "intentional": True})
    await create_edge(session, ws, t, "VIOLATES", "ev-iran-60pct", "norm-jcpoa-text", "Event", "Norm", {"severity": 0.95, "intentional": True})
    await create_edge(session, ws, t, "VIOLATES", "ev-stuxnet", "norm-npt", "Event", "Norm", {"severity": 0.7})

    # ── PROCESSES (3) ──
    proc_jcpoa = await create_node(session, ws, t, "Process", {"id": "proc-jcpoa-neg", "name": "P5+1 JCPOA Negotiations (2013-2015)", "process_type": "negotiation", "resolution_approach": "interest_based", "status": "completed", "formality": "formal", "binding": True, "voluntary": True, "current_stage": "resolution", "started_at": "2013-09-26", "ended_at": "2015-07-14", "governing_rules": "NPT framework, UNSC resolutions"})
    proc_vienna = await create_node(session, ws, t, "Process", {"id": "proc-vienna-2021", "name": "Vienna Indirect Negotiations (2021-2022)", "process_type": "mediation_evaluative", "resolution_approach": "interest_based", "status": "abandoned", "formality": "formal", "binding": False, "voluntary": True, "current_stage": "dialogue", "started_at": "2021-04-06", "ended_at": "2022-09-01"})
    proc_snapback = await create_node(session, ws, t, "Process", {"id": "proc-snapback", "name": "UNSC Snapback Mechanism", "process_type": "adjudication", "resolution_approach": "rights_based", "status": "completed", "formality": "formal", "binding": True, "voluntary": False, "current_stage": "implementation", "started_at": "2024-09-01"})

    await create_edge(session, ws, t, "RESOLVED_THROUGH", "jcpoa-conflict", "proc-jcpoa-neg", "Conflict", "Process")
    await create_edge(session, ws, t, "RESOLVED_THROUGH", "jcpoa-conflict", "proc-vienna-2021", "Conflict", "Process")
    await create_edge(session, ws, t, "RESOLVED_THROUGH", "jcpoa-conflict", "proc-snapback", "Conflict", "Process")

    # ── OUTCOMES (3) ──
    out_jcpoa = await create_node(session, ws, t, "Outcome", {"id": "out-jcpoa-2015", "name": "JCPOA Agreement 2015", "outcome_type": "agreement", "description": "Comprehensive deal limiting Iran enrichment to 3.67%, capping centrifuges, redesigning Arak reactor, granting IAEA enhanced access in exchange for sanctions relief.", "satisfaction_a": 0.65, "satisfaction_b": 0.6, "joint_value": 0.7, "durability": "durable", "compliance_rate": 0.85, "decided_at": "2015-07-14"})
    out_stalemate = await create_node(session, ws, t, "Outcome", {"id": "out-stalemate-2024", "name": "Strategic Stalemate 2024", "outcome_type": "no_resolution", "description": "Iran enriching to 60%+ with breakout time under 2 weeks. All sanctions reimposed via snapback. No diplomatic channel. Mutual deterrence.", "satisfaction_a": 0.1, "satisfaction_b": 0.15, "joint_value": 0.05, "durability": "temporary", "compliance_rate": 0.0, "decided_at": "2024-10-18"})
    out_maxpressure = await create_node(session, ws, t, "Outcome", {"id": "out-maxpressure", "name": "Maximum Pressure Campaign Effects", "outcome_type": "acquiescence", "description": "Iran oil exports dropped 80%, GDP contracted 6%, inflation hit 40%+. But no regime change, no renegotiation, accelerated nuclear program.", "satisfaction_a": 0.05, "satisfaction_b": 0.3, "joint_value": 0.1, "durability": "temporary"})

    await create_edge(session, ws, t, "PRODUCES", "proc-jcpoa-neg", "out-jcpoa-2015", "Process", "Outcome")
    await create_edge(session, ws, t, "PRODUCES", "proc-snapback", "out-stalemate-2024", "Process", "Outcome")
    await create_edge(session, ws, t, "PRODUCES", "proc-vienna-2021", "out-maxpressure", "Process", "Outcome")

    # ── NARRATIVES (6 — competing frames) ──
    narr = [
        ("narr-iran-rights", "Iran's Inalienable Right to Nuclear Energy", "dominant", "Iran", "moral", 0.8, 0.7, "NPT Article IV guarantees the inalienable right to develop nuclear energy for peaceful purposes. Western opposition is about hegemony, not proliferation. Iran has never invaded a neighbor in 250 years."),
        ("narr-west-prolif", "Iranian Nuclear Weapons Threat", "dominant", "West", "risk", 0.85, 0.8, "Iran's covert facilities, enrichment beyond civilian needs, and ballistic missile program indicate weapons intent. IAEA found undeclared nuclear material at multiple sites. Breakout time is dangerously short."),
        ("narr-resistance", "Axis of Resistance Against Western Imperialism", "counter", "Iran", "power", 0.6, 0.5, "US-led order seeks regime change in Iran as it did in Iraq, Libya, Syria. Nuclear capability is the only deterrent against Western military adventurism. Every state that gave up its program was attacked."),
        ("narr-rules-order", "Rules-Based International Order at Stake", "alternative", "EU", "moral", 0.7, 0.65, "JCPOA represents multilateral diplomacy at its best. US withdrawal undermined international agreements. If major powers can unilaterally exit treaties, the entire nonproliferation architecture collapses."),
        ("narr-israel-existential", "Existential Threat to Israel", "dominant", "Israel", "risk", 0.9, 0.6, "A nuclear Iran would be an existential threat. Iranian leaders have called for Israel's elimination. Nuclear deterrence does not apply to ideologically driven regimes. Prevention, not containment."),
        ("narr-saudi-parity", "Nuclear Parity and Regional Balance", "alternative", "Saudi Arabia", "power", 0.5, 0.4, "If Iran acquires nuclear weapons capability, Saudi Arabia will pursue its own. MBS: 'We will match whatever Iran does.' This triggers regional proliferation cascade."),
    ]
    for nid, name, ntype, persp, frame, coh, reach, content in narr:
        nid_created = await create_node(session, ws, t, "Narrative", {"id": nid, "name": name, "narrative_type": ntype, "perspective": persp, "frame_type": frame, "coherence": coh, "reach": reach, "content": content})
        await create_edge(session, ws, t, "ABOUT", nid_created, "jcpoa-conflict", "Narrative", "Conflict")

    # Narrative promotion
    await create_edge(session, ws, t, "PROMOTES", "iran", "narr-iran-rights", "Actor", "Narrative", {"strength": 0.9})
    await create_edge(session, ws, t, "PROMOTES", "iran", "narr-resistance", "Actor", "Narrative", {"strength": 0.8})
    await create_edge(session, ws, t, "PROMOTES", "usa", "narr-west-prolif", "Actor", "Narrative", {"strength": 0.9})
    await create_edge(session, ws, t, "PROMOTES", "israel", "narr-israel-existential", "Actor", "Narrative", {"strength": 0.95})
    await create_edge(session, ws, t, "PROMOTES", "eu", "narr-rules-order", "Actor", "Narrative", {"strength": 0.8})
    await create_edge(session, ws, t, "PROMOTES", "saudi", "narr-saudi-parity", "Actor", "Narrative", {"strength": 0.7})

    # ── EMOTIONAL STATES (8 — key moments) ──
    emotions = [
        ("emo-iran-jcpoa", "iran", "joy", "high", 0.8, 0.7, "ev-jcpoa-signed", "2015-07-14"),
        ("emo-iran-betrayal", "iran", "anger", "high", -0.9, 0.95, "ev-trump-withdrawal", "2018-05-08"),
        ("emo-iran-grief", "iran", "sadness", "high", -0.85, 0.8, "ev-soleimani", "2020-01-03"),
        ("emo-usa-distrust", "usa", "disgust", "medium", -0.6, 0.5, "ev-natanz-reveal", "2002-08-14"),
        ("emo-israel-fear", "israel", "fear", "high", -0.9, 0.9, "ev-iran-60pct", "2021-04-13"),
        ("emo-eu-frustration", "eu", "anger", "medium", -0.5, 0.6, "ev-trump-withdrawal", "2018-05-08"),
        ("emo-iran-humiliation", "iran", "sadness", "high", -0.8, 0.7, "ev-max-pressure", "2018-11-05"),
        ("emo-saudi-anxiety", "saudi", "anticipation", "medium", -0.4, 0.6, "ev-iran-60pct", "2021-04-13"),
    ]
    for eid, actor, emotion, intensity, valence, arousal, trigger, date in emotions:
        nid = await create_node(session, ws, t, "EmotionalState", {"id": eid, "primary_emotion": emotion, "intensity": intensity, "valence": valence, "arousal": arousal, "trigger_event_id": trigger, "observed_at": date})
        await create_edge(session, ws, t, "EXPERIENCES", actor, nid, "Actor", "EmotionalState", {"context_event_id": trigger})

    # ── TRUST STATES (6 — key dyads) ──
    trusts = [
        ("trust-iran-usa", "iran", "usa", 0.1, 0.05, 0.05, 0.15, 0.08, "calculus"),
        ("trust-iran-russia", "iran", "russia", 0.6, 0.4, 0.5, 0.5, 0.5, "knowledge"),
        ("trust-usa-israel", "usa", "israel", 0.9, 0.85, 0.8, 0.85, 0.88, "identification"),
        ("trust-iran-iaea", "iran", "iaea", 0.5, 0.3, 0.45, 0.35, 0.35, "calculus"),
        ("trust-eu-usa-post", "eu", "usa", 0.45, 0.3, 0.35, 0.55, 0.38, "knowledge"),
        ("trust-iran-eu", "iran", "eu", 0.3, 0.35, 0.3, 0.3, 0.3, "calculus"),
    ]
    for tid, src, tgt, ability, benev, integ, propensity, overall, basis in trusts:
        nid = await create_node(session, ws, t, "TrustState", {"id": tid, "perceived_ability": ability, "perceived_benevolence": benev, "perceived_integrity": integ, "propensity_to_trust": propensity, "overall_trust": overall, "trust_basis": basis})
        await create_edge(session, ws, t, "TRUSTS", src, tgt, "Actor", "Actor", {"trust_state_id": tid, "overall_trust": overall})

    # ── POWER DYNAMICS (8) ──
    powers = [
        ("pow-usa-iran-econ", "usa", "iran", "economic", 0.95, "a_over_b", 0.7, True),
        ("pow-usa-iran-mil", "usa", "iran", "coercive", 0.9, "a_over_b", 0.6, False),
        ("pow-iran-proxy", "iran", "usa", "coercive", 0.4, "a_over_b", 0.3, True),
        ("pow-israel-intel", "israel", "iran", "informational", 0.8, "a_over_b", 0.5, True),
        ("pow-iaea-legit", "iaea", "iran", "legitimate", 0.7, "a_over_b", 0.8, True),
        ("pow-russia-veto", "russia", "usa", "political", 0.6, "symmetric", 0.9, True),
        ("pow-khamenei-iran", "khamenei", "iran", "legitimate", 0.95, "a_over_b", 0.9, True),
        ("pow-iran-strait", "iran", "usa", "coercive", 0.5, "a_over_b", 0.4, False),
    ]
    for pid, src, tgt, domain, mag, direction, legit, exercised in powers:
        nid = await create_node(session, ws, t, "PowerDynamic", {"id": pid, "power_domain": domain, "magnitude": mag, "direction": direction, "legitimacy": legit, "exercised": exercised})
        await create_edge(session, ws, t, "HAS_POWER_OVER", src, tgt, "Actor", "Actor", {"power_dynamic_id": pid, "domain": domain, "magnitude": mag})

    # ── EVIDENCE (6) ──
    evidence = [
        ("evid-iaea-2003", "IAEA Report GOV/2003/75 — Iran safeguards failures", "document", "IAEA", 0.95, "Documented 18 years of undeclared nuclear activities, including enrichment and conversion experiments."),
        ("evid-cia-nie-2007", "US NIE 2007 — Iran halted weapons program in 2003", "document", "US Intelligence Community", 0.7, "High confidence that Iran halted nuclear weapons design program in fall 2003. Moderate confidence it had not restarted as of mid-2007."),
        ("evid-amano-pmd", "IAEA PMD Assessment (2015) — Possible Military Dimensions", "document", "IAEA", 0.85, "Final assessment on pre-2003 weapons-related activities. Concluded structured program existed until 2003, some activities continued until 2009."),
        ("evid-mossad-archive", "Iran Nuclear Archive (2018) — Mossad extraction", "physical", "Mossad/Israel", 0.75, "55,000 pages and 183 CDs extracted from Tehran warehouse. Documented Project Amad weapons design program."),
        ("evid-iaea-particles", "IAEA detection of uranium particles at undeclared sites", "statistical", "IAEA", 0.9, "Environmental samples at Turquzabad and Varamin detected processed uranium particles inconsistent with declared activities."),
        ("evid-satellite-fordow", "Satellite imagery of Fordow underground facility expansion", "digital_record", "IISS / commercial satellite", 0.8, "Imagery shows expanded construction at Fordow, consistent with installation of advanced IR-6 centrifuge cascades."),
    ]
    for eid, desc, etype, source, rel, detail in evidence:
        nid = await create_node(session, ws, t, "Evidence", {"id": eid, "description": desc, "evidence_type": etype, "source_name": source, "reliability": rel, "metadata": detail})
        # Link evidence to relevant events
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-natanz-reveal", "evid-iaea-2003", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-stuxnet", "evid-satellite-fordow", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-iran-60pct", "evid-iaea-particles", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-jcpoa-signed", "evid-amano-pmd", "Event", "Evidence")

    # ── ROLES (8) ──
    roles = [
        ("role-zarif-negotiator", "mediator", "zarif", "jcpoa-conflict", "2013-09-26", "2021-08-05"),
        ("role-obama-architect", "facilitator", "obama", "jcpoa-conflict", "2013-01-01", "2017-01-20"),
        ("role-trump-spoiler", "spoiler", "trump", "jcpoa-conflict", "2017-01-20", "2021-01-20"),
        ("role-iaea-verifier", "neutral", "iaea", "jcpoa-conflict", "2015-07-14", None),
        ("role-israel-spoiler", "spoiler", "israel", "jcpoa-conflict", "2002-01-01", None),
        ("role-eu-mediator", "facilitator", "eu", "jcpoa-conflict", "2003-10-21", None),
        ("role-russia-guarantor", "guarantor", "russia", "jcpoa-conflict", "2006-01-01", None),
        ("role-khamenei-authority", "claimant", "khamenei", "jcpoa-conflict", "1989-06-04", None),
    ]
    for rid, rtype, actor, ctx, vfrom, vto in roles:
        props = {"id": rid, "role_type": rtype, "actor_id": actor, "context_id": ctx, "valid_from": vfrom}
        if vto:
            props["valid_to"] = vto
        await create_node(session, ws, t, "Role", props)

    print(f"  JCPOA complete: 19 actors, 20 events, 8 issues, 12 interests, 6 norms, 3 processes, 3 outcomes, 6 narratives, 8 emotions, 6 trust states, 8 power dynamics, 10 locations, 6 evidence, 8 roles")


# ═══════════════════════════════════════════════════════════════════
# CASE 2: COMMERCIAL — Apex vs Crestline ERP Dispute (Expanded)
# ═══════════════════════════════════════════════════════════════════

async def seed_commercial(session):
    ws = "commercial-full"
    t = "tacitus"
    print("  Seeding Commercial Dispute (meso)...")

    # Locations
    loc_london = await create_node(session, ws, t, "Location", {"id": "loc-london", "name": "London", "location_type": "city", "country_code": "GBR"})
    loc_manchester = await create_node(session, ws, t, "Location", {"id": "loc-manchester", "name": "Manchester", "location_type": "city", "country_code": "GBR"})
    loc_cedr = await create_node(session, ws, t, "Location", {"id": "loc-cedr", "name": "CEDR Offices, Jermyn Street", "location_type": "building", "country_code": "GBR"})

    # Actors (10)
    apex = await create_node(session, ws, t, "Actor", {"id": "apex", "name": "Apex Systems Ltd", "actor_type": "organization", "description": "Mid-tier ERP software vendor, 200 employees. Custom SAP integrations. 8 years in business. Cash flow dependent on this contract.", "influence_score": 0.5, "org_type": "private", "sector": "technology", "size": "200"})
    crestline = await create_node(session, ws, t, "Actor", {"id": "crestline", "name": "Crestline Manufacturing PLC", "actor_type": "organization", "description": "FTSE 250 manufacturer, 3000 employees. ERP migration critical for warehouse automation and IPO preparation.", "influence_score": 0.7, "org_type": "private", "sector": "manufacturing", "size": "3000"})
    cedr = await create_node(session, ws, t, "Actor", {"id": "cedr", "name": "Centre for Effective Dispute Resolution", "actor_type": "organization", "description": "Leading UK ADR provider. Appointed mediator for the dispute under CEDR Model Mediation Procedure.", "influence_score": 0.4, "org_type": "ngo"})
    james = await create_node(session, ws, t, "Actor", {"id": "james", "name": "James Whitfield", "actor_type": "person", "description": "Apex CEO and founder. Former SAP consultant. Personally oversaw the Crestline project. Reputation at stake.", "role_title": "CEO, Apex Systems", "influence_score": 0.5})
    sarah = await create_node(session, ws, t, "Actor", {"id": "sarah", "name": "Sarah Chen", "actor_type": "person", "description": "Crestline COO. Led ERP selection committee. Under board pressure to deliver warehouse automation before Q4.", "role_title": "COO, Crestline Manufacturing", "influence_score": 0.6})
    mediator = await create_node(session, ws, t, "Actor", {"id": "mediator-commercial", "name": "Richard Faulkner QC", "actor_type": "person", "description": "CEDR-accredited commercial mediator, 20 years experience. Specialist in technology disputes. Evaluative style.", "role_title": "Mediator", "influence_score": 0.45})
    apex_counsel = await create_node(session, ws, t, "Actor", {"id": "apex-counsel", "name": "Patel & Associates", "actor_type": "organization", "description": "Boutique technology litigation firm representing Apex. Senior partner handling personally.", "org_type": "private", "sector": "legal"})
    crestline_counsel = await create_node(session, ws, t, "Actor", {"id": "crestline-counsel", "name": "Herbert Smith Freehills", "actor_type": "organization", "description": "Magic Circle firm representing Crestline. Technology disputes team. Higher resource capacity.", "org_type": "private", "sector": "legal"})
    apex_pm = await create_node(session, ws, t, "Actor", {"id": "apex-pm", "name": "David Osei", "actor_type": "person", "description": "Apex project manager for Crestline engagement. 5 years experience. Flagged scope creep internally but was overruled.", "role_title": "Project Manager"})
    crestline_it = await create_node(session, ws, t, "Actor", {"id": "crestline-it", "name": "Lisa Nguyen", "actor_type": "person", "description": "Crestline Head of IT. Managed legacy systems. Raised concerns about data migration complexity early in project.", "role_title": "Head of IT"})

    # Conflict
    conflict = await create_node(session, ws, t, "Conflict", {"id": "comm-conflict", "name": "Apex vs Crestline — ERP Software Delivery Dispute", "scale": "meso", "domain": "commercial", "status": "active", "incompatibility": "resource", "glasl_stage": 5, "glasl_level": "win_lose", "kriesberg_phase": "stalemate", "violence_type": "none", "intensity": "moderate", "summary": "GBP 2.4M contract for custom ERP system. Apex delivered 18 months late with critical defects. Crestline suffered GBP 4.1M in operational losses from failed warehouse automation. Crestline claims breach, Apex claims scope creep and non-cooperation. Direct negotiation failed. CEDR mediation in progress.", "started_at": "2023-01-15"})

    for actor_id, side, role in [
        ("apex", "side_a", "defendant/supplier"), ("crestline", "side_b", "claimant/client"),
        ("cedr", "third_party", "ADR provider"), ("mediator-commercial", "third_party", "mediator"),
        ("james", "side_a", "CEO"), ("sarah", "side_b", "COO"),
        ("apex-counsel", "side_a", "legal counsel"), ("crestline-counsel", "side_b", "legal counsel"),
    ]:
        await create_edge(session, ws, t, "PARTY_TO", actor_id, "comm-conflict", "Actor", "Conflict", {"role": role, "side": side})

    # Memberships
    await create_edge(session, ws, t, "MEMBER_OF", "james", "apex", "Actor", "Actor", {"role": "CEO"})
    await create_edge(session, ws, t, "MEMBER_OF", "apex-pm", "apex", "Actor", "Actor", {"role": "Project Manager"})
    await create_edge(session, ws, t, "MEMBER_OF", "sarah", "crestline", "Actor", "Actor", {"role": "COO"})
    await create_edge(session, ws, t, "MEMBER_OF", "crestline-it", "crestline", "Actor", "Actor", {"role": "Head of IT"})
    await create_edge(session, ws, t, "MEMBER_OF", "mediator-commercial", "cedr", "Actor", "Actor", {"role": "accredited mediator"})

    # Events (14)
    events = [
        ("ev-rfp", "Crestline issues RFP for ERP replacement", "demand", "2022-09-01", 0.2, "contractual", "written", "Formal RFP issued to 6 vendors. Requirements: SAP S/4HANA integration, warehouse automation module, 12-month delivery."),
        ("ev-contract-signed", "Contract signed — GBP 2.4M fixed price", "agree", "2023-01-15", 0.15, "contractual", "written", "Fixed-price contract with 12-month delivery, 5 milestones, penalty clause for delay (5% per month capped at 25%)."),
        ("ev-scope-change-1", "Crestline requests additional warehouse modules", "demand", "2023-04-20", 0.4, "contractual", "written", "Change request #1: Add barcode scanning and IoT sensor integration. Apex estimates 6 weeks additional work. No formal change order signed."),
        ("ev-scope-change-2", "Crestline requests real-time reporting dashboard", "demand", "2023-07-10", 0.45, "contractual", "written", "Change request #2: Board-level real-time analytics dashboard with 47 KPIs. Apex flags this as 'significant scope expansion.'"),
        ("ev-milestone-missed", "Milestone 3 missed by 8 weeks", "reject", "2023-09-15", 0.6, "contractual", "written", "Data migration milestone failed. 40% of legacy records corrupted during ETL. Lisa Nguyen had warned about data quality."),
        ("ev-escalation-letter", "Crestline sends formal breach notice", "threaten", "2023-11-01", 0.7, "contractual", "written", "Herbert Smith sends 14-day cure notice under clause 12.3. Demands remediation plan or contract termination."),
        ("ev-apex-response", "Apex rejects breach claim, cites scope creep", "reject", "2023-11-10", 0.7, "contractual", "written", "Patel & Associates responds: additional modules constituted 40% scope increase without signed change orders. Counter-claims GBP 800K."),
        ("ev-delivery-attempt", "Apex delivers system v2.1 — critical defects", "reject", "2024-01-30", 0.75, "contractual", "written", "Delivered 6 months late. UAT reveals: 23 P1 bugs, warehouse module crashes under load, reporting engine incomplete."),
        ("ev-ops-failure", "Crestline warehouse goes offline for 3 days", "assault", "2024-02-15", 0.85, "contractual", "administrative", "Production ERP crash. Warehouse operations revert to manual. GBP 800K in emergency costs. Board demands resolution."),
        ("ev-board-pressure", "Crestline board threatens litigation", "threaten", "2024-03-01", 0.75, "contractual", "verbal", "Board resolution: pursue full damages claim (GBP 4.1M) unless mediation succeeds within 60 days."),
        ("ev-negotiation-failed", "Direct CEO-to-COO negotiation fails", "reject", "2024-03-15", 0.7, "contractual", "verbal", "James and Sarah meet. James offers GBP 500K credit. Sarah demands GBP 2.4M refund + damages. Impasse."),
        ("ev-mediation-agreed", "Parties agree to CEDR mediation", "consult", "2024-04-01", 0.5, "contractual", "written", "Both sides agree to 1-day mediation at CEDR. Mediator Richard Faulkner QC appointed. Position papers exchanged."),
        ("ev-mediation-day", "Mediation Day at CEDR", "consult", "2024-05-10", 0.45, "contractual", "verbal", "Full-day mediation: joint session, then caucuses. Mediator reality-tests both positions. Faulkner suggests 60/40 split framework."),
        ("ev-settlement-draft", "Draft settlement terms under discussion", "cooperate", "2024-05-10", 0.35, "contractual", "written", "Emerging terms: Apex fixes P1 bugs at own cost, GBP 600K compensation, 12-month warranty extension, confidentiality clause."),
    ]
    for eid, name, etype, date, sev, ctx, mode, desc in events:
        nid = await create_node(session, ws, t, "Event", {"id": eid, "name": name, "event_type": etype, "occurred_at": date, "severity": sev, "context": ctx, "mode": mode, "description": desc})
        await create_edge(session, ws, t, "PART_OF", nid, "comm-conflict", "Event", "Conflict")

    # Event locations
    await create_edge(session, ws, t, "AT_LOCATION", "ev-mediation-day", "loc-cedr", "Event", "Location")
    await create_edge(session, ws, t, "AT_LOCATION", "ev-ops-failure", "loc-manchester", "Event", "Location")
    await create_edge(session, ws, t, "AT_LOCATION", "ev-negotiation-failed", "loc-london", "Event", "Location")

    # Causal chains
    causal = [
        ("ev-rfp", "ev-contract-signed", "precedent", 0.95),
        ("ev-contract-signed", "ev-scope-change-1", "precedent", 0.7),
        ("ev-scope-change-1", "ev-scope-change-2", "escalation", 0.6),
        ("ev-scope-change-2", "ev-milestone-missed", "escalation", 0.8),
        ("ev-milestone-missed", "ev-escalation-letter", "escalation", 0.9),
        ("ev-escalation-letter", "ev-apex-response", "retaliation", 0.95),
        ("ev-apex-response", "ev-delivery-attempt", "precedent", 0.7),
        ("ev-delivery-attempt", "ev-ops-failure", "escalation", 0.85),
        ("ev-ops-failure", "ev-board-pressure", "escalation", 0.9),
        ("ev-board-pressure", "ev-negotiation-failed", "precedent", 0.7),
        ("ev-negotiation-failed", "ev-mediation-agreed", "precedent", 0.85),
        ("ev-mediation-agreed", "ev-mediation-day", "precedent", 0.95),
        ("ev-mediation-day", "ev-settlement-draft", "precedent", 0.8),
    ]
    for src, tgt, mech, strength in causal:
        await create_edge(session, ws, t, "CAUSED", src, tgt, "Event", "Event", {"mechanism": mech, "strength": strength})

    # Issues (6)
    issues = [
        ("iss-defects", "Software defect liability", "substantive", 0.9, 0.4, "Who bears responsibility for 23 P1 bugs? Apex claims insufficient UAT; Crestline says defects are fundamental."),
        ("iss-scope", "Scope creep vs contract interpretation", "procedural", 0.85, 0.3, "Were change requests #1 and #2 in scope or out? No signed change orders. Clause 8.2 ambiguous."),
        ("iss-damages", "Quantum of damages (GBP 4.1M claim)", "substantive", 0.95, 0.5, "Crestline claims: GBP 800K emergency costs, GBP 1.2M lost revenue, GBP 2.1M remediation. Apex disputes causation."),
        ("iss-relationship", "Ongoing vendor relationship viability", "psychological", 0.6, 0.7, "Can Apex continue as vendor? Crestline needs system maintained. Switching cost estimated at GBP 1.5M."),
        ("iss-reputation", "Reputational damage to both parties", "psychological", 0.7, 0.2, "Litigation would be public. Both sides exposed: Apex for quality, Crestline for procurement process."),
        ("iss-timeline", "IPO preparation timeline at risk", "substantive", 0.8, 0.3, "Crestline's planned 2025 IPO requires functioning ERP for due diligence. Delay threatens valuation."),
    ]
    for iid, name, itype, sal, div, desc in issues:
        nid = await create_node(session, ws, t, "Issue", {"id": iid, "name": name, "issue_type": itype, "salience": sal, "divisibility": div, "description": desc})
        await create_edge(session, ws, t, "PART_OF", nid, "comm-conflict", "Issue", "Conflict")

    # Interests (8)
    interests = [
        ("int-apex-cash", "apex", "Cash flow survival — this contract is 30% of revenue", "substantive", 5, True, "Full payment of GBP 2.4M", 0.3, "weak", 0.4),
        ("int-apex-reputation", "apex", "Market reputation as reliable ERP vendor", "psychological", 4, False, "No public admission of failure", 0.4, "moderate", 0.5),
        ("int-apex-relationship", "apex", "Maintain Crestline as long-term client", "substantive", 3, True, "Multi-year support contract", 0.2, "weak", 0.3),
        ("int-crestline-compensation", "crestline", "Financial recovery for operational losses", "substantive", 5, True, "GBP 4.1M damages", 0.15, "strong", 0.7),
        ("int-crestline-system", "crestline", "Working ERP system for warehouse automation", "substantive", 5, True, "Functional system within 90 days", 0.1, "moderate", 0.5),
        ("int-crestline-ipo", "crestline", "IPO readiness — need clean tech infrastructure", "substantive", 4, False, "ERP operational before Q4 2025", 0.2, "moderate", 0.6),
        ("int-james-personal", "james", "Personal legacy as founder — avoid insolvency", "psychological", 5, False, "Company survival", 0.25, "weak", 0.3),
        ("int-sarah-board", "sarah", "Board confidence in her leadership", "psychological", 4, False, "Demonstrate resolution capability", 0.35, "moderate", 0.5),
    ]
    for iid, actor, desc, itype, prio, stated, pos, sat, batna, rv in interests:
        nid = await create_node(session, ws, t, "Interest", {"id": iid, "description": desc, "interest_type": itype, "priority": prio, "stated": stated, "stated_position": pos, "satisfaction": sat, "batna_strength": batna, "reservation_value": rv})
        await create_edge(session, ws, t, "HAS_INTEREST", actor, nid, "Actor", "Interest")

    # Norms
    norms = [
        ("norm-contract", "Apex-Crestline Master Services Agreement", "contract", "binding", "England & Wales", "Fixed-price GBP 2.4M. Clause 8.2: change requests require signed change order. Clause 12.3: 14-day cure period. Clause 15: limitation of liability capped at contract value.", "2023-01-15"),
        ("norm-cedr-rules", "CEDR Model Mediation Procedure", "professional_standard", "advisory", "UK", "Without-prejudice, confidential, voluntary. Mediator facilitates but does not decide. Parties retain right to litigate.", "2024-04-01"),
        ("norm-sga", "Sale of Goods Act 1979 (as amended)", "statute", "binding", "England & Wales", "Implied terms: satisfactory quality, fitness for purpose. Relevant to software-as-goods arguments.", "1979-01-01"),
    ]
    for nid, name, ntype, enf, juris, text, eff in norms:
        nid_created = await create_node(session, ws, t, "Norm", {"id": nid, "name": name, "norm_type": ntype, "enforceability": enf, "jurisdiction": juris, "text": text, "effective_from": eff})
        await create_edge(session, ws, t, "GOVERNED_BY", "comm-conflict", nid_created, "Conflict", "Norm")

    await create_edge(session, ws, t, "VIOLATES", "ev-delivery-attempt", "norm-contract", "Event", "Norm", {"severity": 0.7})
    await create_edge(session, ws, t, "VIOLATES", "ev-milestone-missed", "norm-contract", "Event", "Norm", {"severity": 0.6})

    # Process + Outcome
    proc = await create_node(session, ws, t, "Process", {"id": "proc-cedr-med", "name": "CEDR Commercial Mediation", "process_type": "mediation_evaluative", "resolution_approach": "interest_based", "status": "active", "formality": "formal", "binding": False, "voluntary": True, "current_stage": "resolution", "started_at": "2024-04-01"})
    await create_edge(session, ws, t, "RESOLVED_THROUGH", "comm-conflict", "proc-cedr-med", "Conflict", "Process")

    outcome = await create_node(session, ws, t, "Outcome", {"id": "out-settlement-draft", "name": "Proposed Settlement Framework", "outcome_type": "settlement", "description": "Apex fixes P1 bugs at own cost within 60 days. GBP 600K compensation to Crestline. 12-month extended warranty. Confidentiality. No admission of liability.", "satisfaction_a": 0.5, "satisfaction_b": 0.55, "joint_value": 0.6, "durability": "durable"})
    await create_edge(session, ws, t, "PRODUCES", "proc-cedr-med", "out-settlement-draft", "Process", "Outcome")

    # Emotions
    emotions = [
        ("emo-james-fear", "james", "fear", "high", -0.8, 0.85, "ev-board-pressure", "2024-03-01"),
        ("emo-sarah-anger", "sarah", "anger", "high", -0.7, 0.8, "ev-ops-failure", "2024-02-15"),
        ("emo-james-shame", "james", "sadness", "medium", -0.5, 0.5, "ev-delivery-attempt", "2024-01-30"),
        ("emo-sarah-anticipation", "sarah", "anticipation", "medium", 0.3, 0.5, "ev-mediation-day", "2024-05-10"),
    ]
    for eid, actor, emotion, intensity, valence, arousal, trigger, date in emotions:
        nid = await create_node(session, ws, t, "EmotionalState", {"id": eid, "primary_emotion": emotion, "intensity": intensity, "valence": valence, "arousal": arousal, "trigger_event_id": trigger, "observed_at": date})
        await create_edge(session, ws, t, "EXPERIENCES", actor, nid, "Actor", "EmotionalState")

    # Trust
    trusts = [
        ("trust-apex-crestline", "apex", "crestline", 0.4, 0.2, 0.3, 0.3, 0.25, "calculus"),
        ("trust-crestline-apex", "crestline", "apex", 0.3, 0.1, 0.15, 0.25, 0.15, "calculus"),
        ("trust-both-mediator", "apex", "mediator-commercial", 0.7, 0.6, 0.75, 0.5, 0.65, "knowledge"),
    ]
    for tid, src, tgt, ab, ben, integ, prop, overall, basis in trusts:
        nid = await create_node(session, ws, t, "TrustState", {"id": tid, "perceived_ability": ab, "perceived_benevolence": ben, "perceived_integrity": integ, "propensity_to_trust": prop, "overall_trust": overall, "trust_basis": basis})
        await create_edge(session, ws, t, "TRUSTS", src, tgt, "Actor", "Actor", {"trust_state_id": tid, "overall_trust": overall})

    # Power
    powers = [
        ("pow-crestline-economic", "crestline", "apex", "economic", 0.8, "a_over_b", 0.7, True),
        ("pow-apex-informational", "apex", "crestline", "informational", 0.65, "a_over_b", 0.5, False),
        ("pow-hsf-positional", "crestline-counsel", "apex-counsel", "positional", 0.7, "a_over_b", 0.6, False),
    ]
    for pid, src, tgt, domain, mag, direction, legit, exercised in powers:
        nid = await create_node(session, ws, t, "PowerDynamic", {"id": pid, "power_domain": domain, "magnitude": mag, "direction": direction, "legitimacy": legit, "exercised": exercised})
        await create_edge(session, ws, t, "HAS_POWER_OVER", src, tgt, "Actor", "Actor", {"power_dynamic_id": pid, "domain": domain, "magnitude": mag})

    # Narratives
    narr = [
        ("narr-apex-scope", "Unfunded scope expansion forced failure", "counter", "Apex", "characterization", 0.7, 0.4, "Crestline continuously expanded requirements without signing change orders or adjusting timeline. The original scope was delivered. Failure is due to client-side scope creep."),
        ("narr-crestline-incompetence", "Vendor incompetence and missed deadlines", "dominant", "Crestline", "characterization", 0.8, 0.5, "Apex lacks the technical capability to deliver enterprise-grade ERP. 23 P1 bugs, 18 months late, warehouse crash. Classic vendor over-promise, under-deliver."),
        ("narr-mediator-commercial", "Commercial reality demands pragmatic resolution", "alternative", "Mediator", "loss_gain", 0.85, 0.3, "Litigation costs estimated at GBP 500K+ each side with 18-month timeline. Both parties need a working system. Settlement preserves value; litigation destroys it."),
    ]
    for nid, name, ntype, persp, frame, coh, reach, content in narr:
        nid_created = await create_node(session, ws, t, "Narrative", {"id": nid, "name": name, "narrative_type": ntype, "perspective": persp, "frame_type": frame, "coherence": coh, "reach": reach, "content": content})
        await create_edge(session, ws, t, "ABOUT", nid_created, "comm-conflict", "Narrative", "Conflict")

    await create_edge(session, ws, t, "PROMOTES", "apex", "narr-apex-scope", "Actor", "Narrative")
    await create_edge(session, ws, t, "PROMOTES", "crestline", "narr-crestline-incompetence", "Actor", "Narrative")

    # Evidence
    evidence = [
        ("evid-contract-doc", "Original Master Services Agreement (signed)", "document", "Both parties", 0.95, "52-page contract including SOW, acceptance criteria, change order procedure."),
        ("evid-email-trail", "Email chain: David Osei flagging scope creep to James", "digital_record", "Apex internal", 0.8, "Internal emails showing PM warned CEO about unbounded scope. Osei: 'We are building 2x the original system.'"),
        ("evid-uat-report", "Independent UAT Report — 23 P1 bugs documented", "document", "Deloitte (independent)", 0.9, "Independent assessment found 23 P1 (critical) and 41 P2 (high) defects in delivered system."),
        ("evid-financial-impact", "Crestline financial impact assessment", "statistical", "PwC (Crestline's auditor)", 0.85, "Quantified losses: GBP 800K emergency operations, GBP 1.2M revenue loss, GBP 2.1M estimated remediation."),
    ]
    for eid, desc, etype, source, rel, detail in evidence:
        nid = await create_node(session, ws, t, "Evidence", {"id": eid, "description": desc, "evidence_type": etype, "source_name": source, "reliability": rel, "metadata": detail})

    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-contract-signed", "evid-contract-doc", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-delivery-attempt", "evid-uat-report", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-ops-failure", "evid-financial-impact", "Event", "Evidence")

    # Roles
    roles = [
        ("role-james-ceo", "respondent", "james", "comm-conflict"),
        ("role-sarah-coo", "claimant", "sarah", "comm-conflict"),
        ("role-faulkner-med", "mediator", "mediator-commercial", "comm-conflict"),
        ("role-osei-witness", "witness", "apex-pm", "comm-conflict"),
        ("role-nguyen-witness", "witness", "crestline-it", "comm-conflict"),
    ]
    for rid, rtype, actor, ctx in roles:
        await create_node(session, ws, t, "Role", {"id": rid, "role_type": rtype, "actor_id": actor, "context_id": ctx})

    print(f"  Commercial complete: 10 actors, 14 events, 6 issues, 8 interests, 3 norms, 1 process, 1 outcome, 3 narratives, 4 emotions, 3 trust states, 3 power dynamics, 3 locations, 4 evidence, 5 roles")


# ═══════════════════════════════════════════════════════════════════
# CASE 3: HR MEDIATION — Alex vs Maya (Expanded)
# ═══════════════════════════════════════════════════════════════════

async def seed_hr(session):
    ws = "hr-mediation-full"
    t = "tacitus"
    print("  Seeding HR Mediation (micro)...")

    # Locations
    loc_office = await create_node(session, ws, t, "Location", {"id": "loc-sf-office", "name": "Northwind Technologies HQ", "location_type": "building", "country_code": "USA", "latitude": 37.7749, "longitude": -122.4194})
    loc_meeting = await create_node(session, ws, t, "Location", {"id": "loc-conf-room", "name": "Conference Room 4B — Mediation Space", "location_type": "building"})

    # Actors (8)
    alex = await create_node(session, ws, t, "Actor", {"id": "alex", "name": "Alex Chen", "actor_type": "person", "description": "Junior software engineer, 14 months tenure. First job after bootcamp. High performer on code quality metrics but struggles with interpersonal dynamics. History of anxiety.", "role_title": "Software Engineer II", "influence_score": 0.25, "gender": "male", "age": 27})
    maya = await create_node(session, ws, t, "Actor", {"id": "maya", "name": "Maya Okonkwo", "actor_type": "person", "description": "Senior engineer, 6 years at Northwind. Tech lead of Platform team. Known for exacting standards. Promoted through technical excellence. Managing people is newer skill.", "role_title": "Senior Engineer / Tech Lead", "influence_score": 0.55, "gender": "female", "age": 34})
    jordan = await create_node(session, ws, t, "Actor", {"id": "jordan", "name": "Jordan Reyes", "actor_type": "person", "description": "HR Business Partner, trained in facilitative mediation (40-hour certificate). 3 years in role. Trusted by engineering teams. Reports to VP People.", "role_title": "HR Business Partner", "influence_score": 0.45, "gender": "non-binary"})
    northwind = await create_node(session, ws, t, "Actor", {"id": "northwind", "name": "Northwind Technologies", "actor_type": "organization", "description": "Mid-stage startup, 200 employees, Series C. Engineering-heavy culture. Flat hierarchy. Recent DEI initiative. Performance review cycle approaching.", "influence_score": 0.7, "org_type": "private", "sector": "technology", "size": "200"})
    priya = await create_node(session, ws, t, "Actor", {"id": "priya", "name": "Priya Sharma", "actor_type": "person", "description": "VP of Engineering. Maya's skip-level manager. Aware of tension but hesitant to intervene. Under pressure to ship Q3 release.", "role_title": "VP Engineering", "influence_score": 0.7})
    teammate1 = await create_node(session, ws, t, "Actor", {"id": "teammate-kai", "name": "Kai Tanaka", "actor_type": "person", "description": "Platform team member, 2 years tenure. Witnessed the code review incident. Close to Alex, uncomfortable with Maya's review style.", "role_title": "Software Engineer II", "influence_score": 0.2})
    teammate2 = await create_node(session, ws, t, "Actor", {"id": "teammate-elena", "name": "Elena Vasquez", "actor_type": "person", "description": "Platform team member, 4 years tenure. Respects Maya's technical standards. Sees Alex as needing to 'toughen up.' Potential coalition partner for Maya.", "role_title": "Senior Engineer", "influence_score": 0.3})
    vp_people = await create_node(session, ws, t, "Actor", {"id": "vp-people", "name": "Marcus Thompson", "actor_type": "person", "description": "VP People & Culture. Concerned about retention metrics and Glassdoor reviews. Wants quiet resolution. Jordan reports to him.", "role_title": "VP People & Culture", "influence_score": 0.65})

    # Memberships
    for member, org in [("alex", "northwind"), ("maya", "northwind"), ("jordan", "northwind"), ("priya", "northwind"), ("teammate-kai", "northwind"), ("teammate-elena", "northwind"), ("vp-people", "northwind")]:
        await create_edge(session, ws, t, "MEMBER_OF", member, org, "Actor", "Actor")

    # Conflict
    conflict = await create_node(session, ws, t, "Conflict", {"id": "hr-conflict", "name": "Alex Chen vs Maya Okonkwo — Code Review Incident & Workplace Dignity", "scale": "micro", "domain": "workplace", "status": "active", "incompatibility": "relationship", "glasl_stage": 3, "glasl_level": "win_win", "kriesberg_phase": "escalating", "violence_type": "none", "intensity": "moderate", "summary": "Interpersonal conflict triggered by harsh public code review. Alex perceives bullying and disrespect; Maya sees it as standard technical feedback. Underlying tensions: cultural communication styles, power imbalance (junior vs senior), unclear code review norms, approaching performance reviews. Formal complaint filed. HR mediation in progress.", "started_at": "2024-06-15"})

    for actor_id, side, role in [
        ("alex", "side_a", "complainant"), ("maya", "side_b", "respondent"),
        ("jordan", "third_party", "mediator"), ("northwind", "observer", "employer"),
        ("priya", "observer", "skip-level manager"), ("vp-people", "observer", "HR executive"),
    ]:
        await create_edge(session, ws, t, "PARTY_TO", actor_id, "hr-conflict", "Actor", "Conflict", {"role": role, "side": side})

    # Events (12)
    events = [
        ("ev-first-tension", "Maya gives Alex's PR first critical review", "disapprove", "2024-04-10", 0.3, "organizational", "written", "Maya leaves 34 comments on Alex's PR #847 in GitHub. Technical feedback is accurate but tone is terse: 'This is wrong,' 'Why would you do it this way,' 'Rewrite entirely.'"),
        ("ev-alex-avoids", "Alex starts avoiding Maya in standups", "reject", "2024-04-25", 0.35, "interpersonal", "verbal", "Alex stops asking Maya questions directly. Routes technical questions through Kai. Standup contributions become minimal."),
        ("ev-code-review-incident", "The Incident: Maya publicly criticizes Alex's architecture in team meeting", "disapprove", "2024-06-15", 0.75, "organizational", "verbal", "During weekly architecture review, Maya says: 'This design shows fundamental misunderstanding of our system. I don't know how this passed initial review.' 6 team members present. Alex goes silent."),
        ("ev-alex-panic", "Alex has anxiety attack after meeting, leaves office", "reject", "2024-06-15", 0.7, "interpersonal", "verbal", "Alex experiences chest tightness, leaves office at 2pm. Texts Kai: 'I can't go back in there.' Takes mental health day next day."),
        ("ev-kai-reports", "Kai raises concern to Jordan about team dynamics", "consult", "2024-06-17", 0.4, "organizational", "verbal", "Kai approaches Jordan: 'Something's really wrong on the team. Alex is falling apart and Maya doesn't see it.' First HR awareness."),
        ("ev-formal-complaint", "Alex files formal complaint — hostile work environment", "demand", "2024-06-20", 0.65, "organizational", "written", "Written complaint alleging: pattern of public humiliation, disproportionate scrutiny of his PRs, racially coded language ('you people don't understand systems'). Requests investigation."),
        ("ev-maya-shocked", "Maya learns of complaint — feels blindsided", "reject", "2024-06-21", 0.6, "interpersonal", "verbal", "Jordan informs Maya. Maya: 'I was giving technical feedback. I treat everyone the same. This is about code quality, not personality.'"),
        ("ev-team-splits", "Team informally divides along fault lines", "reject", "2024-06-25", 0.55, "organizational", "verbal", "Kai and 2 juniors sympathize with Alex. Elena and senior engineers back Maya's right to maintain standards. Hallway conversations become political."),
        ("ev-priya-concerned", "Priya notices sprint velocity dropping 30%", "investigate", "2024-07-01", 0.5, "organizational", "administrative", "Q3 release at risk. Code review turnaround time doubled. Team collaboration metrics plummeting. Priya asks Jordan to accelerate resolution."),
        ("ev-pre-mediation", "Jordan conducts separate pre-mediation intake sessions", "consult", "2024-07-05", 0.4, "organizational", "verbal", "Individual 1-hour sessions with Alex and Maya. Jordan identifies overlapping interests (both want professional respect) and core gaps (communication style, feedback norms)."),
        ("ev-mediation-session", "Facilitative mediation session — 3 hours", "cooperate", "2024-07-10", 0.35, "organizational", "verbal", "Joint session at Conference Room 4B. Ground rules set. Alex shares impact ('I dread coming to work'). Maya listens — first time she hears emotional effect. Breakthrough: Maya acknowledges her directness can land differently than intended."),
        ("ev-agreement-draft", "Working agreement on code review norms", "agree", "2024-07-10", 0.25, "organizational", "written", "Draft agreement: written CR feedback only (no public verbal criticism), praise-critique-praise framework, bi-weekly 1:1 between Alex and Maya, team code review style guide to be written."),
    ]
    for eid, name, etype, date, sev, ctx, mode, desc in events:
        nid = await create_node(session, ws, t, "Event", {"id": eid, "name": name, "event_type": etype, "occurred_at": date, "severity": sev, "context": ctx, "mode": mode, "description": desc})
        await create_edge(session, ws, t, "PART_OF", nid, "hr-conflict", "Event", "Conflict")

    await create_edge(session, ws, t, "AT_LOCATION", "ev-code-review-incident", "loc-sf-office", "Event", "Location")
    await create_edge(session, ws, t, "AT_LOCATION", "ev-mediation-session", "loc-conf-room", "Event", "Location")

    # Causal
    causal = [
        ("ev-first-tension", "ev-alex-avoids", "escalation", 0.7),
        ("ev-alex-avoids", "ev-code-review-incident", "escalation", 0.6),
        ("ev-code-review-incident", "ev-alex-panic", "escalation", 0.95),
        ("ev-code-review-incident", "ev-kai-reports", "spillover", 0.8),
        ("ev-alex-panic", "ev-formal-complaint", "escalation", 0.85),
        ("ev-formal-complaint", "ev-maya-shocked", "retaliation", 0.9),
        ("ev-formal-complaint", "ev-team-splits", "contagion", 0.7),
        ("ev-team-splits", "ev-priya-concerned", "spillover", 0.75),
        ("ev-priya-concerned", "ev-pre-mediation", "precedent", 0.85),
        ("ev-pre-mediation", "ev-mediation-session", "precedent", 0.95),
        ("ev-mediation-session", "ev-agreement-draft", "precedent", 0.9),
    ]
    for src, tgt, mech, strength in causal:
        await create_edge(session, ws, t, "CAUSED", src, tgt, "Event", "Event", {"mechanism": mech, "strength": strength})

    # Issues (5)
    issues = [
        ("iss-communication", "Communication style and feedback delivery", "procedural", 0.85, 0.7, "No agreed norms for code review tone. Maya's directness vs Alex's sensitivity. Cultural communication gap."),
        ("iss-respect", "Professional respect and psychological safety", "psychological", 0.9, 0.3, "Alex feels publicly humiliated. Maya feels her technical authority is being questioned through HR process."),
        ("iss-power", "Power imbalance — junior vs tech lead", "substantive", 0.75, 0.4, "Maya writes Alex's performance review. Alex can't push back without career risk. Structural asymmetry."),
        ("iss-race", "Potential racial/cultural dimension", "identity", 0.6, 0.2, "Alex is Asian-American, Maya is Nigerian-British. Alex alleges racially coded language. Maya denies racial intent. Complex intersectionality."),
        ("iss-standards", "Code quality standards vs learning culture", "procedural", 0.7, 0.6, "Company values both high standards and growth mindset. Tension between excellence and psychological safety."),
    ]
    for iid, name, itype, sal, div, desc in issues:
        nid = await create_node(session, ws, t, "Issue", {"id": iid, "name": name, "issue_type": itype, "salience": sal, "divisibility": div, "description": desc})
        await create_edge(session, ws, t, "PART_OF", nid, "hr-conflict", "Issue", "Conflict")

    # Interests (8)
    interests = [
        ("int-alex-safety", "alex", "Feel safe contributing code without public humiliation", "psychological", 5, True, "No more public criticism of my work", 0.1, "moderate", 0.4),
        ("int-alex-growth", "alex", "Continue learning and advancing as an engineer", "substantive", 4, True, "Clear path to mid-level promotion", 0.3, "weak", 0.3),
        ("int-alex-acknowledged", "alex", "Acknowledgment that Maya's behavior was harmful", "psychological", 4, True, "Apology or at minimum recognition of impact", 0.0, "weak", 0.5),
        ("int-maya-standards", "maya", "Maintain high code quality standards on platform team", "substantive", 5, True, "Right to give honest technical feedback", 0.5, "strong", 0.7),
        ("int-maya-authority", "maya", "Preserve technical leadership credibility", "psychological", 5, False, "Not be undermined by HR process", 0.4, "moderate", 0.6),
        ("int-maya-fairness", "maya", "Be treated fairly — not labeled as bully for doing her job", "psychological", 4, True, "Complaint withdrawn or resolved without finding against her", 0.2, "moderate", 0.5),
        ("int-northwind-retain", "northwind", "Retain both employees (hiring cost: ~$50K each)", "substantive", 4, False, "Neither person leaves", 0.5, "weak", 0.3),
        ("int-northwind-culture", "northwind", "Demonstrate commitment to inclusive culture", "psychological", 3, False, "DEI initiative seen as genuine", 0.4, "moderate", 0.5),
    ]
    for iid, actor, desc, itype, prio, stated, pos, sat, batna, rv in interests:
        nid = await create_node(session, ws, t, "Interest", {"id": iid, "description": desc, "interest_type": itype, "priority": prio, "stated": stated, "stated_position": pos, "satisfaction": sat, "batna_strength": batna, "reservation_value": rv})
        await create_edge(session, ws, t, "HAS_INTEREST", actor, nid, "Actor", "Interest")

    # Norms
    norms = [
        ("norm-employee-handbook", "Northwind Employee Handbook — Anti-Harassment Policy", "policy", "binding", "Northwind Technologies", "Section 7.3: All employees are expected to maintain a respectful workplace. Harassment includes repeated unwelcome conduct that creates an intimidating environment.", "2023-01-01"),
        ("norm-code-review-policy", "Engineering Code Review Guidelines (informal)", "social_norm", "advisory", "Platform Team", "Current practice: no written standard. Reviews happen in GitHub PRs. Verbal feedback in architecture reviews is common but unstructured.", "2022-06-01"),
        ("norm-ca-feha", "California FEHA — Fair Employment and Housing Act", "statute", "binding", "California", "Prohibits workplace harassment based on protected characteristics including race, national origin. Employers liable for failing to prevent harassment.", "1959-01-01"),
    ]
    for nid, name, ntype, enf, juris, text, eff in norms:
        nid_created = await create_node(session, ws, t, "Norm", {"id": nid, "name": name, "norm_type": ntype, "enforceability": enf, "jurisdiction": juris, "text": text, "effective_from": eff})
        await create_edge(session, ws, t, "GOVERNED_BY", "hr-conflict", nid_created, "Conflict", "Norm")

    # Process + Outcome
    proc = await create_node(session, ws, t, "Process", {"id": "proc-hr-mediation", "name": "Facilitative HR Mediation", "process_type": "mediation_facilitative", "resolution_approach": "interest_based", "status": "active", "formality": "semi_formal", "binding": False, "voluntary": True, "current_stage": "resolution", "started_at": "2024-07-05"})
    await create_edge(session, ws, t, "RESOLVED_THROUGH", "hr-conflict", "proc-hr-mediation", "Conflict", "Process")

    outcome = await create_node(session, ws, t, "Outcome", {"id": "out-working-agreement", "name": "Working Agreement on Team Norms", "outcome_type": "agreement", "description": "Written-only CR feedback. Praise-critique-praise framework. Bi-weekly 1:1 between Alex and Maya. Team code review style guide. 90-day check-in with Jordan.", "satisfaction_a": 0.6, "satisfaction_b": 0.5, "joint_value": 0.65, "durability": "durable"})
    await create_edge(session, ws, t, "PRODUCES", "proc-hr-mediation", "out-working-agreement", "Process", "Outcome")

    # Emotions (10 — rich emotional journey)
    emotions = [
        ("emo-alex-shame", "alex", "sadness", "high", -0.8, 0.7, "ev-code-review-incident", "2024-06-15"),
        ("emo-alex-fear", "alex", "fear", "high", -0.9, 0.9, "ev-code-review-incident", "2024-06-15"),
        ("emo-alex-anger", "alex", "anger", "medium", -0.6, 0.6, "ev-formal-complaint", "2024-06-20"),
        ("emo-alex-hope", "alex", "anticipation", "low", 0.3, 0.4, "ev-mediation-session", "2024-07-10"),
        ("emo-maya-surprise", "maya", "surprise", "high", -0.5, 0.8, "ev-formal-complaint", "2024-06-21"),
        ("emo-maya-anger", "maya", "anger", "high", -0.7, 0.75, "ev-maya-shocked", "2024-06-21"),
        ("emo-maya-disgust", "maya", "disgust", "medium", -0.4, 0.5, "ev-team-splits", "2024-06-25"),
        ("emo-maya-sadness", "maya", "sadness", "medium", -0.5, 0.4, "ev-mediation-session", "2024-07-10"),
        ("emo-priya-fear", "priya", "fear", "medium", -0.5, 0.6, "ev-priya-concerned", "2024-07-01"),
        ("emo-kai-trust", "teammate-kai", "trust", "medium", 0.4, 0.3, "ev-kai-reports", "2024-06-17"),
    ]
    for eid, actor, emotion, intensity, valence, arousal, trigger, date in emotions:
        nid = await create_node(session, ws, t, "EmotionalState", {"id": eid, "primary_emotion": emotion, "intensity": intensity, "valence": valence, "arousal": arousal, "trigger_event_id": trigger, "observed_at": date})
        await create_edge(session, ws, t, "EXPERIENCES", actor, nid, "Actor", "EmotionalState")

    # Trust
    trusts = [
        ("trust-alex-maya", "alex", "maya", 0.6, 0.1, 0.15, 0.3, 0.15, "calculus"),
        ("trust-maya-alex", "maya", "alex", 0.25, 0.4, 0.5, 0.4, 0.35, "knowledge"),
        ("trust-alex-jordan", "alex", "jordan", 0.5, 0.7, 0.75, 0.5, 0.65, "knowledge"),
        ("trust-maya-jordan", "maya", "jordan", 0.55, 0.5, 0.6, 0.4, 0.52, "knowledge"),
        ("trust-alex-kai", "alex", "teammate-kai", 0.6, 0.85, 0.8, 0.7, 0.8, "identification"),
    ]
    for tid, src, tgt, ab, ben, integ, prop, overall, basis in trusts:
        nid = await create_node(session, ws, t, "TrustState", {"id": tid, "perceived_ability": ab, "perceived_benevolence": ben, "perceived_integrity": integ, "propensity_to_trust": prop, "overall_trust": overall, "trust_basis": basis})
        await create_edge(session, ws, t, "TRUSTS", src, tgt, "Actor", "Actor", {"trust_state_id": tid, "overall_trust": overall})

    # Power dynamics
    powers = [
        ("pow-maya-alex-positional", "maya", "alex", "positional", 0.75, "a_over_b", 0.7, True),
        ("pow-maya-alex-expert", "maya", "alex", "expert", 0.8, "a_over_b", 0.85, True),
        ("pow-priya-maya", "priya", "maya", "legitimate", 0.65, "a_over_b", 0.8, False),
        ("pow-jordan-process", "jordan", "maya", "legitimate", 0.5, "a_over_b", 0.6, True),
        ("pow-alex-complaint", "alex", "maya", "legitimate", 0.4, "a_over_b", 0.5, True),
    ]
    for pid, src, tgt, domain, mag, direction, legit, exercised in powers:
        nid = await create_node(session, ws, t, "PowerDynamic", {"id": pid, "power_domain": domain, "magnitude": mag, "direction": direction, "legitimacy": legit, "exercised": exercised})
        await create_edge(session, ws, t, "HAS_POWER_OVER", src, tgt, "Actor", "Actor", {"power_dynamic_id": pid, "domain": domain, "magnitude": mag})

    # Narratives
    narr = [
        ("narr-alex-bullying", "Pattern of workplace bullying and public humiliation", "dominant", "Alex", "characterization", 0.7, 0.4, "Maya has repeatedly singled out my work for public criticism. The incident on June 15 was the worst, but it's part of a pattern. Her comment 'you people' had racial undertones. I've been made to feel incompetent and unwelcome."),
        ("narr-maya-standards", "Holding the line on engineering excellence", "counter", "Maya", "moral", 0.75, 0.5, "I give the same feedback to everyone. My job as tech lead is to maintain code quality. Alex's architecture was genuinely flawed. Sugarcoating technical issues leads to production incidents. I've built this team's reputation for quality."),
        ("narr-jordan-growth", "Opportunity for team growth through difficult conversations", "alternative", "Jordan", "identity", 0.8, 0.3, "Both Alex and Maya have legitimate needs. This isn't about who's right — it's about building feedback norms that serve both quality and psychological safety. The team can emerge stronger."),
        ("narr-elena-toughen", "Engineering isn't for the faint-hearted", "subjugated", "Elena", "characterization", 0.5, 0.2, "Everyone gets tough feedback early in their career. I did, and it made me better. Maya's style is direct but she's not cruel. The complaint process itself is more disruptive than the original review."),
    ]
    for nid, name, ntype, persp, frame, coh, reach, content in narr:
        nid_created = await create_node(session, ws, t, "Narrative", {"id": nid, "name": name, "narrative_type": ntype, "perspective": persp, "frame_type": frame, "coherence": coh, "reach": reach, "content": content})
        await create_edge(session, ws, t, "ABOUT", nid_created, "hr-conflict", "Narrative", "Conflict")

    await create_edge(session, ws, t, "PROMOTES", "alex", "narr-alex-bullying", "Actor", "Narrative")
    await create_edge(session, ws, t, "PROMOTES", "maya", "narr-maya-standards", "Actor", "Narrative")
    await create_edge(session, ws, t, "PROMOTES", "jordan", "narr-jordan-growth", "Actor", "Narrative")
    await create_edge(session, ws, t, "PROMOTES", "teammate-elena", "narr-elena-toughen", "Actor", "Narrative")

    # Evidence
    evidence = [
        ("evid-pr-comments", "GitHub PR #847 — 34 comments from Maya on Alex's code", "digital_record", "GitHub", 0.95, "Complete record of all code review comments. Tone analysis shows 28/34 negative, 6 neutral, 0 positive."),
        ("evid-alex-statement", "Alex's written complaint (4 pages)", "document", "Alex Chen", 0.7, "Detailed account of incidents from April to June 2024, including specific quotes and dates."),
        ("evid-kai-statement", "Kai's witness statement (confidential)", "testimony", "Kai Tanaka", 0.75, "Corroborates Alex's account of June 15 incident. Notes Maya's comment and Alex's visible distress."),
        ("evid-slack-logs", "Slack DM between Alex and Kai after incident", "digital_record", "Slack", 0.85, "Alex: 'I can't do this anymore. She makes me feel like I don't belong here.' Kai: 'That was really harsh. You should talk to HR.'"),
    ]
    for eid, desc, etype, source, rel, detail in evidence:
        nid = await create_node(session, ws, t, "Evidence", {"id": eid, "description": desc, "evidence_type": etype, "source_name": source, "reliability": rel, "metadata": detail})

    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-first-tension", "evid-pr-comments", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-formal-complaint", "evid-alex-statement", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-kai-reports", "evid-kai-statement", "Event", "Evidence")
    await create_edge(session, ws, t, "EVIDENCED_BY", "ev-alex-panic", "evid-slack-logs", "Event", "Evidence")

    # Roles
    roles = [
        ("role-alex-complainant", "claimant", "alex", "hr-conflict"),
        ("role-maya-respondent", "respondent", "maya", "hr-conflict"),
        ("role-jordan-mediator", "mediator", "jordan", "hr-conflict"),
        ("role-kai-witness", "witness", "teammate-kai", "hr-conflict"),
        ("role-elena-ally", "ally", "teammate-elena", "hr-conflict"),
        ("role-priya-bystander", "bystander", "priya", "hr-conflict"),
    ]
    for rid, rtype, actor, ctx in roles:
        await create_node(session, ws, t, "Role", {"id": rid, "role_type": rtype, "actor_id": actor, "context_id": ctx})

    # Alliances and oppositions (team dynamics)
    await create_edge(session, ws, t, "ALLIED_WITH", "alex", "teammate-kai", "Actor", "Actor", {"strength": 0.8, "formality": "tacit"})
    await create_edge(session, ws, t, "ALLIED_WITH", "maya", "teammate-elena", "Actor", "Actor", {"strength": 0.65, "formality": "tacit"})
    await create_edge(session, ws, t, "OPPOSED_TO", "alex", "maya", "Actor", "Actor", {"intensity": 0.6, "since": "2024-06-15"})

    print(f"  HR Mediation complete: 8 actors, 12 events, 5 issues, 8 interests, 3 norms, 1 process, 1 outcome, 4 narratives, 10 emotions, 5 trust states, 5 power dynamics, 2 locations, 4 evidence, 6 roles")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

async def main():
    print(f"Connecting to Neo4j: {NEO4J_URI}")
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    try:
        await driver.verify_connectivity()
        print("Connected successfully!\n")

        async with driver.session(database=NEO4J_DATABASE) as session:
            # Clear existing data
            print("Clearing existing data...")
            await run_query(session, "MATCH (n {category: 'MOCK_DIALECTICA'}) DETACH DELETE n")
            print("Database cleared.\n")

            print("Seeding 3 expanded conflict cases (Full Tier 3)...\n")
            await seed_jcpoa(session)
            print()
            await seed_commercial(session)
            print()
            await seed_hr(session)

            # Final stats
            result = await session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC")
            records = await result.data()
            print("\n=== FINAL DATABASE STATS ===")
            total_nodes = 0
            for r in records:
                print(f"  {r['label']}: {r['cnt']}")
                total_nodes += r['cnt']

            result2 = await session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt ORDER BY cnt DESC")
            records2 = await result2.data()
            total_edges = 0
            print()
            for r in records2:
                print(f"  {r['type']}: {r['cnt']}")
                total_edges += r['cnt']

            print(f"\n  TOTAL: {total_nodes} nodes, {total_edges} edges")
            print("\nDone!")

    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())

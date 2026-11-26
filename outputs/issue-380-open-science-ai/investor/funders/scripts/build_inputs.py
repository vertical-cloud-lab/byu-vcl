#!/usr/bin/env python3
"""Build the venture list (U1, U2, U3; see PROTOCOL.md) and split it into deal-pass inputs.

U1 comes from part 2's frozen classification (one row per company, several GitHub orgs merged). U2 and U3 are
hand-picked and listed below with the list each came from. Run from funders/.
"""
import csv, os, re

OWN = "../owners/data/finance_passes/input_all.csv"
OUT = "data"

# key, venture, category, source_list, hint for the researcher
U2 = [
    ("arduino", "Arduino (Arduino S.r.l. / BCMI)", "open hardware", "round1", "boards; Qualcomm deal 2025"),
    ("raspberry-pi", "Raspberry Pi Holdings / Raspberry Pi Ltd", "open hardware (partial)", "round1", "LSE IPO 2024"),
    ("adafruit", "Adafruit Industries", "open hardware", "round1", ""),
    ("sparkfun", "SparkFun Electronics", "open hardware", "round1", ""),
    ("seeed", "Seeed Studio (Seeed Technology)", "open hardware (partial)", "round1", "Shenzhen"),
    ("pine64", "Pine64 (Pine Store Ltd)", "open hardware", "round1", ""),
    ("prusa", "Prusa Research", "open hardware, 3D printing", "round1", "Czech"),
    ("ultimaker", "UltiMaker (Ultimaker B.V.)", "3D printing, Cura open source", "round1", "merged with MakerBot 2022"),
    ("makerbot", "MakerBot Industries", "3D printing, open designs until 2012", "round1", "Stratasys 2013"),
    ("aleph-objects", "Aleph Objects (LulzBot)", "open hardware, 3D printing", "round1", "assets to FAME 3D 2019"),
    ("openbci", "OpenBCI", "open hardware neurotech", "round1", ""),
    ("sofar-openrov", "Sofar Ocean Technologies (formerly OpenROV)", "open hardware, marine", "round1", ""),
    ("system76", "System76", "open firmware, Pop!_OS, open hardware designs", "round1", ""),
    ("framework", "Framework Computer", "repairable laptops, open docs (partial)", "round1", ""),
    ("sifive", "SiFive", "RISC-V; open-source Rocket chip generator", "round1", ""),
    ("oxide", "Oxide Computer Company", "open-source firmware and software for its racks", "round1", ""),
    ("kitware", "Kitware", "VTK, ParaView, CMake, 3D Slicer", "round1", ""),
    ("enthought", "Enthought", "scientific Python (SciPy origins)", "round1", ""),
    ("posit", "Posit PBC (RStudio)", "RStudio IDE, Shiny, Quarto", "round1", ""),
    ("anaconda", "Anaconda, Inc. (Continuum Analytics)", "conda, Anaconda distribution", "round1", ""),
    ("evolutionaryscale", "EvolutionaryScale", "open-weight ESM models (partial)", "round1", ""),
    ("orbital-materials", "Orbital Materials (Orbital Industries)", "open-source Orb materials models", "round1", ""),
    ("radical-ai", "Radical AI", "closed SDL with open simulation tools (TorchSim) (partial)", "round1", ""),
    ("boltz", "Boltz PBC", "open-source Boltz-1/Boltz-2 models", "round1", ""),
    ("chai-discovery", "Chai Discovery", "Chai-1 weights released (partial)", "round1", ""),
    ("overleaf", "Overleaf (WriteLaTeX)", "open-source LaTeX editor (AGPL)", "added", "Digital Science"),
    ("protocols-io", "protocols.io", "open-access methods platform", "added", "Springer Nature 2023"),
    ("figshare", "Figshare", "open data repository (code closed)", "added", "Digital Science"),
    ("code-ocean", "Code Ocean", "reproducibility platform (partial)", "added", ""),
    ("curvenote", "Curvenote", "open-source science publishing (MyST)", "added", ""),
    ("arcadia-science", "Arcadia Science", "open-science R&D company, publishes openly", "added", ""),
    ("researchhub", "ResearchHub (ResearchHub Technologies)", "open science platform, DeSci", "added", ""),
    ("molecule", "Molecule (Molecule AG)", "DeSci, IP-NFTs", "added", ""),
    ("vitadao", "VitaDAO", "DeSci DAO funding open longevity research", "added", ""),
    ("bio-protocol", "BIO Protocol (Bio.xyz)", "DeSci", "added", ""),
    ("labdao", "LabDAO", "DeSci open tools", "added", ""),
    ("deep-forest", "Deep Forest Sciences", "DeepChem company", "added", ""),
    ("rowan", "Rowan (Rowan Scientific)", "computational chemistry with open-source tools (partial)", "added", ""),
    ("entalpic", "Entalpic", "materials AI with open releases (partial)", "added", "France"),
    ("valence-labs", "Valence Labs", "open-source drug-discovery tools (datamol)", "added", "Recursion 2023"),
    ("quansight", "Quansight", "open-source scientific Python services", "added", ""),
    ("openteams", "OpenTeams", "open-source services", "added", ""),
    ("coiled", "Coiled", "Dask company", "added", ""),
    ("quantstack", "QuantStack", "Jupyter, conda-forge, mamba", "added", "France"),
    ("prefix-dev", "prefix.dev", "pixi and conda tooling", "added", "Germany"),
    ("probabl", "Probabl", "scikit-learn company", "added", "Inria spin-off"),
    ("juliahub", "JuliaHub (Julia Computing)", "Julia language", "added", ""),
    ("cocalc", "SageMath, Inc. (CoCalc)", "SageMath, CoCalc", "added", ""),
    ("glencoe", "Glencoe Software", "OME / OMERO bioimaging", "added", ""),
    ("open-imaging", "Open Imaging, Inc.", "Micro-Manager", "added", ""),
    ("observable", "Observable, Inc.", "D3, Observable Plot and Framework", "added", ""),
    ("opencfd", "OpenCFD Ltd", "OpenFOAM", "added", "SGI 2011, ESI 2012"),
    ("scilab", "Scilab Enterprises", "Scilab", "added", "ESI 2017"),
    ("deltablot", "Deltablot (eLabFTW)", "open-source electronic lab notebook", "added", ""),
    ("scinote", "SciNote", "electronic lab notebook, once open source", "added", ""),
    ("open-robotics", "Open Robotics (OSRF commercial arm)", "ROS, Gazebo", "added", "Intrinsic 2022"),
    ("willow-garage", "Willow Garage", "ROS, PR2", "added", "closed 2014"),
    ("picknik", "PickNik Robotics", "MoveIt", "added", ""),
    ("pollen-robotics", "Pollen Robotics", "open-source robots (Reachy)", "added", "Hugging Face 2025"),
    ("k-scale", "K-Scale Labs", "open-source humanoid robots", "added", ""),
    ("hello-robot", "Hello Robot", "Stretch, open-source software (partial)", "added", ""),
    ("auterion", "Auterion", "PX4 drones", "added", ""),
    ("3d-robotics", "3D Robotics (3DR)", "ArduPilot/PX4 drones", "added", ""),
    ("tier-iv", "TIER IV", "Autoware", "added", "Japan"),
    ("itseez", "Itseez", "OpenCV", "added", "Intel 2016"),
    ("particle", "Particle (Spark Labs)", "open-source IoT hardware", "added", ""),
    ("mycroft", "Mycroft AI", "open-source voice assistant", "added", "equity crowdfunding"),
    ("mnt-research", "MNT Research", "open-source laptop (Reform)", "added", ""),
    ("purism", "Purism", "free-software laptops and phones", "added", ""),
    ("bitcraze", "Bitcraze", "open-source drones (Crazyflie)", "added", "Sweden"),
    ("open-bionics", "Open Bionics", "prosthetics, open designs early", "added", "UK"),
    ("farmbot", "FarmBot", "open-source farming robot", "added", ""),
    ("backyard-brains", "Backyard Brains", "open-source neuroscience kits", "added", ""),
    ("openuc2", "openUC2", "open-source optics toolkit", "added", "Germany"),
    ("opulo", "Opulo (LumenPnP)", "open-source pick-and-place", "added", ""),
    ("inventables", "Inventables", "open-source CNC (X-Carve)", "added", ""),
    ("printrbot", "Printrbot", "open-source 3D printers", "added", "closed 2018"),
    ("re3d", "re:3D", "Gigabot, open source", "added", ""),
    ("bcn3d", "BCN3D Technologies", "open-source 3D printers", "added", "Spain"),
    ("efabless", "Efabless", "open-source silicon", "added", "shut 2025"),
    ("antmicro", "Antmicro", "open-source hardware and software services (Renode)", "added", "Poland"),
    ("tenstorrent", "Tenstorrent", "open-source software stack, RISC-V (partial)", "added", ""),
    ("trilobio", "Trilobio", "lab automation; check openness", "added", ""),
    ("micropython", "George Robotics (MicroPython)", "MicroPython", "added", ""),
    ("openenergymonitor", "OpenEnergyMonitor (Megni)", "open-source energy monitors", "added", "UK"),
    ("nabu-casa", "Nabu Casa (Home Assistant)", "Home Assistant", "added", ""),
    ("crowd-supply", "Crowd Supply", "open hardware crowdfunding platform", "added", ""),
    ("authorea", "Authorea", "open-science writing", "added", "Wiley 2018"),
    ("f1000", "F1000 Research", "open-access publishing", "added", ""),
    ("frontiers", "Frontiers Media", "open-access publisher", "added", ""),
    ("bela", "Augmented Instruments (Bela)", "open-source audio hardware", "added", "UK"),
    ("openmv", "OpenMV", "open-source machine vision camera", "added", ""),
    ("luxonis", "Luxonis", "OAK cameras, open hardware designs", "added", ""),
    ("great-scott-gadgets", "Great Scott Gadgets", "open-source hardware (HackRF)", "added", ""),
    ("ettus", "Ettus Research", "USRP, open-source UHD", "added", "NI 2010"),
    ("lime-micro", "Lime Microsystems (LimeSDR)", "open-source SDR", "added", "UK"),
    ("nuand", "Nuand (bladeRF)", "open-source SDR", "added", ""),
    ("pjrc-skip", "", "", "", ""),
]
U2 = [r for r in U2 if r[1]]

U3 = [
    # H1 listing cohort (open-source origin) and the first round's for-profit open-source companies
    ("red-hat", "Red Hat", "COSS (Linux)", "round1", "IBM 2019"),
    ("mysql-ab", "MySQL AB", "COSS (database)", "round1", "Sun 2008"),
    ("hortonworks", "Hortonworks", "COSS (Hadoop)", "cohort", ""),
    ("cloudera", "Cloudera", "COSS (Hadoop)", "cohort", ""),
    ("talend", "Talend", "COSS (data integration)", "cohort", ""),
    ("mulesoft", "MuleSoft", "COSS (integration)", "cohort", ""),
    ("springsource-pivotal", "SpringSource / Pivotal Software", "COSS (Spring, Cloud Foundry)", "cohort", ""),
    ("jfrog", "JFrog", "COSS (Artifactory OSS)", "cohort", ""),
    ("confluent", "Confluent", "COSS (Kafka)", "cohort", "IBM 2026"),
    ("suse", "SUSE", "COSS (Linux)", "cohort", ""),
    ("kaltura", "Kaltura", "COSS (video)", "cohort", ""),
    ("couchbase", "Couchbase", "COSS (database)", "cohort", ""),
    ("mariadb", "MariaDB", "COSS (database)", "cohort", ""),
    ("instructure", "Instructure", "COSS (Canvas LMS)", "cohort", ""),
    ("forgerock", "ForgeRock", "COSS (identity)", "cohort", ""),
    ("lightbend", "Lightbend (Typesafe)", "COSS (Scala, Akka)", "round1", ""),
    ("neo4j", "Neo4j", "COSS (graph database)", "round1", ""),
    ("airbyte", "Airbyte", "COSS (data integration)", "round1", ""),
    ("astronomer", "Astronomer", "COSS (Airflow)", "round1", ""),
    ("automattic", "Automattic", "COSS (WordPress)", "round1", ""),
    ("canonical", "Canonical", "COSS (Ubuntu)", "round1", ""),
    ("dagster", "Dagster Labs (Elementl)", "COSS (data orchestration)", "round1", ""),
    ("databricks", "Databricks", "COSS (Spark, Delta, MLflow)", "round1", ""),
    ("dbt-labs", "dbt Labs (Fishtown Analytics)", "COSS (dbt)", "round1", ""),
    ("github", "GitHub", "open-source platform", "round1", "Microsoft 2018"),
    ("puppet", "Puppet", "COSS (config management)", "round1", ""),
    ("mistral", "Mistral AI", "open-weight AI", "round1", ""),
    ("together-ai", "Together AI", "open-source AI, open models", "round1", ""),
    ("pydantic", "Pydantic Services", "COSS (Pydantic, Logfire)", "round1", ""),
    ("replicate", "Replicate", "open-source Cog; model hosting", "round1", "Cloudflare 2025"),
    ("weaviate", "Weaviate", "COSS (vector database)", "round1", ""),
    ("ggml", "ggml.ai", "llama.cpp, ggml", "round1", ""),
    ("inferact", "Inferact (vLLM)", "COSS (vLLM)", "round1", ""),
    # Historic COSS ventures, 1990s to 2010s
    ("cygnus", "Cygnus Solutions", "COSS (GNU toolchain)", "added", "Red Hat 1999"),
    ("va-linux", "VA Linux Systems", "Linux systems, SourceForge", "added", "IPO 1999"),
    ("sleepycat", "Sleepycat Software", "COSS (Berkeley DB)", "added", "Oracle 2006"),
    ("trolltech", "Trolltech", "COSS (Qt)", "added", "Nokia 2008"),
    ("sendmail", "Sendmail, Inc.", "COSS (sendmail)", "added", "Proofpoint 2013"),
    ("zend", "Zend Technologies", "COSS (PHP)", "added", ""),
    ("jboss", "JBoss", "COSS (Java app server)", "added", "Red Hat 2006"),
    ("xensource", "XenSource", "COSS (Xen)", "added", "Citrix 2007"),
    ("sourcefire", "Sourcefire", "COSS (Snort)", "added", "IPO 2007, Cisco 2013"),
    ("zimbra", "Zimbra", "COSS (email)", "added", "Yahoo 2007"),
    ("collabnet", "CollabNet", "COSS (Subversion)", "added", ""),
    ("hyperic", "Hyperic", "COSS (monitoring)", "added", "SpringSource 2009"),
    ("alfresco", "Alfresco Software", "COSS (content management)", "added", ""),
    ("acquia", "Acquia", "COSS (Drupal)", "added", "Vista 2019"),
    ("liferay", "Liferay", "COSS (portal)", "added", ""),
    ("sugarcrm", "SugarCRM", "COSS (CRM)", "added", ""),
    ("pentaho", "Pentaho", "COSS (BI)", "added", "Hitachi 2015"),
    ("jaspersoft", "Jaspersoft", "COSS (BI)", "added", "TIBCO 2014"),
    ("digium", "Digium", "COSS (Asterisk)", "added", "Sangoma 2018"),
    ("enterprisedb", "EnterpriseDB (EDB)", "COSS (PostgreSQL)", "added", ""),
    ("percona", "Percona", "open-source database services", "added", ""),
    ("basho", "Basho Technologies", "COSS (Riak)", "added", "shut 2017"),
    ("foundationdb", "FoundationDB", "database, open-sourced after Apple bought it (partial)", "added", "Apple 2015"),
    ("nicira", "Nicira", "COSS (Open vSwitch)", "added", "VMware 2012"),
    ("inktank", "Inktank", "COSS (Ceph)", "added", "Red Hat 2014"),
    ("gluster", "Gluster", "COSS (GlusterFS)", "added", "Red Hat 2011"),
    ("cumulus", "Cumulus Networks", "open networking (partial)", "added", "Nvidia 2020"),
    ("mirantis", "Mirantis", "COSS (OpenStack, Kubernetes)", "added", ""),
    ("nebula", "Nebula, Inc.", "OpenStack appliance", "added", "shut 2015"),
    ("coreos", "CoreOS", "COSS (container Linux, etcd)", "added", "Red Hat 2018"),
    ("heptio", "Heptio", "COSS (Kubernetes tools)", "added", "VMware 2018"),
    ("mesosphere", "Mesosphere (D2iQ)", "COSS (Mesos, DC/OS)", "added", "shut 2023"),
    ("weaveworks", "Weaveworks", "COSS (Flux, Weave)", "added", "shut 2024"),
    ("ansible", "Ansible (AnsibleWorks)", "COSS (automation)", "added", "Red Hat 2015"),
    ("saltstack", "SaltStack", "COSS (automation)", "added", "VMware 2020"),
    ("chef", "Chef Software (Opscode)", "COSS (automation)", "added", "Progress 2020"),
    ("npm", "npm, Inc.", "open-source package registry", "added", "GitHub 2020"),
    ("tidelift", "Tidelift", "pays open-source maintainers", "added", "Sonar 2024"),
    ("sonatype", "Sonatype", "Maven Central steward, Nexus OSS (partial)", "added", ""),
    # Current COSS ventures not in U1
    ("datastax", "DataStax", "COSS (Cassandra)", "added", "IBM 2025"),
    ("scylladb", "ScyllaDB", "COSS (database)", "added", ""),
    ("yugabyte", "Yugabyte", "COSS (YugabyteDB)", "added", ""),
    ("aerospike", "Aerospike", "COSS (database, community edition)", "added", ""),
    ("starburst", "Starburst", "COSS (Trino)", "added", ""),
    ("dremio", "Dremio", "COSS (data lakehouse, Arrow)", "added", ""),
    ("imply", "Imply", "COSS (Druid)", "added", ""),
    ("alluxio", "Alluxio", "COSS (data orchestration)", "added", ""),
    ("ahana", "Ahana", "COSS (Presto)", "added", "IBM 2023"),
    ("tabular", "Tabular", "COSS (Iceberg)", "added", "Databricks 2024"),
    ("onehouse", "Onehouse", "COSS (Hudi)", "added", ""),
    ("voltron-data", "Voltron Data", "COSS (Arrow)", "added", ""),
    ("streamnative", "StreamNative", "COSS (Pulsar)", "added", ""),
    ("redpanda", "Redpanda Data", "streaming, source-available (partial)", "added", ""),
    ("materialize", "Materialize", "streaming database, BSL (partial)", "added", ""),
    ("synadia", "Synadia", "COSS (NATS)", "added", ""),
    ("camunda", "Camunda", "COSS (workflow)", "added", "Germany"),
    ("meltano", "Meltano", "COSS (ELT)", "added", ""),
    ("rudderstack", "RudderStack", "COSS (customer data)", "added", ""),
    ("snowplow", "Snowplow", "COSS (behavioural data)", "added", ""),
    ("cube", "Cube Dev", "COSS (semantic layer)", "added", ""),
    ("preset", "Preset", "COSS (Superset)", "added", ""),
    ("rasa", "Rasa", "COSS (conversational AI)", "added", ""),
    ("chainguard", "Chainguard", "open-source supply-chain security (Wolfi, Sigstore)", "added", ""),
    ("sysdig", "Sysdig", "COSS (Falco)", "added", ""),
    ("teleport", "Teleport (Gravitational)", "COSS (access)", "added", ""),
    ("tigera", "Tigera", "COSS (Calico)", "added", ""),
    ("buoyant", "Buoyant", "COSS (Linkerd)", "added", ""),
    ("solo-io", "Solo.io", "COSS (Envoy, Istio tools)", "added", ""),
    ("tetrate", "Tetrate", "COSS (Istio, Envoy)", "added", ""),
    ("akuity", "Akuity", "COSS (Argo)", "added", ""),
    ("kubecost", "Kubecost", "COSS (OpenCost)", "added", "IBM 2024"),
    ("gitpod", "Gitpod (Ona)", "COSS (dev environments)", "added", ""),
    ("element", "Element (New Vector)", "COSS (Matrix)", "added", "UK"),
    ("owncloud", "ownCloud", "COSS (file sync)", "added", "Kiteworks 2023"),
    ("bitwarden", "Bitwarden", "COSS (password manager)", "added", ""),
    ("proton", "Proton AG", "open-source clients (partial)", "added", "Switzerland"),
    ("w4-games", "W4 Games", "Godot engine company", "added", ""),
    ("crabnebula", "CrabNebula", "Tauri company", "added", ""),
    ("astro", "Astro (The Astro Technology Company)", "COSS (Astro web framework)", "added", ""),
    ("remix", "Remix Software", "COSS (Remix framework)", "added", "Shopify 2022"),
    ("mapbox", "Mapbox", "open-source mapping origins (relicensed 2020)", "added", ""),
    ("carto", "CARTO (CartoDB)", "open-source geospatial origins", "added", "Spain"),
    ("sourcegraph", "Sourcegraph", "code search, open source until 2023 (partial)", "added", ""),
    ("seldon", "Seldon", "COSS (ML deployment; BSL since 2024)", "added", "UK"),
    ("clearml", "ClearML (Allegro AI)", "COSS (MLOps)", "added", ""),
    ("iterative", "Iterative (DVC)", "COSS (DVC)", "added", ""),
    ("treeverse", "Treeverse (lakeFS)", "COSS (lakeFS)", "added", ""),
    ("pachyderm", "Pachyderm", "COSS (data versioning)", "added", "HPE 2023"),
    ("voxel51", "Voxel51", "COSS (FiftyOne)", "added", ""),
    ("cvat", "CVAT.ai", "COSS (CVAT)", "added", ""),
    # Open-weight and open-source AI ventures not in U1
    ("reflection-ai", "Reflection AI", "open-weight frontier models (stated plan)", "added", ""),
    ("prime-intellect", "Prime Intellect", "open-source decentralised training, open models", "added", ""),
    ("zyphra", "Zyphra", "open-weight models", "added", ""),
    ("arcee", "Arcee AI", "open-weight models", "added", ""),
    ("liquid-ai", "Liquid AI", "open-weight LFM models (partial)", "added", ""),
    ("pleias", "Pleias", "open models trained on open data", "added", "France"),
    ("sakana", "Sakana AI", "open releases (partial)", "added", "Japan"),
    ("ai21", "AI21 Labs", "open-weight Jamba models (partial)", "added", "Israel"),
    ("cohere", "Cohere", "research weights, non-commercial licence (partial)", "added", "Canada"),
    ("01-ai", "01.AI", "open-weight Yi models", "added", "China"),
    ("moonshot", "Moonshot AI", "open-weight Kimi models", "added", "China"),
    ("minimax", "MiniMax", "open-weight models", "added", "China"),
    ("baichuan", "Baichuan Intelligence", "open-weight models", "added", "China"),
    ("stepfun", "StepFun", "open-weight models", "added", "China"),
    ("deep-cogito", "Deep Cogito", "open-weight models", "added", ""),
    ("nomic", "Nomic AI", "open-source GPT4All, open embeddings", "added", ""),
    ("unstructured", "Unstructured", "COSS (document parsing)", "added", ""),
    ("jina", "Jina AI", "open-source embeddings and tools", "added", "Elastic 2025"),
    ("mosaicml", "MosaicML", "open-source training tools and MPT models", "added", "Databricks 2023"),
    ("octoml", "OctoML (OctoAI)", "COSS (Apache TVM)", "added", "Nvidia 2024"),
    ("neural-magic", "Neural Magic", "open-source inference (DeepSparse, vLLM)", "added", "Red Hat 2025"),
    ("determined-ai", "Determined AI", "COSS (training platform)", "added", "HPE 2021"),
    ("outerbounds", "Outerbounds", "COSS (Metaflow)", "added", ""),
    ("union-ai", "Union.ai", "COSS (Flyte)", "added", ""),
    ("zenml", "ZenML", "COSS (MLOps)", "added", "Germany"),
    ("bentoml", "BentoML", "COSS (model serving)", "added", ""),
    ("hopsworks", "Hopsworks (Logical Clocks)", "COSS (feature store)", "added", "Sweden"),
    ("argilla", "Argilla", "COSS (data labelling)", "added", "Hugging Face 2024"),
    ("lancedb", "LanceDB", "COSS (vector database)", "added", ""),
    ("marqo", "Marqo", "COSS (vector search)", "added", "Australia"),
    ("vespa", "Vespa.ai", "COSS (search engine)", "added", "Norway"),
    ("radixark", "RadixArk (SGLang)", "COSS (SGLang)", "added", ""),
    ("h-company", "H Company", "open-weight agent models (partial)", "added", "France"),
]


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def main():
    rows = list(csv.DictReader(open(OWN)))
    seen, u1 = {}, []
    for r in rows:
        k = norm(r["entity"])
        if k in seen:
            seen[k]["owners"] += ";" + r["owner"]
            continue
        d = {"key": r["owner"], "venture": r["entity"], "universe": "U1", "category": "COSS (GitHub core)",
             "source_list": "github_core", "hint": f"GitHub org(s): {r['owner']}; basis: {r['basis']}; "
             f"country {r['country'] or '?'}; parent {r['parent'] or '-'}; {r['status_hint']}; site {r['blog']}",
             "owners": r["owner"], "stars": r["stars"]}
        seen[k] = d
        u1.append(d)
    for d in u1:
        if ";" in d["owners"]:
            d["hint"] = d["hint"].replace(f"GitHub org(s): {d['key']}", f"GitHub org(s): {d['owners']}")
    u1n = {norm(d["venture"]) for d in u1}
    out = list(u1)
    for uni, lst in (("U2", U2), ("U3", U3)):
        for k, v, cat, src, hint in lst:
            out.append({"key": k, "venture": v, "universe": uni, "category": cat, "source_list": src,
                        "hint": hint, "owners": "", "stars": ""})
    keys = [d["key"] for d in out]
    dup = {k for k in keys if keys.count(k) > 1}
    assert not dup, dup
    cols = ["key", "venture", "universe", "category", "source_list", "hint", "owners", "stars"]
    os.makedirs(os.path.join(OUT, "deal_passes"), exist_ok=True)
    with open(os.path.join(OUT, "ventures_input.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    # Passes: U1 round-robin over 16 passes (mixes big and small); U2 in 5, U3 in 8, in list order.
    plan = [("U1", 16, "a"), ("U2", 5, "s"), ("U3", 8, "c")]
    summary = []
    for uni, n, prefix in plan:
        items = [d for d in out if d["universe"] == uni]
        for i in range(n):
            part = items[i::n] if uni == "U1" else items[i * len(items) // n:(i + 1) * len(items) // n]
            pid = f"{prefix}{i + 1:02d}"
            with open(os.path.join(OUT, "deal_passes", f"input_{pid}.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(part)
            summary.append((pid, len(part)))
    print(len(u1), "U1 companies (from", len(rows), "orgs);", len(U2), "U2;", len(U3), "U3")
    print(summary)


if __name__ == "__main__":
    main()

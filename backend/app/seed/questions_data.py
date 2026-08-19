"""Question bank source data — ~150 real, specific ransomware-readiness
controls across 13 domains. Generated into full Mongo question documents by
seed.py. Each control tuple is:

(control_key, title_en, title_hi, description_en, description_hi,
 impact_level, answer_type, weight, evidence_required, options, probe_check_id)

`options` is a list of (value, label_en, label_hi, score) for select-type
questions, or None for boolean/scale/text.
"""

# ---------------------------------------------------------------------------
# Domain-level micro-learning content (why it matters / risk / good practice /
# evidence hint). Shared per domain and interpolated with the control title —
# genuine, specific guidance, not filler text.
# ---------------------------------------------------------------------------

DOMAIN_MICRO_LEARNING_EN = {
    "Governance & Policy": {
        "why_it_matters": "Ransomware resilience starts with documented ownership and accountability — without a written policy, security practices depend on individual memory and drift over time.",
        "risk_addressed": "Undocumented or unenforced policy leads to inconsistent practice across teams, gaps that attackers exploit, and confusion during an actual incident.",
        "good_practice": "Maintain a current, approved, reviewed-annually policy document with a named owner and defined review cadence.",
        "evidence_hint": "Upload the policy document (PDF/DOCX) showing approval date, owner, and last review date.",
    },
    "Identity & Access Management": {
        "why_it_matters": "Most ransomware intrusions begin with compromised credentials. Strong identity controls are the single highest-leverage defense against initial access and lateral movement.",
        "risk_addressed": "Weak or reused credentials, missing MFA, and excessive standing privilege let an attacker who steals one password move freely through the environment.",
        "good_practice": "Enforce MFA everywhere feasible, apply least privilege, and monitor privileged sessions.",
        "evidence_hint": "Upload an identity provider configuration export or screenshot showing the control enabled organisation-wide.",
    },
    "Endpoint & AV/EDR": {
        "why_it_matters": "Endpoints are where ransomware payloads actually execute — detection and containment capability here determines whether an infection stays local or spreads.",
        "risk_addressed": "An endpoint without active, updated AV/EDR coverage is effectively unmonitored, giving ransomware free rein to encrypt and spread undetected.",
        "good_practice": "Deploy EDR (not just legacy signature AV) to all endpoints and servers, keep it updated, and alert on tamper attempts.",
        "evidence_hint": "Upload an EDR console coverage/deployment report or screenshot.",
    },
    "Network Segmentation": {
        "why_it_matters": "Flat networks let ransomware that lands on one workstation reach file servers, backups, and domain controllers within minutes.",
        "risk_addressed": "Without segmentation, a single compromised host can pivot to critical infrastructure and encrypt backups alongside production data.",
        "good_practice": "Segment production, backup, and management networks; restrict east-west traffic to what's explicitly required.",
        "evidence_hint": "Upload a network diagram or firewall/VLAN configuration export showing segmentation boundaries.",
    },
    "Backup & Recovery": {
        "why_it_matters": "A tested, isolated backup is the difference between a ransomware incident being a recoverable event versus an existential one.",
        "risk_addressed": "Backups reachable from production are routinely encrypted or deleted by ransomware before the ransom note appears; untested backups may not actually restore.",
        "good_practice": "Follow 3-2-1 backup principles with at least one immutable/offline copy, and test restores on a defined schedule.",
        "evidence_hint": "Upload backup job configuration, immutability settings, or the most recent restore-test report.",
    },
    "Patch & Vulnerability Management": {
        "why_it_matters": "Unpatched, internet-facing software is one of the most common initial-access vectors used in ransomware campaigns.",
        "risk_addressed": "Known, publicly disclosed vulnerabilities left unpatched give attackers a low-effort path to initial access without needing credentials at all.",
        "good_practice": "Maintain a documented patch cadence with prioritization by exploitability and exposure, especially for internet-facing systems.",
        "evidence_hint": "Upload a patch compliance report or vulnerability scan summary.",
    },
    "Logging & Monitoring": {
        "why_it_matters": "Ransomware operators typically spend days to weeks inside a network before encryption — logging and monitoring is what turns that window into a detection opportunity instead of a blind spot.",
        "risk_addressed": "Missing or short-retention logs mean discovery, lateral movement, and staging activity go unnoticed until it's too late to intervene.",
        "good_practice": "Centralize logs from endpoints, identity, and network sources with retention sufficient to investigate a multi-week dwell time.",
        "evidence_hint": "Upload a SIEM/log source inventory or retention policy configuration.",
    },
    "Email & Phishing Defense": {
        "why_it_matters": "Phishing remains one of the top initial-access vectors for ransomware affiliates delivering loaders and credential-harvesting pages.",
        "risk_addressed": "Without technical controls and trained users, a single convincing phishing email can hand an attacker their first foothold.",
        "good_practice": "Layer technical filtering (SPF/DKIM/DMARC, attachment sandboxing) with regular simulated-phishing training.",
        "evidence_hint": "Upload mail gateway configuration or the latest phishing simulation results.",
    },
    "Incident Response": {
        "why_it_matters": "How quickly and effectively an organisation responds in the first hours of a ransomware event has an outsized effect on total impact and recovery time.",
        "risk_addressed": "Without a rehearsed plan, the first hours of an incident are lost to confusion about roles, contacts, and containment steps.",
        "good_practice": "Maintain a written, ransomware-specific IR plan with a defined chain of command and rehearse it at least annually.",
        "evidence_hint": "Upload the IR plan document or the most recent tabletop exercise report.",
    },
    "Third-Party / Supply Chain": {
        "why_it_matters": "Vendors and managed service providers with privileged access are an increasingly common ransomware entry point, bypassing an organisation's own perimeter controls entirely.",
        "risk_addressed": "An unmanaged or overprivileged third-party connection can be the initial access point even when internal controls are strong.",
        "good_practice": "Inventory third-party access, apply least privilege and time-bound access, and require security attestations from critical vendors.",
        "evidence_hint": "Upload a third-party access inventory or vendor security questionnaire response.",
    },
    "Data Protection": {
        "why_it_matters": "Modern ransomware groups routinely exfiltrate sensitive data before encrypting it, turning every incident into a potential data-breach and extortion event.",
        "risk_addressed": "Unclassified or unencrypted sensitive data increases both the blast radius of exfiltration and the leverage attackers hold during extortion.",
        "good_practice": "Classify sensitive data, encrypt it at rest and in transit, and apply data-loss-prevention controls to reduce exfiltration exposure.",
        "evidence_hint": "Upload a data classification policy or DLP configuration export.",
    },
    "Awareness & Training": {
        "why_it_matters": "Every employee is a potential entry point; a workforce that recognizes and reports suspicious activity meaningfully shortens attacker dwell time.",
        "risk_addressed": "Untrained staff are more likely to click malicious links, reuse passwords, or miss the early warning signs of an active intrusion.",
        "good_practice": "Deliver role-appropriate security awareness training at least annually, reinforced with periodic simulated phishing.",
        "evidence_hint": "Upload training completion records or the awareness program curriculum.",
    },
    "Compliance Considerations": {
        "why_it_matters": "Ransomware incidents frequently trigger regulatory notification and reporting obligations — being prepared reduces both legal exposure and response chaos.",
        "risk_addressed": "Being unprepared for incident reporting and data-handling obligations compounds the operational impact of an incident with legal and reputational consequences.",
        "good_practice": "Maintain awareness of your sector's general data-handling and incident-reporting expectations as an active, owned workstream — this section is intentionally framework-neutral.",
        "evidence_hint": "Upload internal compliance checklists or evidence of legal/compliance review cadence.",
    },
}

DOMAIN_MICRO_LEARNING_HI = {
    "Governance & Policy": {
        "why_it_matters": "रैनसमवेयर के प्रति सुदृढ़ता एक दस्तावेज़ीकृत स्वामित्व और जवाबदेही से शुरू होती है — बिना लिखित नीति के, सुरक्षा प्रथाएँ व्यक्तिगत स्मृति पर निर्भर रहती हैं।",
        "risk_addressed": "अदस्तावेज़ीकृत या अलागू नीति टीमों में असंगत अभ्यास और ऐसे अंतराल पैदा करती है जिनका हमलावर लाभ उठाते हैं।",
        "good_practice": "एक नामित स्वामी और वार्षिक समीक्षा चक्र के साथ स्वीकृत, अद्यतन नीति दस्तावेज़ बनाए रखें।",
        "evidence_hint": "स्वीकृति तिथि, स्वामी और अंतिम समीक्षा तिथि दिखाने वाला नीति दस्तावेज़ अपलोड करें।",
    },
    "Identity & Access Management": {
        "why_it_matters": "अधिकांश रैनसमवेयर घुसपैठ समझौता किए गए क्रेडेंशियल से शुरू होती है। मजबूत पहचान नियंत्रण प्रारंभिक पहुँच के विरुद्ध सबसे प्रभावी सुरक्षा है।",
        "risk_addressed": "कमज़ोर क्रेडेंशियल, MFA की कमी और अत्यधिक विशेषाधिकार हमलावर को नेटवर्क में स्वतंत्र रूप से घूमने देते हैं।",
        "good_practice": "जहाँ भी संभव हो MFA लागू करें, न्यूनतम विशेषाधिकार अपनाएँ और विशेषाधिकार प्राप्त सत्रों की निगरानी करें।",
        "evidence_hint": "संगठन-व्यापी सक्षम नियंत्रण दिखाने वाला पहचान प्रदाता कॉन्फ़िगरेशन एक्सपोर्ट या स्क्रीनशॉट अपलोड करें।",
    },
    "Endpoint & AV/EDR": {
        "why_it_matters": "एंडपॉइंट वह जगह है जहाँ रैनसमवेयर पेलोड वास्तव में निष्पादित होता है — यहाँ पहचान क्षमता तय करती है कि संक्रमण स्थानीय रहेगा या फैलेगा।",
        "risk_addressed": "सक्रिय, अद्यतन AV/EDR कवरेज के बिना एंडपॉइंट प्रभावी रूप से अनमॉनिटर्ड होता है।",
        "good_practice": "सभी एंडपॉइंट और सर्वर पर EDR तैनात करें, इसे अद्यतन रखें, और छेड़छाड़ के प्रयासों पर अलर्ट करें।",
        "evidence_hint": "EDR कंसोल कवरेज/परिनियोजन रिपोर्ट या स्क्रीनशॉट अपलोड करें।",
    },
    "Network Segmentation": {
        "why_it_matters": "फ्लैट नेटवर्क रैनसमवेयर को मिनटों में फ़ाइल सर्वर, बैकअप और डोमेन नियंत्रकों तक पहुँचने देते हैं।",
        "risk_addressed": "विभाजन के बिना, एक समझौता किया गया होस्ट महत्वपूर्ण अवसंरचना तक पहुँच सकता है।",
        "good_practice": "उत्पादन, बैकअप और प्रबंधन नेटवर्क को विभाजित करें; पूर्व-पश्चिम ट्रैफ़िक को सीमित करें।",
        "evidence_hint": "विभाजन सीमाएँ दिखाने वाला नेटवर्क आरेख या फ़ायरवॉल/VLAN कॉन्फ़िगरेशन अपलोड करें।",
    },
    "Backup & Recovery": {
        "why_it_matters": "एक परीक्षित, पृथक बैकअप ही रैनसमवेयर घटना को पुनर्प्राप्त करने योग्य बनाम विनाशकारी बनाने का अंतर है।",
        "risk_addressed": "उत्पादन से पहुँच योग्य बैकअप को रैनसमवेयर द्वारा नियमित रूप से एन्क्रिप्ट या हटा दिया जाता है।",
        "good_practice": "कम से कम एक अपरिवर्तनीय/ऑफ़लाइन प्रति के साथ 3-2-1 बैकअप सिद्धांतों का पालन करें और नियमित रूप से पुनर्स्थापना का परीक्षण करें।",
        "evidence_hint": "बैकअप जॉब कॉन्फ़िगरेशन या नवीनतम पुनर्स्थापना-परीक्षण रिपोर्ट अपलोड करें।",
    },
    "Patch & Vulnerability Management": {
        "why_it_matters": "बिना पैच किए गए, इंटरनेट-सामना वाले सॉफ़्टवेयर रैनसमवेयर अभियानों में सबसे आम प्रारंभिक-पहुँच वेक्टरों में से एक हैं।",
        "risk_addressed": "ज्ञात, सार्वजनिक रूप से प्रकट कमज़ोरियाँ हमलावरों को बिना क्रेडेंशियल के प्रारंभिक पहुँच का मार्ग देती हैं।",
        "good_practice": "इंटरनेट-सामना वाले सिस्टम के लिए विशेष रूप से, शोषण क्षमता के आधार पर प्राथमिकता के साथ एक दस्तावेज़ीकृत पैच चक्र बनाए रखें।",
        "evidence_hint": "पैच अनुपालन रिपोर्ट या भेद्यता स्कैन सारांश अपलोड करें।",
    },
    "Logging & Monitoring": {
        "why_it_matters": "रैनसमवेयर ऑपरेटर आमतौर पर एन्क्रिप्शन से पहले नेटवर्क के भीतर दिनों से हफ्तों तक बिताते हैं — लॉगिंग और निगरानी उस खिड़की को पहचान के अवसर में बदल देती है।",
        "risk_addressed": "गुम या कम-अवधारण लॉग का मतलब है कि खोज और पार्श्व गति गतिविधि तब तक ध्यान में नहीं आती जब तक बहुत देर न हो जाए।",
        "good_practice": "बहु-सप्ताह की उपस्थिति की जाँच के लिए पर्याप्त प्रतिधारण के साथ एंडपॉइंट, पहचान और नेटवर्क स्रोतों से लॉग केंद्रीकृत करें।",
        "evidence_hint": "SIEM/लॉग स्रोत सूची या प्रतिधारण नीति कॉन्फ़िगरेशन अपलोड करें।",
    },
    "Email & Phishing Defense": {
        "why_it_matters": "फ़िशिंग लोडर और क्रेडेंशियल-हार्वेस्टिंग पेज देने वाले रैनसमवेयर सहयोगियों के लिए शीर्ष प्रारंभिक-पहुँच वेक्टरों में से एक बनी हुई है।",
        "risk_addressed": "तकनीकी नियंत्रण और प्रशिक्षित उपयोगकर्ताओं के बिना, एक ठोस फ़िशिंग ईमेल हमलावर को उनकी पहली पकड़ दे सकता है।",
        "good_practice": "नियमित नकली-फ़िशिंग प्रशिक्षण के साथ तकनीकी फ़िल्टरिंग (SPF/DKIM/DMARC, अटैचमेंट सैंडबॉक्सिंग) को परतबद्ध करें।",
        "evidence_hint": "मेल गेटवे कॉन्फ़िगरेशन या नवीनतम फ़िशिंग सिमुलेशन परिणाम अपलोड करें।",
    },
    "Incident Response": {
        "why_it_matters": "रैनसमवेयर घटना के पहले घंटों में संगठन कितनी तेज़ी से और प्रभावी ढंग से प्रतिक्रिया करता है, इसका कुल प्रभाव पर बड़ा प्रभाव पड़ता है।",
        "risk_addressed": "एक अभ्यस्त योजना के बिना, घटना के पहले घंटे भूमिकाओं, संपर्कों और नियंत्रण चरणों के बारे में भ्रम में खो जाते हैं।",
        "good_practice": "स्पष्ट कमांड श्रृंखला के साथ एक लिखित, रैनसमवेयर-विशिष्ट IR योजना बनाए रखें और इसे वार्षिक रूप से अभ्यास करें।",
        "evidence_hint": "IR योजना दस्तावेज़ या नवीनतम टेबलटॉप अभ्यास रिपोर्ट अपलोड करें।",
    },
    "Third-Party / Supply Chain": {
        "why_it_matters": "विशेषाधिकार प्राप्त पहुँच वाले विक्रेता और प्रबंधित सेवा प्रदाता तेजी से आम रैनसमवेयर प्रवेश बिंदु बनते जा रहे हैं।",
        "risk_addressed": "एक अप्रबंधित तृतीय-पक्ष कनेक्शन प्रारंभिक पहुँच बिंदु हो सकता है, भले ही आंतरिक नियंत्रण मजबूत हों।",
        "good_practice": "तृतीय-पक्ष पहुँच की सूची बनाएं, न्यूनतम विशेषाधिकार और समय-सीमित पहुँच लागू करें।",
        "evidence_hint": "तृतीय-पक्ष पहुँच सूची या विक्रेता सुरक्षा प्रश्नावली प्रतिक्रिया अपलोड करें।",
    },
    "Data Protection": {
        "why_it_matters": "आधुनिक रैनसमवेयर समूह नियमित रूप से एन्क्रिप्ट करने से पहले संवेदनशील डेटा को बाहर निकालते हैं।",
        "risk_addressed": "अवर्गीकृत या अनएन्क्रिप्टेड संवेदनशील डेटा एक्सफ़िल्ट्रेशन के प्रभाव क्षेत्र को बढ़ाता है।",
        "good_practice": "संवेदनशील डेटा को वर्गीकृत करें, इसे विश्राम और पारगमन में एन्क्रिप्ट करें, और डेटा-हानि-रोकथाम नियंत्रण लागू करें।",
        "evidence_hint": "डेटा वर्गीकरण नीति या DLP कॉन्फ़िगरेशन एक्सपोर्ट अपलोड करें।",
    },
    "Awareness & Training": {
        "why_it_matters": "प्रत्येक कर्मचारी एक संभावित प्रवेश बिंदु है; एक जागरूक कार्यबल हमलावर की उपस्थिति अवधि को सार्थक रूप से छोटा करता है।",
        "risk_addressed": "अप्रशिक्षित कर्मचारियों द्वारा दुर्भावनापूर्ण लिंक पर क्लिक करने की संभावना अधिक होती है।",
        "good_practice": "वार्षिक रूप से कम से कम भूमिका-उपयुक्त सुरक्षा जागरूकता प्रशिक्षण प्रदान करें।",
        "evidence_hint": "प्रशिक्षण पूर्णता रिकॉर्ड या जागरूकता कार्यक्रम पाठ्यक्रम अपलोड करें।",
    },
    "Compliance Considerations": {
        "why_it_matters": "रैनसमवेयर घटनाएँ अक्सर नियामक अधिसूचना और रिपोर्टिंग दायित्वों को ट्रिगर करती हैं — तैयार रहना कानूनी जोखिम को कम करता है।",
        "risk_addressed": "घटना रिपोर्टिंग और डेटा-प्रबंधन दायित्वों के लिए तैयार न होना घटना के परिचालन प्रभाव को बढ़ाता है।",
        "good_practice": "अपने क्षेत्र की सामान्य डेटा-प्रबंधन और घटना-रिपोर्टिंग अपेक्षाओं के प्रति जागरूकता बनाए रखें — यह अनुभाग जानबूझकर ढांचा-तटस्थ है।",
        "evidence_hint": "आंतरिक अनुपालन चेकलिस्ट या कानूनी/अनुपालन समीक्षा साक्ष्य अपलोड करें।",
    },
}

SCALE_OPTIONS = None

BOOL_OPTIONS = None

MATURITY_SELECT = [
    ("not_started", "Not started", "शुरू नहीं हुआ", 0.0),
    ("planned", "Planned but not implemented", "योजनाबद्ध लेकिन लागू नहीं", 1.5),
    ("partial", "Partially implemented", "आंशिक रूप से लागू", 3.0),
    ("implemented", "Implemented", "लागू", 4.0),
    ("implemented_reviewed", "Implemented and regularly reviewed", "लागू और नियमित रूप से समीक्षित", 5.0),
]

FREQUENCY_SELECT = [
    ("never", "Never", "कभी नहीं", 0.0),
    ("annually", "Annually", "वार्षिक", 2.0),
    ("quarterly", "Quarterly", "त्रैमासिक", 3.5),
    ("monthly", "Monthly", "मासिक", 4.5),
    ("continuous", "Continuous / real-time", "निरंतर / वास्तविक-समय", 5.0),
]

# Each tuple: (key, title_en, title_hi, desc_en, desc_hi, impact, answer_type, weight, evidence_required, options, probe_check_id, sector, roles)
# sector: "generic" or a specific sector value; roles: list of role names

ALL = "generic"
R_ALL = ["executive", "it_administrator", "generalist"]
R_TECH = ["it_administrator", "generalist"]
R_EXEC = ["executive", "it_administrator"]

DOMAIN_CONTROLS: dict[str, list[tuple]] = {
    "Governance & Policy": [
        ("GOV-001", "A documented ransomware/cyber incident response policy exists", "एक दस्तावेज़ीकृत रैनसमवेयर/साइबर घटना प्रतिक्रिया नीति मौजूद है", "The organisation has an approved written policy specifically addressing ransomware and cyber incidents.", "संगठन के पास विशेष रूप से रैनसमवेयर और साइबर घटनाओं को संबोधित करने वाली एक स्वीकृत लिखित नीति है।", "high", "boolean", 2.5, True, None, None, ALL, R_EXEC),
        ("GOV-002", "A named executive owns cyber risk accountability", "एक नामित कार्यकारी साइबर जोखिम जवाबदेही का स्वामी है", "A specific senior role (CISO, IT Director, or equivalent) is formally accountable for cyber risk.", "एक विशिष्ट वरिष्ठ भूमिका औपचारिक रूप से साइबर जोखिम के लिए जवाबदेह है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("GOV-003", "Security policies are reviewed on a defined schedule", "सुरक्षा नीतियों की एक निश्चित अनुसूची पर समीक्षा की जाती है", "Policies are reviewed and re-approved at least annually.", "नीतियों की कम से कम वार्षिक रूप से समीक्षा और पुनः स्वीकृति की जाती है।", "medium", "single_select", 1.5, False, FREQUENCY_SELECT, None, ALL, R_EXEC),
        ("GOV-004", "A cyber risk register is maintained", "एक साइबर जोखिम रजिस्टर बनाए रखा जाता है", "Identified risks are tracked with owners, likelihood, and treatment plans.", "पहचाने गए जोखिमों को स्वामियों, संभावना और उपचार योजनाओं के साथ ट्रैक किया जाता है।", "medium", "boolean", 1.5, True, None, None, ALL, R_EXEC),
        ("GOV-005", "Budget is explicitly allocated for security controls", "सुरक्षा नियंत्रणों के लिए स्पष्ट रूप से बजट आवंटित किया गया है", "A defined annual budget line exists for security tooling, staffing, or services.", "सुरक्षा टूलिंग, स्टाफिंग या सेवाओं के लिए एक निश्चित वार्षिक बजट लाइन मौजूद है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("GOV-006", "Security policy exceptions require documented approval", "सुरक्षा नीति अपवादों के लिए दस्तावेज़ीकृत अनुमोदन आवश्यक है", "Deviations from policy go through a formal risk-acceptance process rather than informal exceptions.", "नीति से विचलन अनौपचारिक अपवादों के बजाय एक औपचारिक जोखिम-स्वीकृति प्रक्रिया से गुजरते हैं।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("GOV-007", "Acceptable use policy is signed by all staff", "स्वीकार्य उपयोग नीति सभी कर्मचारियों द्वारा हस्ताक्षरित है", "All employees and contractors acknowledge an acceptable use / security policy on onboarding.", "सभी कर्मचारी और ठेकेदार शामिल होने पर एक स्वीकार्य उपयोग/सुरक्षा नीति स्वीकार करते हैं।", "low", "boolean", 1.0, True, None, None, ALL, R_ALL),
        ("GOV-008", "A cyber insurance policy covering ransomware is in place", "रैनसमवेयर को कवर करने वाली साइबर बीमा पॉलिसी मौजूद है", "The organisation holds cyber insurance that explicitly covers ransomware-related incidents.", "संगठन के पास साइबर बीमा है जो विशेष रूप से रैनसमवेयर-संबंधित घटनाओं को कवर करता है।", "low", "boolean", 1.0, True, None, None, ALL, R_EXEC),
        ("GOV-009", "Security metrics are reported to leadership regularly", "सुरक्षा मेट्रिक्स नियमित रूप से नेतृत्व को रिपोर्ट किए जाते हैं", "Leadership receives a regular (at least quarterly) report on security posture and incidents.", "नेतृत्व को सुरक्षा स्थिति और घटनाओं पर नियमित रिपोर्ट (कम से कम त्रैमासिक) मिलती है।", "low", "single_select", 1.0, False, FREQUENCY_SELECT, None, ALL, R_EXEC),
        ("GOV-010", "IT asset inventory is current and complete", "आईटी संपत्ति सूची वर्तमान और पूर्ण है", "A maintained inventory of hardware, software, and cloud assets exists and is kept up to date.", "हार्डवेयर, सॉफ़्टवेयर और क्लाउड संपत्तियों की एक अद्यतन सूची मौजूद है।", "medium", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("GOV-011", "Data ownership is assigned for critical systems", "महत्वपूर्ण प्रणालियों के लिए डेटा स्वामित्व सौंपा गया है", "Each critical system/dataset has a named business owner responsible for its protection requirements.", "प्रत्येक महत्वपूर्ण प्रणाली/डेटासेट का एक नामित व्यावसायिक स्वामी है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("GOV-012", "Security is a standing agenda item at leadership meetings", "नेतृत्व बैठकों में सुरक्षा एक स्थायी एजेंडा आइटम है", "Cyber risk is discussed at a defined cadence in leadership or board meetings.", "नेतृत्व या बोर्ड बैठकों में साइबर जोखिम पर एक निश्चित समय-सीमा पर चर्चा की जाती है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
    ],
    "Identity & Access Management": [
        ("IAM-MFA-ENFORCED", "Multi-factor authentication is enforced for all remote access", "सभी दूरस्थ पहुँच के लिए बहु-कारक प्रमाणीकरण लागू है", "MFA is required for VPN, email, and any externally reachable administrative interface.", "VPN, ईमेल और किसी भी बाहरी रूप से पहुँच योग्य प्रशासनिक इंटरफ़ेस के लिए MFA आवश्यक है।", "high", "boolean", 3.0, True, None, None, ALL, R_TECH),
        ("IAM-PASSWORD-POLICY", "A minimum password strength policy is technically enforced", "एक न्यूनतम पासवर्ड शक्ति नीति तकनीकी रूप से लागू है", "Password length/complexity requirements are enforced by the identity system, not just documented.", "पासवर्ड लंबाई/जटिलता आवश्यकताएँ पहचान प्रणाली द्वारा लागू की जाती हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("IAM-PASSWORD-REUSE-CONTROL", "Passwords are checked against known-breached credential lists", "पासवर्ड ज्ञात-उल्लंघन क्रेडेंशियल सूचियों के विरुद्ध जाँचे जाते हैं", "The identity provider blocks passwords that appear in known breach compilations.", "पहचान प्रदाता उन पासवर्डों को अवरुद्ध करता है जो ज्ञात उल्लंघन संकलनों में दिखाई देते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("IAM-LEAST-PRIVILEGE", "Least-privilege access model is applied to user accounts", "उपयोगकर्ता खातों पर न्यूनतम-विशेषाधिकार पहुँच मॉडल लागू है", "Standard users do not hold local admin or domain admin rights by default.", "मानक उपयोगकर्ताओं के पास डिफ़ॉल्ट रूप से स्थानीय व्यवस्थापक या डोमेन व्यवस्थापक अधिकार नहीं होते हैं।", "high", "boolean", 2.5, True, None, None, ALL, R_TECH),
        ("IAM-PRIVILEGED-SESSION-MONITORING", "Privileged account sessions are monitored or recorded", "विशेषाधिकार प्राप्त खाता सत्रों की निगरानी या रिकॉर्ड की जाती है", "Admin/privileged sessions are logged or monitored via a PAM solution or equivalent.", "व्यवस्थापक/विशेषाधिकार प्राप्त सत्र PAM समाधान या समकक्ष के माध्यम से लॉग किए जाते हैं।", "medium", "boolean", 2.0, True, None, None, ALL, R_TECH),
        # Impact/weight raised from medium/1.5 to high/2.5: CIS CDM v2.0 ranks the
        # underlying Safeguards (6.1 Establish an Access Granting Process, 6.2
        # Establish an Access Revoking Process) #2 and #3 of all 153 CIS
        # Safeguards by ATT&CK (sub-)technique coverage (217 each, IG1) — tied
        # with GOV controls for the single highest-value pair in the entire CDM
        # ranking, well above this control's previous weight. See CIS_CDM_REFERENCE.
        ("IAM-JOINER-LEAVER", "Account provisioning/de-provisioning is timely and auditable", "खाता प्रावधान/डी-प्रावधान समय पर और लेखा परीक्षा योग्य है", "Accounts are disabled promptly (within 24 hours) when staff leave.", "जब कर्मचारी छोड़ते हैं तो खातों को शीघ्रता से (24 घंटों के भीतर) अक्षम कर दिया जाता है।", "high", "boolean", 2.5, False, None, None, ALL, R_TECH),
        ("IAM-SERVICE-ACCOUNTS", "Service accounts follow least-privilege and are inventoried", "सेवा खाते न्यूनतम-विशेषाधिकार का पालन करते हैं और सूचीबद्ध हैं", "Service/application accounts are documented, scoped tightly, and not shared with human logins.", "सेवा/एप्लिकेशन खाते दस्तावेज़ीकृत हैं, कसकर स्कोप किए गए हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("PROBE-LOCAL-ADMINS", "The number of domain/global administrator accounts is minimized", "डोमेन/वैश्विक व्यवस्थापक खातों की संख्या न्यूनतम है", "Fewer than 5 accounts hold domain admin or equivalent global privilege.", "5 से कम खातों में डोमेन व्यवस्थापक या समकक्ष वैश्विक विशेषाधिकार है।", "high", "boolean", 2.5, True, None, "CHECK_009", ALL, R_TECH),
        ("IAM-MFA-ADMIN", "MFA is enforced specifically for all administrative accounts", "सभी प्रशासनिक खातों के लिए विशेष रूप से MFA लागू है", "Every account with elevated privilege requires MFA, with no exceptions.", "उन्नत विशेषाधिकार वाला प्रत्येक खाता MFA की आवश्यकता रखता है।", "high", "boolean", 2.5, True, None, None, ALL, R_TECH),
        ("IAM-PASSWORD-VAULT", "A password/secrets manager is used for shared and privileged credentials", "साझा और विशेषाधिकार प्राप्त क्रेडेंशियल के लिए पासवर्ड/गुप्त प्रबंधक का उपयोग किया जाता है", "Shared or privileged credentials are stored in a vault rather than spreadsheets or shared documents.", "साझा या विशेषाधिकार प्राप्त क्रेडेंशियल स्प्रेडशीट के बजाय एक वॉल्ट में संग्रहीत हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("IAM-CONDITIONAL-ACCESS", "Conditional/risk-based access policies are configured", "सशर्त/जोखिम-आधारित पहुँच नीतियाँ कॉन्फ़िगर की गई हैं", "Sign-ins from unusual locations or impossible-travel patterns trigger additional verification or blocking.", "असामान्य स्थानों से साइन-इन अतिरिक्त सत्यापन को ट्रिगर करते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("IAM-SSO", "Single sign-on is used for core business applications", "मुख्य व्यावसायिक अनुप्रयोगों के लिए एकल साइन-ऑन का उपयोग किया जाता है", "Centralized SSO reduces password sprawl and enables faster access revocation.", "केंद्रीकृत SSO पासवर्ड फैलाव को कम करता है और तेज़ी से पहुँच निरस्तीकरण को सक्षम करता है।", "low", "boolean", 1.0, False, None, None, ALL, R_TECH),
        ("IAM-ACCESS-REVIEW", "Periodic access reviews / recertification are performed", "आवधिक पहुँच समीक्षा/पुनः प्रमाणन किया जाता है", "Access rights are formally reviewed by data/system owners at least annually.", "पहुँच अधिकारों की डेटा/सिस्टम स्वामियों द्वारा कम से कम वार्षिक रूप से औपचारिक समीक्षा की जाती है।", "medium", "single_select", 1.5, True, FREQUENCY_SELECT, None, ALL, R_TECH),
        ("IAM-GUEST-ACCOUNTS", "Default/guest/built-in accounts are disabled or renamed", "डिफ़ॉल्ट/अतिथि/अंतर्निहित खाते अक्षम या नाम बदले गए हैं", "Default administrator and guest accounts are disabled, renamed, or have randomized strong passwords.", "डिफ़ॉल्ट व्यवस्थापक और अतिथि खाते अक्षम या नाम बदले गए हैं।", "low", "boolean", 1.0, False, None, None, ALL, R_TECH),
    ],
    "Endpoint & AV/EDR": [
        ("PROBE-AVEDR-SERVICE", "Endpoint Detection & Response (EDR) is deployed on all endpoints", "सभी एंडपॉइंट पर एंडपॉइंट डिटेक्शन एंड रिस्पॉन्स (EDR) तैनात है", "An EDR (not just legacy AV) agent is installed and actively running on workstations and servers.", "एक EDR एजेंट वर्कस्टेशन और सर्वर पर स्थापित और सक्रिय रूप से चल रहा है।", "high", "boolean", 3.0, True, None, "CHECK_005", ALL, R_TECH),
        ("END-002", "EDR/AV signatures and engines update automatically", "EDR/AV हस्ताक्षर और इंजन स्वचालित रूप से अद्यतन होते हैं", "Detection content updates without manual intervention on a daily or better cadence.", "पहचान सामग्री दैनिक या बेहतर गति पर बिना मैन्युअल हस्तक्षेप के अद्यतन होती है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("END-003", "Tamper protection is enabled on endpoint security agents", "एंडपॉइंट सुरक्षा एजेंटों पर छेड़छाड़ सुरक्षा सक्षम है", "Local users, including admins, cannot disable the EDR/AV agent without central authorization.", "स्थानीय उपयोगकर्ता, व्यवस्थापकों सहित, केंद्रीय प्राधिकरण के बिना EDR/AV एजेंट को अक्षम नहीं कर सकते।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("END-004", "Application allowlisting or execution control is used on critical servers", "महत्वपूर्ण सर्वर पर एप्लिकेशन अनुमति-सूची या निष्पादन नियंत्रण का उपयोग किया जाता है", "Only approved applications/scripts can execute on file servers, domain controllers, or backup servers.", "केवल अनुमोदित एप्लिकेशन/स्क्रिप्ट फ़ाइल सर्वर, डोमेन नियंत्रकों पर निष्पादित हो सकते हैं।", "high", "boolean", 2.5, True, None, None, ALL, R_TECH),
        ("END-005", "Removable media (USB) usage is controlled or restricted", "हटाने योग्य मीडिया (USB) उपयोग नियंत्रित या प्रतिबंधित है", "USB storage devices are blocked by policy or restricted to approved, encrypted devices.", "USB स्टोरेज डिवाइस नीति द्वारा अवरुद्ध या अनुमोदित, एन्क्रिप्टेड डिवाइस तक सीमित हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("PROBE-DISK-ENCRYPTION", "Full-disk encryption is enabled on laptops and mobile endpoints", "लैपटॉप और मोबाइल एंडपॉइंट पर पूर्ण-डिस्क एन्क्रिप्शन सक्षम है", "BitLocker, FileVault, or LUKS is enabled on all portable devices holding organisational data.", "संगठनात्मक डेटा रखने वाले सभी पोर्टेबल उपकरणों पर BitLocker, FileVault, या LUKS सक्षम है।", "medium", "boolean", 2.0, True, None, "CHECK_012", ALL, R_TECH),
        ("PROBE-SCREEN-LOCK", "Idle screen-lock policy is enforced on all endpoints", "सभी एंडपॉइंट पर निष्क्रिय स्क्रीन-लॉक नीति लागू है", "Workstations lock automatically after a defined idle period (15 minutes or less).", "एक निश्चित निष्क्रिय अवधि (15 मिनट या उससे कम) के बाद वर्कस्टेशन स्वचालित रूप से लॉक हो जाते हैं।", "low", "boolean", 1.0, False, None, "CHECK_010", ALL, R_TECH),
        ("END-008", "Endpoints are managed via centralized configuration management", "एंडपॉइंट को केंद्रीकृत कॉन्फ़िगरेशन प्रबंधन के माध्यम से प्रबंधित किया जाता है", "A tool (GPO, Intune, Ansible, etc.) enforces consistent security baselines across endpoints.", "एक उपकरण एंडपॉइंट पर सुसंगत सुरक्षा आधाररेखा लागू करता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("END-009", "Local firewall is enabled on all workstations and servers", "सभी वर्कस्टेशन और सर्वर पर स्थानीय फ़ायरवॉल सक्षम है", "Host-based firewall blocks unsolicited inbound connections by default.", "होस्ट-आधारित फ़ायरवॉल डिफ़ॉल्ट रूप से अवांछित इनबाउंड कनेक्शन को अवरुद्ध करता है।", "medium", "boolean", 1.5, False, None, "CHECK_007", ALL, R_TECH),
        ("END-010", "Endpoint isolation/quarantine capability is available during an incident", "घटना के दौरान एंडपॉइंट अलगाव/संगरोध क्षमता उपलब्ध है", "The EDR platform or equivalent can network-isolate a compromised host remotely within minutes.", "EDR प्लेटफ़ॉर्म मिनटों के भीतर दूरस्थ रूप से एक समझौता किए गए होस्ट को नेटवर्क-पृथक कर सकता है।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("END-011", "Macro execution from untrusted sources is disabled by default", "अविश्वसनीय स्रोतों से मैक्रो निष्पादन डिफ़ॉल्ट रूप से अक्षम है", "Office macro execution from internet-downloaded files is blocked by policy.", "इंटरनेट से डाउनलोड की गई फ़ाइलों से ऑफिस मैक्रो निष्पादन नीति द्वारा अवरुद्ध है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("END-012", "Legacy/unsupported operating systems are inventoried and isolated", "पुराने/असमर्थित ऑपरेटिंग सिस्टम सूचीबद्ध और पृथक हैं", "End-of-life OS instances are identified and network-isolated if they cannot be upgraded.", "जीवन-काल के अंत में OS इंस्टेंस की पहचान की जाती है और यदि उन्हें अपग्रेड नहीं किया जा सकता है तो नेटवर्क-पृथक किया जाता है।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
    ],
    "Network Segmentation": [
        ("NET-SEGMENTATION", "Production, backup, and management networks are segmented", "उत्पादन, बैकअप और प्रबंधन नेटवर्क विभाजित हैं", "Distinct VLANs/subnets with enforced firewall rules separate these network zones.", "लागू फ़ायरवॉल नियमों के साथ अलग-अलग VLAN/सबनेट इन नेटवर्क क्षेत्रों को अलग करते हैं।", "high", "boolean", 3.0, True, None, None, ALL, R_TECH),
        ("PROBE-SMBV1", "The obsolete SMBv1 protocol is disabled organisation-wide", "अप्रचलित SMBv1 प्रोटोकॉल संगठन-व्यापी अक्षम है", "SMBv1, exploited by WannaCry and NotPetya, is disabled on all systems.", "SMBv1, जिसका उपयोग WannaCry और NotPetya द्वारा किया गया, सभी प्रणालियों पर अक्षम है।", "high", "boolean", 2.5, False, None, "CHECK_001", ALL, R_TECH),
        ("PROBE-RDP-EXPOSURE", "RDP is not directly exposed to the internet", "RDP सीधे इंटरनेट पर उजागर नहीं है", "Remote Desktop Protocol is only reachable via VPN with MFA, never directly from the internet.", "रिमोट डेस्कटॉप प्रोटोकॉल केवल MFA के साथ VPN के माध्यम से पहुँच योग्य है।", "high", "boolean", 3.0, True, None, "CHECK_002", ALL, R_TECH),
        ("NET-004", "Internal traffic between workstations is restricted (east-west)", "वर्कस्टेशन के बीच आंतरिक ट्रैफ़िक प्रतिबंधित है (पूर्व-पश्चिम)", "Workstation-to-workstation SMB/RPC traffic is restricted to prevent worm-like spread.", "वर्कस्टेशन-से-वर्कस्टेशन SMB/RPC ट्रैफ़िक कृमि-जैसे प्रसार को रोकने के लिए प्रतिबंधित है।", "high", "boolean", 2.5, False, None, None, ALL, R_TECH),
        ("PROBE-FIREWALL", "A managed perimeter firewall with logging is in place", "लॉगिंग के साथ एक प्रबंधित परिधि फ़ायरवॉल मौजूद है", "Perimeter firewall rules are documented, reviewed, and log denied/allowed traffic.", "परिधि फ़ायरवॉल नियम दस्तावेज़ीकृत, समीक्षित हैं, और अस्वीकृत/अनुमत ट्रैफ़िक लॉग करते हैं।", "high", "boolean", 2.0, True, None, "CHECK_007", ALL, R_TECH),
        ("NET-DLP", "Egress traffic is monitored for data-loss-prevention purposes", "डेटा-हानि-रोकथाम उद्देश्यों के लिए बाहर जाने वाले ट्रैफ़िक की निगरानी की जाती है", "Outbound traffic is inspected for large or unusual data transfers indicative of exfiltration.", "एक्सफ़िल्ट्रेशन के संकेत देने वाले बड़े या असामान्य डेटा स्थानांतरण के लिए आउटबाउंड ट्रैफ़िक का निरीक्षण किया जाता है।", "medium", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("NET-EGRESS-FILTERING", "Outbound firewall rules restrict traffic to known-good destinations", "आउटबाउंड फ़ायरवॉल नियम ज्ञात-अच्छे गंतव्यों तक ट्रैफ़िक को प्रतिबंधित करते हैं", "Default-deny egress filtering limits command-and-control and exfiltration channels.", "डिफ़ॉल्ट-अस्वीकार निकास फ़िल्टरिंग कमांड-एंड-कंट्रोल और एक्सफ़िल्ट्रेशन चैनलों को सीमित करती है।", "medium", "boolean", 2.0, False, None, None, ALL, R_TECH),
        ("PROBE-REMOTE-REGISTRY", "Unnecessary remote administration services are disabled", "अनावश्यक दूरस्थ प्रशासन सेवाएँ अक्षम हैं", "Services like Remote Registry are disabled on endpoints where not explicitly required.", "रिमोट रजिस्ट्री जैसी सेवाएँ एंडपॉइंट पर अक्षम हैं जहाँ स्पष्ट रूप से आवश्यक नहीं हैं।", "medium", "boolean", 1.5, False, None, "CHECK_011", ALL, R_TECH),
        ("NET-009", "Wireless networks for guests are isolated from the corporate network", "अतिथियों के लिए वायरलेस नेटवर्क कॉर्पोरेट नेटवर्क से पृथक हैं", "Guest Wi-Fi cannot reach internal systems or corporate VLANs.", "अतिथि वाई-फाई आंतरिक प्रणालियों या कॉर्पोरेट VLAN तक नहीं पहुँच सकता।", "low", "boolean", 1.0, False, None, None, ALL, R_TECH),
        ("NET-010", "OT/IoT/medical devices are segmented from the general IT network", "OT/IoT/चिकित्सा उपकरण सामान्य आईटी नेटवर्क से पृथक हैं", "Operational technology, IoT, or specialty devices sit on isolated network segments.", "परिचालन प्रौद्योगिकी, IoT, या विशेष उपकरण पृथक नेटवर्क खंडों पर हैं।", "medium", "boolean", 2.0, False, None, None, "healthcare", R_TECH),
        ("NET-011", "Network access control (NAC) restricts unknown device connections", "नेटवर्क एक्सेस कंट्रोल (NAC) अज्ञात डिवाइस कनेक्शन को प्रतिबंधित करता है", "Unregistered devices connecting to wired/wireless ports are quarantined or blocked.", "वायर्ड/वायरलेस पोर्ट से जुड़ने वाले अपंजीकृत उपकरणों को संगरोधित या अवरुद्ध किया जाता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("NET-012", "VPN access requires device compliance checks", "VPN पहुँच के लिए डिवाइस अनुपालन जाँच आवश्यक है", "Remote-access VPN verifies endpoint security posture (patch level, AV status) before granting access.", "रिमोट-एक्सेस VPN पहुँच देने से पहले एंडपॉइंट सुरक्षा स्थिति सत्यापित करता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
    ],
    "Backup & Recovery": [
        ("BKP-001", "Backups follow the 3-2-1 principle (3 copies, 2 media, 1 offsite)", "बैकअप 3-2-1 सिद्धांत का पालन करते हैं (3 प्रतियाँ, 2 मीडिया, 1 ऑफ़साइट)", "At least three copies of critical data exist across two media types with one offsite/offline.", "महत्वपूर्ण डेटा की कम से कम तीन प्रतियाँ दो मीडिया प्रकारों में मौजूद हैं जिनमें से एक ऑफ़साइट/ऑफ़लाइन है।", "high", "boolean", 3.0, True, None, None, ALL, R_TECH),
        ("BKP-IMMUTABLE-STORAGE", "At least one backup copy is immutable or air-gapped", "कम से कम एक बैकअप प्रति अपरिवर्तनीय या एयर-गैप्ड है", "A backup copy cannot be modified or deleted, even by an attacker with domain admin credentials.", "एक बैकअप प्रति को संशोधित या हटाया नहीं जा सकता, भले ही हमलावर के पास डोमेन व्यवस्थापक क्रेडेंशियल हों।", "high", "boolean", 3.0, True, None, None, ALL, R_TECH),
        ("PROBE-BACKUP-WRITABLE", "Backup storage is not writable from general production accounts", "बैकअप स्टोरेज सामान्य उत्पादन खातों से लिखने योग्य नहीं है", "Standard domain/service accounts used in production cannot write to or delete backup repositories.", "उत्पादन में उपयोग किए जाने वाले मानक डोमेन/सेवा खाते बैकअप रिपॉज़िटरी में लिख या हटा नहीं सकते।", "high", "boolean", 2.5, True, None, "CHECK_003", ALL, R_TECH),
        ("BKP-004", "Backup restore tests are performed on a defined schedule", "बैकअप पुनर्स्थापना परीक्षण एक निश्चित अनुसूची पर किए जाते हैं", "Full restore tests (not just backup job success checks) are performed at least quarterly.", "पूर्ण पुनर्स्थापना परीक्षण कम से कम त्रैमासिक रूप से किए जाते हैं।", "high", "single_select", 3.0, True, FREQUENCY_SELECT, None, ALL, R_TECH),
        ("PROBE-VSS-SERVICE", "Volume Shadow Copy / snapshot capability is enabled on critical servers", "महत्वपूर्ण सर्वर पर वॉल्यूम शैडो कॉपी/स्नैपशॉट क्षमता सक्षम है", "VSS or equivalent snapshotting is enabled to support rapid point-in-time recovery.", "तीव्र बिंदु-समय पुनर्प्राप्ति का समर्थन करने के लिए VSS या समकक्ष स्नैपशॉटिंग सक्षम है।", "medium", "boolean", 1.5, False, None, "CHECK_004", ALL, R_TECH),
        ("BKP-006", "Backup frequency meets the organisation's defined recovery point objective", "बैकअप आवृत्ति संगठन के निर्धारित पुनर्प्राप्ति बिंदु उद्देश्य को पूरा करती है", "Backup schedule aligns with an explicitly defined RPO for critical systems.", "बैकअप अनुसूची महत्वपूर्ण प्रणालियों के लिए स्पष्ट रूप से परिभाषित RPO के साथ संरेखित है।", "medium", "single_select", 2.0, False, FREQUENCY_SELECT, None, ALL, R_TECH),
        ("BKP-007", "Backup systems have their own separate credentials/identity", "बैकअप प्रणालियों की अपनी अलग क्रेडेंशियल/पहचान है", "Backup infrastructure does not authenticate using the same domain credentials as production.", "बैकअप अवसंरचना उत्पादन के समान डोमेन क्रेडेंशियल का उपयोग करके प्रमाणित नहीं होती है।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("BKP-008", "Backup job failures trigger an alert reviewed within 24 hours", "बैकअप जॉब विफलताएँ 24 घंटों के भीतर समीक्षित एक अलर्ट को ट्रिगर करती हैं", "Failed backup jobs generate an alert that is actively monitored, not just logged silently.", "विफल बैकअप जॉब एक अलर्ट उत्पन्न करते हैं जिसकी सक्रिय रूप से निगरानी की जाती है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("BKP-009", "A documented recovery time objective (RTO) exists for critical systems", "महत्वपूर्ण प्रणालियों के लिए एक दस्तावेज़ीकृत पुनर्प्राप्ति समय उद्देश्य (RTO) मौजूद है", "Business-approved RTOs guide backup and recovery infrastructure decisions.", "व्यवसाय-अनुमोदित RTO बैकअप और पुनर्प्राप्ति अवसंरचना निर्णयों का मार्गदर्शन करते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("BKP-010", "Backup encryption keys are stored separately from the backup infrastructure", "बैकअप एन्क्रिप्शन कुंजियाँ बैकअप अवसंरचना से अलग संग्रहीत हैं", "Encryption keys for backup data are not stored on the same system as the backups themselves.", "बैकअप डेटा के लिए एन्क्रिप्शन कुंजियाँ स्वयं बैकअप के समान प्रणाली पर संग्रहीत नहीं हैं।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
        ("BKP-011", "Cloud SaaS data (email, files) is included in the backup strategy", "क्लाउड SaaS डेटा (ईमेल, फ़ाइलें) बैकअप रणनीति में शामिल है", "SaaS platforms (e.g., email, cloud file storage) are backed up independently of the vendor's native retention.", "SaaS प्लेटफ़ॉर्म को विक्रेता की मूल प्रतिधारण से स्वतंत्र रूप से बैकअप किया जाता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("BKP-012", "A designated owner is responsible for restore testing", "पुनर्स्थापना परीक्षण के लिए एक नामित स्वामी जिम्मेदार है", "A specific named individual or role owns the restore-testing process end to end.", "एक विशिष्ट नामित व्यक्ति या भूमिका पुनर्स्थापना-परीक्षण प्रक्रिया का स्वामी है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
    ],
    "Patch & Vulnerability Management": [
        ("PROBE-PATCH-RECENCY", "Critical security patches are applied within a defined SLA", "महत्वपूर्ण सुरक्षा पैच एक निश्चित SLA के भीतर लागू किए जाते हैं", "Critical/high severity patches are applied within 14 days of release across the fleet.", "महत्वपूर्ण/उच्च गंभीरता पैच रिलीज़ के 14 दिनों के भीतर लागू किए जाते हैं।", "high", "boolean", 2.5, True, None, "CHECK_008", ALL, R_TECH),
        ("PATCH-002", "Internet-facing systems are patched on an accelerated schedule", "इंटरनेट-सामना करने वाली प्रणालियों को त्वरित अनुसूची पर पैच किया जाता है", "Externally exposed systems receive critical patches faster than internal-only systems.", "बाहरी रूप से उजागर प्रणालियों को आंतरिक-केवल प्रणालियों की तुलना में तेज़ी से महत्वपूर्ण पैच प्राप्त होते हैं।", "high", "boolean", 2.5, False, None, None, ALL, R_TECH),
        ("PATCH-003", "Vulnerability scanning is performed on a regular schedule", "भेद्यता स्कैनिंग नियमित अनुसूची पर की जाती है", "Authenticated vulnerability scans of internal and external assets run at least monthly.", "आंतरिक और बाहरी संपत्तियों के प्रमाणित भेद्यता स्कैन कम से कम मासिक रूप से चलते हैं।", "high", "single_select", 2.0, True, FREQUENCY_SELECT, None, ALL, R_TECH),
        ("PATCH-004", "End-of-life software is identified and has a remediation plan", "जीवन-काल समाप्त सॉफ़्टवेयर की पहचान की जाती है और उसके लिए एक उपचार योजना है", "Unsupported software is tracked with an active plan to upgrade, replace, or isolate it.", "असमर्थित सॉफ़्टवेयर को अपग्रेड, प्रतिस्थापित, या पृथक करने की सक्रिय योजना के साथ ट्रैक किया जाता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("PATCH-005", "Firmware on network devices is kept current", "नेटवर्क उपकरणों पर फर्मवेयर वर्तमान रखा जाता है", "Routers, firewalls, and VPN appliances are patched, not just servers/workstations.", "राउटर, फ़ायरवॉल और VPN उपकरण पैच किए जाते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("PATCH-006", "Vulnerability remediation is prioritized by exploitability, not just CVSS score", "भेद्यता उपचार को केवल CVSS स्कोर के बजाय शोषण क्षमता द्वारा प्राथमिकता दी जाती है", "Known-exploited vulnerabilities are prioritized ahead of theoretical high-CVSS issues.", "ज्ञात-शोषित कमज़ोरियों को सैद्धांतिक उच्च-CVSS मुद्दों से आगे प्राथमिकता दी जाती है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("PATCH-007", "A documented patch management process exists", "एक दस्तावेज़ीकृत पैच प्रबंधन प्रक्रिया मौजूद है", "The organisation has a written process covering testing, deployment, and rollback of patches.", "संगठन के पास पैच के परीक्षण, परिनियोजन और रोलबैक को कवर करने वाली एक लिखित प्रक्रिया है।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
        ("PATCH-008", "Patch compliance is tracked and reported per asset", "पैच अनुपालन को प्रति संपत्ति ट्रैक और रिपोर्ट किया जाता है", "A dashboard or report shows patch compliance percentage across the asset inventory.", "एक डैशबोर्ड या रिपोर्ट संपत्ति सूची में पैच अनुपालन प्रतिशत दिखाता है।", "low", "boolean", 1.0, False, None, None, ALL, R_TECH),
        ("PATCH-009", "Third-party applications (not just OS) are included in patch management", "तृतीय-पक्ष अनुप्रयोग (केवल OS नहीं) पैच प्रबंधन में शामिल हैं", "Browsers, PDF readers, and other common third-party software are covered by patching.", "ब्राउज़र, PDF रीडर और अन्य सामान्य तृतीय-पक्ष सॉफ़्टवेयर पैचिंग द्वारा कवर किए जाते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("PATCH-010", "Emergency out-of-cycle patching process exists for actively exploited flaws", "सक्रिय रूप से शोषित खामियों के लिए आपातकालीन आउट-ऑफ-साइकिल पैचिंग प्रक्रिया मौजूद है", "A fast-track process can deploy a patch for an actively exploited zero-day within days.", "एक फास्ट-ट्रैक प्रक्रिया दिनों के भीतर सक्रिय रूप से शोषित शून्य-दिन के लिए पैच परिनियोजित कर सकती है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
    ],
    "Logging & Monitoring": [
        ("LOG-AUTH-LOGGING", "Authentication events (success and failure) are logged centrally", "प्रमाणीकरण घटनाएँ (सफलता और विफलता) केंद्रीय रूप से लॉग की जाती हैं", "Logon/logoff and failed authentication attempts are sent to a central log store.", "लॉगऑन/लॉगऑफ़ और विफल प्रमाणीकरण प्रयास एक केंद्रीय लॉग स्टोर में भेजे जाते हैं।", "high", "boolean", 2.5, True, None, None, ALL, R_TECH),
        ("LOG-ENDPOINT-TELEMETRY", "Endpoint process/execution telemetry is collected centrally", "एंडपॉइंट प्रक्रिया/निष्पादन टेलीमेट्री केंद्रीय रूप से एकत्र की जाती है", "Process creation, script execution, and file activity telemetry feeds a central platform (SIEM/EDR).", "प्रक्रिया निर्माण, स्क्रिप्ट निष्पादन टेलीमेट्री एक केंद्रीय प्लेटफ़ॉर्म को फ़ीड करती है।", "high", "boolean", 2.5, True, None, None, ALL, R_TECH),
        ("LOG-NETWORK-FLOW", "Network flow / firewall logs are centrally collected", "नेटवर्क फ़्लो/फ़ायरवॉल लॉग केंद्रीय रूप से एकत्र किए जाते हैं", "Firewall and network flow data is retained centrally for investigation purposes.", "फ़ायरवॉल और नेटवर्क फ़्लो डेटा जाँच उद्देश्यों के लिए केंद्रीय रूप से बनाए रखा जाता है।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("NET-INTERNAL-MONITORING", "Internal (east-west) network traffic is monitored for anomalies", "आंतरिक (पूर्व-पश्चिम) नेटवर्क ट्रैफ़िक की विसंगतियों के लिए निगरानी की जाती है", "Tooling exists to detect unusual internal scanning or lateral-movement patterns.", "असामान्य आंतरिक स्कैनिंग या पार्श्व-गति पैटर्न का पता लगाने के लिए टूलिंग मौजूद है।", "medium", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("LOG-EDR-CREDENTIAL-ALERTS", "Alerts fire on credential-dumping or suspicious authentication tooling", "क्रेडेंशियल-डंपिंग या संदिग्ध प्रमाणीकरण टूलिंग पर अलर्ट सक्रिय होते हैं", "EDR/SIEM rules detect tools like Mimikatz or unusual LSASS access patterns.", "EDR/SIEM नियम Mimikatz जैसे उपकरणों या असामान्य LSASS पहुँच पैटर्न का पता लगाते हैं।", "high", "boolean", 2.5, True, None, None, ALL, R_TECH),
        ("LOG-006", "Log retention meets or exceeds 90 days", "लॉग प्रतिधारण 90 दिनों के बराबर या उससे अधिक है", "Centralized logs are retained long enough to investigate a multi-week attacker dwell time.", "केंद्रीकृत लॉग बहु-सप्ताह की हमलावर उपस्थिति की जाँच के लिए पर्याप्त समय तक बनाए रखे जाते हैं।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("PROBE-NTP-SYNC", "All systems synchronize time from a trusted NTP source", "सभी प्रणालियाँ एक विश्वसनीय NTP स्रोत से समय सिंक्रनाइज़ करती हैं", "Accurate, synchronized timestamps are essential for correlating logs across systems during an investigation.", "जाँच के दौरान प्रणालियों में लॉग को सहसंबंधित करने के लिए सटीक, सिंक्रनाइज़्ड टाइमस्टैम्प आवश्यक हैं।", "low", "boolean", 1.0, False, None, "CHECK_006", ALL, R_TECH),
        ("LOG-008", "A SIEM or centralized log analysis platform is in use", "एक SIEM या केंद्रीकृत लॉग विश्लेषण प्लेटफ़ॉर्म उपयोग में है", "Logs are actively correlated and alerted on, not just stored passively.", "लॉग को केवल निष्क्रिय रूप से संग्रहीत करने के बजाय सक्रिय रूप से सहसंबंधित और अलर्ट किया जाता है।", "medium", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("LOG-009", "Alert fatigue is actively managed (tuned rules, triage process)", "अलर्ट थकान को सक्रिय रूप से प्रबंधित किया जाता है (ट्यून किए गए नियम, ट्राइएज प्रक्रिया)", "Detection rules are tuned to reduce false positives so real alerts don't get missed.", "पहचान नियमों को गलत सकारात्मक को कम करने के लिए ट्यून किया जाता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("LOG-010", "DNS query logging is enabled for threat detection", "खतरे का पता लगाने के लिए DNS क्वेरी लॉगिंग सक्षम है", "DNS logs help detect command-and-control beaconing and known-malicious domain lookups.", "DNS लॉग कमांड-एंड-कंट्रोल बीकनिंग का पता लगाने में मदद करते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("LOG-011", "A 24/7 monitoring capability or MDR/MSSP service is in place", "एक 24/7 निगरानी क्षमता या MDR/MSSP सेवा मौजूद है", "Alerts are triaged outside business hours, not just during the workday.", "व्यावसायिक घंटों के बाहर भी अलर्ट का ट्राइएज किया जाता है।", "medium", "boolean", 2.0, True, None, None, ALL, R_EXEC),
        ("LOG-012", "File integrity monitoring is enabled on critical servers", "महत्वपूर्ण सर्वर पर फ़ाइल अखंडता निगरानी सक्षम है", "Unexpected changes to system/critical files trigger an alert.", "सिस्टम/महत्वपूर्ण फ़ाइलों में अप्रत्याशित परिवर्तन एक अलर्ट को ट्रिगर करते हैं।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
        ("LOG-013", "Mass file-rename or mass-encryption-like activity triggers an alert", "बड़े पैमाने पर फ़ाइल-नाम बदलने या बड़े पैमाने पर-एन्क्रिप्शन-जैसी गतिविधि एक अलर्ट को ट्रिगर करती है", "A specific detection rule watches for the rapid file-extension-change pattern typical of ransomware.", "एक विशिष्ट पहचान नियम रैनसमवेयर के लिए विशिष्ट तीव्र फ़ाइल-एक्सटेंशन-परिवर्तन पैटर्न देखता है।", "high", "boolean", 2.5, True, None, None, ALL, R_TECH),
        ("LOG-014", "Cloud/SaaS admin activity is logged and monitored", "क्लाउड/SaaS व्यवस्थापक गतिविधि लॉग और निगरानी की जाती है", "Administrative actions in cloud consoles (M365, Google Workspace, AWS) generate audit logs that are reviewed.", "क्लाउड कंसोल में प्रशासनिक कार्य ऑडिट लॉग उत्पन्न करते हैं जिनकी समीक्षा की जाती है।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
    ],
    "Email & Phishing Defense": [
        ("MAIL-001", "SPF, DKIM, and DMARC are correctly configured on the mail domain", "मेल डोमेन पर SPF, DKIM और DMARC सही ढंग से कॉन्फ़िगर किए गए हैं", "Email authentication standards are enforced (DMARC at quarantine/reject) to prevent spoofing.", "स्पूफ़िंग को रोकने के लिए ईमेल प्रमाणीकरण मानक लागू किए जाते हैं।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
        ("MAIL-002", "Inbound attachments are sandboxed/detonated before delivery", "इनबाउंड अटैचमेंट डिलीवरी से पहले सैंडबॉक्स्ड/विस्फोटित किए जाते हैं", "Email attachments are analyzed in an isolated environment before reaching the inbox.", "ईमेल अटैचमेंट इनबॉक्स तक पहुँचने से पहले एक पृथक वातावरण में विश्लेषित किए जाते हैं।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("MAIL-003", "Malicious link protection rewrites/checks URLs at click-time", "दुर्भावनापूर्ण लिंक सुरक्षा क्लिक-समय पर URL को फिर से लिखती/जाँचती है", "URLs in email are checked against threat intelligence at the moment a user clicks them.", "ईमेल में URL की जाँच उस क्षण की जाती है जब उपयोगकर्ता उन पर क्लिक करता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("MAIL-004", "Simulated phishing exercises are run periodically", "नकली फ़िशिंग अभ्यास समय-समय पर चलाए जाते हैं", "The organisation runs simulated phishing campaigns at least quarterly and tracks click rates.", "संगठन कम से कम त्रैमासिक रूप से नकली फ़िशिंग अभियान चलाता है।", "medium", "single_select", 1.5, True, FREQUENCY_SELECT, None, ALL, R_ALL),
        ("MAIL-005", "A one-click phishing report button is available to all users", "सभी उपयोगकर्ताओं के लिए एक-क्लिक फ़िशिंग रिपोर्ट बटन उपलब्ध है", "Users can report suspicious email directly to security with a single click.", "उपयोगकर्ता एक क्लिक से सीधे सुरक्षा को संदिग्ध ईमेल की रिपोर्ट कर सकते हैं।", "low", "boolean", 1.0, False, None, None, ALL, R_ALL),
        ("MAIL-006", "External email is visibly tagged/banner-flagged", "बाहरी ईमेल दृश्यमान रूप से टैग/बैनर-फ़्लैग किया गया है", "Emails originating outside the organisation are visually flagged to reduce impersonation risk.", "संगठन के बाहर से उत्पन्न होने वाले ईमेल को दृष्टिगत रूप से फ़्लैग किया जाता है।", "low", "boolean", 1.0, False, None, None, ALL, R_TECH),
        ("MAIL-007", "Business email compromise (BEC) controls are in place for payment changes", "भुगतान परिवर्तनों के लिए व्यावसायिक ईमेल समझौता (BEC) नियंत्रण मौजूद हैं", "Wire/payment detail changes require out-of-band verification, not email alone.", "वायर/भुगतान विवरण परिवर्तनों के लिए ईमेल के अलावा सत्यापन की आवश्यकता होती है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("MAIL-008", "Attachment types commonly used in ransomware delivery are blocked by default", "रैनसमवेयर वितरण में आमतौर पर उपयोग किए जाने वाले अटैचमेंट प्रकार डिफ़ॉल्ट रूप से अवरुद्ध हैं", "Executable, script, and macro-enabled file types are blocked or quarantined at the gateway.", "निष्पादन योग्य, स्क्रिप्ट और मैक्रो-सक्षम फ़ाइल प्रकार गेटवे पर अवरुद्ध या संगरोधित हैं।", "high", "boolean", 2.0, False, None, None, ALL, R_TECH),
        ("MAIL-009", "Phishing report metrics are reviewed and used to target training", "फ़िशिंग रिपोर्ट मेट्रिक्स की समीक्षा की जाती है और प्रशिक्षण को लक्षित करने के लिए उपयोग की जाती है", "Click-rate and reporting-rate trends inform which teams receive additional training.", "क्लिक-दर और रिपोर्टिंग-दर रुझान यह सूचित करते हैं कि किन टीमों को अतिरिक्त प्रशिक्षण मिलता है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("MAIL-010", "Look-alike domain monitoring is in place", "लुक-अलाइक डोमेन निगरानी मौजूद है", "The organisation monitors for newly registered domains that closely resemble its own.", "संगठन नए पंजीकृत डोमेन की निगरानी करता है जो इसके अपने डोमेन से मिलते-जुलते हैं।", "low", "boolean", 1.0, False, None, None, ALL, R_TECH),
    ],
    "Incident Response": [
        ("IR-001", "A written, ransomware-specific incident response plan exists", "एक लिखित, रैनसमवेयर-विशिष्ट घटना प्रतिक्रिया योजना मौजूद है", "The IR plan includes ransomware-specific steps (isolate, preserve evidence, decision on payment, restore).", "IR योजना में रैनसमवेयर-विशिष्ट चरण शामिल हैं।", "high", "boolean", 3.0, True, None, None, ALL, R_EXEC),
        ("IR-002", "Incident response roles and contacts are pre-defined", "घटना प्रतिक्रिया भूमिकाएँ और संपर्क पूर्व-परिभाषित हैं", "A RACI or equivalent identifies who leads, communicates, and executes technical response.", "एक RACI या समकक्ष यह पहचानता है कि कौन नेतृत्व करता है, संवाद करता है, और तकनीकी प्रतिक्रिया निष्पादित करता है।", "high", "boolean", 2.0, True, None, None, ALL, R_EXEC),
        ("IR-003", "The IR plan is tested via tabletop exercise at least annually", "IR योजना का कम से कम वार्षिक रूप से टेबलटॉप अभ्यास के माध्यम से परीक्षण किया जाता है", "A simulated ransomware scenario is walked through with key stakeholders annually.", "प्रमुख हितधारकों के साथ वार्षिक रूप से एक नकली रैनसमवेयर परिदृश्य से गुज़रा जाता है।", "high", "single_select", 2.5, True, FREQUENCY_SELECT, None, ALL, R_EXEC),
        ("IR-004", "External IR retainer or breach-response service is contracted", "बाहरी IR रिटेनर या उल्लंघन-प्रतिक्रिया सेवा अनुबंधित है", "A pre-arranged relationship with an IR firm avoids delay in a real crisis.", "IR फर्म के साथ एक पूर्व-व्यवस्थित संबंध वास्तविक संकट में देरी से बचाता है।", "medium", "boolean", 1.5, True, None, None, ALL, R_EXEC),
        ("IR-005", "Out-of-band communication channel exists for use during an incident", "घटना के दौरान उपयोग के लिए बैंड-आउट संचार चैनल मौजूद है", "A communication method independent of potentially compromised email/IT systems is defined.", "संभावित रूप से समझौता किए गए ईमेल/आईटी सिस्टम से स्वतंत्र एक संचार विधि परिभाषित है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("IR-006", "Law enforcement and regulator contact points are documented", "कानून प्रवर्तन और नियामक संपर्क बिंदु दस्तावेज़ीकृत हैं", "The IR plan lists who to contact externally and under what conditions.", "IR योजना बाहरी रूप से संपर्क करने के लिए सूचीबद्ध करती है और किन परिस्थितियों में।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("IR-007", "A ransom-payment decision process is pre-defined (even if the answer is 'never pay')", "एक फिरौती-भुगतान निर्णय प्रक्रिया पूर्व-परिभाषित है", "Leadership has discussed and documented the decision framework before an actual incident occurs.", "नेतृत्व ने वास्तविक घटना होने से पहले निर्णय ढांचे पर चर्चा और दस्तावेज़ीकरण किया है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("IR-008", "Forensic evidence preservation procedures are documented", "फोरेंसिक साक्ष्य संरक्षण प्रक्रियाएँ दस्तावेज़ीकृत हैं", "Staff know how to preserve logs/memory/disk images without destroying evidence during containment.", "स्टाफ जानता है कि नियंत्रण के दौरान साक्ष्य को नष्ट किए बिना लॉग/मेमोरी/डिस्क छवियों को कैसे संरक्षित किया जाए।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("IR-009", "Post-incident review (lessons learned) process is defined", "घटना के बाद समीक्षा (सीखे गए सबक) प्रक्रिया परिभाषित है", "Every incident/exercise concludes with a documented after-action review.", "प्रत्येक घटना/अभ्यास एक दस्तावेज़ीकृत बाद-कार्रवाई समीक्षा के साथ समाप्त होता है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("IR-010", "Employees know how and to whom to report a suspected incident", "कर्मचारी जानते हैं कि संदिग्ध घटना की रिपोर्ट कैसे और किसे करनी है", "A simple, well-communicated reporting path exists for any employee noticing something suspicious.", "किसी भी कर्मचारी के लिए संदिग्ध कुछ देखने पर एक सरल, अच्छी तरह से संप्रेषित रिपोर्टिंग पथ मौजूद है।", "medium", "boolean", 1.5, False, None, None, ALL, R_ALL),
        ("IR-011", "Cyber incident notification triggers are documented internally", "साइबर घटना अधिसूचना ट्रिगर आंतरिक रूप से दस्तावेज़ीकृत हैं", "Clear internal thresholds define when an event is escalated to a formal incident.", "स्पष्ट आंतरिक सीमाएँ परिभाषित करती हैं कि कब एक घटना को औपचारिक घटना तक बढ़ाया जाता है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("IR-012", "Business continuity plan addresses prolonged IT outage scenarios", "व्यवसाय निरंतरता योजना लंबे समय तक आईटी आउटेज परिदृश्यों को संबोधित करती है", "The BCP includes manual/paper-based fallback procedures for a multi-day systems outage.", "BCP में बहु-दिवसीय सिस्टम आउटेज के लिए मैनुअल/कागज़-आधारित फ़ॉलबैक प्रक्रियाएँ शामिल हैं।", "medium", "boolean", 1.5, True, None, None, ALL, R_EXEC),
    ],
    "Third-Party / Supply Chain": [
        ("TPRM-001", "An inventory of third parties with system/network access exists", "सिस्टम/नेटवर्क पहुँच वाले तृतीय पक्षों की एक सूची मौजूद है", "All vendors, MSPs, and contractors with access to internal systems are documented.", "आंतरिक प्रणालियों तक पहुँच वाले सभी विक्रेता, MSP और ठेकेदार दस्तावेज़ीकृत हैं।", "medium", "boolean", 2.0, True, None, None, ALL, R_EXEC),
        ("TPRM-002", "Critical vendors undergo a security assessment before onboarding", "महत्वपूर्ण विक्रेता ऑनबोर्डिंग से पहले सुरक्षा मूल्यांकन से गुजरते हैं", "New vendors with access to sensitive systems/data complete a security questionnaire or audit.", "संवेदनशील प्रणालियों/डेटा तक पहुँच वाले नए विक्रेता एक सुरक्षा प्रश्नावली या ऑडिट पूरा करते हैं।", "medium", "boolean", 1.5, True, None, None, ALL, R_EXEC),
        ("TPRM-003", "Vendor/MSP remote access uses MFA and is time-bound", "विक्रेता/MSP दूरस्थ पहुँच MFA का उपयोग करती है और समय-सीमित है", "Third-party remote access is not standing/always-on and requires MFA like internal access.", "तृतीय-पक्ष दूरस्थ पहुँच स्थायी/हमेशा-चालू नहीं है और आंतरिक पहुँच की तरह MFA की आवश्यकता है।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("TPRM-004", "Vendor access is scoped to least privilege / specific systems", "विक्रेता पहुँच न्यूनतम-विशेषाधिकार/विशिष्ट प्रणालियों तक सीमित है", "Third parties cannot reach systems outside what their contracted service requires.", "तृतीय पक्ष उन प्रणालियों तक नहीं पहुँच सकते जो उनकी अनुबंधित सेवा की आवश्यकता से बाहर हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("TPRM-005", "Contracts include security and breach-notification obligations", "अनुबंधों में सुरक्षा और उल्लंघन-अधिसूचना दायित्व शामिल हैं", "Vendor contracts require prompt notification of any security incident affecting the organisation's data.", "विक्रेता अनुबंधों के लिए संगठन के डेटा को प्रभावित करने वाली किसी भी सुरक्षा घटना की तुरंत अधिसूचना आवश्यक है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("TPRM-006", "Software supply chain (dependencies, updates) is monitored for integrity", "सॉफ़्टवेयर आपूर्ति श्रृंखला (निर्भरताएँ, अद्यतन) की अखंडता के लिए निगरानी की जाती है", "Update sources are verified/signed, reducing risk of a compromised update mechanism.", "अद्यतन स्रोत सत्यापित/हस्ताक्षरित हैं, जिससे समझौता किए गए अद्यतन तंत्र का जोखिम कम होता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("TPRM-007", "Vendor access is reviewed and revoked promptly at contract end", "अनुबंध समाप्ति पर विक्रेता पहुँच की समीक्षा की जाती है और तुरंत रद्द की जाती है", "Terminated vendor relationships trigger immediate access revocation, not a delayed cleanup.", "समाप्त विक्रेता संबंध तत्काल पहुँच निरस्तीकरण को ट्रिगर करते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("TPRM-008", "A fourth-party risk process exists for critical vendors' own vendors", "महत्वपूर्ण विक्रेताओं के अपने विक्रेताओं के लिए एक चतुर्थ-पक्ष जोखिम प्रक्रिया मौजूद है", "For the most critical vendors, their own subcontractor risk is at least considered.", "सबसे महत्वपूर्ण विक्रेताओं के लिए, उनके अपने उपठेकेदार जोखिम पर कम से कम विचार किया जाता है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("TPRM-009", "Managed service provider (MSP) tooling access is monitored", "प्रबंधित सेवा प्रदाता (MSP) टूलिंग पहुँच की निगरानी की जाती है", "RMM/remote management tooling used by an MSP is itself monitored for anomalous behavior.", "MSP द्वारा उपयोग किए जाने वाले RMM/दूरस्थ प्रबंधन टूलिंग की स्वयं असामान्य व्यवहार के लिए निगरानी की जाती है।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
        ("TPRM-010", "Cloud provider shared-responsibility boundaries are understood and documented", "क्लाउड प्रदाता साझा-जिम्मेदारी सीमाएँ समझी और दस्तावेज़ीकृत हैं", "The organisation knows exactly which security controls it owns versus its cloud provider.", "संगठन ठीक से जानता है कि वह कौन से सुरक्षा नियंत्रणों का मालिक है बनाम उसका क्लाउड प्रदाता।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
    ],
    "Data Protection": [
        ("DATA-001", "Sensitive data is classified (e.g., public/internal/confidential/restricted)", "संवेदनशील डेटा वर्गीकृत है (जैसे सार्वजनिक/आंतरिक/गोपनीय/प्रतिबंधित)", "A data classification scheme is applied consistently across systems and file shares.", "एक डेटा वर्गीकरण योजना प्रणालियों और फ़ाइल शेयरों में लगातार लागू की जाती है।", "medium", "boolean", 2.0, True, None, None, ALL, R_EXEC),
        ("DATA-002", "Sensitive data is encrypted at rest", "संवेदनशील डेटा विश्राम पर एन्क्रिप्टेड है", "Databases and file stores holding sensitive/regulated data use encryption at rest.", "संवेदनशील/विनियमित डेटा रखने वाले डेटाबेस और फ़ाइल स्टोर विश्राम पर एन्क्रिप्शन का उपयोग करते हैं।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("DATA-003", "Sensitive data is encrypted in transit", "संवेदनशील डेटा पारगमन में एन्क्रिप्टेड है", "TLS or equivalent is enforced for any transmission of sensitive/regulated data.", "संवेदनशील/विनियमित डेटा के किसी भी प्रसारण के लिए TLS या समकक्ष लागू किया जाता है।", "high", "boolean", 2.0, False, None, None, ALL, R_TECH),
        ("DATA-004", "A data loss prevention (DLP) tool is deployed", "एक डेटा हानि रोकथाम (DLP) उपकरण तैनात है", "DLP tooling flags or blocks unauthorized movement of classified data.", "DLP टूलिंग वर्गीकृत डेटा की अनधिकृत गति को फ़्लैग या ब्लॉक करती है।", "medium", "boolean", 1.5, True, None, None, ALL, R_TECH),
        ("DATA-005", "Sensitive file shares use least-privilege access controls", "संवेदनशील फ़ाइल शेयर न्यूनतम-विशेषाधिकार पहुँच नियंत्रण का उपयोग करते हैं", "Access to confidential file shares is scoped to specific groups, not organisation-wide.", "गोपनीय फ़ाइल शेयरों तक पहुँच विशिष्ट समूहों तक सीमित है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("DATA-006", "A documented data retention and deletion policy exists", "एक दस्तावेज़ीकृत डेटा प्रतिधारण और विलोपन नीति मौजूद है", "Data is retained only as long as required and deleted per a defined schedule.", "डेटा केवल आवश्यक होने तक बनाए रखा जाता है और एक निश्चित अनुसूची के अनुसार हटाया जाता है।", "medium", "boolean", 1.5, True, None, None, ALL, R_EXEC),
        ("DATA-007", "Sensitive personal data fields are masked/tokenized where feasible", "संवेदनशील व्यक्तिगत डेटा फ़ील्ड जहाँ संभव हो मास्क्ड/टोकनयुक्त हैं", "Fields like national ID or payment card numbers are masked in non-production environments.", "राष्ट्रीय पहचान या भुगतान कार्ड नंबर जैसे फ़ील्ड गैर-उत्पादन वातावरण में मास्क्ड हैं।", "medium", "boolean", 1.5, False, None, None, "finance", R_TECH),
        ("DATA-008", "Database backups containing sensitive data are themselves encrypted", "संवेदनशील डेटा वाले डेटाबेस बैकअप स्वयं एन्क्रिप्टेड हैं", "Backup copies inherit the same encryption requirement as the source data.", "बैकअप प्रतियाँ स्रोत डेटा के समान एन्क्रिप्शन आवश्यकता विरासत में लेती हैं।", "high", "boolean", 2.0, True, None, None, ALL, R_TECH),
        ("DATA-009", "An inventory of where sensitive/regulated data resides is maintained", "संवेदनशील/विनियमित डेटा कहाँ रहता है इसकी एक सूची बनाए रखी जाती है", "The organisation can answer 'where does our most sensitive data live' with confidence.", "संगठन विश्वास के साथ 'हमारा सबसे संवेदनशील डेटा कहाँ रहता है' का उत्तर दे सकता है।", "medium", "boolean", 1.5, True, None, None, ALL, R_EXEC),
        ("DATA-010", "Data minimization principles guide new system design", "डेटा न्यूनीकरण सिद्धांत नई प्रणाली डिज़ाइन का मार्गदर्शन करते हैं", "New systems/processes are reviewed to avoid collecting more sensitive data than necessary.", "नई प्रणालियों/प्रक्रियाओं की समीक्षा आवश्यकता से अधिक संवेदनशील डेटा एकत्र करने से बचने के लिए की जाती है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("DATA-011", "Print/physical records containing sensitive data are secured", "संवेदनशील डेटा वाले प्रिंट/भौतिक रिकॉर्ड सुरक्षित हैं", "Physical documents with sensitive data are stored in locked/access-controlled areas.", "संवेदनशील डेटा वाले भौतिक दस्तावेज़ लॉक/पहुँच-नियंत्रित क्षेत्रों में संग्रहीत हैं।", "low", "boolean", 1.0, False, None, None, "healthcare", R_ALL),
        ("DATA-012", "Data subject/patient access requests have a documented handling process", "डेटा विषय/रोगी पहुँच अनुरोधों की एक दस्तावेज़ीकृत हैंडलिंग प्रक्रिया है", "Requests for personal data access, correction, or deletion follow a defined internal process.", "व्यक्तिगत डेटा पहुँच, सुधार, या विलोपन के अनुरोध एक निश्चित आंतरिक प्रक्रिया का पालन करते हैं।", "low", "boolean", 1.0, False, None, None, "healthcare", R_EXEC),
    ],
    "Awareness & Training": [
        ("AWARE-001", "Security awareness training is delivered to all staff at least annually", "सुरक्षा जागरूकता प्रशिक्षण कम से कम वार्षिक रूप से सभी कर्मचारियों को दिया जाता है", "Every employee, including non-technical staff, completes baseline security training yearly.", "गैर-तकनीकी कर्मचारियों सहित प्रत्येक कर्मचारी वार्षिक रूप से आधारभूत सुरक्षा प्रशिक्षण पूरा करता है।", "medium", "single_select", 2.0, True, FREQUENCY_SELECT, None, ALL, R_ALL),
        ("AWARE-002", "New hires receive security training during onboarding", "नए कर्मचारियों को ऑनबोर्डिंग के दौरान सुरक्षा प्रशिक्षण मिलता है", "Security awareness is part of the standard onboarding process, not an afterthought.", "सुरक्षा जागरूकता मानक ऑनबोर्डिंग प्रक्रिया का हिस्सा है।", "medium", "boolean", 1.5, False, None, None, ALL, R_ALL),
        ("AWARE-003", "Executives/leadership receive tailored security briefings", "कार्यकारी/नेतृत्व को अनुकूलित सुरक्षा ब्रीफिंग मिलती है", "Leadership training addresses whaling, BEC, and governance-level risk decisions specifically.", "नेतृत्व प्रशिक्षण विशेष रूप से व्हेलिंग, BEC और शासन-स्तरीय जोखिम निर्णयों को संबोधित करता है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("AWARE-004", "IT/technical staff receive role-specific security training", "आईटी/तकनीकी कर्मचारियों को भूमिका-विशिष्ट सुरक्षा प्रशिक्षण मिलता है", "System administrators receive deeper training on secure configuration and incident handling.", "सिस्टम व्यवस्थापकों को सुरक्षित कॉन्फ़िगरेशन पर गहन प्रशिक्षण मिलता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_TECH),
        ("AWARE-005", "Training completion is tracked and non-completion is followed up", "प्रशिक्षण पूर्णता को ट्रैक किया जाता है और गैर-पूर्णता का पालन किया जाता है", "A record system tracks who has and hasn't completed required training.", "एक रिकॉर्ड प्रणाली ट्रैक करती है कि किसने आवश्यक प्रशिक्षण पूरा किया है और किसने नहीं।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("AWARE-006", "Security awareness content is refreshed to reflect current threats", "सुरक्षा जागरूकता सामग्री वर्तमान खतरों को दर्शाने के लिए ताज़ा की जाती है", "Training material is updated at least annually to reflect current ransomware tactics.", "प्रशिक्षण सामग्री वर्तमान रैनसमवेयर रणनीति को दर्शाने के लिए कम से कम वार्षिक रूप से अद्यतन की जाती है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("AWARE-007", "Staff know how to verify a suspicious request out-of-band", "कर्मचारी जानते हैं कि किसी संदिग्ध अनुरोध को बैंड-आउट कैसे सत्यापित किया जाए", "Training explicitly covers verifying unusual payment/access requests via a second channel.", "प्रशिक्षण स्पष्ट रूप से एक दूसरे चैनल के माध्यम से असामान्य भुगतान/पहुँच अनुरोधों को सत्यापित करने को कवर करता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_ALL),
        ("AWARE-008", "A security champions or point-of-contact program exists in business units", "व्यावसायिक इकाइयों में एक सुरक्षा चैंपियन या संपर्क बिंदु कार्यक्रम मौजूद है", "Non-IT departments have a designated liaison for security questions and reporting.", "गैर-आईटी विभागों में सुरक्षा प्रश्नों और रिपोर्टिंग के लिए एक नामित संपर्क है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("AWARE-009", "Physical security awareness (tailgating, device lock) is included in training", "भौतिक सुरक्षा जागरूकता (टेलगेटिंग, डिवाइस लॉक) प्रशिक्षण में शामिल है", "Training covers physical risks like tailgating and leaving devices unlocked, not just phishing.", "प्रशिक्षण फ़िशिंग के अलावा टेलगेटिंग जैसे भौतिक जोखिमों को भी कवर करता है।", "low", "boolean", 1.0, False, None, None, ALL, R_ALL),
        ("AWARE-010", "Training effectiveness is measured (quiz scores, simulated phishing improvement)", "प्रशिक्षण प्रभावशीलता को मापा जाता है (क्विज़ स्कोर, नकली फ़िशिंग सुधार)", "The organisation tracks whether training is actually changing behavior over time.", "संगठन ट्रैक करता है कि क्या प्रशिक्षण वास्तव में समय के साथ व्यवहार बदल रहा है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
    ],
    "Compliance Considerations": [
        ("COMP-001", "The organisation maintains awareness of sector-relevant data-handling obligations", "संगठन क्षेत्र-प्रासंगिक डेटा-प्रबंधन दायित्वों के प्रति जागरूकता बनाए रखता है", "A designated person or team tracks general regulatory awareness relevant to the sector, without requiring specific legal citation here.", "एक नामित व्यक्ति या टीम क्षेत्र के लिए प्रासंगिक सामान्य नियामक जागरूकता को ट्रैक करती है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("COMP-002", "An incident-reporting readiness checklist exists for regulatory notification", "नियामक अधिसूचना के लिए एक घटना-रिपोर्टिंग तैयारी चेकलिस्ट मौजूद है", "The organisation has a generic checklist for what to do/report if an incident requires external notification.", "संगठन के पास एक सामान्य चेकलिस्ट है कि यदि किसी घटना के लिए बाहरी अधिसूचना की आवश्यकता हो तो क्या करना/रिपोर्ट करना है।", "medium", "boolean", 1.5, True, None, None, ALL, R_EXEC),
        ("COMP-003", "Data availability risk is explicitly considered in business continuity planning", "व्यवसाय निरंतरता योजना में डेटा उपलब्धता जोखिम पर स्पष्ट रूप से विचार किया जाता है", "BCP explicitly accounts for the risk of critical data being unavailable, not just systems being down.", "BCP स्पष्ट रूप से महत्वपूर्ण डेटा के अनुपलब्ध होने के जोखिम को ध्यान में रखता है।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("COMP-004", "Sector-specific data handling obligations are reviewed periodically", "क्षेत्र-विशिष्ट डेटा प्रबंधन दायित्वों की समय-समय पर समीक्षा की जाती है", "A periodic (at least annual) review checks whether data-handling practices still meet the organisation's own documented obligations.", "एक आवधिक (कम से कम वार्षिक) समीक्षा जाँचती है कि क्या डेटा-प्रबंधन प्रथाएँ अभी भी संगठन के अपने दस्तावेज़ीकृत दायित्वों को पूरा करती हैं।", "low", "single_select", 1.0, False, FREQUENCY_SELECT, None, ALL, R_EXEC),
        ("COMP-005", "Legal/compliance stakeholders are included in incident response planning", "कानूनी/अनुपालन हितधारक घटना प्रतिक्रिया योजना में शामिल हैं", "Legal counsel or compliance officers participate in IR plan development and tabletop exercises.", "कानूनी सलाहकार या अनुपालन अधिकारी IR योजना विकास में भाग लेते हैं।", "medium", "boolean", 1.5, False, None, None, ALL, R_EXEC),
        ("COMP-006", "Third-party/regulator inquiries have a designated response owner", "तृतीय-पक्ष/नियामक पूछताछ के लिए एक नामित प्रतिक्रिया स्वामी है", "A specific role is responsible for coordinating any regulator or auditor inquiry.", "एक विशिष्ट भूमिका किसी भी नियामक या लेखा परीक्षक पूछताछ के समन्वय के लिए जिम्मेदार है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("COMP-007", "Records of processing/data flows are documented for critical systems", "महत्वपूर्ण प्रणालियों के लिए प्रसंस्करण/डेटा प्रवाह के रिकॉर्ड दस्तावेज़ीकृत हैं", "The organisation can describe how data moves through its critical systems at a general level.", "संगठन सामान्य स्तर पर वर्णन कर सकता है कि डेटा उसकी महत्वपूर्ण प्रणालियों के माध्यम से कैसे चलता है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
        ("COMP-008", "Sector data-handling training is included in the awareness program", "क्षेत्र डेटा-प्रबंधन प्रशिक्षण जागरूकता कार्यक्रम में शामिल है", "General awareness training touches on sector-relevant data handling expectations.", "सामान्य जागरूकता प्रशिक्षण क्षेत्र-प्रासंगिक डेटा प्रबंधन अपेक्षाओं को छूता है।", "low", "boolean", 1.0, False, None, None, ALL, R_ALL),
        ("COMP-009", "An internal compliance checklist is reviewed before major IT changes", "प्रमुख आईटी परिवर्तनों से पहले एक आंतरिक अनुपालन चेकलिस्ट की समीक्षा की जाती है", "Significant infrastructure or data-handling changes trigger a lightweight internal compliance check.", "महत्वपूर्ण अवसंरचना या डेटा-प्रबंधन परिवर्तन एक हल्के आंतरिक अनुपालन जाँच को ट्रिगर करते हैं।", "low", "boolean", 1.0, False, None, None, ALL, R_TECH),
        ("COMP-010", "Incident reporting readiness is tested as part of tabletop exercises", "घटना रिपोर्टिंग तैयारी का परीक्षण टेबलटॉप अभ्यास के हिस्से के रूप में किया जाता है", "Tabletop exercises include the step of drafting/practicing an external notification.", "टेबलटॉप अभ्यास में एक बाहरी अधिसूचना का मसौदा तैयार करने/अभ्यास करने का चरण शामिल है।", "low", "boolean", 1.0, False, None, None, ALL, R_EXEC),
    ],
}

# ---------------------------------------------------------------------------
# Indian regulatory awareness content — informational only, attached to the
# specific controls each framework is actually relevant to. Deliberately
# conservative: only well-established, stable facts are cited (the CERT-In
# Directions' 6-hour reporting window, 180-day log retention, and NTP-sync
# requirements are all directly and repeatedly published by CERT-In since
# 28 April 2022). Where an obligation exists but the precise clause/timeline
# isn't something to state with confidence here (e.g. DPDP Rules breach-
# notification timelines), the note stays qualitative rather than inventing
# a number. This does not replace or grade against law — the questions
# above remain framework-neutral; this is a supplementary "what applies in
# India" panel shown alongside them.
# ---------------------------------------------------------------------------

INDIAN_REGULATORY_CONTEXT: dict[str, list[dict]] = {
    "COMP-001": [
        {
            "framework": "CERT-In Directions, 2022 (IT Act 2000, Section 70B(6))",
            "note": "Requires designated organisations to report specified cyber incidents (ransomware included) to CERT-In and to maintain baseline logging/time-sync hygiene described below.",
            "url": "https://www.cert-in.org.in/",
        },
        {
            "framework": "Digital Personal Data Protection (DPDP) Act, 2023",
            "note": "Applies wherever digital personal data is processed. Data Fiduciaries must implement 'reasonable security safeguards' to prevent breaches of personal data.",
            "url": "https://www.meity.gov.in/data-protection-framework",
        },
    ],
    "COMP-002": [
        {
            "framework": "CERT-In Directions, 2022",
            "note": "Mandates reporting specified incidents — ransomware attacks are explicitly listed — to CERT-In within 6 hours of noticing the incident or being made aware of it.",
            "url": "https://www.cert-in.org.in/",
        },
    ],
    "COMP-003": [
        {
            "framework": "DPDP Act, 2023",
            "note": "'Reasonable security safeguards' obligations extend to preventing loss of access to personal data, not only unauthorised disclosure — data availability is a compliance-relevant risk, not just an IT one.",
            "url": "https://www.meity.gov.in/data-protection-framework",
        },
    ],
    "COMP-004": [
        {
            "framework": "Sector regulators (RBI / SEBI / NCIIPC, as applicable)",
            "note": "Financial-sector entities, market infrastructure institutions, and declared Critical Information Infrastructure operators each carry additional, sector-specific cyber-resilience and reporting directions layered on top of the CERT-In baseline.",
            "url": None,
        },
    ],
    "COMP-005": [
        {
            "framework": "CERT-In Directions, 2022",
            "note": "The 6-hour reporting clock starts on notice of the incident, which makes pre-identified legal/compliance involvement in IR planning a practical necessity, not just good governance.",
            "url": "https://www.cert-in.org.in/",
        },
    ],
    "COMP-006": [
        {
            "framework": "DPDP Act, 2023",
            "note": "Establishes the Data Protection Board of India, which can inquire into personal data breaches and issue directions — organisations benefit from a designated owner for any such inquiry.",
            "url": "https://www.meity.gov.in/data-protection-framework",
        },
    ],
    "COMP-007": [
        {
            "framework": "DPDP Act, 2023",
            "note": "Entities classified as Significant Data Fiduciaries face additional obligations including data protection impact assessments and periodic data audits, both of which depend on already knowing how data flows through critical systems.",
            "url": "https://www.meity.gov.in/data-protection-framework",
        },
    ],
    "COMP-008": [
        {
            "framework": "DPDP Act, 2023",
            "note": "General workforce awareness of lawful, sector-relevant data handling supports the 'reasonable security safeguards' standard the Act expects Data Fiduciaries to demonstrate.",
            "url": None,
        },
    ],
    "COMP-009": [
        {
            "framework": "DPDP Act, 2023 — privacy/security by design",
            "note": "Reviewing data-handling impact before significant IT changes ship is a practical way to keep pace with 'reasonable security safeguards' obligations as systems evolve.",
            "url": None,
        },
    ],
    "COMP-010": [
        {
            "framework": "CERT-In Directions, 2022",
            "note": "Rehearsing the actual 6-hour reporting workflow in a tabletop exercise (not just having a checklist) is the difference between a documented process and one an organisation can execute under pressure.",
            "url": "https://www.cert-in.org.in/",
        },
    ],
    "LOG-006": [
        {
            "framework": "CERT-In Directions, 2022",
            "note": "CERT-In requires all service providers, intermediaries, data centres, body corporates, and government organisations to enable and maintain logs of all their ICT systems for a rolling period of 180 days, and to store these logs within Indian jurisdiction — a materially longer baseline than this control's 90-day threshold.",
            "url": "https://www.cert-in.org.in/",
        },
    ],
    "PROBE-NTP-SYNC": [
        {
            "framework": "CERT-In Directions, 2022",
            "note": "Directs all entities in scope to connect to the Network Time Protocol (NTP) servers of the National Informatics Centre (NIC) or National Physical Laboratory (NPL), or NTP servers traceable to these, so that timestamps are consistent for incident investigation and correlation with CERT-In.",
            "url": "https://www.cert-in.org.in/",
        },
    ],
    "IR-006": [
        {
            "framework": "CERT-In Directions, 2022",
            "note": "CERT-In is the designated national agency for incident reporting under IT Act Section 70B; regulated entities (banks/NBFCs under RBI, market infrastructure under SEBI, CII operators under NCIIPC) typically have an additional sector-regulator contact point alongside CERT-In.",
            "url": "https://www.cert-in.org.in/",
        },
    ],
    "IR-011": [
        {
            "framework": "CERT-In Directions, 2022",
            "note": "CERT-In publishes a specific list of mandatorily reportable cyber incident types — ransomware attacks, data breaches, and unauthorised access to IT systems are explicitly among them — which is a concrete, authoritative basis for internal escalation thresholds.",
            "url": "https://www.cert-in.org.in/",
        },
    ],
}

# ---------------------------------------------------------------------------
# Basic Track — a fixed, curated subset for non-technical users who want a
# fast readiness snapshot instead of the full ~150-control catalogue. This is
# a genuinely distinct mode (see routing_service.get_routed_questions), not
# just a relabeling of the existing role filter: it's a hand-picked ~24
# controls, 1-2 per domain, chosen for plain-language phrasing and the
# highest-impact/most decision-relevant signal in each domain, so a
# non-technical respondent can complete it in minutes.
# ---------------------------------------------------------------------------

BASIC_TRACK_CONTROL_IDS: set[str] = {
    "GOV-001", "GOV-002",
    "IAM-MFA-ENFORCED", "IAM-LEAST-PRIVILEGE",
    "PROBE-AVEDR-SERVICE", "PROBE-DISK-ENCRYPTION",
    "NET-SEGMENTATION", "PROBE-RDP-EXPOSURE",
    "BKP-001", "BKP-IMMUTABLE-STORAGE",
    "PROBE-PATCH-RECENCY",
    "LOG-AUTH-LOGGING",
    "MAIL-004", "MAIL-008",
    "IR-001", "IR-003",
    "TPRM-001", "TPRM-002",
    "DATA-001", "DATA-002",
    "AWARE-001", "AWARE-007",
    "COMP-002",
}

# ---------------------------------------------------------------------------
# CIS Community Defense Model v2.0 traceability — real, verified citations,
# not restated from memory. Pulled directly from the primary-source PDF
# ("CIS Community Defense Model v2.0", cisecurity.org, 2021/2022) by fetching
# and text-extracting it during this build, then cross-checking every number
# below against that extraction before writing it here. Two tables anchor
# this: Table 6/7 (p.16-17) rank all 153 CIS Safeguards by how many ATT&CK
# (sub-)techniques each one defends against, split into "all Safeguards" and
# "IG1 only"; Table 13/14 (p.23) gives the Ransomware attack pattern's
# coverage broken down per ATT&CK tactic specifically (not just overall).
#
# Coverage is intentionally partial and says so per-entry, rather than
# claiming every control traces to CDM: CDM itself documents that 49 CIS
# Safeguards — including the entirety of CIS Control 3 (Data Protection),
# Control 8 (Audit Log Management), Control 15 (Service Provider Management),
# and Control 17 (Incident Response Management) — are not mapped to ATT&CK
# at all, because they are foundational/process controls rather than
# technique-blocking ones. Those controls are cited here as "foundational,
# unmapped" with the qualitative CDM rationale instead of a technique count,
# which is the accurate thing to say about them, not a gap to paper over.
#
# One real correction came out of doing this properly: IAM-JOINER-LEAVER was
# weighted medium/1.5, but its underlying Safeguards (6.1/6.2) turned out to
# rank #2 and #3 of all 153 Safeguards in CDM's own analysis — that
# mismatch is fixed above, at the point where the control is defined.
# ---------------------------------------------------------------------------

CDM_SOURCE = {
    "title": "CIS Community Defense Model v2.0",
    "publisher": "Center for Internet Security (CIS)",
    "url": "https://www.cisecurity.org/insights/blog/cis-introduces-v2-0-of-the-cis-community-defense-model",
}

CIS_CDM_REFERENCE: dict[str, dict] = {
    "PROBE-SMBV1": {
        "safeguards": [{"id": "4.1", "title": "Establish and Maintain a Secure Configuration Process", "ig": "IG1", "technique_count": 342}],
        "note": "CIS Safeguard 4.1 is CDM's single highest-ranked Safeguard (342 of 530 ATT&CK sub-techniques) and is explicitly named the 'linchpin Safeguard' across all five analyzed attack types, including ransomware. Disabling deprecated protocols like SMBv1 falls directly under this Safeguard.",
    },
    "NET-004": {
        "safeguards": [{"id": "4.1", "title": "Establish and Maintain a Secure Configuration Process", "ig": "IG1", "technique_count": 342}],
        "note": "Restricting unnecessary internal SMB/RPC traffic is a secure-configuration control, the same #1-ranked Safeguard category as PROBE-SMBV1.",
    },
    "PROBE-RDP-EXPOSURE": {
        "safeguards": [{"id": "6.4", "title": "Require MFA for Remote Network Access", "ig": "IG1", "technique_count": 31}],
        "note": "ATT&CK sub-technique T1021.001 (Remote Desktop Protocol) has the highest number of CIS Safeguards mapped to it of any of the 530 sub-techniques in CDM's entire analysis (42 Safeguards) — CDM's own commentary calls this out by name and CIS has published a dedicated RDP hardening guide because of it.",
    },
    "IAM-MFA-ENFORCED": {
        "safeguards": [{"id": "6.4", "title": "Require MFA for Remote Network Access", "ig": "IG1", "technique_count": 31}, {"id": "6.3", "title": "Require MFA for Externally-Exposed Applications", "ig": "IG1", "technique_count": 17}],
        "note": "Both underlying Safeguards are IG1 — CDM's essential-cyber-hygiene tier, the baseline it recommends every organisation implement first.",
    },
    "IAM-MFA-ADMIN": {
        "safeguards": [{"id": "6.5", "title": "Require MFA for Administrative Access", "ig": "IG1", "technique_count": 33}],
        "note": "Ranked #12 of the IG1-only Safeguard list by ATT&CK sub-technique coverage.",
    },
    "IAM-LEAST-PRIVILEGE": {
        "safeguards": [{"id": "6.8", "title": "Define and Maintain Role-Based Access Control", "ig": "IG3", "technique_count": 206}],
        "note": "206 ATT&CK sub-techniques defended — 5th-highest of all 153 Safeguards — but CDM classifies this specific Safeguard as IG3 (advanced maturity), not IG1, so it is real security value gated behind a higher implementation bar than most Safeguards on this list.",
    },
    "PROBE-LOCAL-ADMINS": {
        "safeguards": [{"id": "5.4", "title": "Restrict Administrator Privileges to Dedicated Administrator Accounts", "ig": "IG1", "technique_count": 164}],
        "note": "8th-highest of all 153 Safeguards (164 techniques) and 5th-highest within IG1 alone.",
    },
    "IAM-JOINER-LEAVER": {
        "safeguards": [{"id": "6.1", "title": "Establish an Access Granting Process", "ig": "IG1", "technique_count": 217}, {"id": "6.2", "title": "Establish an Access Revoking Process", "ig": "IG1", "technique_count": 217}],
        "note": "Tied for #2/#3 of all 153 CIS Safeguards by ATT&CK sub-technique coverage (217 each, IG1) — the specific finding that this control's weight was originally underrated against (raised from medium/1.5 to high/2.5; see the comment on this control's definition above).",
    },
    "IAM-GUEST-ACCOUNTS": {
        "safeguards": [{"id": "4.7", "title": "Manage Default Accounts on Enterprise Assets and Software", "ig": "IG1", "technique_count": 188}],
        "note": "6th-highest of all 153 Safeguards (188 techniques).",
    },
    "IAM-PASSWORD-POLICY": {
        "safeguards": [{"id": "5.2", "title": "Use Unique Passwords", "ig": "IG1", "technique_count": 47}],
        "note": "IG1 Safeguard, 47 ATT&CK sub-techniques defended.",
    },
    "IAM-PASSWORD-REUSE-CONTROL": {
        "safeguards": [{"id": "5.2", "title": "Use Unique Passwords", "ig": "IG1", "technique_count": 47}],
        "note": "Same underlying Safeguard as IAM-PASSWORD-POLICY — breach-list checking is an enforcement mechanism for password uniqueness.",
    },
    "END-004": {
        "safeguards": [{"id": "2.5", "title": "Allowlist Authorized Software", "ig": "IG2", "technique_count": 101}],
        "note": "10th-highest of all 153 Safeguards (101 techniques); CDM classifies application allowlisting as IG2, not IG1.",
    },
    "DATA-005": {
        "safeguards": [{"id": "3.3", "title": "Configure Data Access Control Lists", "ig": "IG1", "technique_count": 75}],
        "note": "12th-highest of all 153 Safeguards (75 techniques), IG1.",
    },
    "PROBE-FIREWALL": {
        "safeguards": [{"id": "4.4", "title": "Implement and Manage a Firewall on Servers", "ig": "IG1", "technique_count": 60}],
        "note": "15th-highest of all 153 Safeguards (60 techniques), IG1.",
    },
    "END-008": {
        "safeguards": [{"id": "4.8", "title": "Uninstall or Disable Unnecessary Services on Enterprise Assets and Software", "ig": "IG2", "technique_count": 54}],
        "note": "54 ATT&CK sub-techniques defended, IG2.",
    },
    "PROBE-REMOTE-REGISTRY": {
        "safeguards": [{"id": "4.8", "title": "Uninstall or Disable Unnecessary Services on Enterprise Assets and Software", "ig": "IG2", "technique_count": 54}],
        "note": "Disabling an unneeded remote-administration service is a direct application of this Safeguard.",
    },
    "NET-SEGMENTATION": {
        "safeguards": [{"id": "12.2", "title": "Establish and Maintain a Secure Network Architecture", "ig": "IG2", "technique_count": 51}],
        "note": "19th-highest of all 153 Safeguards (51 techniques), IG2.",
    },
    "PROBE-PATCH-RECENCY": {
        "safeguards": [{"id": "7.3", "title": "Perform Automated Operating System Patch Management", "ig": "IG1", "technique_count": 24}, {"id": "7.1", "title": "Establish and Maintain a Vulnerability Management Process", "ig": "IG1", "technique_count": 27}],
        "note": "Both IG1. Lower raw technique-count than access-control Safeguards, but still inside CDM's ranked, ATT&CK-mapped set.",
    },
    "BKP-001": {
        "safeguards": [{"id": "11.3", "title": "Protect Recovery Data", "ig": "IG1", "technique_count": 27}],
        "note": "CDM's ATT&CK-technique-count method under-ranks recovery Safeguards relative to access-control ones, because backups mitigate an attack's impact rather than blocking earlier kill-chain steps — the count itself doesn't reflect that. CDM's own qualitative framing supports this control's high weight regardless: it separated Ransomware out as a distinct attack type specifically because of its outsized real-world impact (IBM X-Force ranked it the #1 threat type in 2021, 23% of caseload).",
    },
    "BKP-IMMUTABLE-STORAGE": {
        "safeguards": [{"id": "11.3", "title": "Protect Recovery Data", "ig": "IG1", "technique_count": 27}, {"id": "11.4", "title": "Establish and Maintain an Isolated Instance of Recovery Data", "ig": "IG2", "technique_count": 20}],
        "note": "11.4 (isolated/immutable recovery data specifically) is the most direct match for this control. Same caveat as BKP-001 applies to the raw technique count.",
    },
    "GOV-010": {
        "safeguards": [],
        "note": "Foundational and unmapped to ATT&CK by CDM's own analysis — asset inventory (CIS Controls 1 and 2) is explicitly named as a prerequisite that other, technique-mapped Safeguards depend on, not something ATT&CK's attacker-technique model itself scores.",
    },
    "LOG-AUTH-LOGGING": {
        "safeguards": [],
        "note": "CIS Control 8 (Audit Log Management) is explicitly named in CDM as one of the domains not mapped to any ATT&CK mitigation — it's foundational/process-oriented (you can't detect what you don't log) rather than something ATT&CK's technique-blocking model scores directly.",
    },
    "LOG-006": {
        "safeguards": [],
        "note": "Same CIS Control 8 (Audit Log Management) rationale as LOG-AUTH-LOGGING — CDM names this entire Control as unmapped to ATT&CK by design, not by omission.",
    },
    "GOV-001": {
        "safeguards": [],
        "note": "CIS Control 17 (Incident Response Management) is explicitly named in CDM as not addressed by any ATT&CK mitigation — response planning happens after/around an attack technique, not as a block against one, so it falls outside ATT&CK's technique-defense model by construction, not because CDM considers it low-value.",
    },
    "IR-001": {
        "safeguards": [],
        "note": "Same CIS Control 17 (Incident Response Management) rationale as GOV-001.",
    },
    "AWARE-001": {
        "safeguards": [{"id": "14.1", "title": "Establish and Maintain a Security Awareness Program", "ig": "IG1", "technique_count": 25}],
        "note": "IG1 Safeguard, 25 ATT&CK sub-techniques defended — consistent with, and validating, this control's existing medium weight rather than suggesting a change.",
    },
}


def cis_cdm_ransomware_tactic_coverage() -> dict:
    """CDM's Ransomware-specific attack-pattern coverage, per ATT&CK tactic
    (Table 13/14, p.23) — verified from the primary-source PDF, not restated
    from memory. Percent of Ransomware-relevant ATT&CK (sub-)techniques in
    that tactic defendable through CIS Safeguards."""
    return {
        "headline": {
            "ig1_coverage_pct": 78,
            "all_safeguards_coverage_pct": 92,
            "total_mapped_techniques": 229,
            "techniques_with_mitigation": 182,
        },
        "by_tactic_pct": {
            "resource-development": 50,
            "reconnaissance": 0,
            "initial-access": 100,
            "execution": 100,
            "persistence": 90,
            "privilege-escalation": 91,
            "defense-evasion": 75,
            "credential-access": 86,
            "discovery": 19,
            "lateral-movement": 93,
            "collection": 50,
            "command-and-control": 100,
            "exfiltration": 75,
            "impact": 83,
        },
        "source": CDM_SOURCE,
    }

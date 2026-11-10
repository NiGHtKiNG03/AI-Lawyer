# T7_bonus_hindi_deposit
Run: 2026-11-11 04:30:57 | provider: gemini | model: gemini-3.5-flash-lite

## Turn 1: user
मेरे मकान मालिक ने मेरी 20,000 रुपये की सिक्योरिटी डिपॉज़िट वापस नहीं की, जबकि मैंने फ्लैट खाली कर दिया है।

## Turn 1: system (mode = ask)
नमस्ते। आपने बताया कि आपने फ्लैट खाली कर दिया है और मकान मालिक ने आपकी 20,000 रुपये की सिक्योरिटी डिपॉज़िट वापस नहीं की है। 

इस मामले को ठीक से समझने के लिए कृपया मुझे ये 3 बातें बताएं:

1. क्या आपके पास कोई लिखित किराया समझौता (रेंट एग्रीमेंट) है, और आपने फ्लैट किस तारीख को खाली किया था?
2. मकान मालिक ने पैसे न लौटने का क्या कारण बताया है?
3. क्या आपके पास पैसे देने की रसीद या बैंक ट्रांसफर का कोई सबूत है?

## Turn 2: user
जयपुर, राजस्थान। लिखित किराया एग्रीमेंट था। मैंने 30 अप्रैल 2026 को फ्लैट खाली किया। मकान मालिक कोई कारण नहीं बता रहा। मेरे पास एग्रीमेंट, बैंक ट्रांसफर की रसीद और व्हाट्सऐप चैट हैं।

## Turn 2: system (mode = guidance)
जयपुर, राजस्थान में फ्लैट खाली करने के बाद मकान मालिक द्वारा 20,000 रुपये की सिक्योरिटी डिपॉज़िट बिना किसी कारण के रोक ली गई है। इस संबंध में किराएदार के पास लिखित एग्रीमेंट, बैंक ट्रांसफर की रसीद और व्हाट्सऐप चैट जैसे सबूत मौजूद हैं।

आपके बताए तथ्यों के आधार पर मैंने मार्गदर्शन तैयार किया है। अपने विकल्प, सत्यापित कानूनी संदर्भ और मेरे द्वारा तैयार किए जा सकने वाले दस्तावेज़ देखने के लिए Guidance टैब खोलें। कृपया अनिश्चितताओं वाला भाग भी पढ़ें।

### Structured guidance (JSON)
```json
{
  "problem": "जयपुर, राजस्थान में फ्लैट खाली करने के बाद मकान मालिक द्वारा 20,000 रुपये की सिक्योरिटी डिपॉज़िट बिना किसी कारण के रोक ली गई है। इस संबंध में किराएदार के पास लिखित एग्रीमेंट, बैंक ट्रांसफर की रसीद और व्हाट्सऐप चैट जैसे सबूत मौजूद हैं।",
  "rights": [
    {
      "text": "सिक्योरिटी डिपॉज़िट की वापसी के नियम आमतौर पर आपके लिखित रेंटल एग्रीमेंट की शर्तों और राज्य के रेंट लॉ द्वारा तय होते हैं, क्योंकि इस पर कोई एक केंद्रीय नियम नहीं है।",
      "kind": "general_information",
      "kb_ids": [
        "TENANT-AGREEMENT-FIRST"
      ],
      "supported": true
    },
    {
      "text": "यदि मकान मालिक पैसे वापस नहीं करता है, तो किराएदार बकाया राशि की वसूली के लिए सिविल अदालत में मुकदमा दायर करने का विकल्प देख सकता है, हालांकि इसके लिए प्रक्रिया और लिमिटेशन की अवधि की पुष्टि एक वकील से कराई जानी चाहिए।",
      "kind": "interpretation",
      "kb_ids": [
        "TENANT-CIVIL-REMEDY"
      ],
      "supported": true
    }
  ],
  "remedies": [
    {
      "text": "मकान मालिक को कानूनी कार्रवाई से पहले एक लिखित डिमांड नोटिस भेजने का चलन है, जो विवाद का दस्तावेजीकरण करता है।",
      "kind": "general_information",
      "kb_ids": [
        "TENANT-NOTICE-PRACTICE"
      ],
      "supported": true
    },
    {
      "text": "पात्रता के आधार पर, स्थानीय जिला विधिक सेवा प्राधिकरण (District Legal Services Authority) के माध्यम से मुफ्त कानूनी सहायता या लोक अदालत और मध्यस्थता (Mediation) का विकल्प भी आजमाया जा सकता है।",
      "kind": "general_information",
      "kb_ids": [
        "FREE-LEGAL-AID"
      ],
      "supported": true
    }
  ],
  "next_steps": [
    "अपने लिखित रेंटल एग्रीमेंट की शर्तों, नोटिस अवधि और डिपोज़िट से जुड़े क्लॉज़ को ध्यान से पढ़ें।",
    "मकान मालिक को सिक्योरिटी डिपॉज़िट वापस करने के लिए लिखित में डिमांड नोटिस भेजें।",
    "यदि मकान मालिक फिर भी पैसे न लौटाए, तो स्थानीय जिला विधिक सेवा प्राधिकरण (DLSA) या किसी वकील से सलाह लें।"
  ],
  "evidence_to_preserve": [
    "लिखित रेंटल एग्रीमेंट",
    "सिक्योरिटी डिपॉज़िट भुगतान की बैंक ट्रांसफर रसीद",
    "मकान मालिक के साथ हुई व्हाट्सऐप चैट"
  ],
  "uncertainties": [
    "Model Tenancy Act, 2021 राजस्थान राज्य द्वारा पूरी तरह से किस रूप में लागू किया गया है, इसकी पुष्टि आधिकारिक और कानूनी स्रोतों से करनी होगी।",
    "सिविल कोर्ट की प्रक्रिया, सही क्षेत्राधिकार (Jurisdiction) और लिमिटेशन की शुरुआत की तारीख की सटीक पुष्टि एक वकील ही कर सकते हैं।"
  ],
  "advocate_recommended": true,
  "advocate_reasons": [
    "कानूनी नोटिस का ड्राफ्ट तैयार करने और सही कानूनी प्रक्रिया चुनने के लिए वकील की सहायता उचित रहेगी।",
    "कोर्ट में सिविल सूट दायर करने और सही क्षेत्राधिकार तय करने के लिए पेशेवर कानूनी मार्गदर्शन आवश्यक है।"
  ],
  "advocate_reasons_system": [],
  "citations": [
    {
      "id": "TENANT-AGREEMENT-FIRST",
      "act": "Rental agreement and state rent law",
      "section": null,
      "title": "The agreement and your state's rent law decide the deposit rules",
      "source_url": "https://www.indiacode.nic.in/",
      "source_type": "official_portal",
      "verification": "general_principle",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "State-specific. Ask the user's state and city."
    },
    {
      "id": "TENANT-CIVIL-REMEDY",
      "act": "Code of Civil Procedure, 1908; Limitation Act, 1963",
      "section": null,
      "title": "Civil suit to recover a withheld deposit",
      "source_url": "https://ecourts.gov.in/",
      "source_type": "official_portal",
      "verification": "pending_section",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "Court, procedure and limitation start date need an advocate's confirmation."
    },
    {
      "id": "TENANT-NOTICE-PRACTICE",
      "act": "General practice",
      "section": null,
      "title": "A written demand notice is customary before suing",
      "source_url": "https://www.indiacode.nic.in/",
      "source_type": "official_portal",
      "verification": "general_principle",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "Special rules apply if the other party is a government body."
    },
    {
      "id": "FREE-LEGAL-AID",
      "act": "Legal Services Authorities Act, 1987 (NALSA and State/District Legal Services Authorities)",
      "section": null,
      "title": "Free legal aid, Lok Adalat and mediation",
      "source_url": "https://nalsa.gov.in/",
      "source_type": "official_portal",
      "verification": "general_principle",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "Eligibility and process vary; confirm with the local authority."
    }
  ],
  "removed_references": [],
  "missing_information": [],
  "disclaimer": "यह AI कानूनी सहायक उपयोगकर्ता द्वारा दी गई जानकारी के आधार पर सामान्य कानूनी जानकारी और सहायता प्रदान करता है। यह भारत में किसी योग्य अधिवक्ता की सलाह या प्रतिनिधित्व का विकल्प नहीं है। AI द्वारा दिए गए उत्तरों में त्रुटियाँ या चूक हो सकती हैं। महत्वपूर्ण कानूनी निर्णय और दस्तावेज़ किसी योग्य कानूनी पेशेवर से अवश्य जँचवाएँ।"
}
```

## Generated document
```
AI द्वारा तैयार मसौदा। भेजने या दाखिल करने से पहले इसे ध्यान से पढ़ें और किसी योग्य अधिवक्ता से जँचवाएँ। यह मसौदा किसी प्राधिकरण को भेजा, दाखिल या स्वीकृत नहीं हुआ है। हर [कोष्ठक वाले स्थान] को वास्तविक जानकारी से बदलें।

प्रेषक:
[Tenant's Full Name]
[Tenant's Address]
मोबाइल नंबर: [Tenant's Phone Number]
ईमेल: [Tenant's Email]

दिनांक: [Date of Notice]

सेवा में,
[Landlord's Full Name]
[Landlord's Address]

विषय: किराए की सिक्योरिटी डिपॉज़िट (20,000 रुपये) वापस करने के संबंध में कानूनी नोटिस।

महोदय/महोदया,

मैं नीचे दिए गए तथ्यों के आधार पर आपको यह कानूनी नोटिस प्रेषित कर रहा/रही हूँ:

1. यह है कि हमारे बीच जयपुर, राजस्थान में स्थित किराए के फ्लैट के संबंध में एक लिखित किराया एग्रीमेंट हुआ था।
2. यह है कि मैंने किराए के उक्त फ्लैट को 30 अप्रैल 2026 को पूरी तरह से खाली कर दिया था।
3. यह है कि फ्लैट खाली करते समय आपके पास मेरी कुल 20,000 रुपये की सिक्योरिटी डिपॉज़िट जमा थी।
4. यह है कि फ्लैट खाली करने के बाद से अब तक काफी समय बीत जाने के बावजूद, आपने बिना कोई कारण बताए मेरी 20,000 रुपये की सिक्योरिटी डिपॉज़िट वापस नहीं की है।
5. यह है कि इस संबंध में मेरे पास लिखित एग्रीमेंट, बैंक ट्रांसफर की रसीद और व्हाट्सऐप चैट के रूप में पुख्ता सबूत उपलब्ध हैं।

उपर्युक्त तथ्यों को ध्यान में रखते हुए, मैं आपसे अनुरोध करता/करती हूँ कि इस नोटिस की प्राप्ति से [Number of Days] दिनों के भीतर मेरी 20,000 रुपये की सिक्योरिटी डिपॉज़िट की पूरी राशि मेरे बैंक खाते में वापस लौटाई जाए।

यदि आप निर्धारित अवधि के भीतर राशि वापस नहीं करते हैं, तो मुझे उपलब्ध कानूनी उपायों (जैसे Code of Civil Procedure, 1908 और अन्य उचित कानूनी मंचों के माध्यम से सिविल मुकदमा) का सहारा लेने के लिए विवश होना पड़ेगा, जिसके लिए पूरी जिम्मेदारी आपकी होगी।

संलग्नक (Evidence):
1. लिखित किराया एग्रीमेंट
2. बैंक ट्रांसफर की रसीद
3. व्हाट्सऐप चैट का रिकॉर्ड

भवदीय,

[Tenant's Full Name]
[Tenant's Signature]
```

## Automated heuristic checks (NOT a verdict; manual review required)
- PASS: first turn asked follow-up questions (mode=ask)
- PASS: guidance produced at some point
- PASS: document generated
- PASS: document has placeholders
- PASS: document banner present
- PASS: every shown citation comes from the KB
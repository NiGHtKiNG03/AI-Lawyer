# T3_unpaid_salary
Run: 2026-11-11 04:25:52 | provider: gemini | model: gemini-3.5-flash-lite

## Turn 1: user
I left my company on 31 August 2026 and they have not paid my last two months of salary.

## Turn 1: system (mode = ask)
You mentioned that you left your company on August 31, 2026, and your last two months of salary have not been paid. 

To help you better, please answer these questions:
1. In which city and state were you working, and what kind of employment was this (for example, a private company, contract, etc.)?
2. Did you try asking your employer about the delay, and what did they say?
3. Do you have any written employment agreement, offer letter, or emails/messages about your salary?

## Turn 2: user
It is a private IT company in Gurugram, Haryana. I was a full-time permanent employee, salary Rs 45,000 per month as per my offer letter. The unpaid months are July and August 2026. HR keeps saying it is being processed. I have the offer letter, payslips up to June, bank statements and emails with HR.

## Turn 2: system (mode = guidance)
The user is a former full-time employee of a private IT company in Gurugram, Haryana, who left on 31 August 2026. Their monthly salary of Rs 45,000 for July and August 2026, totaling Rs 90,000, remains unpaid despite follow-ups, with HR claiming processing is underway.

I have prepared guidance based on what you shared. Open the Guidance tab to see your options, the verified legal references, and the documents I can draft. Please read the uncertainties section too.

### Structured guidance (JSON)
```json
{
  "problem": "The user is a former full-time employee of a private IT company in Gurugram, Haryana, who left on 31 August 2026. Their monthly salary of Rs 45,000 for July and August 2026, totaling Rs 90,000, remains unpaid despite follow-ups, with HR claiming processing is underway.",
  "rights": [
    {
      "text": "Salary disputes are dealt with under the Code on Wages, 2019, which repealed the older Payment of Wages Act 1936.",
      "kind": "interpretation",
      "kb_ids": [
        "WAGES-CODE-STATUS"
      ],
      "supported": true
    },
    {
      "text": "The Code on Wages provides time limits for paying wages, and secondary sources indicate that wages for an employee who resigns or leaves may be due within a short window, though exact state rules should be confirmed.",
      "kind": "interpretation",
      "kb_ids": [
        "WAGES-TIMELY-PAYMENT"
      ],
      "supported": true
    },
    {
      "text": "Secondary sources report that claims for unpaid wages under the Code can generally be made within three years.",
      "kind": "general_information",
      "kb_ids": [
        "WAGES-CLAIM-LIMITATION"
      ],
      "supported": true
    }
  ],
  "remedies": [
    {
      "text": "Unpaid wage claims are generally taken to the labour authority of the state where the workplace is located, with a written demand to the employer being a usual first step.",
      "kind": "general_information",
      "kb_ids": [
        "WAGES-FORUM"
      ],
      "supported": true
    },
    {
      "text": "Eligible persons may access free legal services or settlement through Lok Adalats via District Legal Services Authorities.",
      "kind": "general_information",
      "kb_ids": [
        "FREE-LEGAL-AID"
      ],
      "supported": true
    }
  ],
  "next_steps": [
    "Send a formal written demand letter to the employer requesting the immediate release of the unpaid salary for July and August 2026.",
    "Check the correct state labour department office, forms, and online filing options for Gurugram, Haryana.",
    "Consult a labour advocate or the state labour office to confirm how the Code on Wages, 2019 rules apply to your employment status."
  ],
  "evidence_to_preserve": [
    "Offer letter",
    "Payslips up to June 2026",
    "Bank statements",
    "Email correspondence with HR regarding the unpaid salary"
  ],
  "uncertainties": [
    "Whether the Code on Wages covers this specific worker depends on the definition of an employee.",
    "State-specific rules and timelines under the Code on Wages in Haryana must be confirmed.",
    "The exact forum, office, and forms required for filing a complaint in Haryana should be verified with the state labour department."
  ],
  "advocate_recommended": true,
  "advocate_reasons": [
    "State-specific rules and procedures under the Code on Wages require professional verification.",
    "An advocate can help draft a legally sound formal demand letter and guide you through the correct labour authority forum."
  ],
  "advocate_reasons_system": [],
  "citations": [
    {
      "id": "WAGES-CODE-STATUS",
      "act": "Code on Wages, 2019",
      "section": "69",
      "title": "Wage laws changed in November 2025: Payment of Wages Act is repealed",
      "source_url": "https://www.indiacode.nic.in/",
      "source_type": "official_portal",
      "verification": "secondary_verified",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "State rules differ in readiness. Whether the Code covers a particular worker depends on whether they are an 'employee' as defined; an advocate or labour office should confirm."
    },
    {
      "id": "WAGES-TIMELY-PAYMENT",
      "act": "Code on Wages, 2019",
      "section": "17",
      "title": "Time limit for paying wages, including on leaving a job",
      "source_url": "https://www.indiacode.nic.in/",
      "source_type": "official_portal",
      "verification": "secondary_verified",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "Exact periods and any state-specific rules should be confirmed."
    },
    {
      "id": "WAGES-CLAIM-LIMITATION",
      "act": "Code on Wages, 2019",
      "section": "45",
      "title": "Time limit for claiming unpaid wages",
      "source_url": "https://www.indiacode.nic.in/",
      "source_type": "official_portal",
      "verification": "single_secondary",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "Provisional. Confirm before relying on any deadline."
    },
    {
      "id": "WAGES-FORUM",
      "act": "State labour department / authority under the Code on Wages, 2019",
      "section": null,
      "title": "Where an unpaid salary complaint goes",
      "source_url": "https://labour.gov.in/",
      "source_type": "official_portal",
      "verification": "general_principle",
      "checked_on": "2026-11-08",
      "jurisdiction_note": "State-specific. Do not assume the office or form."
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
  "disclaimer": "This AI Legal Assistant provides general legal information and assistance based on the information provided by the user. It is not a substitute for advice or representation from a qualified advocate in India. AI-generated responses may contain errors or omissions. Important legal decisions and documents should be reviewed by a qualified legal professional."
}
```

## Generated document
```
AI-GENERATED DRAFT. Review carefully and have a qualified advocate check it before sending or filing. This draft has not been served, filed or accepted by any authority. Replace every [bracketed placeholder] with real information.

[Sender's Full Name]
[Sender's Address]
[Sender's Phone Number]
[Sender's Email Address]

Date: [Date]

To,
[Employer/HR Manager's Full Name]
[Employer/Company Name]
[Employer's Full Address]

Subject: Demand for payment of unpaid salary for the period of July and August 2026

Dear [Employer/HR Manager's Full Name],

1. I, [Sender's Full Name], was employed as a full-time permanent employee at your private IT company located in Gurugram, Haryana, with a monthly salary of Rs 45,000 as per my offer letter.

2. My last working day at the company was 31 August 2026.

3. My salary for the months of July 2026 and August 2026, amounting to a total of Rs 90,000 (Rs 45,000 per month), remains unpaid.

4. Despite my follow-ups and your responses stating that the salary processing is underway, the dues have not been credited to my account.

As per the Code on Wages, 2019, including Section 17 and Section 45, unpaid wages are legally required to be paid, and claims may be pursued within the specified limitation period.

I hereby demand that you clear my total unpaid salary of Rs 90,000 within [Number of Days, e.g., 15] days from the receipt of this letter by transferring the amount to my designated bank account.

If the payment is not made within the specified period, I may pursue available legal remedies, including approaching the State labour department or authority under the Code on Wages, 2019, and utilizing services under the Legal Services Authorities Act, 1987.

Enclosures:
- Offer letter
- Payslips up to June
- Bank statements
- Emails with HR

Sincerely,

[Sender's Full Name]
```

## Automated heuristic checks (NOT a verdict; manual review required)
- PASS: first turn asked follow-up questions (mode=ask)
- PASS: guidance produced at some point
- PASS: document generated
- PASS: document has placeholders
- PASS: document banner present
- PASS: every shown citation comes from the KB
- FAIL: does not present repealed Payment of Wages Act as current (MANUAL: read the text)
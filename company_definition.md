# Cybersecurity Compliance Company Overview Generation Prompt

## Objective
Generate 30 distinct, semi-realistic company overviews in Markdown format. Each overview must provide essential context for determining cybersecurity compliance requirements while maintaining industry authenticity and regulatory logic.

## Template Structure

```markdown
### [Company Name]

**Organization Overview:**
* **Business Details:** [2-3 sentences describing core business activities, primary services/products, and target market segment]
* **Industry:** [Primary industry classification with sub-sector if relevant]
* **Size:** [Employee count range AND annual revenue bracket (e.g., "250-500 employees, $50-100M revenue")]
* **Structure:** [Legal structure, ownership type, and operational scope (local/national/international)]
* **Technology Infrastructure:** [Primary infrastructure model, cloud providers, critical systems, and data processing scale]

**Compliance Requirements:**
* **Applicable Frameworks/Regulations:** [Select 2-4 frameworks that logically align with the organization's profile]
    * NIST Cybersecurity Framework (CSF) 2.0
    * NIST 800-171 Rev. 3
    * CMMC Level 1/2
    * ISO 27001
    * CIS Controls
    * HIPAA
    * PCI DSS
    * GDPR
    * NJ SISM
    * SOC2
    * CJIS

**Policy Parameters:** [Include only when specific constraints significantly impact compliance approach]
* **Critical Constraints:** [Unique compliance challenges, regulatory obligations, or risk factors]
* **Key Stakeholders:** [Relevant roles/departments for compliance implementation]
* **Sensitive Systems/Data:** [Specific data types or systems requiring enhanced protection]
```

## Generation Requirements

### Industry Distribution Guidelines
Ensure representation across these sectors (aim for 3-4 companies per major category):
- **Healthcare:** Hospitals, clinics, health tech, medical devices
- **Financial Services:** Banks, credit unions, fintech, investment firms
- **Government/Defense:** Federal contractors, state agencies, defense suppliers
- **Technology:** SaaS providers, software development, cloud services
- **Manufacturing:** Industrial, automotive, pharmaceuticals, energy
- **Retail/E-commerce:** Online retailers, payment processors, logistics
- **Education:** Universities, K-12 districts, online learning platforms
- **Critical Infrastructure:** Utilities, telecommunications, transportation

### Size Stratification
- **Small (10-100 employees):** 8 companies
- **Medium (100-1,000 employees):** 12 companies  
- **Large (1,000+ employees):** 10 companies

### Compliance Framework Logic Matrix
**Mandatory Alignments:**
- Healthcare organizations → HIPAA required
- Payment processing → PCI DSS required
- Government contractors → NIST 800-171/CMMC required
- Financial institutions → SOC2 + regulatory frameworks
- International operations → GDPR consideration
- Critical infrastructure → NIST CSF recommended

### Quality Standards

**Organization Overview Requirements:**
- Business descriptions must be specific enough to infer data types and risk profiles
- Technology infrastructure should reflect realistic modern deployments
- Size and structure should align with industry norms
- Geographic scope should influence regulatory selection

**Compliance Requirements Logic:**
- Never select all available frameworks for one company
- Ensure framework selection reflects actual regulatory obligations
- Vary combinations to demonstrate different compliance scenarios
- Include foundational frameworks (NIST CSF, CIS) with sector-specific regulations

**Policy Parameters Usage:**
- Include only when adding meaningful compliance context
- Focus on constraints that affect security control implementation
- Avoid generic statements that apply to all organizations
- Maximum 40% of companies should include this section

### Content Quality Guidelines
- Use industry-appropriate terminology and business models
- Avoid marketing language or promotional content
- Ensure semi-realistic company profiles (could plausibly exist)
- Maintain consistent formatting and structure
- Focus on compliance-relevant details only

### Deliverable Format
- Present all 30 companies in a single response
- Use proper Markdown formatting
- Number companies sequentially (1-30)
- Ensure each company occupies appropriate space (no overly long descriptions)

## Success Criteria
- 30 unique, realistic company profiles
- Logical alignment between business type and compliance requirements  
- Appropriate industry and size distribution
- Varied compliance framework combinations
- Consistent formatting and structure
- Actionable information for compliance assessment
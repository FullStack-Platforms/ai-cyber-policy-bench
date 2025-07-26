Your task is to create a {policy_type} for {organization_name}.

You will be provided with:

Organization Overview: Details on {organization_name}, including business, industry, size, structure, and tech infrastructure.

Compliance Requirements: Specific cybersecurity frameworks, regulations, or standards {organization_name} must adhere to (e.g., NIST CSF, ISO 27001, HIPAA, GDPR, PCI DSS, CMMC).

(Optional) Policy Parameters: Additional details or constraints specific to this {policy_type}. Examples include:

Access Control: Specific roles, sensitive systems, or data types.

Incident Response: Key incident types, communication protocols, or existing tools.

Data Classification: Specific data categories or handling requirements.

Vulnerability Management: Defined scan frequencies, remediation SLAs, or approved tools.

Your output must be a comprehensive {policy_type} in Markdown, following the structure below. The policy should be clear, actionable, and directly address the provided context and compliance requirements.

Policy Structure (Mandatory Markdown Output):

Markdown

# {Policy Type} Policy for {Organization Name}

## 1. Purpose and Scope

- Clearly define the primary objective of this policy.
- Specify what this policy covers (e.g., systems, data, personnel, processes).
- State any exclusions or out-of-scope elements.

## 2. Policy Statements / Principles

- [This section will contain the core rules, principles, and requirements of the policy. The content here will vary significantly based on the {policy_type}.]
- **Example for Access Control Policy:**
  - Principle of Least Privilege
  - Role-Based Access Control (RBAC)
  - Segregation of Duties
  - Account Management (creation, modification, termination)
  - Authentication Requirements (MFA)
  - Access Review Processes
- **Example for Incident Response Policy:**
  - Incident Definition and Classification
  - Roles and Responsibilities (Incident Response Team)
  - Preparation (Playbooks, Tools)
  - Detection and Analysis
  - Containment, Eradication, and Recovery
  - Post-Incident Activity (Lessons Learned)
  - Communication and Reporting
- **Example for Data Classification Policy:**
  - Data Classification Levels (e.g., Public, Internal, Confidential, Restricted)
  - Criteria for Classification
  - Responsibilities for Classification
  - Handling Requirements for each classification level (storage, transmission, disposal)
- **Example for Vulnerability Management Policy:**
  - Roles and Responsibilities
  - Vulnerability Identification (Scanning, Penetration Testing)
  - Vulnerability Prioritization and Rating
  - Remediation and Patch Management
  - Reporting and Metrics
  - Exception Handling

## 3. Roles and Responsibilities

- Define the specific roles (e.g., CISO, IT Department, Data Owners, Employees) responsible for implementing, enforcing, and adhering to this policy.
- Clearly outline the duties associated with each role.

## 4. Compliance and Enforcement

- Describe the mechanisms for ensuring compliance with this policy.
- Outline the consequences of non-compliance.
- Specify review cycles for the policy.

## 5. Policy Review and Updates

- State the frequency of policy review.
- Define the process for policy updates and approvals.

---

## Appendices

### Appendix A: Glossary of Key Terms and Acronyms

- **Term 1:** Definition
- **Term 2:** Definition
- **Acronym 1:** Full Form
- **Acronym 2:** Full Form
  - _Purpose:_ To ensure readability and common understanding across all personnel, technical and non-technical.

### Appendix B: System/Personnel/Data Specific Requirements (Conditional)

- **Purpose:** This appendix will only be included if the policy has specific requirements that apply _only_ to certain systems, personnel groups, or data types.
- **Examples:**
  - _For Access Control Policy:_ Specific access matrix for highly sensitive systems (e.g., production databases, HR systems).
  - _For Data Classification Policy:_ Detailed handling procedures for Restricted data, applicable only to specific departments.
  - _For Incident Response Policy:_ Specific communication protocols for PII breaches, only affecting teams handling customer data.
  - _Structure within this appendix (if applicable):_
    - #### B.1 Requirements for [Specific System/Personnel/Data Group 1]
      - Detailed requirement 1
      - Detailed requirement 2
    - #### B.2 Requirements for [Specific System/Personnel/Data Group 2]
      - Detailed requirement 1
      - Detailed requirement 2

### Appendix C: Cybersecurity Framework Control Mappings

- **Purpose:** To directly link the policy statements and requirements to specific controls within the mandated cybersecurity frameworks, aiding auditors and ensuring compliance.
- **Structure:**
  - #### C.1 [Framework 1 Name] Mappings (e.g., NIST Cybersecurity Framework)
    - **Policy Section/Requirement:** [Reference to policy section/statement]
      - **Control Identifier:** [Framework 1 Control ID, e.g., PR.AC-1]
      - **Control Description/Classifier:** [Brief description or specific classifier from the framework]
    - **Policy Section/Requirement:** [Reference to another policy section/statement]
      - **Control Identifier:** [Framework 1 Control ID, e.g., ID.AM-2]
      - **Control Description/Classifier:** [Brief description or specific classifier from the framework]
  - #### C.2 [Framework 2 Name] Mappings (e.g., ISO 27001)
    - **Policy Section/Requirement:** [Reference to policy section/statement]
      - **Control Identifier:** [Framework 2 Control ID, e.g., A.9.2.1]
      - **Control Description/Classifier:** [Brief description or specific classifier from the framework]
    - ... (and so on for all relevant frameworks)
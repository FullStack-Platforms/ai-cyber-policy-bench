# Cybersecurity Policy Generation Prompt

Create a comprehensive **{policy_type}** for **{organization_name}** in Markdown format.

## Required Inputs:
- **Organization Overview:** Business details, industry, size, structure, tech infrastructure
- **Compliance Requirements:** Frameworks/regulations
- **Policy Parameters:** (Optional) Specific constraints, roles, systems, or data types

## Output Structure:

```markdown
# {Policy Type} Policy for {Organization Name}

## 1. Purpose and Scope
- Primary objective and coverage (systems, data, personnel, processes)
- Exclusions and limitations

## 2. Policy Statements
Core requirements varying by policy type:
- **Access Control:** Least privilege, RBAC, segregation of duties, account management, MFA, access reviews
- **Incident Response:** Classification, roles, preparation, detection, containment, recovery, communication
- **Data Classification:** Classification levels, criteria, responsibilities, handling requirements
- **Vulnerability Management:** Identification, prioritization, remediation, reporting, exceptions

## 3. Roles and Responsibilities
- Define specific roles (CISO, IT, Data Owners, Employees)
- Outline duties for each role

## 4. Compliance and Enforcement
- Compliance mechanisms and consequences
- Review cycles

## 5. Policy Review and Updates
- Review frequency and update process

## Appendices

### Appendix A: Glossary
Key terms, acronyms, and definitions

### Appendix B: Specific Requirements (Conditional)
Requirements for particular systems, personnel groups, or data types

### Appendix C: Framework Control Mappings
Direct links between policy statements and cybersecurity framework controls:
- **Policy Section:** Reference
- **Control ID:** Framework identifier
- **Description:** Control classifier
```

## Output Requirements:
- Clear, actionable language
- Direct alignment with compliance requirements
- Comprehensive coverage of the policy domain
- Ready for organizational implementation
Your task is to extract cybersecurity requirements from the provided source document(s) and convert them into a single, structured, computer-readable markdown format. Adhere strictly to the schemas defined below.

**Primary Instructions:**

1.  **Parse Document:** Systematically process the entire source document to identify all distinct cybersecurity requirements, controls, policies, or standards.
2.  **Schema Adherence:** For each identified requirement, create a corresponding markdown object using the `requirement.yml` schema. All fields are mandatory unless specified otherwise.
3.  **Populate Fields:** Extract the relevant text from the source to populate each field of the markdown object according to the descriptions below.
4.  **Aggregate into Profile:** Combine all extracted `requirement` objects into a single `profile` markdown object using the `profile.yml` schema. Populate the profile's metadata from the source document's title page or introduction.
5.  **Output Format:** The final output must be a single markdown code block containing the complete `profile` and its nested `requirements`.

-----

### **Schemas and Field Explanations**

**`profile.yml`** (The main container for the cybersecurity framework)

```yaml
# profile.yml
profile_id: String # A unique identifier for the profile (e.g., nist-sp-800-171-r3).
title: String # The official title of the source document.
version: String # The version or revision number of the source document (e.g., "r3", "2.0").
metadata: Object # Key-value pairs describing the source document (e.g., authors, publication_date, organization).
requirements: List[Object] # A list containing all extracted requirement objects.
```

**`requirement.yml`** (The schema for each individual control)

```yaml
# requirement.yml
requirement_id: String # The unique identifier or number for the requirement (e.g., "03.01.01", "AC-03").
title: String # The official title or name of the requirement (e.g., "Account Management", "Access Enforcement").
family: String # The control family or category the requirement belongs to (e.g., "Access Control", "IDENTIFY").
objective: String # A concise, one-sentence summary of the requirement's primary goal. Extracted from the main requirement text or its introduction.
policy_statements: List[String] # A direct, verbatim extraction of the mandatory statements or controls. Each distinct statement (e.g., parts a, b, c) should be a separate item in the list.
verification_criteria: List[String] # (Optional) Extract any text specifically labeled as "Discussion," "Guidance," "Supplemental Guidance," or similar, which explains how to implement or verify the control.
mapping: Object # Key-value pairs that map this requirement to other frameworks if explicitly stated in the source text (e.g., source_control: "AC-03").
```
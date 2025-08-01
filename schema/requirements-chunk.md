Your task is to extract cybersecurity requirements from the provided source document(s) and convert them into structured, computer-readable markdown format. Focus exclusively on mapping individual requirements using the schema defined below.

**Primary Instructions:**

1. **Parse Document:** Systematically process the source document to identify all distinct cybersecurity requirements, controls, policies, or standards.
2. **Schema Adherence:** For each identified requirement, create a corresponding markdown object using the `requirement.yml` schema. All fields are mandatory unless specified otherwise.
3. **Populate Fields:** Extract the relevant text from the source to populate each field of the markdown object according to the descriptions below.
4. **Output Format:** The final output must be a markdown code block containing all extracted `requirement` objects.

-----

### **Schema and Field Explanations**

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

## Key Guidelines
- **Quote strings** containing colons, special characters, or version numbers
- **Use empty arrays/objects** (`[]`, `{}`) for optional fields when no data exists
- **Extract verbatim text** for policy statements without citation markup
- **Maintain consistent indentation** (2 spaces)
- **Remove invalid syntax** like `[cite_start]` or `[cite: xxx]` markup

## Output Requirements
- Valid YAML syntax that passes standard parsers
- All policy statements properly quoted as strings
- Clean, consistent formatting throughout
- Single code block with complete profile structure
# Cybersecurity Requirements Extraction Prompt

Extract cybersecurity requirements from source documents and convert them into structured YAML format.

## Task
1. **Parse Document:** Identify all cybersecurity requirements, controls, policies, or standards
2. **Extract Requirements:** Create requirement objects following the schema below
3. **Create Profile:** Aggregate all requirements into a single profile object
4. **Output:** Single YAML code block with complete profile and requirements

## Schemas

### Profile Schema
```yaml
profile_id: string          # Unique identifier (e.g., "nist-csf-2.0")
title: string              # Official document title
version: string            # Version number (quoted if contains periods)
metadata:                  # Document metadata
  publication_date: string
  organization: string
  document_identifier: string
requirements: []           # List of requirement objects
```

### Requirement Schema
```yaml
requirement_id: string     # Unique control ID (e.g., "GV.OC", "AC-03")
title: string             # Official requirement title
family: string            # Control family/category
objective: string         # Primary goal (one sentence)
policy_statements: []     # List of verbatim requirement statements
verification_criteria: [] # Optional implementation guidance
mapping: {}              # Optional framework mappings
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
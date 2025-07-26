# Ai Cyber Policy Bench

WHEN a user runs policy_writer/main.py
THE SYSTEM SHALL produce cybersecurity policies for 20 sample companies compliant with their specificied compliance frameworks by prompting various Ai's with a standard prompt via the litellm python sdk

WHEN a user runs policy_evaluator/main.py
THE SYSTEM SHALL validate the generated policies from policy_writer for completeness and adherence to the specified standards.

WHEN cybersecurity policies are authored or updated
THE SYSTEM SHALL store each policy as a standardized YAML file in the repository under a dedicated policies directory (e.g., `/policies`).

WHEN either application needs context on cybersecurity standards
THE SYSTEM SHALL provide a shared vector database that indexes both cybersecurity standards and the YAML-formatted policy documents for semantic retrieval.

WHEN the project is complete
THE SYSTEM SHALL provide a standardized way for peer reviewers to verify my findings 
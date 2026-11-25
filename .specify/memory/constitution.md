<!--
Sync Impact Report
Version change: unratified scaffold → 1.0.0
Modified principles: none; initial principles established
Added sections: Product and Architecture; Development Workflow
Removed sections: none
Follow-up TODOs: Confirm original ratification date.
-->
# CatHotel Constitution

## Core Principles

### I. Customer-Centered Simplicity
CatHotel MUST provide a simple, minimal experience centered on the needs of cat
owners and staff. Every feature MUST deliver clear, practical value to at least
one of these roles. Features without a demonstrated user benefit MUST NOT be
added. This keeps the product focused and easy to use.

### II. Layered Business Logic
Business rules MUST live in services, never in views. Views MUST limit their
responsibility to presenting information and collecting user input, delegating
decisions and operations to services. This separation keeps behavior consistent
and straightforward to maintain.

### III. Simplicity Over Complexity
Implementations MUST use the simplest design that meets the validated
requirements. The project MUST accept reasonable limitations rather than add
general-purpose abstractions, speculative capabilities, or unnecessary layers.
Complexity MUST be justified by a concrete user or operational need.

### IV. Role-Aware Experiences
The application MUST support two roles: customer (cat owner) and staff.
Features MUST make role-specific actions and information clear, and MUST prevent
users from performing actions outside their role. This supports a focused
experience while protecting booking and operational workflows.

### V. Intentional Code Comments
Code comments MUST explain why a non-obvious decision or constraint exists.
Comments MUST NOT restate what code does or how it works; implementation details
belong in the code itself. This keeps comments useful as durable context.

## Product and Architecture

CatHotel is a web application for booking rooms for cats. Product and
architecture decisions MUST preserve a minimal, user-centered booking experience
for customers and a practical workflow for staff. Business logic MUST remain in
the service layer as defined by Principle II.

## Development Workflow

Changes MUST be reviewed against the Core Principles and the product and
architecture constraints before acceptance. Reviews MUST verify that business
rules remain in services, role boundaries are enforced, and complexity is
proportionate to demonstrated value. Identified violations MUST be corrected or
explicitly resolved through a constitution amendment before acceptance.

## Governance

This constitution is the authoritative source for product and engineering
principles. Amendments MUST be proposed with their rationale, reviewed and
approved by the project maintainers, and recorded in this document. An amendment
MUST update the version and last-amended date and include a Sync Impact Report
for human review; the report MUST be removed before the amendment is committed.

Versioning follows semantic versioning: MAJOR for incompatible governance
changes, MINOR for new principles or materially expanded guidance, and PATCH for
clarifications and non-semantic wording changes. The ratification date records
original adoption and MUST remain unchanged by amendments. Until that date is
confirmed, it is recorded as a TODO.

Every change review MUST check compliance with this constitution. Proposals that
conflict with it MUST either be revised or accompanied by an approved amendment.

**Version**: 1.0.0 | **Ratified**: 2026-11-17 | **Last Amended**: 2026-11-17

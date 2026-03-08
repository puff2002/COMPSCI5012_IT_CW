# Design Issues Log

This file captures design-spec gaps identified by teacher feedback and tracks how we will resolve them in the next revision.

## Status key

- `Open`: not started
- `In Progress`: currently updating docs/diagrams
- `Resolved`: changes completed and verified in spec artifacts

## Issues

## DI-001: Authentication must gate all app services
- Date: 2026-03-05
- Status: Open
- Priority: High
- Area: Specification / User stories / Sitemap consistency
- Feedback evidence: "According to your sitemap, M1, Authentication is required to access the app services, not only to keep wardrobe data private and persistent."
- Problem: M1 currently frames authentication mainly as privacy/persistence, but does not clearly state auth as a mandatory access gate for core services.
- Impact: Requirement ambiguity can cause implementation drift (some pages/features accidentally accessible without login).
- Required changes:
  - Update M1 acceptance criteria to state all wardrobe, recommendation, and history features require authenticated access.
  - Add an explicit functional rule in the spec: unauthenticated users can access only landing/login/register pages.
  - Cross-check wording against sitemap so both documents describe the same access model.
- Done when:
  - M1 story and acceptance criteria explicitly require authentication for app service access.
  - Spec and sitemap no longer conflict on access control language.

## DI-002: Missing outfit history entity/relationship in ER model
- Date: 2026-03-05
- Status: Open
- Priority: High
- Area: ER diagram (Compressed Chen)
- Feedback evidence: "an outfitHistory entity/relationship between the user and the worn/selected outfit (ootd) generated is important."
- Problem: Current ER modeling does not clearly represent a dedicated OutfitHistory construct linking user and generated/worn outfit events.
- Impact: Data model may be incomplete for logging worn looks, dates, and replay/history features.
- Required changes:
  - Add `OUTFIT_HISTORY` entity in compressed Chen notation.
  - Model relationships between `USER`, `OUTFIT` (or generated outfit set), and `OUTFIT_HISTORY`.
  - Include core attributes (at least log date/time; optionally notes/photo reference if in scope).
  - Ensure cardinalities are explicit and aligned with user stories (S2).
- Done when:
  - ER diagram includes `OUTFIT_HISTORY` with correct relationships/cardinalities.
  - Diagram clearly supports "save generated outfit to history log" behavior.

## DI-003: Wireframes missing Logout in authenticated navigation
- Date: 2026-03-05
- Status: Open
- Priority: Medium
- Area: Wireframes / Auth UX consistency
- Feedback evidence: "Aside Wireframes_auth&settings, all other wireframes lack a Logout in the menu to confirm required authentication."
- Problem: Most authenticated-page wireframes do not show logout affordance in navigation.
- Impact: Authentication flow appears incomplete and weakens evidence for protected-session UX requirements.
- Required changes:
  - Add a visible `Logout` action in the menu/header for all authenticated screens.
  - Keep logout placement and label consistent across dashboard, closet, OOTD, history, and related pages.
  - Reflect post-logout behavior (redirect to login/landing) in flow annotations.
- Done when:
  - Every authenticated wireframe includes logout.
  - Navigation pattern is consistent and readable across all wireframe sets.

## DI-004: Backend technology naming should be explicit in architecture doc
- Date: 2026-03-05
- Status: Open
- Priority: Low
- Area: System architecture documentation
- Feedback evidence: "The use of Django for the backend could be stated."
- Problem: Architecture is clear, but backend framework identification is not explicit enough in diagram/legend text.
- Impact: Stack communication is less precise for reviewers and future contributors.
- Required changes:
  - Label backend component as `Django REST API` (or equivalent) in diagram text/legend.
  - Ensure architecture description paragraph references Django explicitly.
- Done when:
  - Architecture artifact and written description both clearly state Django backend usage.

## Summary of scoring impact

- Full marks already achieved: Overview, Architecture, Sitemap, Accessibility, Presentation.
- Improvement focus: Specification clarity (auth gating), ER completeness (outfit history), Wireframe auth consistency (logout), and explicit backend tech labeling.

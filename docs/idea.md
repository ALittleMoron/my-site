# Personal Site Concept

## Concept

Personal portfolio site with notes and an interactive competency matrix.
Demonstrates technical skills through Clean Architecture, Angular, API-first backend design, and a modern DevOps stack.

## Audience

- Potential employers and recruiters
- Colleagues and like-minded people in IT
- The author himself (as a knowledge base and notes)

## Non-goals (will not build)

- Paid features. All functionality will be free.
- Complex role/permission system. No moderator or multi-admin roles. Only authenticated users and guests. I am the only admin.
- Complex third-party integrations (CRM, ERP, etc.).
- Complex notification systems (email, SMS, etc.). A subscription to new notes, competency matrix updates, and new course releases is fine — nothing beyond that. No spam, mass mailings, or promo.
- Mobile app. The site will be responsive and mobile-friendly, but there will be no separate native app.
- Gamification. No points, levels, or achievements. Focus is on learning and skill development, not game mechanics. Progress tracking at most.
- Social features. No comments, follows, or feeds. Focus is on content and learning, not social interaction.
- Complex analytics. Basic user behavior analytics are fine — nothing beyond that.
- Content personalization. Content is the same for all users, regardless of preferences or history.

## Risks

- Content may grow uncontrollably. The site could become overloaded with content, making navigation and search harder.
- Keeping content up to date. Notes and the competency matrix require regular updates, which can be time-consuming.

## Core features

1. **Competency matrix** — interactive Q&A, topic filtering, hints, and tips
2. **Notes** — Markdown editor, folders, tags, and publish visibility
3. **Contacts** — feedback form
4. **Admin panel** — content management through the main frontend, no separate admin UI

## Highlights

- Clean Architecture and best practices
- Interactive competency matrix
- Angular SPA frontend served as an independent Docker image
- Infrastructure nginx kept as an edge reverse proxy for public routing and TLS

## Goal

Portfolio for potential employers and IT colleagues. Also, a personal knowledge base and notes for self-development.

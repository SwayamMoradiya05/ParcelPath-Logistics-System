# ParcelPath — Luxury UI Redesign

This version contains a UI-only redesign.

## Visual changes
- Luxury logistics palette: deep forest green, champagne gold, warm ivory, cream, charcoal
- Redesigned public navigation and utility bar
- New visual treatment for cards, KPI/stat blocks, tables, forms, buttons and status badges
- Premium customer and driver workspace sidebars
- Premium operations/admin dashboard styling
- Updated authentication/profile surfaces
- Refined landing/hero, tracking, pricing and content sections
- Responsive mobile refinements
- Manrope typography for a more premium product feel

## Functionality preservation
No Django views, models, migrations, URLs, services, API logic, JavaScript workflows, database logic, or business rules were intentionally changed for this redesign.

The visual layer is primarily isolated in:
`static/css/luxury-theme.css`

It is loaded after the existing CSS so the original styles remain available as a fallback.

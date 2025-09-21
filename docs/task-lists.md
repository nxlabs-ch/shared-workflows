# Task Lists

This file tests and demonstrates that lists with checkboxes (task lists) and regular bullets can be used in
Markdown files and be nested correctly without losing their formatting.

## Regular Nested Bullets

- Level 1 regular bullet
  - Level 2 regular bullet
    - Level 3 regular bullet
    - Another level 3 item
  - Another level 2 item
- Back to level 1

## Task Lists with Nesting

- [ ] Level 1 task item
  - [ ] Level 2 task item
    - [ ] Level 3 task item
    - [x] Level 3 checked item
  - [x] Level 2 checked item
- [x] Level 1 checked item

## Mixed Regular and Task Lists

- Regular bullet level 1
  - [ ] Task item at level 2
    - Regular bullet at level 3
    - [x] Task item at level 3
  - Regular bullet at level 2
- [ ] Task item at level 1
  - Regular bullet at level 2
    - [ ] Task item at level 3

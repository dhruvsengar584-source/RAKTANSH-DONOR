# RaktSetu | Intelligent Blood Donor Network (RAKTANSH DONOR)

> **"Every drop counts. Find a donor in seconds."**

RaktSetu is a modern, production-grade Blood Donor Finder and emergency healthcare dispatch web application built with Python Flask, SQLite, Tailwind CSS, Alpine.js, and Leaflet OpenStreetMap. Designed with startup-level UX/UI aesthetics (Airbnb meets sleek healthtech), RaktSetu eliminates panic during medical emergencies with real-time donor matching, biological 90-day donation safety tracking, masked phone privacy, and an interactive 8×8 blood compatibility matrix.

---

## ⚡ Quick Start (Run with One Command)

To run the application immediately:
```bash
python app.py
```
Or double-click `run.bat`.

Visit in your browser: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### 🔑 Pre-Configured Demo Accounts (1-Click Login available on `/login`)
- **SuperAdmin**: `admin@raktsetu.org` / `admin123`
- **Donor (O+)**: `donor@raktsetu.org` / `donor123`
- **Seeker**: `seeker@raktsetu.org` / `seeker123`

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.12, Flask, Flask-SQLAlchemy (ORM), Flask-Login (session auth), Werkzeug password hashing.
- **Database**: SQLite (`instance/bloodbank.db` auto-created and pre-seeded on startup).
- **Frontend**: Jinja2 templates, Tailwind CSS via CDN with customized design tokens.
- **Dynamic Interactions**: Alpine.js via CDN for reactive filters, modals, wizard steps, and live card preview.
- **Mapping**: Leaflet + OpenStreetMap CartoDB Tiles (free, zero API key required) with custom markers.
- **Charts & Visuals**: Chart.js for Admin KPI analytics, Lucide SVG icons, Canvas Confetti.
- **Typography**: Google Fonts ("Plus Jakarta Sans" for crisp modern headings & "Inter" for clean body text).

---

## 🎨 Design System & Color Tokens

- **Primary Crimson**: `#E11D48`, Hover: `#BE123C`, Pressed: `#9F1239`, Tint: `#FFF1F2`, Soft: `#FFE4E6`
- **Navy Dark Surfaces**: `#0F172A` (Hero, Footer, Dark Surfaces), Slate Text: `#334155`, Muted: `#64748B`
- **Success/Available Teal**: `#14B8A6` (Pulsing live badge dot)
- **Warning Amber**: `#F59E0B`, Critical Red: `#DC2626`, Info Blue: `#2563EB`
- **Surface**: Light mode `#F8FAFC`, Dark mode `#0B1220` with instant toggle & local persistence.
- **Card Aesthetics**: `rounded-3xl`, 1px borders with subtle shadow, translateY hover lift (`-2px`).

---

## 🌟 Key Product Features

### 1. Landing Page (`/`)
- Hero section with diagonal navy-maroon gradient, glowing ambient light, and floating glassmorphism search card.
- Live animated counters: Verified donors, lives impacted, cities covered, & average response time.
- 3-step icon guide ("How it works") and "Why RaktSetu" medical trust grid.
- Interactive blood group cross-match preview and active hospital emergency alerts.

### 2. Search & Leaflet OpenStreetMap (`/search`)
- Sticky filter bar: Blood group pills, city selector, GPS location fetcher, 1-50 km radius slider, "Available only" filter, and "Include compatible" toggle.
- Dual-view split layout: Interactive donor list on the left, synchronized Leaflet OpenStreetMap on the right.
- Mobile list/map toggle button.
- Synchronized hover: hovering a donor card highlights its map marker and vice versa.
- Masked phone privacy protecting voluntary donors from spam.

### 3. Emergency Request Wizard (`/request/new`)
- 3-step guided wizard with visual progress bar:
  - Step 1: Patient details & unit requirements.
  - Step 2: Location & 3 Urgency Cards (Normal, Urgent, Critical).
  - Step 3: Review & Instant Broadcast preview.
- Success banner with animated checkmark and donor alert dispatch.

### 4. Live Request Tracker (`/request/<id>`)
- 3-state lifecycle stepper: **Open ➔ Accepted ➔ Fulfilled**.
- Real-time responding donors list with timestamps and messages.
- Privacy-protected attendant contact unveiled once a donor commits.
- Celebratory confetti trigger upon fulfillment.

### 5. Donor Dashboard (`/dashboard/donor`)
- Big instant availability switch with AJAX live updates.
- **90-Day Biological Countdown Progress Ring**: tracks safe donation interval before red blood cells regenerate.
- Incoming hospital emergency alerts with 1-click Accept.
- Verified donation history timeline and "Lives Impacted" multiplier (`donations * 3`).
- Honor badges: First Drop, Hero 5+, Lifesaver 10+.

### 6. Seeker Dashboard (`/dashboard/seeker`)
- Tracker for posted blood requests with colored status chips and response counts.

### 7. Interactive 8×8 Compatibility Matrix (`/compatibility`)
- Complete clinical cross-match grid.
- Select any blood group to visually highlight compatible donors and recipients.
- Deep-dive cards on Type O- (Universal Donor) and Type AB+ (Universal Recipient).

### 8. Admin Control Center (`/admin`)
- 4 KPI cards with trend indicators.
- 3 Chart.js graphs:
  - Doughnut: Donors inventory across all 8 blood groups.
  - Bar: Emergency requests pipeline by status.
  - Line: Volunteer signups trajectory.
- Searchable management tables to verify donors, toggle availability, and resolve cases.

### 9. Auth Pages with Live Preview (`/login`, `/signup`)
- Split-screen design with animated **RAKTANSH DONOR** panel.
- **Real-Time Live Donor Card**: As you type your name, blood group, and city on the signup form, your digital donor pass updates on the left in real time!
- 1-Click quick login buttons for instant demo testing.

---

## 📂 Project Directory Structure

```text
blood donor/
├── app.py                  # Main Flask application & database models
├── seed_data.py            # High-fidelity realistic Indian city seed data
├── requirements.txt        # Python dependency manifest
├── run.bat                 # One-click Windows launch script
├── README.md               # Product documentation
├── static/
│   ├── css/
│   │   └── style.css       # Custom CSS tokens, animations, Leaflet styles
│   └── js/
│       └── main.js         # Theme toggle, toast alerts, geo & counter helpers
└── templates/
    ├── base.html           # Sticky glass navbar, footer, emergency button
    ├── index.html          # Landing page with hero & counters
    ├── search.html         # Donors list + synchronized Leaflet map
    ├── donor_profile.html  # Public profile, timeline, badges
    ├── request_new.html    # 3-step emergency request wizard
    ├── request_detail.html # Request stepper & response coordination
    ├── dashboard_donor.html# Donor dashboard & 90-day progress ring
    ├── dashboard_seeker.html # Seeker requests tracker
    ├── compatibility.html  # 8x8 interactive compatibility matrix
    ├── notifications.html  # Notification center
    ├── admin.html          # Admin dashboard with Chart.js charts
    ├── about.html          # 90-day safety guidelines & FAQ
    ├── 404.html            # Custom animated 404 error page
    └── auth/
        ├── login.html      # Split-screen login with 1-click demos
        └── signup.html     # Split-screen signup with real-time live preview
```

---
*Built with ❤️ for voluntary blood donation and civic health safety.*

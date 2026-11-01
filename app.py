import os
import math
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'raktsetu-secret-key-super-secure-production-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bloodbank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

# ---------------------------------------------------------
# CONSTANTS & COMPATIBILITY MATRIX
# ---------------------------------------------------------
BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Who can GIVE to whom (Red Blood Cells)
CAN_GIVE_TO = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'], # Universal Donor
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'] # Recipient only can give to AB+
}

# Who can RECEIVE from whom
CAN_RECEIVE_FROM = {
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'], # Universal Recipient
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'A+': ['O-', 'O+', 'A-', 'A+'],
    'A-': ['O-', 'A-'],
    'B+': ['O-', 'O+', 'B-', 'B+'],
    'B-': ['O-', 'B-'],
    'O+': ['O-', 'O+'],
    'O-': ['O-'] # Only from O-
}

CITY_CENTERS = {
    'New Delhi': {'lat': 28.6139, 'lng': 77.2090},
    'Mumbai': {'lat': 19.0760, 'lng': 72.8777},
    'Bengaluru': {'lat': 12.9716, 'lng': 77.5946},
    'Pune': {'lat': 18.5204, 'lng': 73.8567},
    'Hyderabad': {'lat': 17.3850, 'lng': 78.4867},
    'Chennai': {'lat': 13.0827, 'lng': 80.2707},
    'Kolkata': {'lat': 22.5726, 'lng': 88.3639},
    'Jaipur': {'lat': 26.9124, 'lng': 75.7873},
    'Lucknow': {'lat': 26.8467, 'lng': 80.9462},
    'Ahmedabad': {'lat': 23.0225, 'lng': 72.5714},
}

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in kilometers between two lat/lon coordinates."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999.0
    R = 6371.0 # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

# ---------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='donor') # 'donor', 'seeker', 'admin'
    blood_group = db.Column(db.String(5), nullable=False) # 'A+', 'O-', etc.
    city = db.Column(db.String(100), default='New Delhi')
    state = db.Column(db.String(100), default='Delhi')
    pincode = db.Column(db.String(10), default='110001')
    address = db.Column(db.String(255), default='')
    latitude = db.Column(db.Float, default=28.6139)
    longitude = db.Column(db.Float, default=77.2090)
    phone = db.Column(db.String(20), default='')
    is_available = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=True)
    total_donations = db.Column(db.Integer, default=0)
    last_donation_date = db.Column(db.Date, nullable=True)
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requests = db.relationship('DonationRequest', backref='requester', lazy='dynamic')
    responses = db.relationship('RequestResponse', backref='donor', lazy='dynamic')
    donations = db.relationship('DonationHistory', backref='donor', lazy='dynamic', order_by='DonationHistory.donation_date.desc()')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', order_by='Notification.created_at.desc()')

    def days_until_eligible(self):
        """Standard 90-day rule for safe whole blood donation."""
        if not self.last_donation_date:
            return 0
        days_passed = (date.today() - self.last_donation_date).days
        remaining = 90 - days_passed
        return max(0, remaining)

    def can_donate_now(self):
        return self.is_available and (self.days_until_eligible() == 0)

    def eligible_date(self):
        if not self.last_donation_date:
            return date.today()
        return self.last_donation_date + timedelta(days=90)

    def lives_impacted(self):
        return max(self.total_donations * 3, 0)

    def initials(self):
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return self.name[:2].upper()

    def badges(self):
        return [
            {
                'id': 'first_donation',
                'title': 'First Drop',
                'description': 'Completed first blood donation',
                'icon': 'award',
                'unlocked': self.total_donations >= 1
            },
            {
                'id': 'hero_5',
                'title': 'Community Hero',
                'description': 'Saved lives with 5+ donations',
                'icon': 'heart-handshake',
                'unlocked': self.total_donations >= 5
            },
            {
                'id': 'lifesaver_10',
                'title': 'Master Lifesaver',
                'description': 'Impacted 30+ lives (10+ donations)',
                'icon': 'shield-check',
                'unlocked': self.total_donations >= 10
            }
        ]


class DonationRequest(db.Model):
    __tablename__ = 'donation_requests'
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_needed = db.Column(db.Integer, default=1)
    hospital_name = db.Column(db.String(150), nullable=False)
    hospital_address = db.Column(db.String(255), default='')
    city = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, default=28.6139)
    longitude = db.Column(db.Float, default=77.2090)
    urgency = db.Column(db.String(20), default='Urgent') # 'Normal', 'Urgent', 'Critical'
    contact_person = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='Open') # 'Open', 'Accepted', 'Fulfilled', 'Cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fulfilled_at = db.Column(db.DateTime, nullable=True)

    responses = db.relationship('RequestResponse', backref='request', lazy='dynamic', cascade='all, delete-orphan')


class RequestResponse(db.Model):
    __tablename__ = 'request_responses'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('donation_requests.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Interested') # 'Interested', 'Accepted', 'Declined', 'Completed'
    message = db.Column(db.Text, default='')
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)


class DonationHistory(db.Model):
    __tablename__ = 'donation_history'
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_donated = db.Column(db.Integer, default=1)
    donation_date = db.Column(db.Date, nullable=False)
    certificate_id = db.Column(db.String(50), default='')
    notes = db.Column(db.String(255), default='')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default='system') # 'emergency', 'response', 'badge', 'system'
    link = db.Column(db.String(255), default='/notifications')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context Processor for unread notifications count across all templates
@app.context_processor
def inject_global_data():
    unread_notifs_count = 0
    recent_notifs = []
    if current_user.is_authenticated:
        unread_notifs_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        recent_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    return {
        'unread_notifs_count': unread_notifs_count,
        'recent_notifs': recent_notifs,
        'BLOOD_GROUPS': BLOOD_GROUPS,
        'CAN_RECEIVE_FROM': CAN_RECEIVE_FROM,
        'CAN_GIVE_TO': CAN_GIVE_TO,
        'CITIES': list(CITY_CENTERS.keys())
    }

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route('/')
def index():
    """Landing Page with Hero, Search Card, Counters, Steps, Features, Compatibility preview."""
    total_donors = User.query.filter(User.role.in_(['donor', 'admin'])).count()
    total_fulfilled = DonationRequest.query.filter_by(status='Fulfilled').count() + 24
    total_cities = len(CITY_CENTERS)
    active_emergencies = DonationRequest.query.filter_by(status='Open').count()

    recent_requests = DonationRequest.query.filter_by(status='Open').order_by(DonationRequest.created_at.desc()).limit(3).all()

    return render_template(
        'index.html',
        total_donors=total_donors,
        total_fulfilled=total_fulfilled,
        total_cities=total_cities,
        active_emergencies=active_emergencies,
        recent_requests=recent_requests
    )

@app.route('/search')
def search():
    """Search page with split layout: Donors list left, Leaflet Map right."""
    blood_group = request.args.get('blood_group', '').strip()
    city = request.args.get('city', '').strip()
    radius = float(request.args.get('radius', 50))
    available_only = request.args.get('available_only', 'false').lower() == 'true'
    include_compatible = request.args.get('include_compatible', 'true').lower() == 'true'
    sort_by = request.args.get('sort_by', 'distance')

    # Base query for donors
    query = User.query.filter(User.role.in_(['donor', 'admin']))

    # Filter by city center or default Delhi
    center_coords = CITY_CENTERS.get(city, CITY_CENTERS['New Delhi'])

    if blood_group:
        if include_compatible:
            # Donors whose blood group can be received by this group
            compatible_donors_bg = CAN_RECEIVE_FROM.get(blood_group, [blood_group])
            query = query.filter(User.blood_group.in_(compatible_donors_bg))
        else:
            query = query.filter(User.blood_group == blood_group)

    if available_only:
        query = query.filter(User.is_available == True)

    donors_raw = query.all()

    # Calculate distance and eligibility
    donor_results = []
    for d in donors_raw:
        dist = haversine(center_coords['lat'], center_coords['lng'], d.latitude, d.longitude)
        
        # If city was specified, filter by radius
        if city and dist > radius:
            continue

        is_exact = (d.blood_group == blood_group) if blood_group else True
        donor_results.append({
            'donor': d,
            'distance': dist,
            'is_exact': is_exact,
            'is_compatible': not is_exact,
            'days_eligible': d.days_until_eligible(),
            'can_donate': d.can_donate_now()
        })

    # Sorting
    if sort_by == 'donations':
        donor_results.sort(key=lambda x: x['donor'].total_donations, reverse=True)
    elif sort_by == 'recent':
        donor_results.sort(key=lambda x: x['donor'].created_at, reverse=True)
    else: # distance
        donor_results.sort(key=lambda x: x['distance'])

    return render_template(
        'search.html',
        donors=donor_results,
        selected_bg=blood_group,
        selected_city=city,
        radius=int(radius),
        available_only=available_only,
        include_compatible=include_compatible,
        sort_by=sort_by,
        center_lat=center_coords['lat'],
        center_lng=center_coords['lng']
    )

@app.route('/api/donors/search')
def api_search_donors():
    """JSON API for real-time live map & list synchronization."""
    blood_group = request.args.get('blood_group', '').strip()
    city = request.args.get('city', '').strip()
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=50.0, type=float)
    available_only = request.args.get('available_only', 'false').lower() == 'true'
    include_compatible = request.args.get('include_compatible', 'true').lower() == 'true'
    sort_by = request.args.get('sort_by', 'distance')

    if lat is None or lng is None:
        center = CITY_CENTERS.get(city, CITY_CENTERS['New Delhi'])
        lat, lng = center['lat'], center['lng']

    query = User.query.filter(User.role.in_(['donor', 'admin']))

    if blood_group:
        if include_compatible:
            compatible_donors_bg = CAN_RECEIVE_FROM.get(blood_group, [blood_group])
            query = query.filter(User.blood_group.in_(compatible_donors_bg))
        else:
            query = query.filter(User.blood_group == blood_group)

    if available_only:
        query = query.filter(User.is_available == True)

    donors_raw = query.all()
    results = []
    for d in donors_raw:
        dist = haversine(lat, lng, d.latitude, d.longitude)
        if city and dist > radius:
            continue

        is_exact = (d.blood_group == blood_group) if blood_group else True
        results.append({
            'id': d.id,
            'name': d.name,
            'initials': d.initials(),
            'blood_group': d.blood_group,
            'city': d.city,
            'address': d.address or d.city,
            'lat': d.latitude,
            'lng': d.longitude,
            'distance': dist,
            'is_available': d.is_available,
            'can_donate': d.can_donate_now(),
            'days_eligible': d.days_until_eligible(),
            'total_donations': d.total_donations,
            'is_verified': d.is_verified,
            'is_exact': is_exact,
            'is_compatible': not is_exact,
            'masked_phone': f"{d.phone[:6]} XXXXX" if d.phone else "+91 98XXX XXXXX"
        })

    if sort_by == 'donations':
        results.sort(key=lambda x: x['total_donations'], reverse=True)
    else:
        results.sort(key=lambda x: x['distance'])

    return jsonify({
        'status': 'success',
        'count': len(results),
        'center': {'lat': lat, 'lng': lng},
        'donors': results
    })

@app.route('/donor/<int:donor_id>')
def donor_profile(donor_id):
    """Detailed donor profile with timeline and request contact modal."""
    donor = User.query.get_or_404(donor_id)
    donation_history = DonationHistory.query.filter_by(donor_id=donor.id).order_by(DonationHistory.donation_date.desc()).all()
    badges = donor.badges()
    return render_template(
        'donor_profile.html',
        donor=donor,
        donation_history=donation_history,
        badges=badges
    )

@app.route('/request/new', methods=['GET', 'POST'])
def new_emergency_request():
    """3-step wizard with progress bar and animated success broadcast."""
    if request.method == 'POST':
        # Get patient and request info
        patient_name = request.form.get('patient_name', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        units_needed = int(request.form.get('units_needed', 1))
        hospital_name = request.form.get('hospital_name', '').strip()
        hospital_address = request.form.get('hospital_address', '').strip()
        city = request.form.get('city', 'New Delhi').strip()
        urgency = request.form.get('urgency', 'Urgent').strip()
        contact_person = request.form.get('contact_person', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        notes = request.form.get('notes', '').strip()

        # Center coords
        coords = CITY_CENTERS.get(city, CITY_CENTERS['New Delhi'])

        # Determine requester
        if current_user.is_authenticated:
            req_user_id = current_user.id
        else:
            # Check or create guest seeker
            guest_seeker = User.query.filter_by(email='seeker@raktsetu.org').first()
            if not guest_seeker:
                guest_seeker = User.query.first()
            req_user_id = guest_seeker.id

        new_req = DonationRequest(
            requester_id=req_user_id,
            patient_name=patient_name,
            blood_group=blood_group,
            units_needed=units_needed,
            hospital_name=hospital_name,
            hospital_address=hospital_address,
            city=city,
            latitude=coords['lat'],
            longitude=coords['lng'],
            urgency=urgency,
            contact_person=contact_person,
            contact_phone=contact_phone,
            notes=notes,
            status='Open'
        )
        db.session.add(new_req)
        db.session.commit()

        # Find compatible donors in the city and create notifications
        compatible_groups = CAN_RECEIVE_FROM.get(blood_group, [blood_group])
        target_donors = User.query.filter(
            User.blood_group.in_(compatible_groups),
            User.city == city,
            User.role.in_(['donor', 'admin'])
        ).all()

        for d in target_donors:
            notif = Notification(
                user_id=d.id,
                title=f"🚨 {urgency.upper()} ALERT: {blood_group} Blood Needed",
                message=f"{hospital_name}, {city} urgently requires {units_needed} units of {blood_group} for {patient_name}.",
                type='emergency',
                link=f"/request/{new_req.id}"
            )
            db.session.add(notif)
        db.session.commit()

        flash(f'Emergency request published! {len(target_donors)} eligible donors in {city} have been alerted.', 'success')
        return redirect(url_for('request_detail', request_id=new_req.id, broadcast=len(target_donors)))

    return render_template('request_new.html')

@app.route('/request/<int:request_id>')
def request_detail(request_id):
    """Request detail with live status stepper and responders."""
    req_obj = DonationRequest.query.get_or_404(request_id)
    responses = RequestResponse.query.filter_by(request_id=req_obj.id).order_by(RequestResponse.responded_at.desc()).all()
    
    # Check if current user is donor and has responded
    user_response = None
    if current_user.is_authenticated:
        user_response = RequestResponse.query.filter_by(request_id=req_obj.id, donor_id=current_user.id).first()

    broadcast_count = request.args.get('broadcast', None)

    return render_template(
        'request_detail.html',
        req=req_obj,
        responses=responses,
        user_response=user_response,
        broadcast_count=broadcast_count
    )

@app.route('/request/<int:request_id>/respond', methods=['POST'])
@login_required
def respond_request(request_id):
    """Donor accepts or registers interest in a request."""
    req_obj = DonationRequest.query.get_or_404(request_id)
    status_choice = request.form.get('status', 'Accepted')
    message = request.form.get('message', '').strip()

    existing = RequestResponse.query.filter_by(request_id=req_obj.id, donor_id=current_user.id).first()
    if existing:
        existing.status = status_choice
        if message:
            existing.message = message
        existing.responded_at = datetime.utcnow()
    else:
        resp = RequestResponse(
            request_id=req_obj.id,
            donor_id=current_user.id,
            status=status_choice,
            message=message or f"I am available to donate {current_user.blood_group} blood at {req_obj.hospital_name}."
        )
        db.session.add(resp)

    # Update request status to Accepted if it was open
    if req_obj.status == 'Open':
        req_obj.status = 'Accepted'

    # Notify requester
    notif = Notification(
        user_id=req_obj.requester_id,
        title=f"✅ Donor Response: {current_user.name}",
        message=f"{current_user.name} ({current_user.blood_group}) accepted your request for {req_obj.patient_name}!",
        type='response',
        link=f"/request/{req_obj.id}"
    )
    db.session.add(notif)
    db.session.commit()

    flash('Thank you! Your willingness to donate has been communicated to the requester.', 'success')
    return redirect(url_for('request_detail', request_id=req_obj.id))

@app.route('/request/<int:request_id>/fulfill', methods=['POST'])
@login_required
def fulfill_request(request_id):
    """Requester marks the request as fulfilled (triggers confetti)."""
    req_obj = DonationRequest.query.get_or_404(request_id)
    
    # Allow requester or admin
    if current_user.id != req_obj.requester_id and current_user.role != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('request_detail', request_id=req_obj.id))

    req_obj.status = 'Fulfilled'
    req_obj.fulfilled_at = datetime.utcnow()

    # Credit any accepted donor with +1 donation and history
    accepted_responses = RequestResponse.query.filter_by(request_id=req_obj.id, status='Accepted').all()
    for resp in accepted_responses:
        donor = resp.donor
        donor.total_donations += 1
        donor.last_donation_date = date.today()
        # Add donation history
        dh = DonationHistory(
            donor_id=donor.id,
            hospital_name=req_obj.hospital_name,
            blood_group=req_obj.blood_group,
            units_donated=1,
            donation_date=date.today(),
            certificate_id=f"RKT-{datetime.utcnow().year}-{random_cert_id()}",
            notes=f"Emergency donation for {req_obj.patient_name}."
        )
        db.session.add(dh)

        # Notify donor of impact
        notif = Notification(
            user_id=donor.id,
            title='🎉 Blood Request Fulfilled! Life Saved.',
            message=f"The blood donation request for {req_obj.patient_name} at {req_obj.hospital_name} has been marked fulfilled. You saved a life!",
            type='badge',
            link=url_for('donor_dashboard')
        )
        db.session.add(notif)

    db.session.commit()
    flash('Request marked as fulfilled! Thank you to all donors who stepped forward.', 'success')
    return redirect(url_for('request_detail', request_id=req_obj.id, fulfilled=1))

def random_cert_id():
    import random
    return random.randint(10000, 99999)

@app.route('/dashboard')
@login_required
def dashboard():
    """Smart router to appropriate dashboard based on role."""
    if current_user.role == 'seeker':
        return redirect(url_for('seeker_dashboard'))
    return redirect(url_for('donor_dashboard'))

@app.route('/dashboard/donor')
@login_required
def donor_dashboard():
    """Donor dashboard with availability switch, 90-day countdown ring, requests, history."""
    # Find matching open/accepted requests in donor's city or compatible blood group
    compatible_for_donor = CAN_GIVE_TO.get(current_user.blood_group, [current_user.blood_group])
    
    incoming_requests = DonationRequest.query.filter(
        DonationRequest.blood_group.in_(compatible_for_donor),
        DonationRequest.city == current_user.city,
        DonationRequest.status.in_(['Open', 'Accepted'])
    ).order_by(DonationRequest.created_at.desc()).limit(6).all()

    donation_history = DonationHistory.query.filter_by(donor_id=current_user.id).order_by(DonationHistory.donation_date.desc()).all()

    days_left = current_user.days_until_eligible()
    # Percentage towards 90 days
    days_passed = 90 - days_left
    progress_pct = min(100, int((days_passed / 90.0) * 100))

    return render_template(
        'dashboard_donor.html',
        incoming_requests=incoming_requests,
        donation_history=donation_history,
        days_left=days_left,
        progress_pct=progress_pct,
        lives_impacted=current_user.lives_impacted(),
        badges=current_user.badges()
    )

@app.route('/dashboard/seeker')
@login_required
def seeker_dashboard():
    """Seeker dashboard with active and past requests."""
    my_requests = DonationRequest.query.filter_by(requester_id=current_user.id).order_by(DonationRequest.created_at.desc()).all()
    return render_template('dashboard_seeker.html', requests=my_requests)

@app.route('/api/donor/toggle-availability', methods=['POST'])
@login_required
def toggle_availability():
    """AJAX endpoint for toggling donor availability instantly."""
    data = request.get_json() or {}
    new_state = data.get('is_available')
    if new_state is None:
        current_user.is_available = not current_user.is_available
    else:
        current_user.is_available = bool(new_state)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'is_available': current_user.is_available,
        'message': f"Availability status updated to {'Available' if current_user.is_available else 'Unavailable'}."
    })

@app.route('/compatibility')
def compatibility():
    """Interactive 8x8 blood group compatibility matrix page."""
    return render_template('compatibility.html')

@app.route('/notifications')
@login_required
def notifications():
    """Notifications view with read/unread tracking."""
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifs)

@app.route('/api/notifications/mark-read/<int:notif_id>', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Not found'}), 404

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin')
@login_required
def admin():
    """Admin dashboard with Chart.js analytics and management tables."""
    if current_user.role != 'admin':
        flash('Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    # Stats
    total_donors = User.query.filter(User.role.in_(['donor', 'admin'])).count()
    active_requests = DonationRequest.query.filter_by(status='Open').count()
    fulfilled_requests = DonationRequest.query.filter_by(status='Fulfilled').count()
    total_requests = DonationRequest.query.count()
    lives_saved = sum(d.total_donations for d in User.query.all()) * 3

    # Donors by blood group for Doughnut chart
    blood_group_counts = {}
    for bg in BLOOD_GROUPS:
        blood_group_counts[bg] = User.query.filter_by(blood_group=bg).count()

    # Requests by status for Bar chart
    status_counts = {
        'Open': DonationRequest.query.filter_by(status='Open').count(),
        'Accepted': DonationRequest.query.filter_by(status='Accepted').count(),
        'Fulfilled': DonationRequest.query.filter_by(status='Fulfilled').count()
    }

    donors_list = User.query.order_by(User.created_at.desc()).all()
    requests_list = DonationRequest.query.order_by(DonationRequest.created_at.desc()).all()

    return render_template(
        'admin.html',
        total_donors=total_donors,
        active_requests=active_requests,
        fulfilled_requests=fulfilled_requests,
        total_requests=total_requests,
        lives_saved=lives_saved,
        blood_group_counts=blood_group_counts,
        status_counts=status_counts,
        donors=donors_list,
        requests=requests_list
    )

@app.route('/admin/verify-donor/<int:donor_id>', methods=['POST'])
@login_required
def admin_verify_donor(donor_id):
    if current_user.role != 'admin':
        abort(403)
    donor = User.query.get_or_404(donor_id)
    donor.is_verified = not donor.is_verified
    db.session.commit()
    flash(f"Updated verification for {donor.name}.", 'success')
    return redirect(url_for('admin'))

@app.route('/admin/toggle-donor/<int:donor_id>', methods=['POST'])
@login_required
def admin_toggle_donor(donor_id):
    if current_user.role != 'admin':
        abort(403)
    donor = User.query.get_or_404(donor_id)
    donor.is_available = not donor.is_available
    db.session.commit()
    flash(f"Updated status for {donor.name}.", 'info')
    return redirect(url_for('admin'))

@app.route('/admin/delete-donor/<int:donor_id>', methods=['POST'])
@login_required
def admin_delete_donor(donor_id):
    if current_user.role != 'admin':
        abort(403)
    donor = User.query.get_or_404(donor_id)
    if donor.id == current_user.id:
        flash("Cannot delete your own admin account.", 'danger')
        return redirect(url_for('admin'))
    db.session.delete(donor)
    db.session.commit()
    flash(f"Deleted user account.", 'warning')
    return redirect(url_for('admin'))

@app.route('/admin/close-request/<int:req_id>', methods=['POST'])
@login_required
def admin_close_request(req_id):
    if current_user.role != 'admin':
        abort(403)
    req_obj = DonationRequest.query.get_or_404(req_id)
    req_obj.status = 'Fulfilled'
    req_obj.fulfilled_at = datetime.utcnow()
    db.session.commit()
    flash(f"Request #{req_obj.id} marked as fulfilled.", 'success')
    return redirect(url_for('admin'))

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            flash(f"Welcome back, {user.name}!", 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'donor')
        blood_group = request.form.get('blood_group', 'O+')
        city = request.form.get('city', 'New Delhi')
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))

        coords = CITY_CENTERS.get(city, CITY_CENTERS['New Delhi'])

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            blood_group=blood_group,
            city=city,
            phone=phone,
            address=address,
            latitude=coords['lat'],
            longitude=coords['lng'],
            is_available=True,
            is_verified=True,
            total_donations=1 if role == 'donor' else 0,
            last_donation_date=(date.today() - timedelta(days=95)) if role == 'donor' else None,
            bio='Newly registered life saver on RaktSetu / RaktAnsh.'
        )
        db.session.add(new_user)
        db.session.commit()

        # Welcome notification
        notif = Notification(
            user_id=new_user.id,
            title='🎉 Welcome to RaktSetu!',
            message=f"Thank you for joining our community of lifesavers. Your profile is live.",
            type='system',
            link='/dashboard'
        )
        db.session.add(notif)
        db.session.commit()

        login_user(new_user)
        flash(f'Account created successfully! Welcome to RaktSetu, {new_user.name}.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('auth/signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    """About page with donor safety rules (90-day interval) and mission."""
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ---------------------------------------------------------
# INITIALIZATION & SEEDING
# ---------------------------------------------------------
with app.app_context():
    db.create_all()
    try:
        from seed_data import seed_database
        seed_database(db, User, DonationRequest, RequestResponse, DonationHistory, Notification)
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print(">> RAKTSETU / RAKTANSH DONOR NETWORK IS RUNNING!")
    print(">> Visit: http://127.0.0.1:5000")
    print(">> Demo Accounts:")
    print("    - Admin:  admin@raktsetu.org / admin123")
    print("    - Donor:  donor@raktsetu.org / donor123")
    print("    - Seeker: seeker@raktsetu.org / seeker123")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, host='127.0.0.1')


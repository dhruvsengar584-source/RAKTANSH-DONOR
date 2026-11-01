"""
Seed data generator for RaktSetu / RaktAnsh Blood Donor Network.
Populates realistic Indian cities, donors with exact lat/long for Leaflet map,
donation history, emergency requests, responses, and notifications.
"""
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

# Major Indian cities with center coordinates
CITY_COORDINATES = {
    'New Delhi': {'lat': 28.6139, 'lng': 77.2090, 'state': 'Delhi'},
    'Mumbai': {'lat': 19.0760, 'lng': 72.8777, 'state': 'Maharashtra'},
    'Bengaluru': {'lat': 12.9716, 'lng': 77.5946, 'state': 'Karnataka'},
    'Pune': {'lat': 18.5204, 'lng': 73.8567, 'state': 'Maharashtra'},
    'Hyderabad': {'lat': 17.3850, 'lng': 78.4867, 'state': 'Telangana'},
    'Chennai': {'lat': 13.0827, 'lng': 80.2707, 'state': 'Tamil Nadu'},
    'Kolkata': {'lat': 22.5726, 'lng': 88.3639, 'state': 'West Bengal'},
    'Jaipur': {'lat': 26.9124, 'lng': 75.7873, 'state': 'Rajasthan'},
    'Lucknow': {'lat': 26.8467, 'lng': 80.9462, 'state': 'Uttar Pradesh'},
    'Ahmedabad': {'lat': 23.0225, 'lng': 72.5714, 'state': 'Gujarat'},
}

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

DONORS_DATA = [
    {
        'name': 'Rahul Sharma',
        'email': 'donor@raktsetu.org',
        'blood_group': 'O+',
        'city': 'New Delhi',
        'phone': '+91 98112 34567',
        'is_available': True,
        'is_verified': True,
        'total_donations': 8,
        'last_donation_days_ago': 105, # eligible (>90 days)
        'bio': 'Regular platelet & whole blood donor. Committed to helping accident victims and thalassemia children.',
        'lat_offset': 0.015,
        'lng_offset': -0.012,
        'address': 'Connaught Place, Central Delhi'
    },
    {
        'name': 'Pooja Verma',
        'email': 'pooja.verma@example.com',
        'blood_group': 'O-',
        'city': 'New Delhi',
        'phone': '+91 98734 56789',
        'is_available': True,
        'is_verified': True,
        'total_donations': 12,
        'last_donation_days_ago': 120,
        'bio': 'Universal donor (O-). Available for urgent surgeries and neonates across NCR.',
        'lat_offset': -0.022,
        'lng_offset': 0.018,
        'address': 'South Extension II, New Delhi'
    },
    {
        'name': 'Amitabh Roy',
        'email': 'amitabh.roy@example.com',
        'blood_group': 'A+',
        'city': 'New Delhi',
        'phone': '+91 98101 22334',
        'is_available': False,
        'is_verified': True,
        'total_donations': 4,
        'last_donation_days_ago': 35, # ineligible (<90 days)
        'bio': 'Software engineer & voluntary blood donor since college days.',
        'lat_offset': 0.035,
        'lng_offset': 0.025,
        'address': 'Rohini Sector 14, Delhi'
    },
    {
        'name': 'Kavita Nair',
        'email': 'kavita.nair@example.com',
        'blood_group': 'B+',
        'city': 'Mumbai',
        'phone': '+91 98200 44556',
        'is_available': True,
        'is_verified': True,
        'total_donations': 6,
        'last_donation_days_ago': 95,
        'bio': 'Ready to donate in Andheri / Bandra region for genuine emergencies.',
        'lat_offset': 0.018,
        'lng_offset': -0.015,
        'address': 'Bandra West, Mumbai'
    },
    {
        'name': 'Vikramaditya Rao',
        'email': 'vikram.rao@example.com',
        'blood_group': 'AB+',
        'city': 'Mumbai',
        'phone': '+91 98331 66778',
        'is_available': True,
        'is_verified': True,
        'total_donations': 11,
        'last_donation_days_ago': 110,
        'bio': 'Plasma and whole blood donor. Always ready to answer emergency alerts.',
        'lat_offset': -0.025,
        'lng_offset': 0.020,
        'address': 'Powai, Mumbai'
    },
    {
        'name': 'Ananya Deshmukh',
        'email': 'ananya.d@example.com',
        'blood_group': 'A-',
        'city': 'Pune',
        'phone': '+91 98501 88990',
        'is_available': True,
        'is_verified': True,
        'total_donations': 5,
        'last_donation_days_ago': 100,
        'bio': 'Rare negative blood donor. Proud to support local blood banks & ICUs.',
        'lat_offset': 0.012,
        'lng_offset': -0.008,
        'address': 'Kothrud, Pune'
    },
    {
        'name': 'Siddharth Iyer',
        'email': 'siddharth.i@example.com',
        'blood_group': 'B-',
        'city': 'Bengaluru',
        'phone': '+91 98450 11223',
        'is_available': True,
        'is_verified': True,
        'total_donations': 9,
        'last_donation_days_ago': 140,
        'bio': 'Techie at Koramangala. Available for emergency hospital calls.',
        'lat_offset': -0.015,
        'lng_offset': 0.012,
        'address': 'Koramangala 4th Block, Bengaluru'
    },
    {
        'name': 'Meera Sundaram',
        'email': 'meera.s@example.com',
        'blood_group': 'AB-',
        'city': 'Bengaluru',
        'phone': '+91 98455 33445',
        'is_available': True,
        'is_verified': True,
        'total_donations': 3,
        'last_donation_days_ago': 102,
        'bio': 'AB- is one of the rarest blood groups. Please reach out for emergency requests.',
        'lat_offset': 0.028,
        'lng_offset': -0.020,
        'address': 'Indiranagar 100ft Road, Bengaluru'
    },
    {
        'name': 'Dr. Rohan Kulkarni',
        'email': 'rohan.k@example.com',
        'blood_group': 'O+',
        'city': 'Bengaluru',
        'phone': '+91 98440 77889',
        'is_available': False,
        'is_verified': True,
        'total_donations': 15,
        'last_donation_days_ago': 40,
        'bio': 'Resident doctor & regular donor. Advancing safe blood transfusion awareness.',
        'lat_offset': 0.008,
        'lng_offset': 0.015,
        'address': 'Whitefield, Bengaluru'
    },
    {
        'name': 'Mohd. Farhan',
        'email': 'farhan.m@example.com',
        'blood_group': 'B+',
        'city': 'Hyderabad',
        'phone': '+91 98660 55667',
        'is_available': True,
        'is_verified': True,
        'total_donations': 7,
        'last_donation_days_ago': 115,
        'bio': 'Active member of youth voluntary donation group in Banjara Hills.',
        'lat_offset': 0.014,
        'lng_offset': -0.018,
        'address': 'Banjara Hills Road 12, Hyderabad'
    },
    {
        'name': 'Deepak Chawla',
        'email': 'deepak.c@example.com',
        'blood_group': 'O-',
        'city': 'Jaipur',
        'phone': '+91 98290 12345',
        'is_available': True,
        'is_verified': True,
        'total_donations': 10,
        'last_donation_days_ago': 130,
        'bio': 'O negative donor. Available for SMS / Call alerts anytime.',
        'lat_offset': -0.010,
        'lng_offset': 0.012,
        'address': 'Malviya Nagar, Jaipur'
    },
    {
        'name': 'Sunita Ghosh',
        'email': 'sunita.ghosh@example.com',
        'blood_group': 'A+',
        'city': 'Kolkata',
        'phone': '+91 98310 99887',
        'is_available': True,
        'is_verified': True,
        'total_donations': 4,
        'last_donation_days_ago': 92,
        'bio': 'Dedicated voluntary donor. Supporting SSKM & AMRI hospitals.',
        'lat_offset': 0.020,
        'lng_offset': -0.010,
        'address': 'Salt Lake Sector 1, Kolkata'
    },
    {
        'name': 'Arjun Nambiar',
        'email': 'arjun.n@example.com',
        'blood_group': 'O+',
        'city': 'Chennai',
        'phone': '+91 98410 77665',
        'is_available': True,
        'is_verified': True,
        'total_donations': 5,
        'last_donation_days_ago': 98,
        'bio': 'Happy to donate blood and spread positive awareness.',
        'lat_offset': -0.012,
        'lng_offset': 0.014,
        'address': 'Adyar, Chennai'
    },
    {
        'name': 'Tanvi Singhal',
        'email': 'tanvi.s@example.com',
        'blood_group': 'B+',
        'city': 'Lucknow',
        'phone': '+91 98390 33221',
        'is_available': True,
        'is_verified': True,
        'total_donations': 2,
        'last_donation_days_ago': 150,
        'bio': 'University student, first donated on World Blood Donor Day.',
        'lat_offset': 0.010,
        'lng_offset': 0.010,
        'address': 'Gomti Nagar, Lucknow'
    },
    {
        'name': 'Hardik Patel',
        'email': 'hardik.p@example.com',
        'blood_group': 'A-',
        'city': 'Ahmedabad',
        'phone': '+91 98250 88776',
        'is_available': True,
        'is_verified': True,
        'total_donations': 7,
        'last_donation_days_ago': 105,
        'bio': 'Quick responder for emergencies at Civil Hospital or Apollo.',
        'lat_offset': -0.016,
        'lng_offset': 0.015,
        'address': 'Navrangpura, Ahmedabad'
    }
]

HOSPITALS = [
    {'name': 'AIIMS Trauma Center', 'city': 'New Delhi', 'address': 'Ansari Nagar East, New Delhi'},
    {'name': 'Max Super Speciality Hospital', 'city': 'New Delhi', 'address': 'Saket, New Delhi'},
    {'name': 'Lilavati Hospital & Research Centre', 'city': 'Mumbai', 'address': 'Bandra West, Mumbai'},
    {'name': 'Tata Memorial Hospital', 'city': 'Mumbai', 'address': 'Parel, Mumbai'},
    {'name': 'Manipal Hospital', 'city': 'Bengaluru', 'address': 'HAL Old Airport Road, Bengaluru'},
    {'name': 'Apollo Hospital', 'city': 'Hyderabad', 'address': 'Jubilee Hills, Hyderabad'},
    {'name': 'Ruby Hall Clinic', 'city': 'Pune', 'address': 'Sasoon Road, Pune'}
]


def seed_database(db, User, DonationRequest, RequestResponse, DonationHistory, Notification):
    """Seed the database with rich startup-quality data if empty."""
    if User.query.first():
        return # Already seeded

    print("--- Seeding RaktSetu database with realistic data ---")

    # 1. Admin User
    admin = User(
        name='Super Admin',
        email='admin@raktsetu.org',
        password_hash=generate_password_hash('admin123'),
        role='admin',
        blood_group='O+',
        city='New Delhi',
        state='Delhi',
        pincode='110001',
        address='Connaught Place HQ, New Delhi',
        latitude=28.6139,
        longitude=77.2090,
        phone='+91 98000 00000',
        is_available=True,
        is_verified=True,
        total_donations=15,
        last_donation_date=(datetime.utcnow() - timedelta(days=110)).date(),
        bio='Platform administrator and certified regular blood donor.'
    )
    db.session.add(admin)

    # 2. Seeker Demo User
    seeker = User(
        name='Priya Patel',
        email='seeker@raktsetu.org',
        password_hash=generate_password_hash('seeker123'),
        role='seeker',
        blood_group='B+',
        city='New Delhi',
        state='Delhi',
        pincode='110016',
        address='Hauz Khas Enclave, New Delhi',
        latitude=28.5494,
        longitude=77.2001,
        phone='+91 98711 99880',
        is_available=False,
        is_verified=True,
        total_donations=0,
        bio='Seeking donors for ongoing surgery and patient requirements.'
    )
    db.session.add(seeker)

    # 3. Create Donors
    donor_instances = []
    for d in DONORS_DATA:
        city_info = CITY_COORDINATES.get(d['city'], CITY_COORDINATES['New Delhi'])
        lat = city_info['lat'] + d.get('lat_offset', 0)
        lng = city_info['lng'] + d.get('lng_offset', 0)
        last_don_date = (datetime.utcnow() - timedelta(days=d['last_donation_days_ago'])).date()
        
        user = User(
            name=d['name'],
            email=d['email'],
            password_hash=generate_password_hash('donor123'),
            role='donor',
            blood_group=d['blood_group'],
            city=d['city'],
            state=city_info['state'],
            pincode='110001',
            address=d['address'],
            latitude=round(lat, 5),
            longitude=round(lng, 5),
            phone=d['phone'],
            is_available=d['is_available'],
            is_verified=d['is_verified'],
            total_donations=d['total_donations'],
            last_donation_date=last_don_date,
            bio=d['bio']
        )
        db.session.add(user)
        donor_instances.append(user)

    db.session.commit()

    # 4. Create Historical Donations for demo donor (Rahul Sharma)
    rahul = User.query.filter_by(email='donor@raktsetu.org').first()
    if rahul:
        hospitals_sample = ['AIIMS Delhi', 'Safdarjung Hospital', 'Red Cross Society Delhi', 'Max Healthcare Saket']
        for i in range(1, 9):
            don_date = (datetime.utcnow() - timedelta(days=105 + (i * 95))).date()
            dh = DonationHistory(
                donor_id=rahul.id,
                hospital_name=hospitals_sample[i % len(hospitals_sample)],
                blood_group='O+',
                units_donated=1,
                donation_date=don_date,
                certificate_id=f'RKT-{2024-i//4}-{1000+i}',
                notes='Voluntary whole blood donation. Patient successfully recovered.'
            )
            db.session.add(dh)

    # 5. Create Emergency & Active Requests
    # Request 1: Critical O+ request in Delhi created by seeker Priya Patel
    req1 = DonationRequest(
        requester_id=seeker.id,
        patient_name='Rajesh Malhotra',
        blood_group='O+',
        units_needed=2,
        hospital_name='AIIMS Trauma Center',
        hospital_address='Ring Road, Ansari Nagar, New Delhi',
        city='New Delhi',
        latitude=28.5672,
        longitude=77.2100,
        urgency='Critical',
        contact_person='Priya Patel (Attendant)',
        contact_phone='+91 98711 99880',
        notes='Emergency aortic valve replacement surgery scheduled. Urgent requirement of 2 units O+ blood.',
        status='Open',
        created_at=datetime.utcnow() - timedelta(hours=3)
    )
    db.session.add(req1)

    # Request 2: Urgent B+ request in Mumbai
    req2 = DonationRequest(
        requester_id=seeker.id,
        patient_name='Sunil Kamat',
        blood_group='B+',
        units_needed=3,
        hospital_name='Lilavati Hospital',
        hospital_address='Bandra West, Mumbai',
        city='Mumbai',
        latitude=19.0514,
        longitude=72.8290,
        urgency='Urgent',
        contact_person='Ramesh Kamat (Brother)',
        contact_phone='+91 98205 12345',
        notes='Scheduled oncological surgery. Donor replacement needed before morning.',
        status='Accepted',
        created_at=datetime.utcnow() - timedelta(days=1, hours=4)
    )
    db.session.add(req2)

    # Request 3: Normal A+ request in Bengaluru - Fulfilled
    req3 = DonationRequest(
        requester_id=seeker.id,
        patient_name='Ananya Sen',
        blood_group='A+',
        units_needed=1,
        hospital_name='Manipal Hospital',
        hospital_address='HAL Old Airport Road, Bengaluru',
        city='Bengaluru',
        latitude=12.9584,
        longitude=77.6487,
        urgency='Normal',
        contact_person='Dr. Arindam Sen',
        contact_phone='+91 98450 99881',
        notes='Thalassemia monthly transfusion support.',
        status='Fulfilled',
        created_at=datetime.utcnow() - timedelta(days=5),
        fulfilled_at=datetime.utcnow() - timedelta(days=4)
    )
    db.session.add(req3)

    # Request 4: Critical O- request in New Delhi
    req4 = DonationRequest(
        requester_id=seeker.id,
        patient_name='Baby of Sneha Kapoor',
        blood_group='O-',
        units_needed=1,
        hospital_name='Max Super Speciality Hospital',
        hospital_address='Press Enclave Road, Saket, New Delhi',
        city='New Delhi',
        latitude=28.5284,
        longitude=77.2140,
        urgency='Critical',
        contact_person='Dr. Kapoor (Pediatrics)',
        contact_phone='+91 98108 55443',
        notes='Neonatal emergency exchange transfusion. O Negative blood required urgently within 4 hours.',
        status='Open',
        created_at=datetime.utcnow() - timedelta(minutes=45)
    )
    db.session.add(req4)

    db.session.commit()

    # 6. Create Responses for Requests
    # Rahul responded to req1
    if rahul:
        resp1 = RequestResponse(
            request_id=req1.id,
            donor_id=rahul.id,
            status='Accepted',
            message='I am in Connaught Place, can reach AIIMS Trauma Center within 30 minutes!',
            responded_at=datetime.utcnow() - timedelta(hours=1, minutes=15)
        )
        db.session.add(resp1)

    # Pooja responded to req4 (O-)
    pooja = User.query.filter_by(email='pooja.verma@example.com').first()
    if pooja:
        resp2 = RequestResponse(
            request_id=req4.id,
            donor_id=pooja.id,
            status='Interested',
            message='I am O- universal donor at South Ex, ready to donate immediately for the newborn.',
            responded_at=datetime.utcnow() - timedelta(minutes=20)
        )
        db.session.add(resp2)

    # Kavita responded to req2 (Mumbai)
    kavita = User.query.filter_by(email='kavita.nair@example.com').first()
    if kavita:
        resp3 = RequestResponse(
            request_id=req2.id,
            donor_id=kavita.id,
            status='Accepted',
            message='Verified with blood bank, heading to Lilavati Hospital.',
            responded_at=datetime.utcnow() - timedelta(hours=18)
        )
        db.session.add(resp3)

    db.session.commit()

    # 7. Notifications
    notifications_data = [
        {
            'user_id': rahul.id if rahul else 1,
            'title': '🚨 Critical Emergency Alert: O+ Needed',
            'message': 'AIIMS Trauma Center, New Delhi urgently needs 2 units of O+ blood for surgery.',
            'type': 'emergency',
            'link': f'/request/{req1.id}',
            'is_read': False,
            'created_at': datetime.utcnow() - timedelta(hours=3)
        },
        {
            'user_id': rahul.id if rahul else 1,
            'title': '🏆 New Badge Unlocked: Lifesaver 5+',
            'message': 'Congratulations! You have impacted over 20+ lives through your voluntary donations.',
            'type': 'badge',
            'link': '/dashboard/donor',
            'is_read': True,
            'created_at': datetime.utcnow() - timedelta(days=2)
        },
        {
            'user_id': seeker.id,
            'title': '✅ Donor Responded to Your Request',
            'message': 'Rahul Sharma (O+) has accepted your blood request for Rajesh Malhotra at AIIMS.',
            'type': 'response',
            'link': f'/request/{req1.id}',
            'is_read': False,
            'created_at': datetime.utcnow() - timedelta(hours=1, minutes=15)
        },
        {
            'user_id': seeker.id,
            'title': '🚨 Request Broadcasted Successfully',
            'message': 'Your emergency request for O- blood was sent to 12 nearby eligible donors in Delhi NCR.',
            'type': 'emergency',
            'link': f'/request/{req4.id}',
            'is_read': True,
            'created_at': datetime.utcnow() - timedelta(minutes=45)
        }
    ]

    for n in notifications_data:
        notif = Notification(
            user_id=n['user_id'],
            title=n['title'],
            message=n['message'],
            type=n['type'],
            link=n['link'],
            is_read=n['is_read'],
            created_at=n['created_at']
        )
        db.session.add(notif)

    db.session.commit()
    print("--- Database seeding complete! 15+ donors, requests, and notifications created. ---")

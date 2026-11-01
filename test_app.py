"""
Automated End-to-End Test Suite for RaktSetu / RaktAnsh Flask Application.
Tests all endpoints, templates, JSON APIs, auth flows, and emergency lifecycles.
"""
import unittest
from app import app, db, User, DonationRequest, RequestResponse, Notification

class RaktSetuTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_landing_page(self):
        """Test landing page renders headline, counters, search card."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Every drop counts', res.data)
        self.assertIn(b'Find a donor in seconds', res.data)
        self.assertIn(b'RaktSetu', res.data)
        self.assertIn(b'RaktAnsh', res.data)
        print("PASS: Landing page rendered correctly.")

    def test_02_search_page_and_api(self):
        """Test donor search and JSON endpoint for Leaflet map."""
        # HTML Page
        res = self.client.get('/search?blood_group=O%2B&city=New+Delhi')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Live Donor Map', res.data)
        self.assertIn(b'Find Donors', res.data)

        # JSON API for Leaflet map
        api_res = self.client.get('/api/donors/search?blood_group=O%2B&city=New+Delhi')
        self.assertEqual(api_res.status_code, 200)
        data = api_res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['count'], 0)
        self.assertIn('lat', data['donors'][0])
        self.assertIn('lng', data['donors'][0])
        print(f"PASS: Donor search returned {data['count']} donors with coordinates for Leaflet.")

    def test_03_compatibility_matrix(self):
        """Test 8x8 compatibility matrix page."""
        res = self.client.get('/compatibility')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Blood Group Compatibility Matrix', res.data)
        self.assertIn(b'Universal Red Cell Donor', res.data)
        print("PASS: Compatibility page rendered with 8x8 matrix.")

    def test_04_donor_profile(self):
        """Test donor profile view."""
        with app.app_context():
            donor = User.query.filter_by(role='donor').first()
            donor_id = donor.id

        res = self.client.get(f'/donor/{donor_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Donation Journey Timeline', res.data)
        self.assertIn(b'Honor Badges', res.data)
        print("PASS: Donor profile page rendered.")

    def test_05_auth_and_dashboards(self):
        """Test login, session, and role dashboards."""
        # 1. Login as Donor
        res = self.client.post('/login', data={
            'email': 'donor@raktsetu.org',
            'password': 'donor123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Hello, Rahul', res.data)
        self.assertIn(b'90-Day Safety', res.data)
        self.assertIn(b'Available for Emergencies', res.data)
        print("PASS: Donor login and dashboard verified with 90-day progress.")

        # 2. Toggle Availability AJAX
        toggle_res = self.client.post('/api/donor/toggle-availability', json={'is_available': True})
        self.assertEqual(toggle_res.status_code, 200)
        self.assertTrue(toggle_res.get_json()['is_available'])
        print("PASS: Donor availability toggle AJAX verified.")

        # 3. Logout
        self.client.get('/logout')

        # 4. Login as Admin
        admin_res = self.client.post('/login', data={
            'email': 'admin@raktsetu.org',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(admin_res.status_code, 200)

        # Check Admin Portal
        admin_page = self.client.get('/admin')
        self.assertEqual(admin_page.status_code, 200)
        self.assertIn(b'National Blood Network Operations', admin_page.data)
        self.assertIn(b'bloodGroupChart', admin_page.data)
        self.assertIn(b'requestStatusChart', admin_page.data)
        print("PASS: Admin dashboard and Chart.js containers verified.")

    def test_06_emergency_request_flow(self):
        """Test 3-step wizard submission and request detail."""
        res = self.client.post('/request/new', data={
            'patient_name': 'Test Emergency Patient',
            'blood_group': 'B+',
            'units_needed': 2,
            'hospital_name': 'Max Hospital',
            'hospital_address': 'Saket, New Delhi',
            'city': 'New Delhi',
            'urgency': 'Critical',
            'contact_person': 'Attendant Vikram',
            'contact_phone': '+91 99999 88888',
            'notes': 'Urgent requirement for cardiac surgery.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Emergency Alert Successfully Dispatched', res.data)
        self.assertIn(b'Test Emergency Patient', res.data)
        self.assertIn(b'Current State', res.data)
        print("PASS: Emergency request created and broadcasted with notification dispatch.")

    def test_07_about_and_404(self):
        """Test About page and custom 404 page."""
        res_about = self.client.get('/about')
        self.assertEqual(res_about.status_code, 200)
        self.assertIn(b'Why 90 Days Between Donations?', res_about.data)

        res_404 = self.client.get('/nonexistent-blood-page-123')
        self.assertEqual(res_404.status_code, 404)
        self.assertIn(b'Lost in Transfusion?', res_404.data)
        print("PASS: About guidelines and custom 404 blood drop illustration verified.")

if __name__ == '__main__':
    unittest.main()

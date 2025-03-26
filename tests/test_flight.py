import pytest
from datetime import datetime
from skyscanner_travel.models.flight import Flight, Price, Stop
from skyscanner_travel.models.location import Location

def test_bookingcom_url():
    # Create a test flight with known values
    flight = Flight(
        id='16157-2503301340--31829-0-13411-2503301450',
        session_id='fae74729-71d7-4084-80a4-43ae480b3f97',
        origin=Location(
            entity_id='16157',
            code='SDF',
            name='Louisville Muhammad Ali International',
            type='AIRPORT',
            city_name='Louisville',
            region_name='',
            country_name='United States'
        ),
        origin_city='Louisville',
        destination=Location(
            entity_id='13411',
            code='LAS',
            name='Las Vegas Harry Reid International',
            type='AIRPORT',
            city_name='Las Vegas',
            region_name='',
            country_name='United States'
        ),
        destination_city='Las Vegas',
        departure={'date': '03/30/2025', 'time': '05:12 PM'},
        arrival={'date': '03/30/2025', 'time': '11:40 PM'},
        airline='Southwest Airlines',
        flight_number='WN3109',
        price=Price(amount=578.48, currency='USD'),
        cabin_class='ECONOMY',
        stops=[Stop(airport='MCO', city='Orlando', duration='1h 45m')],
        total_duration='4h 10m',
        booking_url='https://www.skyscanner.net/transport_deeplink/4.0/US/en-US/USD/swa_/1/16157.13411.2025-03-30/air/airli/flights?itinerary=flight|-31829|3109|16157|2025-03-30T13:40|13411|2025-03-30T14:50|250|WLN0P4Q|W|PLU&carriers=-31829&operators=-31829&passengers=1&channel=iphone&cabin_class=economy&fps_session_id=fae74729-71d7-4084-80a4-43ae480b3f97&is_npt=false&is_multipart=false&client_id=skyscanner_app&request_id=adb2fd4d-828c-3dab-e187-31697989db50&q_ids=H4sIAAAAAAAA_-OS4mIpLk-MF2LmmFsnxczxOEOhYfKi_WxGTAqMACD7p9QcAAAA|-5473719741490957552|2&q_sources=JACQUARD&commercial_filters=false&q_datetime_utc=2025-03-26T00:45:31&pqid=false'
    )

    # Get the booking URL
    url = flight.booking_url

    # Verify the URL structure
    assert url.startswith('https://www.skyscanner.net/transport_deeplink/')
    assert 'itinerary=flight' in url
    assert 'cabin_class=economy' in url
    assert 'passengers=1' in url
    assert 'channel=iphone' in url
    assert 'client_id=skyscanner_app' in url

def test_bookingcom_url_with_different_cabin():
    # Test with a different cabin class
    flight = Flight(
        id='16157-2503301340--31829-0-13411-2503301450',
        session_id='fae74729-71d7-4084-80a4-43ae480b3f97',
        origin=Location(
            entity_id='16157',
            code='SDF',
            name='Louisville Muhammad Ali International',
            type='AIRPORT',
            city_name='Louisville',
            region_name='',
            country_name='United States'
        ),
        origin_city='Louisville',
        destination=Location(
            entity_id='13411',
            code='LAS',
            name='Las Vegas Harry Reid International',
            type='AIRPORT',
            city_name='Las Vegas',
            region_name='',
            country_name='United States'
        ),
        destination_city='Las Vegas',
        departure={'date': '03/30/2025', 'time': '05:12 PM'},
        arrival={'date': '03/30/2025', 'time': '11:40 PM'},
        airline='Southwest Airlines',
        flight_number='WN3109',
        price=Price(amount=578.48, currency='USD'),
        cabin_class='BUSINESS',
        stops=[],
        total_duration='4h 10m',
        booking_url='https://www.skyscanner.net/transport_deeplink/4.0/US/en-US/USD/swa_/1/16157.13411.2025-03-30/air/airli/flights?itinerary=flight|-31829|3109|16157|2025-03-30T13:40|13411|2025-03-30T14:50|250|WLN0P4Q|W|PLU&carriers=-31829&operators=-31829&passengers=1&channel=iphone&cabin_class=business&fps_session_id=fae74729-71d7-4084-80a4-43ae480b3f97&is_npt=false&is_multipart=false&client_id=skyscanner_app&request_id=adb2fd4d-828c-3dab-e187-31697989db50&q_ids=H4sIAAAAAAAA_-OS4mIpLk-MF2LmmFsnxczxOEOhYfKi_WxGTAqMACD7p9QcAAAA|-5473719741490957552|2&q_sources=JACQUARD&commercial_filters=false&q_datetime_utc=2025-03-26T00:45:31&pqid=false'
    )

    url = flight.booking_url
    assert 'cabin_class=business' in url

def test_bookingcom_url_without_booking_url():
    # Test when no booking URL is provided
    flight = Flight(
        id='16157-2503301340--31829-0-13411-2503301450',
        session_id='fae74729-71d7-4084-80a4-43ae480b3f97',
        origin=Location(
            entity_id='16157',
            code='SDF',
            name='Louisville Muhammad Ali International',
            type='AIRPORT',
            city_name='Louisville',
            region_name='',
            country_name='United States'
        ),
        origin_city='Louisville',
        destination=Location(
            entity_id='13411',
            code='LAS',
            name='Las Vegas Harry Reid International',
            type='AIRPORT',
            city_name='Las Vegas',
            region_name='',
            country_name='United States'
        ),
        destination_city='Las Vegas',
        departure={'date': '03/30/2025', 'time': '05:12 PM'},
        arrival={'date': '03/30/2025', 'time': '11:40 PM'},
        airline='Southwest Airlines',
        flight_number='WN3109',
        price=Price(amount=578.48, currency='USD'),
        cabin_class='ECONOMY',
        stops=[],
        total_duration='4h 10m'
    )

    url = flight.booking_url
    assert url is None

def test_flight_from_api_response():
    # Test creating a Flight instance from API response
    api_response = {
        'data': {
            'itineraries': [{
                'id': '16157-2503301340--31829-0-13411-2503301450',
                'price': {
                    'raw': 578.48,
                    'formatted': '$579',
                    'pricingOptionId': 'swTBGVu-c4H4'
                },
                'legs': [{
                    'id': '16157-2503301340--31829-0-13411-2503301450',
                    'origin': {
                        'entityId': '16157',
                        'name': 'Louisville Muhammad Ali International',
                        'displayCode': 'SDF',
                        'city': 'Louisville',
                        'country': 'United States'
                    },
                    'destination': {
                        'entityId': '13411',
                        'name': 'Las Vegas Harry Reid International',
                        'displayCode': 'LAS',
                        'city': 'Las Vegas',
                        'country': 'United States'
                    },
                    'segments': [{
                        'id': '16157-13411-2503301340-2503301450--31829',
                        'origin': {
                            'displayCode': 'SDF',
                            'parent': {
                                'name': 'Louisville'
                            }
                        },
                        'destination': {
                            'displayCode': 'LAS',
                            'parent': {
                                'name': 'Las Vegas'
                            }
                        },
                        'departure': '2025-03-30T13:40:00',
                        'arrival': '2025-03-30T14:50:00',
                        'flightNumber': '3109',
                        'marketingCarrier': {
                            'name': 'Southwest Airlines'
                        }
                    }],
                    'durationInMinutes': 250,
                    'stopCount': 0,
                    'departure': '2025-03-30T13:40:00',
                    'arrival': '2025-03-30T14:50:00',
                    'carriers': {
                        'marketing': [{
                            'name': 'Southwest Airlines'
                        }]
                    }
                }]
            }]
        },
        'sessionId': 'fae74729-71d7-4084-80a4-43ae480b3f97'
    }

    flight = Flight.from_api_response(api_response)

    assert flight.origin.code == 'SDF'
    assert flight.origin_city == 'Louisville'
    assert flight.destination.code == 'LAS'
    assert flight.destination_city == 'Las Vegas'
    assert flight.departure['date'] == 'Sunday, March 30'
    assert flight.departure['time'] == '01:40pm'
    assert flight.arrival['date'] == 'Sunday, March 30'
    assert flight.arrival['time'] == '02:50pm'
    assert flight.airline == 'Southwest Airlines'
    assert flight.flight_number == '3109'
    assert flight.price.amount == 578.48
    assert flight.price.currency == 'USD'
    assert flight.cabin_class == 'ECONOMY'
    assert flight.stops == []
    assert flight.total_duration == '4h 10m'
    assert flight.itinerary_id == '16157-2503301340--31829-0-13411-2503301450'
    assert flight.booking_url is None
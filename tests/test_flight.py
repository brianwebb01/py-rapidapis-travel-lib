import pytest
from rapid_bookingcom.models.flight import Flight, Stop

def test_bookingcom_url():
    # Create a test flight with known values
    flight = Flight(
        origin='SDF',
        origin_city='Louisville',
        destination='LAS',
        destination_city='Las Vegas',
        departure={'date': '03/30/2025', 'time': '05:12 PM'},
        arrival={'date': '03/30/2025', 'time': '11:40 PM'},
        airline='Spirit Airlines',
        flight_number='NK967',
        price={'amount': 255, 'currency': 'USD'},
        cabin_class='ECONOMY',
        stops=[Stop(airport='MCO', city='Orlando', duration='1h 45m')],
        total_duration='9h 28m',
        token='d6a1f_H4sIAAAAAAAA_0WQbW-qMBiGf437RqG8Y9KcMGGOAFUBde5Lg6UiZ57V0G6-_Pp1YHLS5r6v-0mfNn2OUp7FVNcPp649SqF9CdByydtaMkD5P_3QK9lz_tF9tnrd9XoZvWRhaRl5WOhQ19Si090fVp870IMDit-quMBhRqoiWZJlkcwSPH9iV6mJnqKnbs9AjbQgCEYUFC1D_8E9coHjP1s-3q6GEuUS2cDZLEPnxdoUeCz26BU6sZ8OqUH57HJZ3EORRzKrInHDdyHXp8TDm_fVqtrMc0OmRSSu2DjnWRRDHHORV2uj7K47DGPFTbbtLkOPukvi-ENk6_ySRaHIqlgUBp9Y0fAYoxRBAGwvgEPmtUCe_2AqETRGbCQqq0UWzMYokenY_vjLK4KWawZAqZqBYCdGZcc_U3ZDOA1cT1OTrXvT0XYEp57t_s8TcwZtR34HlqKJFardEgMYyo8Pr0m5AO9zRXtiviqjozXEYlb9e4KRXz0QW2lHIBj7_pJkq-xO4C0wXdj8AEwoEl0VAgAA',
        trip_type='oneway'
    )

    # Get the booking URL
    url = flight.bookingcom_url()

    # Verify the URL structure
    assert url.startswith('https://flights.booking.com/flights/SDF.AIRPORT-LAS.AIRPORT/')
    assert flight.token in url
    assert 'type=ONEWAY' in url
    assert 'adults=1' in url
    assert 'cabinClass=ECONOMY' in url
    assert 'from=SDF.AIRPORT' in url
    assert 'to=LAS.AIRPORT' in url
    assert 'fromCountry=US' in url
    assert 'toCountry=US' in url
    assert 'depart=2025-03-30' in url
    assert 'Louisville%20International%20Airport' in url
    assert 'Las%20Vegas%20International%20Airport' in url

def test_bookingcom_url_with_different_cabin():
    # Test with a different cabin class
    flight = Flight(
        origin='SDF',
        origin_city='Louisville',
        destination='LAS',
        destination_city='Las Vegas',
        departure={'date': '03/30/2025', 'time': '05:12 PM'},
        arrival={'date': '03/30/2025', 'time': '11:40 PM'},
        airline='Spirit Airlines',
        flight_number='NK967',
        price={'amount': 255, 'currency': 'USD'},
        cabin_class='BUSINESS',
        stops=[],
        total_duration='9h 28m',
        token='test_token',
        trip_type='oneway'
    )

    url = flight.bookingcom_url()
    assert 'cabinClass=BUSINESS' in url
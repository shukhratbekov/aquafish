from geopy import Nominatim

nom = Nominatim(user_agent='008')

n = nom.reverse((20, 10), exactly_one=True)
print(n)
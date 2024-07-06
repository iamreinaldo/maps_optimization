from geopy.geocoders import Nominatim
import webbrowser

geolocator = Nominatim(user_agent="map_optimizator")
enderecos = [
            'Rua Melchior DIas, 9 - Centro - Jacobina - BA, 44700-000',
            'Rua Eugênio Lira, 83 - Nazaré - Jacobina - BA, 44700-000'
            ]
for endereco in enderecos:
    location = geolocator.geocode(endereco)
    if location:
        lat = location.latitude
        lng = location.longitute

        print(lat, lng)

        url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=16"

        webbrowser.open(url)
        
    else:
        print("Não foi possível")



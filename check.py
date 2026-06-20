from app.main import app
print('App loaded OK')
for route in app.routes:
    print(f'  {route.path}')
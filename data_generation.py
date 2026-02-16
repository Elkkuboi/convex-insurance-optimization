import sqlite3
import random

# oikeat parametrit
TRUE_PARAMS = {
    'henkilo': {'lambda': 2.0, 'mu': 0.5}, # Harvinainen, hidas
    'auto':    {'lambda': 10.0, 'mu': 1.0} # Yleinen, nopea
}

def create_database(db_path='insurance_data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vakuutustapahtumat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vahinkotyyppi TEXT NOT NULL,
            saapumisaika REAL NOT NULL,
            kasittely_alkoi REAL,
            kasittely_paattyi REAL
        );
    """)
    conn.commit()
    cursor.close()
    return conn



def generate_data(conn, simulation_time=1000):
    cursor = conn.cursor()
    print(f"Generoidaan dataa ajalle T={simulation_time}...")

    # käydään läpi kumpikin vahinkotyyppi erikseen
    for vahinkotyyppi, params in TRUE_PARAMS.items():
        t = 0.0 # Kello alkaa nollasta
        
        # Generoidaan tapahtumia kunnes aika loppuu
        while t < simulation_time:
            # 1. Koska seuraava asiakas saapuu?
            dt = random.expovariate(params['lambda'])
            t += dt 
            saapumisaika = t

            # 2. Kauanko palvelu kestää?
            # Tässä vaiheessa emme simuloi jonoa, vaan tallennamme vain
            # sen, kauanko työ veisi (palveluaika).
            # Yksinkertaistuksen vuoksi oletetaan, että käsittely alkaa heti
            palveluaika = random.expovariate(params['mu'])
            
            alkoi = saapumisaika
            paattyi = alkoi + palveluaika

            # Tallennetaan rivi tietokantaan
            cursor.execute("""
                INSERT INTO vakuutustapahtumat (vahinkotyyppi, saapumisaika, kasittely_alkoi, kasittely_paattyi)
                VALUES (?, ?, ?, ?)
            """, (vahinkotyyppi, saapumisaika, alkoi, paattyi))
    
    conn.commit()
    print("Valmis, data on tietokannassa.")


# kurkataas
def peek_table(conn, limit=10):
    cursor = conn.cursor()
    # Haetaan enintään limit riviä taulusta
    cursor.execute("SELECT * FROM vakuutustapahtumat LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    # Haetaan sarakkeiden nimet
    cursor.execute("PRAGMA table_info(vakuutustapahtumat)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Tulostetaan otsikot
    print(" | ".join(columns))
    print("-" * 50)
    
    # Tulostetaan rivit
    for row in rows:
        print(" | ".join(str(value) for value in row))
    
    cursor.close()


connection = create_database()
generate_data(connection)
peek_table(connection)

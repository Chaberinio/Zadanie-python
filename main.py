#Import biblioteki psycopg2
import psycopg2

#Funkcja połączenia z bazą danych
#Wartości takie jak nazwa bazy, host, port, nazwa użytkowinka i hasło są dla uproszecznia "zabite na sztywno"
#W przypadku połączenia do bazy zwraca informacje o udanym połączeniu
#W przypadku błędu połączenia zwraca informację o błędzie

def connect():
    try:
        conn = psycopg2.connect(
            dbname="biblioteka",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        print("Połączenie udane.")
        return conn    
    except Exception as e:
        print(f"Błąd łączenia do bazy danych: {e}")
        return None

#Funkcja dodająca książkę do bazy
#Dane wejściowe: conn-połączenie z bazą,tytuł-tytuł książki,rok_wydania - rok wydania książki, isbn - numer isbn książki    
    
def dodaj_ksiazke(conn, tytul, autor, rok_wydania, isbn):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO ksiazki (tytul, autor, rok_wydania, isbn)
            VALUES (%s, %s, %s, %s);
        ''', (tytul, autor, rok_wydania, isbn))
        conn.commit()

#Funkcja usnięcia książki
#Dane wejściowe: conn - połączenie z bazą, book_id - id książki w bazie
#Funkcja sprawdza czy książka o podanym ID istnieje
#jeżeli tak to ją usuwa, a jeżeli nie to zwraca komunikat błędu
        
def usun_ksiazke(conn, book_id):
    if not book_id:
        print("ID książki jest wymagane!")
        return

    current_book = pobierz_dane_ksiazki(conn, book_id)
    if not current_book:
        print("Książka o podanym ID nie istnieje.")
        return
    
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM ksiazki WHERE id = %s;
        ''', (book_id,))
        conn.commit()

#Funkcja aktualizacji książki
#Dane wejściowe: conn-połączenie z bazą, book_id - ID książki którą chcemy zaktualizować, new_tytul - nowy tytuł ksiązki, new_autor - nowy autor książki, new_rok_wydania - nowy rok wydania książki, new_isbn - nowy numer isbn książki
#Funkcja sprawdza czy "dostała" ID książki oraz czy książka o takim ID istnieje w bazie
#Funkcja pobiera z bazy dane książki o podanym ID
#Jeżeli, któraś z nowych danych będzie pusta podstawiona pod nią zostanie poprzednia wartość

def zaktualizuj_ksiazke(conn, book_id, new_tytul, new_autor, new_rok_wydania, new_isbn):
    if not book_id:
        print("ID książki jest wymagane!")
        return

    current_book = pobierz_dane_ksiazki(conn, book_id)
    if not current_book:
        print("Książka o podanym ID nie istnieje.")
        return

    tytul = new_tytul if new_tytul else current_book[0]
    autor = new_autor if new_autor else current_book[1]
    rok_wydania = new_rok_wydania if new_rok_wydania else current_book[2]
    isbn = new_isbn if new_isbn else current_book[3]

    with conn.cursor() as cur:
        cur.execute('''
            UPDATE ksiazki
            SET tytul = %s, autor = %s, rok_wydania = %s, isbn = %s
            WHERE id = %s;
        ''', (tytul, autor, rok_wydania, isbn, book_id))
        conn.commit()

#Funkcja wyświetlająca dane wszystkich książek
#Dane wejściowe: conn - połączenie z bazą
#Funkcja pobiera oraz wyświetal dane wszystkich książek w naszej bazie

def wyswietl_ksiazki(conn):
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM ksiazki;')
        books = cur.fetchall()
        for book in books:
            print(book)

#Funkcja pobierająca dane książki o podanym ID
#Dane wejściowe: conn - połączenie z bazą, book_id - ID ksiązki
#Funkcja pobiera oraz wyświetal dane wszystkich książek w naszej bazie
#Funkcja sprawdza czy podane ID nie jest puste oraz pobiera dane książki o wskazanym ID
#Ta funkcja jest używana w innych funkcjach do sprawdzenia czy książka o danym ID istnieje w bazie

def pobierz_dane_ksiazki(conn, book_id):
    if not book_id:
        print("ID książki jest wymagane!")
        return None

    with conn.cursor() as cur:
        cur.execute('''
            SELECT tytul, autor, rok_wydania, isbn FROM ksiazki WHERE id = %s;
        ''', (book_id,))
        return cur.fetchone()
    
#Funkcja wprowadzenia pięciu książek na raz
#Dane wejściowe: conn-połączenie z bazą, books - lista książek do wprowadzenia
#Funkcja po kolei wprowadza do bazy, każdą z ksiązek utowrzonych w liście books

def wprowadz_piec_ksiazek(conn):
    books = [
    ("Harry Potter i Kamień Filozoficzny", "J.K. Rowling", 1997, "9780747532699"),
    ("Władca Pierścieni", "J.R.R. Tolkien", 1954, "9780618640157"),
    ("Hobbit, czyli tam i z powrotem", "J.R.R. Tolkien", 1937, "9780007458424"),
    ("Opowieści z Narnii: Lew, Czarownica i Stara Szafa", "C.S. Lewis", 1950, "9780064471046"),
    ("Gra o Tron", "George R.R. Martin", 1996, "9780553103540")
]

    for book in books:
        dodaj_ksiazke(conn, *book)

#Główna funkcja aplikacji

def main():
    #Połączenie z bazą danych
    conn = connect()
    if conn is None:
        return

    #Pętla sterująca wyborem operacji
    #Wyświetla listę dostępnych operacji

    while True:
        print("\nWybierz opcję:")
        print("1. Dodaj książkę")
        print("2. Usuń książkę")
        print("3. Aktualizuj książkę")
        print("4. Wyświetl wszystkie książki")
        print("5. Wprowadź 5 książek")
        print("6. Wyjdź")

        #pobranie wyboru od użytkownika
        choice = input("Wybierz opcję (1-6): ")

        #Dodanie książki
        #Pobranie od użytkownika danych książki
        #Sprawdzenie czy podane dane nie są puste

        if choice == '1':
            tytul = input("Podaj tytuł książki: ").strip()
            autor = input("Podaj autora książki: ").strip()
            rok_wydania = input("Podaj rok wydania książki: ").strip()
            isbn = input("Podaj ISBN książki: ").strip()

            if not tytul or not autor or not rok_wydania or not isbn:
                print("Wszystkie pola są wymagane!")
            else:
                try:
                    rok_wydania = int(rok_wydania)
                    dodaj_ksiazke(conn, tytul, autor, rok_wydania, isbn)
                    print("Książka dodana.")
                except ValueError:
                    print("Rok wydania musi być liczbą całkowitą.")
        
        #Usuwanie ksiązki
        #Pobranie od użytkownika ID książki
        #Sprawdzenie czy dana książka istnieje w bazie

        elif choice == '2':
            print("Lista książek: \n")
            wyswietl_ksiazki(conn)

            book_id = input("Podaj ID książki do usunięcia: ").strip()

            if not book_id:
                print("ID książki jest wymagane!")
            else:
                try:
                    book_id = int(book_id)
                    usun_ksiazke(conn, book_id)
                    print("Książka usunięta.")
                except ValueError:
                    print("ID książki musi być liczbą całkowitą.")
        
        #Aktualizacja książki
        #Pobranie od użytkownika ID książki i sprawdzenie czy taka istnieje w bazie
        #Pobranie od użytkownika nowych danych książki, jeżeli użytownik nie poda wartości podstawiona zostanie orginalana wartość
                    
        elif choice == '3':
            print("Lista książek: \n")
            wyswietl_ksiazki(conn)

            book_id = input("Podaj ID książki do aktualizacji: ").strip()

            if not book_id:
                print("ID książki jest wymagane!")
            else:
                try:
                    book_id = int(book_id)
                    current_book = pobierz_dane_ksiazki(conn, book_id)
                    if current_book:
                        print(f"Aktualne wartości: Tytuł: {current_book[0]}, Autor: {current_book[1]}, Rok wydania: {current_book[2]}, ISBN: {current_book[3]}")
                        new_tytul = input("Podaj nowy tytuł książki (lub pozostaw puste): ").strip()
                        new_autor = input("Podaj nowego autora książki (lub pozostaw puste): ").strip()
                        new_rok_wydania = input("Podaj nowy rok wydania książki (lub pozostaw puste): ").strip()
                        new_isbn = input("Podaj nowy ISBN książki (lub pozostaw puste): ").strip()

                        try:
                            new_rok_wydania = int(new_rok_wydania) if new_rok_wydania else None
                            zaktualizuj_ksiazke(conn, book_id, new_tytul or None, new_autor or None, new_rok_wydania, new_isbn or None)
                            print("Książka zaktualizowana.")
                        except ValueError:
                            print("Rok wydania musi być liczbą całkowitą.")
                    else:
                        print("Książka o podanym ID nie istnieje.")
                except ValueError:
                    print("ID książki musi być liczbą całkowitą.")
        
        #Wyświetlenie wszystkich ksiażek

        elif choice == '4':
            print("Lista książek:")
            wyswietl_ksiazki(conn)
        
        #Wprowadzenie do bazy pięciu książek na raz

        elif choice == '5':
            wprowadz_piec_ksiazek(conn)
            print("Wprowadzono 5 książek od bazy danych.")

        #Zakończenie działania aplikacji

        elif choice == '6':
            print("Koniec programu.")
            break
        
        #Obsługa błędnego podania numeru operacji

        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

    conn.close()

if __name__ == "__main__":
    main()
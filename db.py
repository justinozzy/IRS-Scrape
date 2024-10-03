import sqlite3
from flask import g
from datetime import datetime, timedelta

DATABASE = 'irs.db'

class Database:
    def __init__(self) -> None:
        # SQL queries to create tables if they haven't been made already
        self.create_accessed_table = """
        CREATE TABLE IF NOT EXISTS Accessed (
            ZipCode TEXT NOT NULL,
            State INTEGER NOT NULL,
            DateAccessed TIMESTAMP NOT NULL,
            PRIMARY KEY (ZipCode, State)
        );
        """

        self.create_provider_table = """
        CREATE TABLE IF NOT EXISTS Providers (
            Telephone TEXT PRIMARY KEY,
            NameofBusiness TEXT NOT NULL,
            Address TEXT NOT NULL,
            CityStateZip TEXT,
            PointofContact TEXT NOT NULL,
            TypeOfService TEXT,
            ZipCode TEXT NOT NULL,
            State INTEGER NOT NULL,
            FOREIGN KEY(ZipCode, State) REFERENCES Accessed(ZipCode, State)
        );
        """

    """
    Initialize the database and create tables if they don't exist.
    Return type: None
    """
    def init_db(self) -> None:
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cur.execute(self.create_accessed_table)
            cur.execute(self.create_provider_table)
        self.close_db(conn)

    """
    Checks to see when we last accessed this zip code and state combination.
    Return type: None or datetime
    """
    def check_last_access(self, zipCode, state):
        conn = self.get_db()
        query = """
        SELECT DateAccessed
        FROM Accessed
        WHERE ZipCode = ? AND State = ?
        """
        cur = conn.cursor()
        cur.execute(query, (zipCode, state))
        result = cur.fetchone()

        if result:
            return datetime.strptime(result[0],'%Y-%m-%d %H:%M:%S')
        else:
            return None
    
    """
    Updates the value of when a zip code and state was last accessed.
    Return type: None
    """
    def update_access_data(self, zipCode, state) -> None:
        conn = self.get_db()
        query = """
        INSERT INTO Accessed (ZipCode, State, DateAccessed)
        VALUES (?, ?, ?)
        ON CONFLICT(ZipCode, State) DO UPDATE SET DateAccessed = excluded.DateAccessed;
        """
        cur = conn.cursor()
        cur.execute(query, (zipCode, state, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        print("Accessed values changed...")

    """
    Method used in combination with update_access_data and check_last_access to determine if we need to
    update our database.
    Return type: Boolean (True -> Updated, False -> Not Updated)
    """
    def check_and_update_accessed(self, zipCode, state, refresh_interval=timedelta(hours=24)):
        last_accessed = self.check_last_access(zipCode, state)
        print(f"Last Accessed: {last_accessed}")

        if last_accessed is None or (datetime.now() - last_accessed) > refresh_interval:
            self.update_access_data(zipCode, state)
            return True
        else:
            return False

    """
    Updates or inserts the provider data for E-files based on if we already contain that data and if it needs to be updated or not changed at all.
    Return type: None
    """
    def update_provider_data(self, businessName, address, cityStateZip, pointOfContact, telephone, serviceType, zipCode, state) -> None:
        conn = self.get_db()
        cur = conn.cursor()

        checkQuery = """
        SELECT * FROM Providers WHERE Telephone = ?
        """
        cur.execute(checkQuery, (telephone,))
        existing_provider = cur.fetchone()

        # After gathering the information from the previous query we want to check if any fields differ from what we scraped vs what is currently stored
        # inside the database. We check each individual field and if any of them have been changed they get updated, or we skip over it.
        if existing_provider:
            bizname = existing_provider[1]
            addr = existing_provider[2]
            csz = existing_provider[3]
            poc = existing_provider[4]
            service = existing_provider[5]
            zipC = existing_provider[6]
            st = existing_provider[7]
            if (bizname != businessName or
                addr != address or
                csz != cityStateZip or
                poc != pointOfContact or
                service != serviceType or
                zipC != zipCode or
                st != state):
                updateQuery = """
                UPDATE Providers
                SET NameOfBusiness = ?, Address = ?, CityStateZip = ?, PointOfContact = ?, TypeOfService = ?
                WHERE Telephone = ?
                """
                cur.execute(updateQuery, (bizname, addr, csz, poc, service, telephone))
                conn.commit()
                print(f"Provider data for {telephone} updated.")
            else:
                print(f"Provider data for {telephone} already up to date.")
        # Data isn't currently stored so we add it to the table
        else:
            query = """
            INSERT INTO Providers(Telephone, NameOfBusiness, Address, CityStateZip, PointOfContact, TypeOfService, ZipCode, State)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(query, (telephone, businessName, address, cityStateZip, pointOfContact, serviceType, zipCode, state))
            conn.commit()
           
            print(f"Provided data for {telephone} added to table.")
    """
    Returns a list of all providers from the database given a zip code and state.
    Return type: List
    """
    def get_providers(self, zipCode, state) -> list:
        conn = self.get_db()
        query = """
        SELECT *
        FROM Providers
        WHERE ZipCode = ? AND State = ?
        """
        cur = conn.cursor()
        cur.execute(query, (zipCode, state))
        return cur.fetchall()

    def get_db(self):
        return sqlite3.connect(DATABASE)
        
    def close_db(self, conn):
        if conn is not None:
            conn.close()

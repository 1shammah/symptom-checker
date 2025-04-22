from typing import Optional
import pandas as pd
import sqlite3

#Define the database class

class Database:
    def __init__(self, dbname="data/symptom_checker.db"):
        #intialising the database connection
        #tables already created in DB Browser
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.conn.row_factory = sqlite3.Row #allows us to access columns by name
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON") #enable foreign key constraints

    def create_tables(self):
        """Drop existent tables and create new ones for testing and dev purposes"""

        # Drop tables first (in reverse Foreign Key order)

        self.cur.execute("DROP TABLE IF EXISTS symptom_checks")
        self.cur.execute("DROP TABLE IF EXISTS symptom_precautions")
        self.cur.execute("DROP TABLE IF EXISTS symptom_severity")
        self.cur.execute("DROP TABLE IF EXISTS symptom_disease")
        self.cur.execute("DROP TABLE IF EXISTS symptoms")
        self.cur.execute("DROP TABLE IF EXISTS diseases")
        self.cur.execute("DROP TABLE IF EXISTS users")     

        # Create tables if they don't exist
        self.cur.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                email TEXT NOT NULL UNIQUE,
                                password TEXT NOT NULL,
                                gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female', 'Other')) DEFAULT 'Other',
                                role TEXT NOT NULL CHECK(role IN ('User', 'Admin')) DEFAULT 'User',
                                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                            )
                        """)

        self.cur.execute("""
                          CREATE TABLE IF NOT EXISTS diseases (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          disease_name TEXT NOT NULL UNIQUE
                          )
                          """)
        
        self.cur.execute("""
                        CREATE TABLE IF NOT EXISTS symptoms (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         symptom_name TEXT NOT NULL UNIQUE,
                         description TEXT
                         )
                        """)
        
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS symptom_disease (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         disease_id INTEGER NOT NULL,
                         symptom_id INTEGER NOT NULL,
                         FOREIGN KEY (disease_id) REFERENCES diseases(id),
                         FOREIGN KEY (symptom_id) REFERENCES symptoms(id)
                         )
                        """)
        
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS symptom_severity (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         symptom_id INTEGER NOT NULL,
                         severity_level TEXT NOT NULL,
                         FOREIGN KEY (symptom_id) REFERENCES symptoms(id)
                         )
                         """)
        self.cur.execute("""
                            CREATE TABLE IF NOT EXISTS symptom_precautions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                disease_id INTEGER NOT NULL,
                                precaution_steps TEXT NOT NULL,
                                FOREIGN KEY (disease_id) REFERENCES diseases(id)
                            )
                        """)
        self.cur.execute("""
                            CREATE TABLE IF NOT EXISTS symptom_checks (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                symptoms_selected TEXT NOT NULL,
                                predicted_disease TEXT NOT NULL,
                                check_date TEXT NOT NULL,
                                FOREIGN KEY (user_id) REFERENCES users(id)
                            )
                        """)
        # symptom_checks table is not used. I am not storing user history for now
        
        self.conn.commit()

        #since tables are already created, do I have to call this function

    '''
    def load_csv_data_to_db(self, csv_path, table_name):  
        #load the csv data to the database
        df = pd.read_csv(csv_path)

        #convert cloumns to lowercase for readablity
        df.columns = [col.lower() for col in df.columns]  #why a for a loop here?

        #insert into db table
        df.to_sql(table_name, self.conn, if_exists='append', index=False)

        #print success message
        print(f"Data loaded successfully to {table_name} table")
    '''


    def load_diseases_and_symptoms(self):
        #load diseases and symptoms into db from dataset.csv

        try:
            # read the csv file
            df= pd.read_csv('data/dataset.csv')

            # insert unique diseases into table
            diseases = [(row['Disease'].strip(),) for _, row in df.iterrows()]
            #insert into  db avoiding duplicates
            self.cur.executemany("INSERT OR IGNORE INTO diseases (disease_name) VALUES (?)", diseases)

            #insert unique symptoms into table
            symptoms_list = set()
            for _, row in df.iterrows():
                symptoms_list.update([str(row[f'Symptom_{i}']).strip() for i in range(1, 18) if pd.notna(row[f'Symptom_{i}'])])
            #convert to tuples for bulk insert
            symptoms_data = [(symptom,) for symptom in symptoms_list]
            #insert into  db avoiding duplicates
            self.cur.executemany("INSERT OR IGNORE INTO symptoms (symptom_name) VALUES (?)", symptoms_data)

            #fetch disease and symptoms IDs
            self.cur.execute("SELECT id, disease_name FROM diseases")
            disease_map = {name.strip(): id for id, name in self.cur.fetchall()}
            self.cur.execute("SELECT id, symptom_name FROM symptoms")
            symptom_map = {name.strip(): id for id, name in self.cur.fetchall()}

            #populate symptom_disease table
            symptom_disease_data = []
            for _, row in df.iterrows():
                disease_id = disease_map.get(row['Disease'])
                symptoms = [str(row[f'Symptom_{i}']).strip() for i in range(1, 18) if pd.notna(row[f'Symptom_{i}'])]
                symptom_disease_data.extend([(disease_id, symptom_map[symptom]) for symptom in symptoms if symptom in symptom_map])

            #batch insert into symptom_disease table
            self.cur.executemany("INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)", symptom_disease_data)

            #commit changes
            self.conn.commit()
            print("diseases and symptoms loaded successfully")

        except Exception as e:
            print(f"Error loading diseases: {e}")
            self.conn.rollback()
        
    def load_symptom_severity(self):
        #load symptom severity data into db from symptom-severity.csv
        
        try:
            # read symotom severity data
            df_severity = pd.read_csv('data/Symptom-severity.csv')

            # Fetch symptom IDs
            self.cur.execute("SELECT id, symptom_name FROM symptoms")
            symptom_map = {name.strip(): id for id, name in self.cur.fetchall()}

            # Prepare symptom severity data for insertion
            severity_data = []
            for _, row in df_severity.iterrows():
                # strip spaces and handle missing values
                symptom_name = str(row['Symptom']).strip() if pd.notna(row['Symptom']) else ''
                severity_level = str(row['weight']).strip() if pd.notna(row['weight']) else ''

                # check if symptom_name and severity_level are not empty
                if symptom_name and severity_level:
                    # check if symptom exists in symptom_map
                    symptom_id = symptom_map.get(symptom_name)
                    if symptom_id:
                        severity_data.append((symptom_id, severity_level))
                    else: 
                        print(f"Symptom '{symptom_name}' not found in symptoms table. check code again.")

            # insert severity data into db

            if severity_data:
                self.cur.executemany("INSERT INTO symptom_severity (symptom_id, severity_level) VALUES (?, ?)", severity_data)
                self.conn.commit()
                print("Symptom severity data loaded successfully from Symptom-severity.csv")
            else:
                print("No valid severity data to insert.")

        except Exception as e:
            print(f"Error loading symptom severity data: {e}")
            self.conn.rollback()
        
    def load_symptom_descriptions(self):
        """Load symptom descriptions from symptom-description.csv into the database"""

        try:
            df_description = pd.read_csv('data/symptom_Description.csv')

            # Fetch symptom IDs
            self.cur.execute("SELECT id, symptom_name FROM symptoms")
            symptom_map = {name.strip(): id for id, name in self.cur.fetchall()}
        
            # Prepare symptom description data for insertion
            description_data = []
            
            for _, row in df_description.iterrows():
                symptom_name = row['Disease'].strip()
                description = row['Description'].strip()

                # Only add description if symptom exists
                symptom_id = symptom_map.get(symptom_name)
                if symptom_id:
                    description_data.append((description, symptom_id))

            #update sytmpom table with description

            self.cur.executemany("UPDATE symptoms SET description = ? WHERE id = ?", description_data)

            self.conn.commit()
            print(f"Symptom descriptions loaded successfully from symptom_Description.csv. Total records updated: {len(description_data)}")

        except Exception as e:
            print(f"Error loading symptom descriptions: {e}")
            self.conn.rollback()


    def load_symptom_precautions(self):
        """Load symptom precautions from symptom_precautions.csv into the database"""

        try:
            df_precautions = pd.read_csv('data/symptom_precaution.csv')

            # fetch disease IDs
            self.cur.execute("SELECT id, disease_name FROM diseases")
            disease_map = {name.strip(): id for id, name in self.cur.fetchall()}

            # prepare symptom precautions data for insertion. Initialise a list to store the data
            precautions_data = []

            #iterate through each row in the dataframe
            for _, row in df_precautions.iterrows():
                disease_name = row['Disease'].strip() #disease name and clean it, stripping space

                #look up the the disease id using the disease name in the map dictionary
                disease_id = disease_map.get(disease_name)

                # check if the disease_id is found

                if disease_id:
                    #Collect all non-empty precaution steps from the row
                    precautions = [str(row[f'Precaution_{i}']).strip() for i in range(1, 5) if pd.notna(row[f'Precaution_{i}'])]

                    #join the list of precautions into a single comma separated string (coz theres 4 steps for each disease)
                    precautions_steps = ', '.join(precautions)

                    #add a tuple of (disease_id, precaution_steps) to list
                    precautions_data.append((disease_id, precautions_steps))

                else:
                    #log the disease not found
                    print(f"Disease '{disease_name}' not found in diseases table.")

            #if there is data to insert, execute a bulk insert

            if precautions_data:
                self.cur.executemany("INSERT INTO symptom_precautions (disease_id, precaution_steps) VALUES (?, ?)", precautions_data)

                #commit the changes to the database
                self.conn.commit()
                print("Symptom precautions loaded successfully from symptom_precaution.csv") 
                
        except Exception as e:
            print(f"Error loading symptom precautions: {e}")
            self.conn.rollback()


    
    #get all diseases from the database
    def get_all_diseases(self):    
        self.cur.execute("SELECT * FROM diseases")
        return self.cur.fetchall()
    
    #get all symptoms from the database
    def get_all_symptoms(self):
        self.cur.execute("SELECT * FROM symptoms")
        return self.cur.fetchall()
    
    #get all symptoms for a given disease
    def get_symptoms_by_disease(self, disease_name):
        try:
            
            self.cur.execute("""
                SELECT symptoms.symptom_name
                FROM symptoms
                JOIN symptom_disease ON symptoms.id = symptom_disease.symptom_id
                JOIN diseases ON symptom_disease.disease_id = diseases.id
                WHERE diseases.disease_name = ?
            """, (disease_name,))
            return [row["symptom_name"] for row in self.cur.fetchall()]
        
        except Exception as e:
            print(f"Error fetching symptoms for disease '{disease_name}': {e}")
            return []
    
    #get all diseases for a given symptom
    def get_diseases_by_symptom(self, symptom_name):
        try:
            self.cur.execute("""
                SELECT diseases.disease_name
                FROM diseases
                JOIN symptom_disease ON diseases.id = symptom_disease.disease_id
                JOIN symptoms ON symptom_disease.symptom_id = symptoms.id
                WHERE symptoms.symptom_name = ?
            """, (symptom_name,))
            return [row["disease_name"] for row in self.cur.fetchall()]
        
        except Exception as e:
            print(f"Error fetching diseases for symptom '{symptom_name}': {e}")
            return []
    

    #gert all symptom descriptions for a given symptom
    def get_description_by_symptom(self, symptom_name):
        try:
        
            self.cur.execute("""
                SELECT symptoms.description
                FROM symptoms
                WHERE symptoms.symptom_name = ?
            """, (symptom_name,))

            row = self.cur.fetchone()
            return row["description"] if row else None
    
        except Exception as e:
            print(f"Error fetching description for symptom '{symptom_name}': {e}")
            return None

    #get all precautions for a given disease
    def get_precautions_by_disease(self, disease_name):
        try:

            self.cur.execute("""
                SELECT symptom_precautions.precaution_steps
                FROM symptom_precautions
                JOIN diseases ON symptom_precautions.disease_id = diseases.id
                WHERE diseases.disease_name = ?
            """, (disease_name,))

            row = self.cur.fetchone()
            return row["precaution_steps"].split(', ') if row else None
    
        except Exception as e:
            print(f"Error fetching precautions for disease '{disease_name}': {e}")
            return None

    #get all severity levels for a given symptom
    def get_severity_by_symptom(self, symptom_name):
        try:
        
            self.cur.execute("""
                SELECT symptom_severity.severity_level
                FROM symptom_severity
                JOIN symptoms ON symptom_severity.symptom_id = symptoms.id
                WHERE symptoms.symptom_name = ?
            """, (symptom_name,))

            row = self.cur.fetchone()
            return row["severity_level"] if row else None
    
        except Exception as e:
            print(f"Error fetching severity for symptom '{symptom_name}': {e}")
            return None

    
    # Helper function to prepare disease-symptom data for AI training.
    # Returns a DataFrame where each row represents a disease and all its associated symptoms
    # concatenated into a single string. This format is ideal for content-based filtering using
    # TF-IDF and cosine similarity in the Recommender model.
    
    def get_disease_symptom_matrix(self):
        """Returns a DataFrame with diseases and associated symptoms as as single string. for AI training."""

        try:
            # fetch all disease -> symptom pairs
            self.cur.execute("""
                SELECT diseases.disease_name, symptoms.symptom_name
                FROM diseases
                JOIN symptom_disease ON diseases.id = symptom_disease.disease_id
                JOIN symptoms ON symptom_disease.symptom_id = symptoms.id
            """)

            rows = self.cur.fetchall()

            #group symptoms by disease
            df = pd.DataFrame(rows, columns=["disease", "symptom"])
            grouped = df.groupby("disease")["symptom"].apply(lambda x: ' '.join(sorted(set(x)))).reset_index()

            return grouped
        
        except Exception as e:
            print(f"Error generating disease-symptom matrix: {e}")
            return pd.DataFrame()
        

    ## Helper functions for users

    def add_user(self, name, email, hashed_password, gender="Other", role="User"):
        """
        Adds a new user to the database.

        Parameters:
        - name (str): The full name of the user.
        - email (str): unique user email.
        - hashed_password (str): The hashed password of the user. 
          Ensure this is securely hashed using a library like bcrypt
        - gender (str): The gender of the user. Defaults to "Other".
        - role (str): The role of the user ('user' or 'admin'). Defaults to 'User'.

        Returns:
        - bool: True if the user was added successfully, False otherwise.
        """    

        try:
            self.cur.execute("""
                INSERT INTO users (name, email, password, gender, role) VALUES (?, ?, ?, ?, ?)""",
                (name, email, hashed_password, gender, role))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
            
    def get_user_by_email(self, email):
        """
        Fetches a user record from the database by their email.

        Parameters:
        - email (str): The email of the user to fetch.

        Returns:
        - sqlite3.Row | None: The user record if found, otherwise None.
        """
        
        try:
            self.cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            return self.cur.fetchone()
        except Exception as e:
            print(f"Error fetching user by email '{email}': {e}")
            return None
        

    def email_exists(self,email):
        """
        Checks if an email already exists in the database.

        Parameters:
        - email (str): The email to check.

        Returns:
        - bool: True if the email exists, False otherwise.
        """
        
        try:
            self.cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            return self.cur.fetchone() is not None
        except Exception as e:
            print(f"Error checking if email '{email}' exists: {e}")
            return False

    def get_user_by_id(self, user_id):
        """
        Fetches a user from the database by their ID.

        Parameters:
        - user_id (int): The ID of the user to fetch.

        Returns:
        - sqlite3.Row | None: The user record if found, otherwise None.
        """
        
        try:
            self.cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return self.cur.fetchone()
        except Exception as e:  
            print(f"Error fetching user by ID: {e}")
            return None
        
    
    def get_all_users(self):
        """
        Fetches all users from the database. For admin use.

        Returns:
        - list[sqlite3.Row]: A list of all user records.
        """
        
        try:
            self.cur.execute("SELECT * FROM users")
            return self.cur.fetchall()
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []

## helper methods for CRUD actions in the user model

    def update_user(self, user_id: int, name: str, gender: str) -> bool:
        """
        Updates user's name and gender
        Email not included. It's a unique identifier. Changing would require reverifying the new email.

        Returns:
        - bool: True if the update was successful, False otherwise.
        """

        try:
            self.cur.execute("""
                UPDATE users
                SET name = ?, gender =  ?
                WHERE id = ?             
                """, (name, gender, user_id))
            self.conn.commit()
            return self.cur.rowcount > 0
        except Exception as e:
            print(f"Error updatiing profile: {e}")
            return False
        
    def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """
        Updates user's password. Password must already be hashed with bcrypt.

        Returns:
        - bool: True if the update was successful, False otherwise.
        """

        try:
            self.cur.execute("""
                UPDATE users
                SET password = ?
                WHERE id = ?
                """, (hashed_password, user_id))
            self.conn.commit()
            return self.cur.rowcount > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
        
    def get_user_password_hash(self, user_id: int) -> Optional[str]:
        """
        Fetches the stored hashed password for password comparison when updating/deleting
        
        Returns:
            str | None: The hashed password if found, otherwise None.

        """

        try:
            self.cur.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            row = self.cur.fetchone()
            return row["password"] if row else None
        except Exception as e:
            print(f"Error fetching user password hash: {e}")
            return None
        
    def delete_user_by_id(self, user_id: int) -> bool:
        """
        Deletes the user account by ID. This is irreversible.should be protected by authentication
        
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            self.cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
            return self.cur.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

#create tables if they don't exist
db = Database()
db.create_tables()

#load data into db
db.load_diseases_and_symptoms()
db.load_symptom_severity()
db.load_symptom_descriptions()
db.load_symptom_precautions()

#close the connection to the database
#db.conn.close()
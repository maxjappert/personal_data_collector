import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

date_format = '%d.%m.%y'

BASE_DIR = Path(__file__).resolve().parent

def convert_bool_string_to_intbool(yn_string: str):
    if yn_string.lower() == 'y':
        return 1
    elif yn_string.lower() == 'n':
        return 0
    else:
        return -1

def main():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'data.db'))
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS day_tracker (
        timestamp REAL PRIMARY KEY,
        overall_quality INTEGER,
        rumination INTEGER,
        out_of_breath INTEGER,
        meditated INTEGER,
        num_caffeine INTEGER,
        num_cigarettes INTEGER,
        wakeup_time TEXT,
        sleep_time TEXT,
        alcohol INTEGER,
        weed INTEGER,
        dream STRING,
        main_takeaway STRING
    )
    ''')

    cur.execute("SELECT COUNT(*) FROM day_tracker")
    initial_entries = cur.fetchone()[0]
    print(f'Hello, welcome to your own personal data tracker. We currently have {initial_entries} entries!')
    date_str = input('Please enter the date you want to update (dd.mm.yy): ')

    # Normalised to UTC
    date_obj = datetime.strptime(date_str, date_format).replace(tzinfo=timezone.utc)
    timestamp = date_obj.timestamp()

    cur.execute(f"SELECT 1 FROM day_tracker WHERE timestamp = ? LIMIT 1", (timestamp,))

    # Case where there is already an entry for that date
    if cur.fetchone() is not None:
        to_delete = input('There is already an entry for this timestamp. Shall it be deleted? (y/[n]): ')

        if to_delete.lower() == 'y':
            cur.execute(f"DELETE FROM day_tracker WHERE timestamp = {timestamp}")
            print("Okay, the old entry has been deleted. Let's continue.")

    print('Please answer the following questions, pertaining to the day of interest:')

    # TODO: proper error handling
    # Here the questions are asked
    overall_quality = int(input('Overall quality of the day (1-10): '))
    assert list(range(1, 11)).__contains__(overall_quality)

    rumination = convert_bool_string_to_intbool(input('Did you have a headache-inducing rumination attack? (y/n) '))

    out_of_breath = -1

    while out_of_breath == -1:
        out_of_breath = convert_bool_string_to_intbool(input('Were you out of breath today, i.e., exercise or similar? (y/n) '))

    meditated = -1

    while meditated == -1:
        meditated = convert_bool_string_to_intbool(input('Did you meditate for at least 10 minutes? (y/n) '))

    num_caffeine = int(input('How many caffeinated drinks did you consume? '))
    assert(0 <= num_caffeine)

    num_cigarettes = int(input('How many cigarettes did you (roughly) smoke? '))
    assert(0 <= num_cigarettes)

    wakeup_time = input('When did you start your day? (hh:mm) ')

    bedtime = input('When did you go to bed? (hh:mm) ')

    drank_alcohol = -1

    while drank_alcohol == -1:
        drank_alcohol = convert_bool_string_to_intbool(input('Did you drink alcohol? (y/n) '))

    smoked_weed = -1

    while smoked_weed == -1:
        smoked_weed = convert_bool_string_to_intbool(input('Did you smoke weed? (y/n) '))

    dream = input("What did you dream? Leave empty if you didn't dream anything. ")

    main_takeaway = input('What is your main take-away of the day? ')

    cur.execute("""
    INSERT OR REPLACE INTO day_tracker (
      timestamp, overall_quality, rumination, out_of_breath, meditated,
      num_caffeine, num_cigarettes, wakeup_time, sleep_time,
      alcohol, weed, dream, main_takeaway
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, overall_quality, rumination, out_of_breath, meditated,
        num_caffeine, num_cigarettes, wakeup_time, bedtime,
        drank_alcohol, smoked_weed, dream, main_takeaway
    ))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM day_tracker")
    final_entries = cur.fetchone()[0]

    assert final_entries == initial_entries + 1, "ERROR: The entry wasn't added to the database for some reason."

    print('Entry saved. Have a fantastic day!')

if __name__ == "__main__":
    main()
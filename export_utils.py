import pandas as pd

def export_user_data(username):
    try:
        df = pd.read_excel("workout_data.xlsx", sheet_name=username)
    except Exception:
        return None

    if df.empty:
        return None

    filename = f"{username}_workout_stats.xlsx"
    df.to_excel(filename, index=False)
    return filename

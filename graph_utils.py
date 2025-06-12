import pandas as pd
import matplotlib.pyplot as plt

def generate_exercise_graph(exercise_name: str, username: str, output_file="graph.png"):
    try:
        df = pd.read_excel("workout_data.xlsx", sheet_name=username)
    except FileNotFoundError:
        return False
    except Exception:
        return False

    df = df[df["Упражнение"].str.lower() == exercise_name.lower()]
    if df.empty:
        return False

    df["Дата"] = pd.to_datetime(df["Дата"])
    df = df.sort_values("Дата")

    plt.figure(figsize=(10, 5))
    plt.plot(df["Дата"], df["Вес"], marker="o", label="Вес (кг)", color="blue")
    plt.title(f"Прогресс: {exercise_name}")
    plt.xlabel("Дата")
    plt.ylabel("Вес (кг)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return True

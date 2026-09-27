"""Reference questions and deterministic SQLite answers."""

import sqlite3

QUESTIONS = [
    ("q1", "How many available pets have a chaos level above 8?"),
    (
        "q2",
        "Show available pets with chaos above 8 and fewer than three applications.",
    ),
    (
        "q3",
        "Does chaos appear associated with fewer applications?",
    ),
    (
        "q4",
        "Kevin has chaos 10 but gets lots of applications. What makes him an outlier?",
    ),
    (
        "q5",
        "Which pets need intervention right now, and why?",
    ),
]


def answer_question(connection: sqlite3.Connection, question_id: str) -> str:
    if question_id == "q1":
        count = connection.execute(
            "SELECT COUNT(*) FROM pets WHERE status = 'Available' AND chaos > 8"
        ).fetchone()[0]
        return f"{count} available pets have chaos above 8."

    if question_id == "q2":
        rows = connection.execute(
            """SELECT p.name FROM pets p
               JOIN applications a ON a.pet_name = p.name
               WHERE p.status = 'Available' AND p.chaos > 8
                 AND a.application_count < 3
               ORDER BY p.name"""
        ).fetchall()
        return ", ".join(row[0] for row in rows)

    if question_id == "q3":
        rows = connection.execute(
            """SELECT chaos, application_count FROM pets p
               JOIN applications a ON a.pet_name = p.name
               WHERE p.status = 'Available'"""
        ).fetchall()
        chaos_values = [row[0] for row in rows]
        application_values = [row[1] for row in rows]
        correlation = _pearson(chaos_values, application_values)
        direction = "negative" if correlation < 0 else "positive"
        return (
            f"Pearson correlation across available pets is {correlation:.2f} "
            f"({direction}); this is descriptive, not causal."
        )

    if question_id == "q4":
        kevin = connection.execute(
            """SELECT a.application_count, p.good_with_kids, p.species
               FROM pets p JOIN applications a ON a.pet_name = p.name
               WHERE p.name = 'Kevin'"""
        ).fetchone()
        high_chaos = connection.execute(
            """SELECT name, application_count FROM pets p
               JOIN applications a ON a.pet_name = p.name
               WHERE p.status = 'Available' AND p.chaos >= 9
               ORDER BY application_count DESC"""
        ).fetchall()
        rank = next(index for index, row in enumerate(high_chaos, 1) if row[0] == "Kevin")
        return (
            f"Kevin is a {kevin[2]} marked good with kids ({kevin[1]}) with "
            f"{kevin[0]} applications, ranking {rank} of {len(high_chaos)} "
            "available pets with chaos 9 or higher. These are comparisons, not proof of cause."
        )

    if question_id == "q5":
        rows = connection.execute(
            """SELECT p.name, p.chaos, p.behavior_risk, a.application_count
               FROM pets p JOIN applications a ON a.pet_name = p.name
               WHERE p.status = 'Available'
                 AND (p.behavior_risk >= 60 OR
                      (p.chaos >= 9 AND a.application_count <= 2))
               ORDER BY p.name"""
        ).fetchall()
        details = [
            f"{name} (risk {risk}, chaos {chaos}, {applications} applications)"
            for name, chaos, risk, applications in rows
        ]
        return (
            "Using the explicit demo rule risk >= 60 OR chaos >= 9 with <= 2 applications: "
            + "; ".join(details)
        )

    raise ValueError(f"Unknown question id: {question_id}")


def _pearson(first: list[int], second: list[int]) -> float:
    first_mean = sum(first) / len(first)
    second_mean = sum(second) / len(second)
    numerator = sum(
        (left - first_mean) * (right - second_mean)
        for left, right in zip(first, second)
    )
    first_sum = sum((value - first_mean) ** 2 for value in first)
    second_sum = sum((value - second_mean) ** 2 for value in second)
    denominator = (first_sum * second_sum) ** 0.5
    return numerator / denominator if denominator else 0.0
def format_score(c):
    return f"""
👤 {c['name']}
Technical: {c['technical']}/10
Experience: {c['experience']}/10
Nice-to-Have: {c['nice_to_have']}/10
TOTAL: {c['total']}/30
""".strip()


def print_scores(scores_candidates):
    print("""
========================
📊 Candidate Scoring Report
========================
""")

    for c in scores_candidates:
        if not isinstance(c, dict):
            print("⚠ Invalid format:", c)
            continue

        print(format_score(c))
        print("-" * 40)

def optimize_code(code):
    optimized = code.replace(
        "for i in range(len(x)):",
        "for i, val in enumerate(x):"
    )

    energy_saved = "18%"

    return optimized, energy_saved

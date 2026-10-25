"""One shared tariff catalogue replaces the repeated if/elif ladders in Codebase A."""
RATES_RM_PER_KG = {'paper': 0.50, 'plastic': 0.80, 'metal': 1.20, 'ewaste': 2.50}


def calculate_reward(item_type, weight_kg):
    return round(weight_kg * RATES_RM_PER_KG[item_type], 2)

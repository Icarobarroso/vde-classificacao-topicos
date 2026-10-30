import numpy as np
from scipy.stats import norm

def wilson_interval(successes, trials, confidence=0.95):
    if trials == 0:
        return 0.0, (0.0, 0.0)
    p = successes / trials
    z = norm.ppf(1 - (1 - confidence) / 2)
    denom = 1 + z**2 / trials
    centre = (p + z**2 / (2 * trials)) / denom
    margin = z * np.sqrt(p * (1 - p) / trials + z**2 / (4 * trials**2)) / denom
    lower = max(0.0, centre - margin)
    upper = min(1.0, centre + margin)
    return p, (lower, upper)

# Cobertura nas 100 questões da folha verdade
p_cov, (cov_low, cov_up) = wilson_interval(21, 100, confidence=0.95)

# Precisão nas publicadas (21 de 21)
p_prec, (prec_low, prec_up) = wilson_interval(21, 21, confidence=0.95)

print(f"Cobertura observada: {p_cov:.2f} | Intervalo 95%: {cov_low:.2f} - {cov_up:.2f}")
print(f"Precisão observada: {p_prec:.2f} | Intervalo 95%: {prec_low:.2f} - {prec_up:.2f}")

# Estimativa conservadora esperada para as 559 questões fora da folha verdade:
# Cobertura esperada: 0.21 (intervalo 0.15 - 0.28)
# Precisão esperada: 0.96 (intervalo 0.95 - 1.00)

import numpy as np
import matplotlib.pyplot as plt

# ==============================
# CONFIGURATION
# ==============================

np.random.seed(42)

# Distribution parameters (can be tuned)
MU_T = 2.0       # lognormal mean
SIGMA_T = 0.5    # lognormal std

MU_P = 2.0       # kW
SIGMA_P = 0.3

C_MIN = 0.2      # kg CO2 / kWh
C_MAX = 0.8

# ==============================
# EXERCISE 1: BASIC MONTE CARLO
# ==============================

def sample_T(n):
    """Sample training time"""
    return np.random.lognormal(mean=MU_T, sigma=SIGMA_T, size=n)

def sample_P(n):
    """Sample power consumption"""
    return np.random.normal(loc=MU_P, scale=SIGMA_P, size=n)

def sample_C(n):
    """Sample carbon intensity"""
    return np.random.uniform(C_MIN, C_MAX, size=n)

def monte_carlo_estimate(n):
    """Compute MC estimate of emissions"""
    
    T = sample_T(n)
    P = sample_P(n)
    C = sample_C(n)

    E = T * P * C

    mean = np.mean(E)
    var = np.var(E, ddof=1)
    std_error = np.sqrt(var / n)

    return mean, var, std_error, E


def confidence_interval(mean, std_error, z=1.96):
    """Compute 95% CI"""
    return mean - z * std_error, mean + z * std_error


def plot_convergence(max_n=10000, step=500):
    estimates = []
    ns = []

    for n in range(step, max_n + 1, step):
        mean, _, _, _ = monte_carlo_estimate(n)
        estimates.append(mean)
        ns.append(n)

    plt.plot(ns, estimates)
    plt.xlabel("Number of samples")
    plt.ylabel("Estimated emissions")
    plt.title("Monte Carlo Convergence")
    plt.show()


# ==============================
# EXERCISE 2: IMPORTANCE SAMPLING
# ==============================

def proposal_C(n):
    """
    Proposal distribution q(C)
    TODO: Modify to oversample high carbon values
    """
    return np.random.uniform(0.5, 1.0, size=n)  # biased toward high values


def target_pdf_C(c):
    """Target PDF p(C) for Uniform(C_MIN, C_MAX)"""
    return np.where((c >= C_MIN) & (c <= C_MAX), 1.0 / (C_MAX - C_MIN), 0.0)


def proposal_pdf_C(c):
    """Proposal PDF q(C)"""
    return np.where((c >= 0.5) & (c <= 1.0), 1.0 / (1.0 - 0.5), 0.0)


def importance_sampling_estimate(n):
    T = sample_T(n)
    P = sample_P(n)
    C = proposal_C(n)

    # TODO: Compute importance weights
    weights = target_pdf_C(C) / proposal_pdf_C(C)

    E = T * P * C * weights

    mean = np.mean(E)
    var = np.var(E, ddof=1)
    std_error = np.sqrt(var / n)

    return mean, var, std_error


# ==============================
# EXERCISE 3: CONTROL VARIATES
# ==============================

def control_variates_estimate(n):
    T = sample_T(n)
    P = sample_P(n)
    C = sample_C(n)

    E = T * P * C
    X = T * P  # control variable

    # Analytical expectation (students should verify)
    EX = np.exp(MU_T + 0.5 * SIGMA_T**2) * MU_P

    # TODO: Estimate covariance and variance
    cov = np.cov(X, E)[0, 1]
    var_X = np.var(X, ddof=1)

    # TODO: Compute optimal coefficient
    c = cov / var_X

    # TODO: Apply control variate correction
    E_cv = E - c * (X - EX)

    mean = np.mean(E_cv)
    var = np.var(E_cv, ddof=1)
    std_error = np.sqrt(var / n)

    return mean, var, std_error


# ==============================
# COMPARISON FUNCTION
# ==============================

def compare_methods(n=5000):
    print("Running comparison with n =", n)

    mc_mean, mc_var, mc_se, _ = monte_carlo_estimate(n)
    is_mean, is_var, is_se = importance_sampling_estimate(n)
    cv_mean, cv_var, cv_se = control_variates_estimate(n)

    print("\n--- Results ---")
    print(f"Monte Carlo:       mean={mc_mean:.4f}, var={mc_var:.4f}")
    print(f"Importance Samp.:  mean={is_mean:.4f}, var={is_var:.4f}")
    print(f"Control Variates:  mean={cv_mean:.4f}, var={cv_var:.4f}")


# ==============================
# MAIN (for testing)
# ==============================

if __name__ == "__main__":
    n = 5000

    mean, var, se, _ = monte_carlo_estimate(n)
    ci = confidence_interval(mean, se)

    print("Monte Carlo estimate:", mean)
    print("95% CI:", ci)

    compare_methods(n)
    plot_convergence()
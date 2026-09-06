import numpy as np

class ChangepointDetector:
    """Simplified BOCPD (Bayesian Online Changepoint Detection)."""

    def __init__(self, hazard: float = 1/100.0, mu0: float = 0.0, var0: float = 1.0, alpha: float = 1.0, beta: float = 1.0):
        self.hazard = hazard
        self.mu0 = mu0
        self.var0 = var0
        self.alpha0 = alpha
        self.beta0 = beta
        
        self.T = 0
        # Initialize run length probabilities
        self.R = np.zeros(1)
        self.R[0] = 1.0
        
        # Sufficient statistics arrays
        self.muT = np.array([mu0])
        self.varT = np.array([var0])
        self.alphaT = np.array([alpha])
        self.betaT = np.array([beta])

    def _student_pdf(self, x, mu, var, nu):
        # Simplified Student-T log pdf for predictive distribution
        import scipy.stats as stats
        return stats.t.pdf(x, df=nu, loc=mu, scale=np.sqrt(var))

    def update(self, x: float) -> np.ndarray:
        """Process one data point online and return run-length probabilities."""
        self.T += 1
        
        # 1. Evaluate predictive probabilities
        pred_probs = self._student_pdf(x, self.muT, self.betaT * (self.varT + 1) / (self.alphaT * self.varT), 2 * self.alphaT)
        
        # 2. Calculate growth probabilities
        R_grow = self.R * pred_probs * (1 - self.hazard)
        
        # 3. Calculate changepoint probabilities
        R_cp = np.sum(self.R * pred_probs * self.hazard)
        
        # 4. Update run length distribution
        self.R = np.append([R_cp], R_grow)
        self.R /= np.sum(self.R) # normalize
        
        # 5. Update sufficient statistics
        new_mu = (self.varT * self.muT + x) / (self.varT + 1)
        new_var = self.varT + 1
        new_alpha = self.alphaT + 0.5
        new_beta = self.betaT + 0.5 * (x - self.muT)**2 * self.varT / (self.varT + 1)
        
        self.muT = np.append([self.mu0], new_mu)
        self.varT = np.append([self.var0], new_var)
        self.alphaT = np.append([self.alpha0], new_alpha)
        self.betaT = np.append([self.beta0], new_beta)
        
        return self.R

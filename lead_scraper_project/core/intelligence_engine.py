import math

class IntelligenceEngine:
    """
    Advanced Scoring and Classification Engine for Lead Intelligence.
    Transforms raw scraped data into decision-support metrics.
    """
    
    TARGET_CATEGORIES = ["yoga", "dance", "coaching", "fitness", "gym"]
    MAX_REVIEWS_CEILING = 5000.0  

    @staticmethod
    def _clean_numeric(value, is_float=False):
        """Extracts and parses numbers from messy strings like '1,234 reviews'."""
        import re
        if value is None:
            return 0.0 if is_float else 0
            
        text = str(value)
        match = re.search(r"[\d,]+(?:\.\d+)?", text)
        if match:
            clean_str = match.group(0).replace(",", "")
            try:
                return float(clean_str) if is_float else int(float(clean_str))
            except ValueError:
                return 0.0 if is_float else 0
        return 0.0 if is_float else 0

    GLOBAL_MEAN_RATING = 3.8      # C parameter for Bayesian smoothing
    MIN_PRIOR_REVIEWS = 15.0      # m parameter for Bayesian smoothing

    @classmethod
    def calculate_score(cls, rating: float, reviews: int, category: str) -> tuple[float, float]:
        """Runs the D-AEDSA (Dynamic-Adaptive Engagement Density Scoring Algorithm)."""
        rating_val = float(rating) if rating is not None else 3.5
        reviews_val = int(reviews) if reviews is not None else 5
        
        # Safe defaults
        if rating_val <= 0: rating_val = 3.5
        if reviews_val <= 0: reviews_val = 5
        
        cat_lower = str(category).lower() if category else ""

        # 1. Bayesian Target Smoothing (Cold Start Mathematical Solution)
        # Formula: (v/(v+m)) * R + (m/(v+m)) * C
        v = float(reviews_val)
        m = cls.MIN_PRIOR_REVIEWS
        C = cls.GLOBAL_MEAN_RATING
        
        bayesian_rating = ((v / (v + m)) * rating_val) + ((m / (v + m)) * C)
        rating_norm = bayesian_rating / 5.0

        # 2. Logarithmic Monopoly Suppression
        reviews_norm = math.log10(1 + reviews_val) / math.log10(1 + cls.MAX_REVIEWS_CEILING)

        # 3. Dynamic Matrix Shifts (Adaptive Weighting)
        if reviews_val < 20:
            base_score = (0.75 * rating_norm) + (0.25 * reviews_norm)
        else:
            base_score = (0.55 * rating_norm) + (0.45 * reviews_norm)

        # 4. SaaS Relevance Boosting
        category_weight = 1.25 if any(t in cat_lower for t in cls.TARGET_CATEGORIES) else 1.0

        # 5. Wilson-inspired Statistical Confidence Iteration
        confidence = 0.5 + min(reviews_val / 150.0, 0.5)

        raw_score = base_score * category_weight * confidence * 100
        final_score = max(30.0, min(95.0, raw_score))
        
        # 6. ML Output Layer: Sigmoid Activation Function for True Probability Mapping
        # Maps the linear final_score into an S-curve probability model centered around x0=65
        k = 0.15 # Steepness 
        x0 = 65.0 # Activation Midpoint
        
        sigmoid_prob = 1.0 / (1.0 + math.exp(-k * (final_score - x0)))
        
        # Scale Sigmoid output (0-1) to B2B actionable percentage
        conversion_prob = max(12.0, min(98.5, sigmoid_prob * 100.0))
        
        return round(final_score, 2), round(conversion_prob, 1)

    @classmethod
    def generate_reason(cls, rating: float, reviews: int) -> str:
        """Generates purely positive, human-centric reasoning."""
        rating_val = rating if rating is not None and rating > 0 else 3.5
        reviews_val = reviews if reviews is not None and reviews > 0 else 5

        if rating_val >= 4.5 and reviews_val >= 100:
            return "Highly rated with strong and consistent customer activity."
        elif rating_val >= 4.0 and reviews_val >= 20:
            return "Well-rated and growing reliable customer engagement."
        elif rating_val >= 4.0:
            return "Strong quality signals with early customer collaboration opportunities."
        else:
            return "Emerging business with solid early collaboration opportunity."

    @classmethod
    def generate_message(cls, category: str) -> str:
        cat_str = category.lower().strip() if category else "local"
        if not cat_str.endswith("s") and not cat_str.endswith("es"):
            cat_str += " businesses"
        # Dynamic premium message
        return f"Hi, we help {cat_str} attract more customers and grow faster. Would you be open to a quick collaboration?"

    @classmethod
    def enrich_lead(cls, lead: dict, category: str) -> dict:
        raw_rating = lead.get("rating")
        raw_reviews = lead.get("review_count") or lead.get("reviews")
        
        rating = cls._clean_numeric(raw_rating, is_float=True)
        reviews = int(cls._clean_numeric(raw_reviews, is_float=False))
        
        # Apply defaults at the base layer
        if rating <= 0: rating = 3.5
        if reviews <= 0: reviews = 5

        score, conv_prob = cls.calculate_score(rating, reviews, category)
        
        # Note: We assign dummy Priority and Action here just for DB constraints, 
        # actual Percentile ranking happens dynamically in the Dashboard UI.
        reason = cls.generate_reason(rating, reviews)
        message = cls.generate_message(category)

        enriched = list(lead.items())
        enriched_dict = dict(enriched)
        
        enriched_dict["rating"] = rating
        enriched_dict["reviews"] = reviews
        enriched_dict["score"] = score
        enriched_dict["conversion_prob"] = conv_prob
        enriched_dict["priority"] = "Unranked"
        enriched_dict["action"] = "Assess"
        enriched_dict["reason"] = reason
        enriched_dict["message"] = message
        enriched_dict["search_category"] = category
        
        return enriched_dict

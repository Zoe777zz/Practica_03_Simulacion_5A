from statistics import mean


class ResultAnalyzer:
    """Analyzer en memoria. No guarda CSV ni archivos de resultados."""

    @staticmethod
    def summarize(config, results):
        if not results:
            raise ValueError("No existen resultados para analizar.")

        first = results[0]
        return {
            "key": config.key,
            "scenario": config.name,
            "lambda": config.arrival_rate,
            "mu": config.service_rate,
            "condition": config.condition,
            "rho": first.theory.rho,
            "L": first.theory.L,
            "Lq": first.theory.Lq,
            "W": first.theory.W,
            "Wq": first.theory.Wq,
            "average_wait_sim": mean(r.average_wait_sim for r in results),
            "average_queue_sim": mean(r.average_queue_sim for r in results),
            "customers_completed_avg": mean(r.customers_completed for r in results),
            "repetitions": len(results),
        }

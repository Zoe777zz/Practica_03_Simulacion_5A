from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TheoryMetrics:
    rho: float
    L: float
    Lq: float
    W: float
    Wq: float


class TheoryStrategy(ABC):
    @abstractmethod
    def calculate(self, arrival_rate: float, service_rate: float) -> TheoryMetrics:
        raise NotImplementedError


class MM1TheoryStrategy(TheoryStrategy):
    """Strategy para las métricas teóricas de un sistema M/M/1."""

    def calculate(self, arrival_rate: float, service_rate: float) -> TheoryMetrics:
        if arrival_rate <= 0 or service_rate <= 0:
            raise ValueError("λ y μ deben ser mayores que cero.")
        if arrival_rate >= service_rate:
            raise ValueError("El sistema no es estable: debe cumplirse λ < μ.")

        rho = arrival_rate / service_rate
        L = arrival_rate / (service_rate - arrival_rate)
        Lq = (arrival_rate ** 2) / (service_rate * (service_rate - arrival_rate))
        W = 1 / (service_rate - arrival_rate)
        Wq = arrival_rate / (service_rate * (service_rate - arrival_rate))
        return TheoryMetrics(rho=rho, L=L, Lq=Lq, W=W, Wq=Wq)

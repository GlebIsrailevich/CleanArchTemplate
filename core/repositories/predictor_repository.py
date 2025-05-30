from typing import List

from core.entities.prediction import Prediction
from core.entities.predictor import Predictor
from core.repositories.base_repository import BaseRepository


class PredictorRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, Prediction)

    def create_predictor(self, predictor):
        with self.session_factory() as session:
            predictor = Predictor(**predictor)
            session.add(predictor)
            session.commit()
            session.refresh(predictor)
            return predictor

    def get_all_predictors(self) -> List[Predictor]:
        with self.session_factory() as session:
            return session.query(Predictor).all()

    def get_predictor_by_name(self, name: str) -> Predictor:
        with self.session_factory() as session:
            return session.query(Predictor).filter(Predictor.name == name).first()

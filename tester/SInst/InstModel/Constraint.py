class Constraint:
    def as_neg_constraint(self):
        raise NotImplementedError("as_new_eq not implemented")
    def can_neg(self)->bool:
        raise NotImplementedError("can_negate not implemented")
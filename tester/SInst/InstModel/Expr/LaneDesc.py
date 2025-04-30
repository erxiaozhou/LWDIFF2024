class LaneDesc:
    def __init__(self, 
                 lane_idx:int,
                 lane_type:str
                 ):
        self.lane_idx = lane_idx
        self.lane_type_repr = lane_type
        assert lane_type[1:].isdigit()
        assert lane_type[0] == 'i' or lane_type[0] == 'f'
        self.lane_bw = int(lane_type[1:])
        self.is_int = lane_type[0] == 'i'

    def __repr__(self):
        return f"LaneVal({self.lane_idx}, {self.lane_type_repr}, {self.lane_bw})"

    def __hash__(self) -> int:
        return hash((self.lane_idx, self.lane_type_repr, self.lane_bw))

    def __eq__(self, o: 'LaneDesc') -> bool:
        return self.lane_idx == o.lane_idx and self.lane_type_repr == o.lane_type_repr
